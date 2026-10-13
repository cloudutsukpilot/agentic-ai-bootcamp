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


@tool
async def get_weather(location: str) -> str:
    """Get weather for a location

    Args:
        location (str): The location to get the weather for.

    Returns:
        str: A string describing the weather for the given location.
    """
    # Simulate fetching weather by returning a random temperature.
    conditions = ["sunny", "cloudy", "rainy", "snowy"]
    condition = conditions[randint(0, len(conditions) - 1)]
    temperature = randint(-10, 35)
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
                description="A sample agent that demonstrates the use of tools in the Microsoft Agent Framework.",
                # Supply behavior instructions separately from the user's request below.
                instructions="You are a helpful assistance agent that uses the Microsoft Agent Framework with Microsoft Foundary to answer queries.",
                tools=[get_weather]
            )
            agent_session=agent.create_session()

            user_message1 = Message(role="user", contents=["Give me 5 bullet points about India"])
            response1 = await agent.run(user_message1, session=agent_session)
            print("---------- Response 1 ---------- ")
            print(response1.text)
            print("---------- End of Response 1 ---------- ")
            user_message2 = Message(role="user", contents=["Add one line description to the each of those bullet points."])
            response2 = await agent.run(user_message2, session=agent_session)
            print("---------- Response 2 ---------- ")
            print(response2.text)
            print("---------- End of Response 2 ---------- ")

            # Await the remote model response without blocking the event loop; this call may incur cost.
            # Create response containing the completed agent result for this single prompt.
            user_message3 = Message(role="user", contents=["Summarize all the above information in one paragraph."])
            response3 = await agent.run(user_message3, session=agent_session)
            # Print only the response text, never tokens or credential configuration.
            print(response3.text)


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
