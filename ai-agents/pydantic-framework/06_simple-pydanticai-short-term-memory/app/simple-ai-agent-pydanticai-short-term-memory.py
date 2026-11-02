# asyncio is Python's built-in library for coordinating asynchronous work.
# Import asyncio to run our agent coroutine on an event loop.
import asyncio
# os is Python's built-in operating-system interface.
# Import os to read configuration inherited by this process.
import os
# pathlib is Python's built-in library for filesystem paths.
# Import Path to locate the shared configuration file for all stages.
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
        # Create chat_model, the Responses API adapter that uses the project's authenticated client.
        chat_model = OpenAIResponsesModel(model_name, provider=OpenAIProvider(openai_client=openai_client))
        # Create agent locally with this model, instructions, and the weather toolset.
        agent = Agent(
            # Pass the model adapter that connects this local agent to the remote deployment.
            model=chat_model,
            # Give the local agent a readable name; this is not a deployed resource ID.
            name="Sample Pydantic AI Foundry Agent",
            # Describe the local agent's purpose for the framework metadata.
            description="A sample agent that demonstrates the use of tools in the Pydantic AI framework.",
            # Supply behavior instructions separately from the user's request below.
            instructions="You are a helpful assistance agent that uses the Pydantic AI framework with Microsoft Foundary to answer queries.",
            # Register the toolset so the model can request get_weather during a run.
            toolsets=[weather_tools],
        )

        # Create the first structured user message that starts the conversation context.
        user_message1: list[UserContent] = ["Give me 5 bullet points about India"]
        # Send the first message without a conversation, so Pydantic AI starts a new one.
        response1 = await agent.run(user_message1)
        # Print a label so the first response is easy to distinguish in the terminal.
        print("---------- Response 1 ---------- ")
        # Print only the first response output, not credentials or request metadata.
        print(response1.output)
        # Print a closing label for the first response block.
        print("---------- End of Response 1 ---------- ")

        # Create a follow-up message whose wording depends on the first response's context.
        user_message2: list[UserContent] = ["Add one line description to the each of those bullet points."]
        # Continue the first run's in-memory conversation so earlier turns are sent with this one.
        response2 = await agent.run(user_message2, conversation=response1.conversation)
        # Print a label so the second response is easy to distinguish in the terminal.
        print("---------- Response 2 ---------- ")
        # Print only the second response output generated with the shared conversation context.
        print(response2.output)
        # Print a closing label for the second response block.
        print("---------- End of Response 2 ---------- ")

        # Create the final structured message asking the agent to summarize the accumulated context.
        user_message3: list[UserContent] = ["Summarize all the above information in one paragraph."]
        # Await the third remote response without blocking the event loop; this call may incur cost.
        # Create response3 by continuing the conversation returned by the second run.
        response3 = await agent.run(user_message3, conversation=response2.conversation)
        # Print only the final response output, never tokens or credential configuration.
        print(response3.output)


# __name__ is '__main__' when launched directly, not when imported by tests.
# Guard the entry point so importing this module does not run the agent.
if __name__ == "__main__":
    # Create an event loop, run main to completion, then close the loop.
    asyncio.run(main())
