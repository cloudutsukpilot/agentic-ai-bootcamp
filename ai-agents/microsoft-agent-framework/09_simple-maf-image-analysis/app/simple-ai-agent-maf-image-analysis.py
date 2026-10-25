# This sample sends image and text content to a Foundry model using Microsoft Agent Framework.
# It registers file-based long-term memory, but no MCP tools.
# Memories are saved as files on disk, so a brand-new session can still recall them.

# asyncio is Python's built-in library for coordinating asynchronous work.
# Import asyncio to run our agent coroutine on an event loop.
import asyncio

# os is Python's built-in operating-system interface.
# Import os to read configuration inherited by this process.
import os

# pathlib is Python's built-in library for filesystem paths.
# Import Path to locate configuration, the image, and memory beside this script.
from pathlib import Path

# Third-party Agent Framework orchestrates local agents; Foundry serves model requests.
# Import Agent (orchestration), Content (image/text payloads), and Message (a conversation item).
# Import FileMemoryProvider, a context provider that gives the agent file-based memory tools.
# Import FileSystemAgentFileStore, the disk-backed storage those memory tools read and write.
from agent_framework import Agent, Content, FileMemoryProvider, FileSystemAgentFileStore, Message
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

# Create MEMORY_DIR, the folder beside this script where long-term memory files are stored.
# Unlike a session, files in this folder survive after the script exits.
MEMORY_DIR = Path(__file__).with_name("memory_store")
# Create USER_ID, the memory scope that groups memories per user instead of per session.
# A real application would use the signed-in user's ID here; this demo uses a fixed value.
USER_ID = "demo_user"

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


# Define a helper function that prints which memory files currently exist on disk.
# This makes the "long-term" part visible: these files are the agent's durable memory.
def print_memory_files() -> None:
    # Print a heading so the file list is easy to spot in the output.
    print("------- Memory files on disk -------")

    # rglob("*") walks the memory folder and its subfolders; sorted gives a stable order.
    # Loop over every path found under the memory folder.
    for path in sorted(MEMORY_DIR.rglob("*")):
        # Skip folders; only files hold memory content.
        if path.is_file():
            # Print the path relative to the memory folder to keep the output short.
            print(path.relative_to(MEMORY_DIR))
    # Print a closing line to mark the end of the file list.
    print("-------- End of memory files ------------")



