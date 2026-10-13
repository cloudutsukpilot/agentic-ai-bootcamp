# This placeholder will demonstrate the Microsoft Agent Framework tool decorator.
# This placeholder will demonstrate the Microsoft Agent Framework agent class.
# asyncio is Python's built-in library for coordinating asynchronous work.
# Import asyncio to run our agent coroutine on an event loop.
import asyncio
# os is Python's built-in operating-system interface.
# Import os to read configuration inherited by this process.
import os
# pathlib is Python's built-in library for filesystem paths.
# Import Path to locate the configuration file beside this script.
from pathlib import Path

# Agent Framework orchestrates agents; Foundry provides the remote model service.
# Import FoundryChatClient, an adapter for the project's OpenAI Responses API.
from agent_framework.foundry import FoundryChatClient
# Import Agent, the local orchestration object that sends instructions through the client.
from agent_framework import Agent, Message, tool
# Azure Identity obtains Entra tokens; access permissions must be assigned separately.
# Import the asynchronous credential so token acquisition fits this async workflow.
from azure.identity.aio import DefaultAzureCredential
# python-dotenv parses configuration without exporting it to the process environment.
# Import dotenv_values to obtain file settings as a dictionary.
from dotenv import dotenv_values

# Import randint from Python's standard library to make the weather demo output vary.
from random import randint

# __file__ identifies this script; with_name keeps its folder and replaces the filename.
# Create settings from the app-local file without printing any configuration values.
settings = dotenv_values(dotenv_path=Path(__file__).with_name(".env"))


# A helper function centralizes lookup and validation for required configuration.
# Define required_setting with a string name parameter and a string return annotation.
def required_setting(name: str) -> str:
    # Create value from the nonempty environment setting, otherwise the file dictionary.
    value = os.getenv(key=name) or settings.get(name)
    # Check whether neither source supplied a nonempty value.
    if not value:
        # Stop before authentication with an error identifying the setting, not its value.
        raise ValueError(f"Missing required Foundry setting: {name}")
    # Return the validated string to the calling client-configuration code.
    return value


# Use the framework decorator to wrap this function as a model-discoverable tool.
@tool
# Define an asynchronous tool with a location input and text result for the agent.
async def get_weather(location: str) -> str:
    # Document the tool's purpose and parameter so the decorator can describe it to the model.
    """Get weather for a location

    Args:
        location (str): The location to get the weather for.

    Returns:
        str: A string describing the weather for the given location.
    """
    # Simulate fetching weather by returning a random temperature.
    # Create conditions containing the weather labels this demo can report.
    conditions = ["sunny", "cloudy", "rainy", "snowy"]
    # Select one weather label using a random valid list index.
    condition = conditions[randint(0, len(conditions) - 1)]
    # Create temperature containing a random Celsius value for the response.
    temperature = randint(-10, 35)
    # Return the tool result that the agent can use when composing its answer.
    return f"The current temperature in {location} is {temperature}°C and the weather is {condition}."

# async def defines a coroutine function whose work is driven by an event loop.
# Define main without parameters; it prints the response and returns no value.
async def main() -> None:
    # Preserve the existing FOUNDARY_* spelling to keep this sample's configuration compatible.
    # Create model containing the Foundry model deployment name, not an agent identifier.
    model = required_setting("FOUNDARY_MODEL")
    # Create project_endpoint containing the Foundry project URL, not an Azure OpenAI resource URL.
    project_endpoint = required_setting("FOUNDARY_PROJECT_ENDPOINT")

    # DefaultAzureCredential tries supported identity sources when a token is requested.
    # Create credential in an async context that closes its transports even on failure.
    async with DefaultAzureCredential() as credential:
        # Create client for model communication; this does not provision a hosted Foundry agent.
        chat_client = FoundryChatClient(
            # Supply the selected deployment as the model keyword argument.
            model=model,
            # Supply the Foundry project URL used to obtain the Responses API client.
            project_endpoint=project_endpoint,
            # Supply the token credential; construction alone does not authenticate or grant RBAC.
            credential=credential,
        )
        # Close both the Azure project and OpenAI HTTP clients when this scope ends.
        async with chat_client.project_client, chat_client.client:
            # Create agent locally with this client and instructions for model behavior.
            agent = Agent(
                # Pass the chat client that connects this local agent to the remote model.
                client=chat_client,
                # Give the local agent a readable name; this is not a deployed resource ID.
                name="Sample MAF Foundry Agent",
                # Describe the sample's purpose for the agent configuration metadata.
                description="A sample agent that demonstrates the use of tools in the Microsoft Agent Framework.",
                # Supply behavior instructions separately from the user's request below.
                instructions="You are a helpful assistance agent that uses the Microsoft Agent Framework with Microsoft Foundary to answer queries.",
                # Register the decorated function so the model can request it during a run.
                tools=[get_weather]
            )

            # Create a structured user message whose contents ask for weather in India.
            user_message = Message(role="user", contents=["What is the weather in India today?"])

            # Await the remote model response without blocking the event loop; this call may incur cost.
            # Create response containing the completed agent result for this single prompt.
            response = await agent.run(user_message)
            # Print only the response text, never tokens or credential configuration.
            print(response.text)


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
