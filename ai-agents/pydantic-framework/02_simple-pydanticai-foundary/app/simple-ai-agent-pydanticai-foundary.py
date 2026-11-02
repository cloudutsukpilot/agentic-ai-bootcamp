# asyncio is Python's built-in library for coordinating asynchronous work.
# Import asyncio to run our agent coroutine on an event loop.
import asyncio
# os is Python's built-in operating-system interface.
# Import os to read configuration inherited by this process.
import os
# pathlib is Python's built-in library for filesystem paths.
# Import Path to locate the shared configuration file for all stages.
from pathlib import Path

# Third-party Azure AI Projects SDK connects to a Foundry project endpoint.
# Import the async AIProjectClient so it can hand us an authenticated OpenAI client.
from azure.ai.projects.aio import AIProjectClient
# Third-party Azure Identity obtains Entra tokens; permissions are assigned separately.
# Import the asynchronous credential so token acquisition fits this async workflow.
from azure.identity.aio import DefaultAzureCredential
# Third-party python-dotenv parses configuration without changing the process environment.
# Import dotenv_values to obtain file settings as a dictionary.
from dotenv import dotenv_values
# Third-party Pydantic AI orchestrates agents; Foundry serves the deployed model.
# Import Agent, the local orchestration object that sends instructions through a model.
from pydantic_ai import Agent
# Import OpenAIResponsesModel, the adapter that calls the OpenAI Responses API.
from pydantic_ai.models.openai import OpenAIResponsesModel
# Import OpenAIProvider so the model can reuse the project's authenticated OpenAI client.
from pydantic_ai.providers.openai import OpenAIProvider


# __file__ identifies this script; parents[2] is the pydantic-framework folder shared by every stage.
# Create settings from the shared file without printing any configuration values.
settings = dotenv_values(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


# A function is reusable code; this helper centralizes required-setting checks.
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


# async def defines a coroutine function whose work is driven by an event loop.
# Define main without parameters; it prints the response and returns no value.
async def main() -> None:
    # Preserve the existing FOUNDARY_* spelling to keep this course's configuration compatible.
    # Create model_name containing the Foundry model deployment name, not an agent identifier.
    model_name = required_setting("FOUNDARY_MODEL")
    # Create project_endpoint containing the Foundry project URL, not an Azure OpenAI resource URL.
    project_endpoint = required_setting("FOUNDARY_PROJECT_ENDPOINT")

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
        # Create agent locally; this does not provision a hosted Foundry agent.
        agent = Agent(
            # Pass a Responses API model that sends requests through the project's OpenAI client.
            OpenAIResponsesModel(model_name, provider=OpenAIProvider(openai_client=openai_client)),
            # Give the local agent a readable name; this is not a deployed resource ID.
            name="Sample Pydantic AI Foundry Agent",
            # Supply behavior instructions separately from the user's request below.
            instructions="You are a helpful agent that explains the Pydantic AI framework.",
        )

        # Await model I/O without starting a thread; the remote request may incur cost.
        # Create response containing the completed agent result for this single prompt.
        response = await agent.run("Explain what the Pydantic AI framework is in one sentence.")
        # Print only the response output, never tokens or credential configuration.
        print(response.output)


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
