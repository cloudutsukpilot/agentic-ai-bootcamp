# asyncio is Python's built-in library for coordinating asynchronous work.
# Import asyncio to run our agent coroutine on an event loop.
import asyncio
# os is Python's built-in operating-system interface.
# Import os to read configuration inherited by this process.
import os
# pathlib is Python's built-in library for filesystem paths.
# Import Path to locate the shared configuration file and this stage's memory folder.
from pathlib import Path
# Import randint from Python's standard library to make the weather demo output vary.
from random import randint

# Azure AI Projects connects to a Foundry project endpoint.
# Import the async AIProjectClient so it can hand us an authenticated OpenAI client.
from azure.ai.projects.aio import AIProjectClient
# Azure Identity obtains Entra tokens; access permissions must be assigned separately.
# Import the asynchronous credential so token acquisition fits this async workflow.
from azure.identity.aio import DefaultAzureCredential
# python-dotenv parses configuration without exporting it to the process environment.
# Import dotenv_values to obtain file settings as a dictionary.
from dotenv import dotenv_values
# file_memory is this stage's local module beside the script, not a third-party package.
# Import the factory that builds file_memory_* tools backed by files on disk.
from file_memory import create_file_memory_toolset
# Pydantic AI orchestrates agents; Foundry provides the remote model service.
# Import Agent, UserContent for prompt items, and FunctionToolset, a container of Python tools.
from pydantic_ai import Agent, FunctionToolset, UserContent
# Import OpenAIResponsesModel, the adapter that calls the OpenAI Responses API.
from pydantic_ai.models.openai import OpenAIResponsesModel
# Import OpenAIProvider so the model can reuse the project's authenticated OpenAI client.
from pydantic_ai.providers.openai import OpenAIProvider

