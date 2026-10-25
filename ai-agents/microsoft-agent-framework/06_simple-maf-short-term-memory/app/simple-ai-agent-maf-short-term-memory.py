# This placeholder will demonstrate Microsoft Agent Framework short-term memory.
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

# Import randint from Python's standard library to make the weather demo output vary.
from random import randint

# Import Agent, the local orchestration object that sends instructions through the client.
from agent_framework import Agent, Message, tool

# Agent Framework orchestrates agents; Foundry provides the remote model service.
# Import FoundryChatClient, an adapter for the project's OpenAI Responses API.
from agent_framework.foundry import FoundryChatClient

# Azure Identity obtains Entra tokens; access permissions must be assigned separately.
# Import the asynchronous credential so token acquisition fits this async workflow.
from azure.identity.aio import DefaultAzureCredential

# python-dotenv parses configuration without exporting it to the process environment.
# Import dotenv_values to obtain file settings as a dictionary.
from dotenv import dotenv_values

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
    # Describe the tool so the framework can expose its purpose and parameter to the model.
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
                # Describe the local agent's purpose for the framework metadata.
                description="A sample agent that demonstrates the use of tools in the Microsoft Agent Framework.",
                # Supply behavior instructions separately from the user's request below.
                instructions="You are a helpful assistance agent that uses the Microsoft Agent Framework with Microsoft Foundary to answer queries.",
                # Register the decorated function so the model can request it during a run.
                tools=[get_weather]
            )
            # Create one in-process session so later runs can receive earlier conversation turns.
            agent_session=agent.create_session()

            # Create the first structured user message that starts the conversation context.
            user_message1 = Message(role="user", contents=["Give me 5 bullet points about India"])
            # Send the first message through the shared session and await the completed model response.
            response1 = await agent.run(user_message1, session=agent_session)
            # Print a label so the first response is easy to distinguish in the terminal.
            print("---------- Response 1 ---------- ")
            # Print only the first response text, not credentials or request metadata.
            print(response1.text)
            # Print a closing label for the first response block.
            print("---------- End of Response 1 ---------- ")
            # Create a follow-up message whose wording depends on the first response's context.
            user_message2 = Message(role="user", contents=["Add one line description to the each of those bullet points."])
            # Send the follow-up through the same session so earlier turns remain available.
            response2 = await agent.run(user_message2, session=agent_session)
            # Print a label so the second response is easy to distinguish in the terminal.
            print("---------- Response 2 ---------- ")
            # Print only the second response text generated with the shared conversation context.
            print(response2.text)
            # Print a closing label for the second response block.
            print("---------- End of Response 2 ---------- ")

            # Create the final structured message asking the agent to summarize the accumulated context.
            user_message3 = Message(role="user", contents=["Summarize all the above information in one paragraph."])
            # Await the third remote response without blocking the event loop; this call may incur cost.
            # Create response containing the completed agent result for the shared session's final turn.
            response3 = await agent.run(user_message3, session=agent_session)
            # Print only the final response text, never tokens or credential configuration.
            print(response3.text)


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
