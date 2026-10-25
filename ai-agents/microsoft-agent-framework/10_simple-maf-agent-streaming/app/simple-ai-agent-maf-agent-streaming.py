# This entry point streams a local agent's answer to a structured user message.
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
from agent_framework import Agent, Message
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
                # Supply behavior instructions separately from the user's request below.
                instructions="You are a helpful agent that explains the Microsoft Agent Framework.",
            )

            # Create a structured message so the speaker role and content items are explicit.
            user_message = Message(
                # Identify the human speaker so the framework classifies this input as user content.
                role="user",
                # Store the prompt as one text item; the sequence can later contain other content types.
                contents=["Explain what is the Message Class in Microsoft Agent Framework with a short description and one example. Provide 10 bullet points about the Message Class."],
            )

            # Create stream to receive response updates before the full answer is ready.
            stream = agent.run(user_message, stream=True)
            # Wait asynchronously for each update without blocking the event loop.
            async for chunk in stream:
                # Inspect each content item because an update can mix text and other data.
                for content in chunk.contents:
                    # Print new text only; the final replace snapshot repeats the full answer.
                    if content.type == "text" and content.merge_mode != "replace":
                        # Display this text immediately without adding a newline between pieces.
                        print(content.text or "", end="", flush=True)
            # Finish the streamed answer with a newline so the shell prompt starts below it.
            print()

# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
