# Simple AgentClass - Microsoft Agent Framework

This is the third learning stage in the Microsoft Agent Framework course. It
shows how an `Agent` object combines a model client, a readable name, and
behavior instructions, then runs one prompt against a model hosted in
Microsoft Foundry.

The agent is created locally in Python. Creating this object does not provision
a separate hosted Foundry agent resource.

## Overview

| Dimension | This stage |
| --- | --- |
| Learning objective | Understand the responsibilities of an agent object |
| Framework | Microsoft Agent Framework for Python |
| Model provider | Microsoft Foundry project with a deployed model |
| Provider client | `FoundryChatClient` from `agent_framework.foundry` |
| Authentication | Microsoft Entra token from async `DefaultAzureCredential` |
| Input | One hardcoded prompt |
| Output | The returned `response.text` printed to standard output |
| Current status | Implemented one-shot learning sample |

In this sample, "AgentClass" describes the agent object used by the lesson.
The actual framework symbol is [`Agent`](app/simple-ai-agent-maf-agentclass.py#L16),
constructed with `Agent(...)` in the entry point.

## What The Agent Represents

The local `Agent` object brings together the parts needed for one agent run:

| Responsibility | Implementation |
| --- | --- |
| Model access | `FoundryChatClient` sends instructions and user input to the deployed model |
| Identity | `name` gives the local agent a readable label |
| Behavior | `instructions` defines the agent's role and response style |
| Prompt execution | `agent.run(...)` sends the user prompt for processing |
| Result handling | `response.text` contains the completed response text |

The agent is not the model itself. `FoundryChatClient` connects the local
Python process to the Foundry project and model deployment. `Agent` adds
application-specific behavior through its name and instructions.

## Why This Stage Adds `Agent`

`Agent` is an application-level execution object: it combines a model client
with role instructions and optional tools, context providers, and middleware.
It provides a common `run(...)` interface for that configuration. This is useful
when an application needs more than an isolated prompt: calling business
functions, continuing a conversation, injecting application context, or
intercepting execution requires explicit configuration and coordination.

### Previous implementation and technical delta

| Previous stage/topic | Current stage | Practical reason for the change |
| --- | --- | --- |
| [Stage 02 factory construction](../02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L53-L69): `client.as_agent(name=..., instructions=...)` | [Stage 03 explicit construction](app/simple-ai-agent-maf-agentclass.py#L56-L74): `Agent(client=chat_client, name=..., instructions=...)` | Agent configuration can be assembled independently of the provider client's factory; a caller supplies a compatible client as a dependency |
| [Stage 02 one-shot execution](../02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L71-L75) | [Stage 03 one-shot execution](app/simple-ai-agent-maf-agentclass.py#L76-L80) | Both use the agent's execution API; Stage 03 establishes an explicit constructor where later configuration can be composed |

**Important API distinction:** Stage 02 already uses an `Agent`: the installed
`as_agent(...)` implementation delegates to `Agent(client=self, ...)`. Direct
construction is not a more powerful agent type. Its technical advantage is an
explicit composition point; the capabilities below are available through
either construction path. Stage 03 currently enables only client binding,
name, instructions, and one completed-response run.

```text
Stage 02: client.as_agent(...) -> Agent -> agent.run(prompt)
Stage 03: Agent(client=chat_client, ...) -> Agent -> agent.run(prompt)
```

Construction assembles local objects. `agent.run(...)` is the operation that
requests model work through the configured client. The changed prompt asks
about the Agent class rather than the framework; that explains the different
response topic, not a new constructor-dependent model capability.

### Technical benefits of the new construct

**1. Explicit dependency injection and provider-independent composition.**
`Agent` accepts a client implementing the framework's chat-response contract
(`SupportsChatGetResponse`). Application code can therefore build the agent
from a client supplied by another module instead of calling a provider-specific
factory inside the agent-configuration code. For example, a future
`build_support_agent(client)` helper could centralize support instructions and
tools while its caller chooses a real provider adapter or an offline fake
client. This separates business behavior from connection setup and gives tests
a replaceable model dependency. Such a helper and tests are not implemented
here; factory-created agents can also be tested and reused.

**2. Reusable configuration for different application roles.**
`instructions`, `tools`, and `default_options` configure agent behavior without
repeating that setup in every user prompt. A future application could construct
a billing agent and a technical-support agent with different instructions and
tool sets while reusing a compatible client. The client handles model access;
each agent carries its role configuration. Sharing a client does not itself
share conversation history, and instructions are not a security boundary.
Stage 03 demonstrates the instructions part with one agent only.

**3. Extension points for execution, context, and interaction.**
Instead of assembling a separate ad hoc mechanism for each feature, an
application can attach supported components to `Agent` and use its execution
API. For example, an order-support agent could combine an order-lookup tool,
a customer-context provider, and middleware that checks requests. A reused
session could carry the conversation into follow-up questions, and streaming
could update a chat UI before the full answer completes. These extensions need
explicit implementation; the following matrix identifies the relevant APIs.

### Supported capabilities and activation requirements

These are verified SDK extension mechanisms, **not features newly enabled by
Stage 03**. The factory also returns an `Agent` and supports them.

| Capability / benefit | API and mechanism | Concrete use case | Previous API support | Current sample status |
| --- | --- | --- | --- | --- |
| Role configuration and reuse | `instructions`, `name`, `default_options` bind role guidance and default request settings to an agent | Configure distinct support roles without rebuilding behavior in every prompt | Factory accepts the same configuration | Name and instructions used; no explicit default options |
| Function tools | `tools` registers callable tools; with compatible model/client support, model-requested function calls can be executed and results returned to the model | Look up an order using application code rather than asking the model to invent its status | Factory accepts `tools`; `run` also accepts per-run tools | Available, not registered |
| Multi-turn conversation context | `create_session()` creates an `AgentSession`; pass the same session to successive `run(..., session=session)` calls to carry history/state through the configured history mechanism | Interpret “What about the second order?” using earlier turns | Available on the factory-created agent | Available, no session created or reused |
| Context injection | `context_providers` supply additional context during invocation | Supply customer details or retrieved knowledge before answering | Factory accepts `context_providers` | Available, no provider configured |
| Execution interception | `middleware` wraps agent execution or chat/tool calls, depending on middleware type | Validate a request, measure execution, or apply a tool policy at the relevant interception layer | Factory accepts `middleware`; `run` also accepts it | Available, no custom middleware attached |
| Streaming output | `run(..., stream=True)` returns a stream of response updates instead of waiting for only the complete result | Display incremental response text in a chat UI | Available on the factory-created agent | Available, sample awaits the complete response |

Sessions do not automatically create durable memory: storage across process
restarts needs a suitable history/state persistence strategy. A context provider
does not automatically create a retrieval index. Tools need implementations,
permissions, and a compatible model; middleware policies and telemetry exports
must be configured explicitly. Neither constructor provisions a hosted agent.

The practical next step is to add one of these mechanisms to the existing
agent configuration, not to expect more capable behavior from `Agent(...)`
alone. See the shared [agent composition guide](../../../docs/ai-concepts.md#explicit-agent-composition)
for the dependency-injection pattern, the official
[agent capabilities overview](https://learn.microsoft.com/en-us/agent-framework/agents/),
and [tool mechanisms and provider support](https://learn.microsoft.com/en-us/agent-framework/agents/tools/).
API details above were inspected in Stage 03's Python 3.12.3 environment with
`agent-framework` 1.21.0 on 2026-10-13; newer documentation may describe
additional APIs not available in that environment.

## Execution Flow

The script follows this sequence:

1. [`dotenv_values`](app/simple-ai-agent-maf-agentclass.py#L27) reads an
   app-local `.env` file into a dictionary without exporting values.
2. [`required_setting`](app/simple-ai-agent-maf-agentclass.py#L32) resolves
   each setting from the process environment first, then the `.env` dictionary.
3. [`DefaultAzureCredential`](app/simple-ai-agent-maf-agentclass.py#L54)
   provides an async Entra credential. The credential chain obtains a token
   from an available identity source; it does not grant Foundry permissions by
   itself.
4. [`FoundryChatClient`](app/simple-ai-agent-maf-agentclass.py#L56) is created
   with the model deployment, project endpoint, and credential.
5. [`Agent`](app/simple-ai-agent-maf-agentclass.py#L67) is created with the
   client, name, and instructions.
6. [`agent.run`](app/simple-ai-agent-maf-agentclass.py#L78) sends one hardcoded
   prompt and the script prints the returned text.
7. Async context managers close the credential and client resources after the
   run completes.

The live response requires a network request to Microsoft Foundry and may
incur provider charges.

## Capabilities

| Capability | Status | Notes |
| --- | --- | --- |
| Agent object with name and instructions | Implemented | `Agent` receives `client`, `name`, and `instructions` |
| Single-agent prompt and response | Implemented | One `agent.run(...)` call returns one response |
| Foundry model client integration | Implemented | `FoundryChatClient` uses the configured project and deployment |
| Local function tools | Not implemented | No tool functions are registered |
| MCP tools | Not implemented | MCP is a later learning stage |
| Short-term conversation memory | Not implemented | No reusable session, thread, or multi-turn history exists |
| Persistent memory | Not implemented | No database, file store, or other persistence is configured |
| Streaming | Not implemented | The complete response is printed after `agent.run` finishes |
| Multi-agent orchestration | Not implemented | This stage focuses on one agent object |
| Retrieval or RAG | Not implemented | No retrieval source or index exists |
| Middleware | Not implemented | No middleware is attached to the agent |

An SDK may support these features without this sample enabling them.

## Folder Contents

```text
03_simple-maf-agentclass/
├── README.md
├── requirements.txt
├── app/
│   └── simple-ai-agent-maf-agentclass.py
├── tests/
└── .venv/
```

- [app/simple-ai-agent-maf-agentclass.py](app/simple-ai-agent-maf-agentclass.py)
  contains configuration loading, client and agent construction, the prompt,
  and output handling.
- [requirements.txt](requirements.txt) lists this stage's dependencies.
- `tests/` is currently a placeholder and does not contain an automated test
  suite.
- `.env`, `.venv/`, `__pycache__/`, and other generated or private files are
  local artifacts and must not be committed.

## Dependencies

The current [requirements.txt](requirements.txt) contains:

- `agent-framework` for the core `Agent` orchestration object.
- `agent-framework-foundry` for `FoundryChatClient`, imported from
  `agent_framework.foundry`.
- `azure-identity` for async `DefaultAzureCredential`.
- `python-dotenv` for reading the app-local `.env` file.

The existing stage 03 virtual environment used for offline checks resolved
these package versions: Python 3.12.3, `agent-framework` 1.21.0,
`agent-framework-foundry` 1.14.1, `azure-identity` 1.26.0, and
`python-dotenv` 1.2.4. The stage manifest is unpinned, so a fresh installation
may resolve different versions.

Useful references:

- [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Microsoft Agent Framework source repository](https://github.com/microsoft/agent-framework)
- [DefaultAzureCredential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python)
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)

## Prerequisites And Setup

Before running the sample, you need:

- Python and an isolated virtual environment.
- A Microsoft Foundry project with a deployed model.
- An Entra identity recognized by `DefaultAzureCredential`.
- Permission for that identity to invoke the selected Foundry deployment.
- Network access for package installation and the live model request.

From the repository root, create the stage environment and install its
dependencies:

```bash
cd ai-agents/microsoft-agent-framework/03_simple-maf-agentclass
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Select `03_simple-maf-agentclass/.venv/bin/python` with **Python: Select
Interpreter** in VS Code.

## Configuration

Create `app/.env` beside the Python entry point:

```dotenv
FOUNDARY_MODEL=your-foundry-model-deployment
FOUNDARY_PROJECT_ENDPOINT=https://your-foundry-project-endpoint
```

The source intentionally retains the existing `FOUNDARY_*` spelling for
compatibility with this sample's configuration. `FOUNDARY_MODEL` is the model
deployment name, not necessarily the model family name. The project endpoint
identifies the Foundry project and should not be replaced with a guessed full
API route.

Configuration precedence is:

1. A nonempty process environment variable.
2. The matching value in `app/.env`.
3. A `ValueError` if neither source contains a value.

The script does not print configuration values. Do not commit credentials,
tokens, or private endpoints to the repository.

## Run

From this stage folder, after configuring Entra access and `app/.env`:

```bash
.venv/bin/python app/simple-ai-agent-maf-agentclass.py
```

The script accepts no command-line input. It sends the hardcoded prompt,
prints the model's text, and exits after the response completes. The response
wording is nondeterministic, so the expected result is explanatory text rather
than an exact sentence.

Authentication, authorization, configuration, network, or provider failures
raise an exception and produce a nonzero process exit. A missing setting raises
`ValueError` before the model request is made.

## Validation

The following offline checks use the existing stage 01 interpreter and do not
make a Foundry request:

```bash
./ai-agents/microsoft-agent-framework/01_simple-maf-openai/.venv/bin/python \
  -m py_compile \
  ai-agents/microsoft-agent-framework/03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py

./ai-agents/microsoft-agent-framework/01_simple-maf-openai/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/microsoft-agent-framework/03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py

./ai-agents/microsoft-agent-framework/01_simple-maf-openai/.venv/bin/python \
  -c 'from agent_framework import Agent; from agent_framework.foundry import FoundryChatClient; from azure.identity.aio import DefaultAzureCredential; from dotenv import dotenv_values; print("Imports OK")'
```

The exact imports, Python syntax, and learning-comment placement were verified
with that existing interpreter. No automated behavior tests exist in `tests/`,
and no live model request was made during documentation validation.

## Troubleshooting

| Symptom | First check |
| --- | --- |
| Framework imports cannot be resolved | Select this stage's `.venv` and install `requirements.txt` |
| `ModuleNotFoundError` with `/usr/bin/python3` | Run with `.venv/bin/python` or select that interpreter in VS Code |
| A required setting is missing | Use the exact `FOUNDARY_*` name in `app/.env` or the process environment |
| Authentication fails | Check the `DefaultAzureCredential` identity source and sign-in state |
| Authorization fails | Check the Foundry project roles assigned to the authenticated identity |
| Deployment or API is not found | Confirm the project endpoint, deployment name, and installed client compatibility |
| A later prompt loses context | This sample has no reusable session or multi-turn conversation history |

## Learning Links

- [Python classes](https://docs.python.org/3/tutorial/classes.html) explains
  classes, instances, attributes, and methods used by the `Agent` object.
- [Python concepts in this repository](../../../docs/python-concepts.md) covers
  asynchronous functions, `await`, clients, agents, and credential lifecycles.
- [Stage 01 README](../01_simple-maf-openai/README.md) shows a neighboring
  single-agent Azure OpenAI sample and distinguishes a model client from a
  local agent.
- [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/)
  and [source repository](https://github.com/microsoft/agent-framework) provide
  the framework references.

This stage is a learning aid, not a production agent. It does not establish
retry behavior, observability, secret storage, authorization policy, data
retention, or production deployment practices.
