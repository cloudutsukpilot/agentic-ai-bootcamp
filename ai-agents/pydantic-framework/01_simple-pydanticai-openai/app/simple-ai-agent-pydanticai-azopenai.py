# asyncio is a built-in Python library for running asynchronous tasks on an event loop.
# Import asyncio so we can start the agent's asynchronous main function.
import asyncio
# os is a built-in Python library for interacting with the operating system.
# Import os so we can read configuration values from environment variables.
import os
# pathlib is a built-in Python library for representing and working with filesystem paths.
# Import Path so we can locate the shared configuration file for all stages.
from pathlib import Path

# python-dotenv is a third-party library for reading key=value configuration from .env files.
# Import dotenv_values to read configuration into a dictionary without changing the process environment.
from dotenv import dotenv_values
# Pydantic AI is a third-party agent framework; Agent coordinates instructions, model, and tools.
# Import Agent, the local object that sends our instructions and prompt through a model.
from pydantic_ai import Agent
# Import OpenAIResponsesModel, Pydantic AI's adapter for the OpenAI Responses API.
from pydantic_ai.models.openai import OpenAIResponsesModel
# Import AzureProvider, which builds an authenticated OpenAI SDK client for an Azure OpenAI resource.
from pydantic_ai.providers.azure import AzureProvider


# __file__ is this script's path; parents[2] is the pydantic-framework folder shared by every stage.
# Create the settings variable containing the dictionary read from the shared .env file.
settings = dotenv_values(Path(__file__).resolve().parents[2] / ".env")


# A function is a reusable block of code that performs a named task.
# Define required_setting with a string parameter named name and a string return annotation.
def required_setting(name: str) -> str:
    # Create the value variable using the environment value first, or the file value if it is empty/missing.
    value = os.getenv(name) or settings.get(name)
    # Check whether value is missing or empty; these values are treated as false in Python.
    if not value:
        # Raise an error naming the missing setting; an f-string inserts the name into the message.
        raise RuntimeError(f"Missing required Azure OpenAI setting: {name}")
    # Return the nonempty configuration string to the code that called this function.
    return value


# A function is reusable code; async def creates a coroutine that an event loop can run.
# Define main without parameters and annotate that it completes without returning a value (None).
async def main() -> None:
    # Create endpoint from the Azure resource URL without a trailing slash or an existing /openai/v1 suffix.
    endpoint = required_setting("AZURE_OPENAI_ENDPOINT").rstrip("/").removesuffix("/openai/v1")

    # Create the provider variable holding an Azure OpenAI connection with API-key authentication.
    provider = AzureProvider(
        # Pass the Azure OpenAI v1 API URL; this route does not need a separate api_version setting.
        azure_endpoint=f"{endpoint}/openai/v1",
        # Pass the secret API key as the api_key keyword argument without printing or hardcoding it.
        api_key=required_setting("AZURE_OPENAI_API_KEY"),
    )

    # Create the model variable that talks to one Azure deployment through the Responses API.
    model = OpenAIResponsesModel(
        # Pass the Azure deployment name as the model name, not the model family.
        required_setting("AZURE_OPENAI_MODEL"),
        # Pass the provider that supplies the authenticated HTTP client for the deployment.
        provider=provider,
    )

    # Create the agent variable by combining the model with a name and model instructions.
    agent = Agent(
        # Pass the model adapter that the agent uses for every request.
        model,
        # Pass a readable label for this agent as the name keyword argument.
        name="Sample Pydantic AI Azure OpenAI Agent",
        # Pass instructions that tell the model how this agent should behave.
        instructions="You are a helpful assistant that generates Pydantic AI files based on user input.",
    )

    # await waits for a coroutine without blocking the event loop; it does not create a new thread.
    # Create the response variable by sending a prompt and awaiting the agent's completed run result.
    response = await agent.run("Explain what the Pydantic AI framework is in one sentence.")
    # Print the result's output attribute, which contains the model's generated text.
    print(response.output)


# __name__ is '__main__' when this script is launched directly, but not when another module imports it.
# Check the script-entry guard so importing this module does not run the agent.
if __name__ == "__main__":
    # Start an event loop, run the main coroutine to completion, and close the loop afterward.
    asyncio.run(main())
