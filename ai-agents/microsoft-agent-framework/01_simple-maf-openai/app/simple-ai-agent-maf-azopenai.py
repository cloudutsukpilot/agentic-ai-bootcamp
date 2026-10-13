# asyncio is a built-in Python library for running asynchronous tasks on an event loop.
# Import asyncio so we can start the agent's asynchronous main function.
import asyncio
# os is a built-in Python library for interacting with the operating system.
# Import os so we can read configuration values from environment variables.
import os
# pathlib is a built-in Python library for representing and working with filesystem paths.
# Import Path so we can locate the configuration file beside this script.
from pathlib import Path

# Agent Framework is a third-party library for building agents that interact with language models.
# Import OpenAIChatClient to connect our agent to the Azure OpenAI Responses API.
from agent_framework.openai import OpenAIChatClient
# python-dotenv is a third-party library for reading key=value configuration from .env files.
# Import dotenv_values to read configuration into a dictionary without changing the process environment.
from dotenv import dotenv_values


# __file__ is this script's path; with_name replaces its filename while keeping the parent folder.
# Create the settings variable containing the dictionary read from the .env file beside this script.
settings = dotenv_values(Path(__file__).with_name(".env"))


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
    # Create the client variable holding an Azure OpenAI client configured with endpoint and API-key authentication.
    client = OpenAIChatClient(
        # Pass the Azure deployment name as the model keyword argument, not a new local variable.
        model=required_setting("AZURE_OPENAI_MODEL"),
        # Pass the Azure resource endpoint as the azure_endpoint keyword argument.
        azure_endpoint=required_setting("AZURE_OPENAI_ENDPOINT"),
        # Pass the secret API key as the api_key keyword argument without printing or hardcoding it.
        api_key=required_setting("AZURE_OPENAI_API_KEY"),
    )

    # Create the agent variable by asking the client to build an agent with a name and model instructions.
    agent = client.as_agent(
        # Pass a readable label for this agent as the name keyword argument.
        name="Sample MAF Azure OpenAI Agent",
        # Pass instructions that tell the model how this agent should behave.
        instructions="You are a helpful assistant that generates MAF files based on user input.",
    )

    # await waits for a coroutine without blocking the event loop; it does not create a new thread.
    # Create the response variable by sending a prompt and awaiting the agent's completed response.
    response = await agent.run("Explain what the Microsoft Agent Framework is in one sentence.")
    # Print the response object's text attribute, which contains the model's generated text.
    print(response.text)


# __name__ is '__main__' when this script is launched directly, but not when another module imports it.
# Check the script-entry guard so importing this module does not run the agent.
if __name__ == "__main__":
    # Start an event loop, run the main coroutine to completion, and close the loop afterward.
    asyncio.run(main())