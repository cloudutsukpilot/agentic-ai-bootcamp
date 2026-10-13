# This sample demonstrates Microsoft Agent Framework long-term memory.
# Memories are saved as files on disk, so a brand-new session can still recall them.
# asyncio is Python's built-in library for coordinating asynchronous work.
# Import asyncio to run our agent coroutine on an event loop.
import asyncio
# os is Python's built-in operating-system interface.
# Import os to read configuration inherited by this process.
import os
# pathlib is Python's built-in library for filesystem paths.
# Import Path to locate the configuration file and memory folder beside this script.
from pathlib import Path
# random is Python's built-in library for pseudo-random numbers.
# Import randint so the demo weather tool can produce randomized values.
from random import randint

# Agent Framework orchestrates agents; Foundry provides the remote model service.
# Import FoundryChatClient, an adapter for the project's OpenAI Responses API.
from agent_framework.foundry import FoundryChatClient
# Import Agent (local orchestration), Message (one structured conversation item), and tool (function-tool decorator).
# Import FileMemoryProvider, a context provider that gives the agent file-based memory tools.
# Import FileSystemAgentFileStore, the disk-backed storage those memory tools read and write.
from agent_framework import Agent, Message, tool, FileMemoryProvider, FileSystemAgentFileStore
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
            # Create agent locally with this client, instructions, memory provider, and tool.
            agent = Agent(
                # Pass the chat client that connects this local agent to the remote model.
                client=chat_client,
                # Give the local agent a readable name; this is not a deployed resource ID.
                name="Sample MAF Long-Term Memory Agent",
                # Describe the local agent's purpose for the framework metadata.
                description="A sample agent that remembers user facts across sessions using file-based memory.",
                # Supply behavior instructions separately from the user's request below.
                instructions=(
                    # Ask the model to write durable facts and preferences into memory.
                    "You are a helpful assistant. When the user shares durable personal facts or preferences, "
                    # Ask the model to read memory first so new sessions can use earlier facts.
                    "save them with the file memory tools. Before answering, check your memory for relevant facts."
                ),
                # Register the memory provider; it runs before and after every agent run.
                context_providers=[memory_provider],
                # Register the decorated function so the model can request it during a run.
                tools=[get_weather]
            )

            # Session A: the first conversation, where the user shares facts worth remembering.
            # Create session_a, a fresh in-process session with no earlier conversation turns.
            session_a=agent.create_session()

            # Create the user's message containing facts the agent should store in long-term memory.
            message_a = Message(
                # Mark this message as coming from the human user.
                role="user",
                # Supply the facts as the single text content item.
                contents=["My name is Alex. I am vegetarian and I prefer answers as 3 short bullet points."],
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

            # Session B: a brand-new conversation with no shared history from session A.
            # Create session_b; it cannot see session A's messages, only the shared memory files.
            session_b = agent.create_session()

            # Create a question that only makes sense if the agent remembers the earlier facts.
            message_b = Message(
                # Mark this message as coming from the human user.
                role="user",
                # Ask for a personalized answer without repeating the facts.
                contents=["Greet me by name and suggest a dinner for me tonight."],
            )
            # Send the message through session B; the model may call file_memory_read to recall facts.
            response_b = await agent.run(message_b, session=session_b)
            # Print a label so the second response is easy to distinguish in the terminal.
            print("---------- Session B Response ---------- ")
            # Print only the second response text, which should use the remembered name and preferences.
            print(response_b.text)
            # Print a closing label for the second response block.
            print("---------- End of Session B Response ---------- ")

            # Session C: a new session that can access the shared memory files but has no direct conversation history with sessions A or B.
            # Create session_c; only facts the model saved to memory are available, not earlier transcripts.
            session_c = agent.create_session()

            # Create a question asking about past conversations, which tests what memory does not store.
            message_c = Message(
                # Mark this message as coming from the human user.
                role="user",
                # Ask for a summary of earlier conversations and stored preferences.
                contents=["Summarize my past conversations and provide a brief overview of my preferences."])
            # Await the third remote response without blocking the event loop; this call may incur cost.
            # Create response_c containing the completed agent result for session C.
            response_c = await agent.run(message_c, session=session_c)
            # Print a label so the third response is easy to distinguish in the terminal.
            print("---------- Session C Response ---------- ")
            # Print only the final response text, never tokens or credential configuration.
            print(response_c.text)
            # Print a closing label for the third response block.
            print("---------- End of Session C Response ---------- ")


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
