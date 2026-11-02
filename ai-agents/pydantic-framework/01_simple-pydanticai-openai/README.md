# Simple Azure OpenAI Agent - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the first learning stage in the Pydantic AI course. It sends one fixed
prompt to an Azure OpenAI deployment through a Pydantic AI `Agent` and prints
the completed answer. It is the Pydantic AI counterpart of the
[Microsoft Agent Framework stage 01](../../microsoft-agent-framework/01_simple-maf-openai/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Connect a model to an agent and run one prompt |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Azure OpenAI resource with a deployed model |
| Provider / model classes | `AzureProvider` + `OpenAIResponsesModel` (Responses API) |
| Authentication | Azure OpenAI API key |
| Input | One hard-coded text prompt |
| Output | `response.output`, the model-generated text |
| Current status | Implemented one-shot prompt/response |

Pydantic AI separates three roles. A **provider** owns the authenticated
connection to a service. A **model** adapter knows which deployment to call and
which API shape (here, the OpenAI Responses API) to use. An **agent** combines
the model with instructions and, in later stages, tools. Constructing these
objects is local; only `agent.run(...)` sends a network request.

## How this maps to the Microsoft Agent Framework stage

| MAF stage 01 | This stage | Notes |
| --- | --- | --- |
| `OpenAIChatClient(model=..., azure_endpoint=..., api_key=...)` | `AzureProvider(...)` + `OpenAIResponsesModel(...)` | Pydantic AI splits the connection (provider) from the deployment/API choice (model). |
| `client.as_agent(name=..., instructions=...)` | `Agent(model, name=..., instructions=...)` | Pydantic AI has no client-side agent factory; `Agent(...)` is the only constructor. |
| `response.text` | `response.output` | `output` holds the final result; with the default `output_type=str` it is text. |

The same three settings are used (`AZURE_OPENAI_MODEL`, `AZURE_OPENAI_ENDPOINT`,
`AZURE_OPENAI_API_KEY`). The script appends `/openai/v1` to the endpoint so
`AzureProvider` targets the
[Azure OpenAI v1 API](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle),
which needs no separate `api_version` setting.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Single local agent and fixed prompt | Implemented | One `Agent` and one `agent.run(...)` call |
| Local function tools | Not implemented | No toolsets are registered; stage 05 adds one |
| MCP tools | Not implemented | Stage 08 adds an MCP server |
| Short-term conversation memory | Not implemented | Each run is independent; stage 06 continues a conversation |
| Persistent memory | Not implemented | Stage 07 adds file-backed memory |
| Streaming | Not implemented | The script awaits one completed response; stage 10 streams |
| Multi-agent orchestration, RAG, observability | Not implemented | Not part of this course's stages |

The instructions say the agent "generates Pydantic AI files", matching the MAF
stage's wording. Instructions only shape the model's text; nothing in this
script writes files.

## How it works

1. [`dotenv_values`](app/simple-ai-agent-pydanticai-azopenai.py#L23-L25) reads
   the shared `ai-agents/pydantic-framework/.env` file into a dictionary without
   exporting it. `parents[2]` walks up from `app/` and the stage folder.
2. [`required_setting`](app/simple-ai-agent-pydanticai-azopenai.py#L28-L38)
   returns a nonempty process environment value first, otherwise the file
   value, and raises `RuntimeError` when neither exists.
3. [The endpoint](app/simple-ai-agent-pydanticai-azopenai.py#L44-L45) is
   normalized, then [`AzureProvider`](app/simple-ai-agent-pydanticai-azopenai.py#L47-L53)
   builds an API-key-authenticated OpenAI SDK client for the `/openai/v1` route.
4. [`OpenAIResponsesModel`](app/simple-ai-agent-pydanticai-azopenai.py#L55-L61)
   binds the deployment name to that provider.
5. [`Agent`](app/simple-ai-agent-pydanticai-azopenai.py#L63-L71) combines the
   model, a readable name, and the instructions.
6. [`await agent.run(...)`](app/simple-ai-agent-pydanticai-azopenai.py#L73-L77)
   sends the prompt, waits for the completed result, and prints `response.output`.
7. The [script entry guard](app/simple-ai-agent-pydanticai-azopenai.py#L80-L84)
   runs `main()` on an event loop only when the file is launched directly.

## Folder contents

```text
01_simple-pydanticai-openai/
├── README.md
└── app/
    └── simple-ai-agent-pydanticai-azopenai.py
```

- [app/simple-ai-agent-pydanticai-azopenai.py](app/simple-ai-agent-pydanticai-azopenai.py)
  contains configuration, provider/model/agent setup, and execution.
- Dependencies live in the shared [requirements.txt](../requirements.txt) and
  are installed once into the shared `ai-agents/pydantic-framework/.venv`.
- Configuration lives in the shared, private `ai-agents/pydantic-framework/.env`.

## Frameworks and libraries

Observed on **2026-11-02** with the shared Linux virtual environment, Python
**3.12.3**. The manifest sets a lower bound for Pydantic AI only, so a fresh
install may resolve newer versions.

| Package / library | Purpose in this sample | Observed version / reference |
| --- | --- | --- |
| `pydantic-ai-slim[openai]` (import `pydantic_ai`) | `Agent`, `OpenAIResponsesModel`, `AzureProvider` | 2.64.0; [Agents](https://pydantic.dev/docs/ai/core-concepts/agent/), [OpenAI models](https://pydantic.dev/docs/ai/models/openai/) |
| `openai` | HTTP client used underneath `AzureProvider` | 3.42.1 (installed by the `openai` extra) |
| `python-dotenv` | Parses the shared `.env` file into a dictionary | 1.2.4; [python-dotenv docs](https://bbc2.github.io/python-dotenv/) |
| Python standard library | `asyncio`, `os`, `pathlib` | [Python docs](https://docs.python.org/3/) |

## Prerequisites and setup

- Python 3.12 (3.12.3 verified).
- An Azure OpenAI (or Foundry) resource with a deployed model that supports the
  Responses API, and an API key for that resource.
- Network access for installation and for the live model request.

**Linux, zsh or bash; start in the repository root.** Every stage shares one
environment, so run this once for the whole course:

```sh
cd ai-agents/pydantic-framework
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

In VS Code, select `ai-agents/pydantic-framework/.venv/bin/python` as the
interpreter for every stage.

## Configuration

Copy [`.env.example`](../.env.example) to `ai-agents/pydantic-framework/.env`
and fill in the values, or set them in the process environment.

| Setting | Required? | Meaning |
| --- | --- | --- |
| `AZURE_OPENAI_ENDPOINT` | Yes | Resource endpoint, such as `https://<resource>.openai.azure.com`; `/openai/v1` is added by the script |
| `AZURE_OPENAI_API_KEY` | Yes | Secret key for that resource |
| `AZURE_OPENAI_MODEL` | Yes | Deployment name, not the model family |

A nonempty process environment value wins over the `.env` value. Never commit
the `.env` file; the repository `.gitignore` already excludes it.

## Run and expected output

**Linux, zsh or bash; working directory: `ai-agents/pydantic-framework`.** This
makes a live, potentially billable request and was not run while writing this
README:

```sh
./.venv/bin/python 01_simple-pydanticai-openai/app/simple-ai-agent-pydanticai-azopenai.py
```

A successful run prints one generated sentence about Pydantic AI; wording is
nondeterministic. Pydantic AI also prints an informational banner to standard
error on first use; set `PYDANTIC_AI_NO_BANNER=1` in your shell to hide it.

## Exercises to try

1. Change the prompt to ask for three bullet points and compare the output.
2. Change the instructions to "Answer like a pirate." Instructions apply to
   every run of this agent; the prompt applies only to this run.
3. Print `response.usage` after the output to see the token counts for the run.

## Validation and troubleshooting

There is no test folder for this stage. From the repository root, run the
comment check with the shared interpreter:

```sh
./ai-agents/pydantic-framework/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/pydantic-framework/01_simple-pydanticai-openai/app/simple-ai-agent-pydanticai-azopenai.py
```

| Symptom | First check |
| --- | --- |
| `Missing required Azure OpenAI setting` | The shared `.env` is at `ai-agents/pydantic-framework/.env` and uses the exact names |
| `ModuleNotFoundError: pydantic_ai` | Use `ai-agents/pydantic-framework/.venv/bin/python`, not a system Python |
| 401 / authentication error | The API key belongs to the same resource as the endpoint |
| 404 / deployment not found | `AZURE_OPENAI_MODEL` is the deployment name and supports the Responses API |

## Learning links and progression

- [AI concepts: Pydantic AI provider, model, and agent](../../../docs/ai-concepts.md#pydantic-ai-provider-model-and-agent)
- [AI concepts: instructions versus user prompts](../../../docs/ai-concepts.md#instructions-versus-user-prompts)
- [Python concepts](../../../docs/python-concepts.md): coroutines, `await`, and helper functions.
- [Course recap](../README.md) for the full stage map.

Next, [stage 02](../02_simple-pydanticai-foundary/README.md) keeps the same
agent pattern but reaches the model through a Foundry project with Entra ID
authentication instead of an API key.
