# Simple Agent Class - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the third learning stage in the Pydantic AI course. It makes the
composition of an agent explicit: a named **provider**, a named **model**, and
an `Agent(model=...)` built from them. It is the counterpart of the
[Microsoft Agent Framework stage 03](../../microsoft-agent-framework/03_simple-maf-agentclass/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | See which object owns which responsibility when building an agent |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a deployed model |
| Construction | `provider = OpenAIProvider(...)` → `chat_model = OpenAIResponsesModel(...)` → `Agent(model=chat_model, ...)` |
| Authentication | Async `DefaultAzureCredential` |
| Input / output | One text prompt about the `Agent` class / `response.output` |
| Current status | Implemented; same capabilities as stage 02 |

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 02](../02_simple-pydanticai-foundary/app/simple-ai-agent-pydanticai-foundary.py#L67-L75) builds the provider and model inline, inside the `Agent(...)` call. | [`provider`](app/simple-ai-agent-pydanticai-agentclass.py#L67-L68), [`chat_model`](app/simple-ai-agent-pydanticai-agentclass.py#L69-L70), and [`Agent(model=chat_model, ...)`](app/simple-ai-agent-pydanticai-agentclass.py#L71-L79) are separate, named steps. | Make the boundary between connection setup and agent behavior visible. |

**This is a readability and design step, not a new capability.** Stage 02's
agent could already do everything this one does. In MAF, stage 02 used the
`client.as_agent(...)` factory and stage 03 switched to `Agent(client=...)`.
Pydantic AI has only one way to build an agent, `Agent(...)`, so the
equivalent lesson here is naming the pieces it is built from.

Why the separation is useful in practice:

| Object | Owns | Could be swapped for |
| --- | --- | --- |
| `OpenAIProvider` | The authenticated HTTP client and base URL | `AzureProvider` (stage 01), or another OpenAI-compatible provider |
| `OpenAIResponsesModel` | Deployment name and the API shape (Responses API) | `OpenAIChatModel` for the Chat Completions API, or `TestModel` in offline tests |
| `Agent` | Name, instructions, tools, output type | Unchanged when the model is swapped |

Because the agent only depends on a model object, you can test agent logic
offline by passing `pydantic_ai.models.test.TestModel()` instead. This sample
does not include such a test.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Single local agent and fixed prompt | Implemented | One `Agent` and one run |
| Explicit provider/model/agent composition | Implemented | Three named objects |
| Tools, MCP, memory, streaming | Not implemented | Added in stages 05–10 |

## How it works

1. [Configuration](app/simple-ai-agent-pydanticai-agentclass.py#L29-L54) is read
   from the shared `.env` file exactly as in stage 02.
2. [The `async with` block](app/simple-ai-agent-pydanticai-agentclass.py#L56-L66)
   opens the credential, the project client, and the project's OpenAI client.
3. [`provider`](app/simple-ai-agent-pydanticai-agentclass.py#L67-L68) wraps the
   OpenAI client; [`chat_model`](app/simple-ai-agent-pydanticai-agentclass.py#L69-L70)
   binds the deployment name and Responses API to that provider.
4. [`Agent(...)`](app/simple-ai-agent-pydanticai-agentclass.py#L71-L79) receives
   the model with the `model=` keyword, a name, and instructions.
5. [`await agent.run(...)`](app/simple-ai-agent-pydanticai-agentclass.py#L81-L88)
   sends the prompt and prints the output.

## Folder contents

```text
03_simple-pydanticai-agentclass/
├── README.md
├── app/
│   └── simple-ai-agent-pydanticai-agentclass.py
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks and libraries

Same packages and versions as [stage 02](../02_simple-pydanticai-foundary/README.md#frameworks-and-libraries):
`pydantic-ai-slim` 2.64.0, `azure-ai-projects` 2.10.0, `azure-identity` 1.27.0,
`aiohttp`, and `python-dotenv`, all from the shared [requirements.txt](../requirements.txt).
Reference: [Pydantic AI agents](https://pydantic.dev/docs/ai/core-concepts/agent/).

## Prerequisites, setup, and configuration

Same as [stage 02](../02_simple-pydanticai-foundary/README.md#prerequisites-and-setup):
the shared `.venv`, a signed-in identity with access to the Foundry project, and
`FOUNDARY_PROJECT_ENDPOINT` / `FOUNDARY_MODEL` in the shared `.env`.

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Live, potentially billable
request; not run while writing this README:

```sh
./.venv/bin/python 03_simple-pydanticai-agentclass/app/simple-ai-agent-pydanticai-agentclass.py
```

Prints a generated explanation of the Pydantic AI `Agent` class with one example.

## Exercises to try

1. Replace `OpenAIResponsesModel` with `OpenAIChatModel` (same arguments, imported
   from `pydantic_ai.models.openai`). The agent code does not change; only the
   API used underneath does.
2. Without calling Azure, build `Agent(model=TestModel())` (import `TestModel`
   from `pydantic_ai.models.test`) in a small separate script and run it. The
   output is canned text, which shows the agent works with any model object.

## Validation and troubleshooting

`tests/` is an empty placeholder. Run the comment checker with the shared
interpreter as shown in [stage 01](../01_simple-pydanticai-openai/README.md#validation-and-troubleshooting).
Troubleshooting is the same as [stage 02](../02_simple-pydanticai-foundary/README.md#validation-and-troubleshooting).

## Learning links and progression

- [AI concepts: Pydantic AI provider, model, and agent](../../../docs/ai-concepts.md#pydantic-ai-provider-model-and-agent)
- [AI concepts: explicit agent composition](../../../docs/ai-concepts.md#explicit-agent-composition) (MAF view of the same idea)

Next, [stage 04](../04_simple-pydanticai-messageclass/README.md) sends the
prompt as a structured list of content items instead of a plain string.
