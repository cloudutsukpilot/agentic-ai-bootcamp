# asyncio is Python's built-in library for coordinating asynchronous work.
# Import asyncio to run our agent coroutine on an event loop.
import asyncio
# os is Python's built-in operating-system interface.
# Import os to read configuration and the NO_COLOR convention from the environment.
import os
# sys is Python's built-in interface to the running interpreter.
# Import sys to check whether standard output is an interactive terminal.
import sys
# pathlib is Python's built-in library for filesystem paths.
# Import Path to locate the shared configuration file, the image, and the memory folder.
from pathlib import Path

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
# Import Agent, BinaryContent for raw file bytes, and UserContent for prompt items.
from pydantic_ai import Agent, BinaryContent, UserContent
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


# Define print_session_text, which prints a labelled prompt or response block, colored in terminals.
# session is the session letter, kind is "Prompt" or "Response", and text is the body to show.
def print_session_text(session: str, kind: str, text: str) -> None:
    # Create use_color: True only for an interactive terminal when NO_COLOR is not set.
    use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    # Create color: an ANSI escape code, cyan for prompts and green for responses, or "" without color.
    color = ("\033[36m" if kind == "Prompt" else "\033[32m") if use_color else ""
    # Create reset: the ANSI code that ends the color, or "" without color.
    reset = "\033[0m" if use_color else ""
    # Print the labelled block; flush=True shows it immediately before the next slow model call.
    print(f"\n{color}---------- Session {session} {kind} ----------\n{text}{reset}", flush=True)


# async def defines a coroutine function whose work is driven by an event loop.
# Define main without parameters; it prints the prompts and responses and returns no value.
async def main() -> None:
    # Preserve the existing FOUNDARY_* spelling to keep this course's configuration compatible.
    # Create model_name containing the Foundry model deployment name, not an agent identifier.
    model_name = required_setting("FOUNDARY_MODEL")
    # Create project_endpoint containing the Foundry project URL, not an Azure OpenAI resource URL.
    project_endpoint = required_setting("FOUNDARY_PROJECT_ENDPOINT")

    # Create memory_tools: file_memory_* tools plus instructions that inject the memories.md index.
    memory_tools = create_file_memory_toolset(root_directory=MEMORY_DIR, scope=USER_ID)

    # Create image_path for the PNG beside the running script.
    image_path = Path(__file__).resolve().with_name("sample-image.png")
    # Create image_data containing the file's raw bytes, then close the file.
    image_data = image_path.read_bytes()

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
        # Create agent locally with the model, image-analysis instructions, and memory tools.
        agent = Agent(
            # Pass the model adapter; the deployment must accept image input for session A.
            model=chat_model,
            # Give the local agent a readable name; this is not a deployed resource ID.
            name="Image Analysis Agent",
            # Describe the local agent's purpose for the framework metadata.
            description="An agent that analyzes the images provided to it and outlines key details.",
            # Ask the model to analyze images and save what it learns to memory every session.
            instructions=(
                # Supply the behavior instructions as one string.
                "You are a helpful assistant. When the user shares images, analyze them and store relevant details in memory in every session. "
            ),
            # Register only the memory toolset; this stage has no other local tools.
            toolsets=[memory_tools],
        )

        # Session A: a fresh conversation whose message contains the image and a question.
        # Create message_a, a list with two content items: image bytes and text.
        message_a: list[UserContent] = [
            # Wrap the PNG bytes with their media type so the model knows how to read them.
            BinaryContent(data=image_data, media_type="image/png"),
            # Add the text question about the image.
            "What does this image contain?",
        ]

        # Show the prompt, naming the image file instead of printing its bytes.
        print_session_text("A", "Prompt", f"[Image: {image_path.name}]\n{message_a[1]}")
        # Await session A; the model sees the image and may save details with file_memory_write.
        response_a = await agent.run(message_a)

        # Show session A's generated response.
        print_session_text("A", "Response", response_a.output)

        # Show which memory files exist on disk after session A.
        print_memory_files()

        # Session B: a fresh conversation without the image; only saved memory can help.
        # Create message_b, a list with one text item.
        message_b: list[UserContent] = [
            # Ask about the earlier image, which this conversation never received.
            "Does the image contain any famous superhero characters? If yes, which one?",
        ]

        # Show session B's prompt.
        print_session_text("B", "Prompt", message_b[0])
        # Await session B, which can only answer from the memory files.
        response_b = await agent.run(message_b)

        # Show session B's generated response.
        print_session_text("B", "Response", response_b.output)

        # Session C: a fresh conversation where the user adds their own interpretation.
        # Create message_c, a list with one text item.
        message_c: list[UserContent] = [
            # Share a user belief the model may store alongside the image description.
            "I believe the image represents a famous superhero character from an India Television show.",
        ]

        # Show session C's prompt.
        print_session_text("C", "Prompt", message_c[0])
        # Await session C; the model may update the memory file with this extra context.
        response_c = await agent.run(message_c)

        # Show session C's generated response.
        print_session_text("C", "Response", response_c.output)

        # Session D: a fresh conversation asking for the character's name.
        # Create message_d, a list with one text item.
        message_d: list[UserContent] = [
            # Ask a question whose answer depends on what sessions A and C saved.
            "What is the name of the Character?",
        ]

        # Show session D's prompt.
        print_session_text("D", "Prompt", message_d[0])
        # Await session D, which relies on the accumulated memory files.
        response_d = await agent.run(message_d)

        # Show session D's generated response.
        print_session_text("D", "Response", response_d.output)


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