# __file__ identifies this script; parents[2] is the pydantic-framework folder shared by every stage.
# Create settings from the shared file without printing any configuration values.
settings = dotenv_values(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# Create MEMORY_DIR, the folder beside this script where memory files are stored.
MEMORY_DIR = Path(__file__).resolve().with_name("memory_store")
# Create USER_ID, the fixed demo scope; every session below shares this user's memory folder.
USER_ID = "demo_user"

# Create weather_tools, an empty toolset that the decorator below fills and the agent later receives.
weather_tools = FunctionToolset()


# A helper function centralizes lookup and validation for required configuration.
# Define required_setting with a string name parameter and a string return annotation.
def required_setting(name: str) -> str:
    # Create value from the nonempty environment setting, otherwise the file dictionary.
    value = os.getenv(key=name) or settings.get(name)
    # Check whether neither source supplied a nonempty value.
    if not value:
        # Stop before authentication with an error identifying the setting, not its value.
        raise ValueError(f"Missing required Foundry setting: {name}")
    # Return the validated string to the calling model-configuration code.
    return value


# Define print_memory_files, a helper that lists saved memory files without printing their contents.
def print_memory_files() -> None:
    # Print a label before the file list.
    print("------- Memory files on disk -------")
    # Loop over every path below the memory folder in sorted order; rglob searches subfolders too.
    for path in sorted(MEMORY_DIR.rglob("*")):
        # Only report files, not folders.
        if path.is_file():
            # Print the path relative to the memory folder, such as demo_user/memories.md.
            print(path.relative_to(MEMORY_DIR))
    # Print a closing label after the file list.
    print("-------- End of memory files ------------")


# A decorator wraps a function; tool_plain registers it as a model-discoverable tool without RunContext.
@weather_tools.tool_plain
# Define an asynchronous tool with a location input and text result for the agent.
async def get_weather(location: str) -> str:
    # Describe the tool so the framework can expose its purpose and parameter to the model.
    """Get weather for a location

    Args:
        location (str): The location to get the weather for.

    Returns:
        str: A string describing the weather for the given location.
    """
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
    # Preserve the existing FOUNDARY_* spelling to keep this course's configuration compatible.
    # Create model_name containing the Foundry model deployment name, not an agent identifier.
    model_name = required_setting("FOUNDARY_MODEL")
    # Create project_endpoint containing the Foundry project URL, not an Azure OpenAI resource URL.
    project_endpoint = required_setting("FOUNDARY_PROJECT_ENDPOINT")

    # Create memory_tools: file_memory_* tools plus instructions that inject the memories.md index.
    memory_tools = create_file_memory_toolset(root_directory=MEMORY_DIR, scope=USER_ID)

    # One async with statement can enter several context managers, in order, left to right;
    # leaving the block closes them in reverse order, even if an error occurs.
    async with (
        # Create credential; DefaultAzureCredential tries supported identity sources when a token is needed.
        DefaultAzureCredential() as credential,
        # Create project_client for the Foundry project; construction does not call the model yet.
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        # Create openai_client pointing at the project's /openai/v1 route with Entra bearer tokens.
        project_client.get_openai_client() as openai_client,
    # Close the list of context managers; the indented block below runs while all are open.
    ):
        # Create chat_model, the Responses API adapter that uses the project's authenticated client.
        chat_model = OpenAIResponsesModel(model_name, provider=OpenAIProvider(openai_client=openai_client))
        # Create agent locally with the model, memory-aware instructions, and both toolsets.
        agent = Agent(
            # Pass the model adapter that connects this local agent to the remote deployment.
            model=chat_model,
            # Give the local agent a readable name; this is not a deployed resource ID.
            name="Sample Pydantic AI Long-Term Memory Agent",
            # Describe the local agent's purpose for the framework metadata.
            description="A sample agent that remembers user facts across sessions using file-based memory.",
            # Tell the model when to save facts and to consult memory before answering.
            instructions=(
                # Explain that durable personal facts should be saved with the memory tools.
                "You are a helpful assistant. When the user shares durable personal facts or preferences, "
                # Ask the model to look up saved facts before it answers.
                "save them with the file memory tools. Before answering, check your memory for relevant facts."
            ),
            # Register the memory toolset and the weather toolset for model-selected calls.
            toolsets=[memory_tools, weather_tools],
        )

        # Session A: a run without a conversation argument starts a brand-new conversation.
        # Create message_a sharing facts the model should save to durable memory.
        message_a: list[UserContent] = [
            # Supply the user's personal facts and answer-format preference.
            "My name is Alex. I am vegetarian and I prefer answers as 3 short bullet points.",
        ]
        # Await session A; the model may call file_memory_write to save the facts.
        response_a = await agent.run(message_a)
        # Print a label for session A's answer.
        print("---------- Session A Response ---------- ")
        # Print session A's generated output.
        print(response_a.output)
        # Print a closing label for session A.
        print("---------- End of Session A Response ---------- ")

        # Show which memory files exist on disk after session A.
        print_memory_files()

        # Session B: another fresh conversation; it has no access to session A's messages.
        # Create message_b, which can only be personalized through saved memory.
        message_b: list[UserContent] = ["Greet me by name and suggest a dinner for me tonight."]
        # Await session B; the injected memory index and file_memory_read supply the saved facts.
        response_b = await agent.run(message_b)
        # Print a label for session B's answer.
        print("---------- Session B Response ---------- ")
        # Print session B's generated output.
        print(response_b.output)
        # Print a closing label for session B.
        print("---------- End of Session B Response ---------- ")

        # Session C: a third fresh conversation asking about past conversations.
        # Create message_c; saved facts are not a transcript, so a full history is unavailable.
        message_c: list[UserContent] = [
            # Supply the request for a summary of past conversations and preferences.
            "Summarize my past conversations and provide a brief overview of my preferences.",
        ]
        # Await session C, which can only use whatever was saved to memory files.
        response_c = await agent.run(message_c)
        # Print a label for session C's answer.
        print("---------- Session C Response ---------- ")
        # Print session C's generated output.
        print(response_c.output)
        # Print a closing label for session C.
        print("---------- End of Session C Response ---------- ")


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