# async def defines a coroutine function whose work is driven by an event loop.
# Define main without parameters; it prints the responses and returns no value.
async def main() -> None:
    # Preserve the existing FOUNDARY_* spelling to keep this sample's configuration compatible.
    # Create model containing the Foundry model deployment name, not an agent identifier.
    model = required_setting("FOUNDARY_MODEL")
    # Create project_endpoint containing the Foundry project URL, not an Azure OpenAI resource URL.
    project_endpoint = required_setting("FOUNDARY_PROJECT_ENDPOINT")

    # Create memory_store, a disk-backed file store rooted at the MEMORY_DIR path.
    # Construction does not touch the disk; the folder is created on the first write.
    memory_store = FileSystemAgentFileStore(root_directory=MEMORY_DIR)
    # Create memory_provider, which adds file_memory_* tools and memory instructions to each run.
    # scope=USER_ID stores memories per user, so every new session for this user shares them.
    memory_provider = FileMemoryProvider(store=memory_store, scope=USER_ID)

    # Create image_path for the PNG beside this script, independent of the working directory.
    image_path = Path(__file__).resolve().with_name("sample-image.png")
    # Create image_data as raw bytes; read_bytes opens in binary mode and closes the file.
    image_data = image_path.read_bytes()

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

        # Enter both client contexts so their network resources are closed even if the run fails.
        async with chat_client.project_client, chat_client.client:
            # Create agent locally with this client, instructions, and memory provider.
            agent = Agent(
                # Pass the chat client that connects this local agent to the remote model.
                client=chat_client,
                # Give the local agent a readable name; this is not a deployed resource ID.
                name="Image Analysis Agent",
                # Describe the local agent's purpose for the framework metadata.
                description="An agent that analyzes the images provided to it and outlines key details.",
                # Supply behavior instructions separately from the user's request below.
                instructions=(
                    # Ask the model to analyze images and write relevant details into memory.
                    "You are a helpful assistant. When the user shares images, analyze them and store relevant details in memory in every session. "
                ),
                # Register the memory provider; it runs before and after every agent run.
                context_providers=[memory_provider],
                # Register no extra tools; the context provider supplies memory tools separately.
                tools=[]
            )

            # Session A: the first conversation, where the user shares facts worth remembering.
            # Create session_a, a fresh in-process session with no earlier conversation turns.
            session_a=agent.create_session()

            # Create message_a containing an image and facts for the agent's long-term memory.
            message_a = Message(
                # Mark this message as coming from the human user.
                role="user",
                # Supply the image and text as two content items in the same user message.
                contents=[
                    # Encode the PNG bytes as inline image content for the model request.
                    Content.from_data(data=image_data, media_type="image/png"),
                    # Add the user's preferences as text alongside the image.
                    Content.from_text("What does this image contain?"),
                ],
            )

            # Send the message through session A; the model may call file_memory_write. This call may incur cost.
            response_a = await agent.run(message_a, session=session_a)

            # Print a label so the first response is easy to distinguish in the terminal.
            print("---------- Session A Response ---------- ")
            # Print only the first response text, not credentials or request metadata.
            print(response_a.text)
            # Print a closing label for the first response block.
            print("---------- End of Session A Response ---------- ")

            # Show the memory files the agent wrote during session A.
            print_memory_files()

            # Session B: the second conversation, where the user expects the agent to remember previous facts.
            # Create session_b, a fresh in-process session with no earlier conversation turns.
            session_b=agent.create_session()

            # Create message_a containing an image and facts for the agent's long-term memory.
            message_b = Message(
                # Mark this message as coming from the human user.
                role="user",
                # Supply the image and text as two content items in the same user message.
                contents=[

                    # Answer the question from the saved memory.
                    Content.from_text("Does the image contain any famous superhero characters? If yes, which one?"),
                ],
            )

            # Send the message through session B; the model may call file_memory_write. This call may incur cost.
            response_b = await agent.run(message_b, session=session_b)

            # Print a label so the first response is easy to distinguish in the terminal.
            print("---------- Session B Response ---------- ")
            # Print only the first response text, not credentials or request metadata.
            print(response_b.text)
            # Print a closing label for the first response block.
            print("---------- End of Session B Response ---------- ")


            # Session C: the third conversation, where the user expects the agent to remember previous facts.
            # Create session_c, a fresh in-process session with no earlier conversation turns.
            session_c=agent.create_session()

            # Create message_a containing an image and facts for the agent's long-term memory.
            message_c = Message(
                # Mark this message as coming from the human user.
                role="user",
                # Supply the image and text as two content items in the same user message.
                contents=[

                    # Answer the question from the saved memory.
                    Content.from_text("I believe the image represents a famous superhero character from an India Television show."),
                ],
            )

            # Send the message through session C; the model may call file_memory_write. This call may incur cost.
            response_c = await agent.run(message_c, session=session_c)

            # Print a label so the first response is easy to distinguish in the terminal.
            print("---------- Session C Response ---------- ")
            # Print only the first response text, not credentials or request metadata.
            print(response_c.text)
            # Print a closing label for the first response block.
            print("---------- End of Session C Response ---------- ")

            # Session D: the fourth conversation, where the user expects the agent to remember previous facts.
            # Create session_c, a fresh in-process session with no earlier conversation turns.
            session_d=agent.create_session()

            # Create message_a containing an image and facts for the agent's long-term memory.
            message_d = Message(
                # Mark this message as coming from the human user.
                role="user",
                # Supply the image and text as two content items in the same user message.
                contents=[

                    # Answer the question from the saved memory.
                    Content.from_text("What is the name of the Character?"),
                ],
            )

            # Send the message through session C; the model may call file_memory_write. This call may incur cost.
            response_d = await agent.run(message_d, session=session_d)

            # Print a label so the first response is easy to distinguish in the terminal.
            print("---------- Session D Response ---------- ")
            # Print only the first response text, not credentials or request metadata.
            print(response_d.text)
            # Print a closing label for the first response block.
            print("---------- End of Session D Response ---------- ")


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
