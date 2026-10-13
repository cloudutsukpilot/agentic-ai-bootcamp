# Simple Short-Term Memory - Microsoft Agent Framework

<!-- markdownlint-configure-file {"MD013": false} -->

This is the sixth learning stage in the Microsoft Agent Framework course. It
keeps the local tool-enabled agent from stage 05, then creates one
`AgentSession` and reuses it for three user turns. The follow-up requests can
refer to earlier turns because the same session is passed to each
`agent.run(...)` call.

Short-term memory here means conversation context held for this running
workflow. It is not a database, a user profile, a durable transcript, or a
retrieval index. The sample does not configure persistence across process
restarts.

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Reuse one session so successive runs share conversation context |
| Framework | Microsoft Agent Framework for Python |
| Model provider | Microsoft Foundry project with a deployed model |
| Provider client | `FoundryChatClient` from `agent_framework.foundry` |
| Authentication | Async `DefaultAzureCredential` and Entra authorization |
| Local tool | `get_weather(location: str)`, registered with `@tool` |
| Conversation input | Three structured `Message(role="user", contents=[...])` objects |
| Session | One `agent.create_session()` object reused for all three runs |
| Output | Three model responses printed in order |
| Current status | Implemented in-process short-term conversation context |

## Previous implementation and technical delta

Stage 05 could already create an `Agent`, register `get_weather`, send one
structured request, and print `response.text`. It could answer a prompt, but
its source did not create a session or send a follow-up run with shared
conversation state. This stage keeps the same Foundry client, credentials,
agent instructions, local tool, message type, and response boundary, then adds
session creation and reuse.

| Previous stage/topic | Current stage | Practical reason for the change |
| --- | --- | --- |
| [Stage 05 creates one tool-enabled agent](../05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py#L92-L104) and runs one [structured request](../05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py#L106-L113). | [This stage creates one session](app/simple-ai-agent-maf-short-term-memory.py#L106-L107) and passes it to each run. | Let a follow-up request such as "those bullet points" refer to earlier turns instead of requiring the whole context in every new prompt. |
| Stage 05's `Agent` API already supported sessions, but did not activate one in its source. | [Three `Message` objects and session-aware runs](app/simple-ai-agent-maf-short-term-memory.py#L109-L135) demonstrate the capability. | Make the lifetime and reuse rule visible: one shared session carries this conversation; a new session starts a separate context. |

The construction and execution paths are:

```text
Previous: client + Agent(tools=[...]) -> Message -> run(prompt) -> response.text
Current:  client + Agent(tools=[...]) -> create_session() -> Message -> run(message, session=session) -> response.text
```

The arrows combine local setup with later model interaction; they do not mean
every arrow is a network call. `Agent(...)`, `Message(...)`, and
`create_session()` are local object construction. Each awaited `agent.run(...)`
can send a model request, and the provider may use the session's accumulated
conversation context when producing the response.

### What remains the same

The model deployment, project endpoint, Entra credential, agent instructions,
local randomized weather tool, structured message type, async cleanup, and
`response.text` output remain in place. The current sample makes three model
runs instead of one, so it can incur more network usage and model cost. Exact
responses and token usage are nondeterministic. Creating a session does not
make a Foundry-hosted agent, grant authorization, or create durable storage.

## Technical benefits of the new construct

`Agent.create_session()` returns an `AgentSession` value that the application
can deliberately pass to later `run(..., session=...)` calls. The framework
can then associate the later user message with the earlier turns held by that
session. This is useful for a support chat, a multi-step writing workflow, or a
research conversation in which a user says "summarize the points above" after
an earlier request.

The important design choice is explicit ownership and lifetime. This sample
creates the session inside `main`, reuses it for the three runs, and lets it
become unreachable when the process finishes. A future application could
choose a new session for a new conversation or add an explicit persistence
strategy, but neither restart persistence nor a database is implemented here.

## Supported capabilities and activation requirements

The matrix separates the current implementation from SDK mechanisms that need
additional application configuration.

| Capability / benefit | API and mechanism | Concrete use case | Previous API support | Current sample status |
| --- | --- | --- | --- | --- |
| Session creation | `agent.create_session()` returns an `AgentSession` | Start an isolated conversation for one user or workflow | Supported by the same `Agent` API, but unused in stage 05 | Implemented at [session creation](app/simple-ai-agent-maf-short-term-memory.py#L106-L107) |
| Context reuse | Pass the same object with `agent.run(message, session=agent_session)` | Resolve "those bullet points" using earlier turns | `Agent.run` accepted the `session` keyword; stage 05 did not pass it | Implemented for all three runs |
| Structured turn boundary | `Message(role="user", contents=[...])` represents each user turn | Keep speaker and content explicit while building multi-turn input | Stage 05 already supported `Message`; this stage uses three messages | Implemented |
| Context reset/isolation | Create a different session for a new conversation | Prevent one customer's chat history from entering another chat | Available through the same session API | Available but not demonstrated |
| Streaming | `agent.run(..., stream=True)` returns response updates | Show incremental text in a chat interface while retaining a session | Supported by the installed `Agent.run` API | Not implemented |
| Persistent conversation storage | Application-owned history store or configured persistence mechanism | Resume a conversation after process restart | Not supplied automatically by `create_session()` | Not implemented |
| Retrieval or RAG | A separately configured context provider and retrieval source | Add durable knowledge documents without treating them as chat history | Not configured by stage 05 or this stage | Not implemented |
| MCP tools | MCP client/server transport and lifecycle | Reuse protocol-based tools alongside a conversation | Separate capability from sessions | Not implemented; stage 08 covers MCP |

Sessions require deliberate reuse. Creating a session and then omitting it from
a later run does not select that context. A session is also not proof of
unlimited context: longer conversations can increase input tokens and cost,
and provider/framework history or compaction behavior may impose limits. Tools
still need registration, implementation, permissions, and compatible model
support. MCP supplies protocol-based tools; it does not itself provide
conversation memory.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Single local agent and fixed instructions | Implemented | One `Agent` is configured with Foundry client and instructions |
| Local function tool | Implemented | `get_weather` is decorated and registered, returning randomized local data |
| Short-term conversation context | Implemented | One session is reused across three `agent.run(...)` calls |
| Session reset or separate-user isolation | SDK-supported, not implemented | The script never creates a second session |
| Persistent memory | Not implemented | No database, file store, retention policy, or restart recovery exists |
| Retrieval or RAG | Not implemented | No retrieval source or index is configured |
| MCP tools | Not implemented | No MCP transport or server is configured |
| Streaming | Not implemented | Each run awaits a completed response |
| Multi-agent orchestration | Not implemented | Only one local agent is configured |
| Observability | Not implemented | No application telemetry or trace exporter is configured |

## Folder contents

```text
06_simple-maf-short-term-memory/
|-- README.md
|-- requirements.txt
|-- app/
|   `-- simple-ai-agent-maf-short-term-memory.py
|-- tests/
|   `-- .gitkeep
`-- .venv/                    # local generated environment, not source
```

- [app/simple-ai-agent-maf-short-term-memory.py](app/simple-ai-agent-maf-short-term-memory.py)
  contains configuration, the local tool, agent setup, session creation, three
  runs, and output.
- [requirements.txt](requirements.txt) lists this stage's unpinned dependencies.
- `tests/.gitkeep` preserves an empty test placeholder; it is not an automated
  test suite.
- `app/.env`, `.venv/`, `__pycache__/`, and credentials are private or generated
  artifacts and are not shipped sample files.

## Frameworks and libraries

The following versions were observed with this stage's Linux virtual-environment
interpreter on **2026-10-13**. The manifest is unpinned, so a fresh install may
resolve different versions.

| Package / library | Purpose in this sample | Observed version / reference |
| --- | --- | --- |
| `agent-framework-foundry` | Provides `FoundryChatClient`; the installed core dependency provides `Agent`, `Message`, and `tool` | 1.14.1; [Foundry provider documentation](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python) |
| `agent-framework-core` | Provides the local agent, message, session, and tool APIs | 1.21.0; [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/) |
| `azure-identity` | Supplies async `DefaultAzureCredential` for Entra token acquisition | 1.26.0; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) |
| `python-dotenv` | Parses the app-local dotenv file into a dictionary | 1.2.4; [python-dotenv documentation](https://bbc2.github.io/python-dotenv/) |
| Python standard library | `asyncio`, `os`, `pathlib`, and `random` support the event loop, configuration, paths, and demo values | [Python documentation](https://docs.python.org/3/) |

Python 3.12.3 was verified here. The installed framework packages declare a
Python 3.10-or-newer floor, but this sample does not certify every supported
interpreter version.

## How it works

1. [`dotenv_values`](app/simple-ai-agent-maf-short-term-memory.py#L29-L31)
   reads an app-local `.env` file beside the script without exporting values.
2. [`required_setting`](app/simple-ai-agent-maf-short-term-memory.py#L34-L44)
   chooses a nonempty process environment value first, then the dotenv
   dictionary, and raises `ValueError` if neither exists.
3. [`get_weather`](app/simple-ai-agent-maf-short-term-memory.py#L47-L68) is
   wrapped by `@tool`. Its annotation and docstring describe a local function
   that can be selected during an agent run; it does not call a weather service.
4. [`DefaultAzureCredential` and `FoundryChatClient`](app/simple-ai-agent-maf-short-term-memory.py#L79-L92)
   prepare authenticated model communication. Construction does not provision a
   hosted Foundry agent.
5. [`Agent`](app/simple-ai-agent-maf-short-term-memory.py#L93-L107) receives the
   client, role instructions, tool, and then creates one local session.
6. [`Message`](app/simple-ai-agent-maf-short-term-memory.py#L109-L110) creates
   each user turn. [`agent.run(..., session=agent_session)`](app/simple-ai-agent-maf-short-term-memory.py#L111-L135)
   sends three requests through the same conversation context.
7. The nested async context managers close credential and client resources, and
   the [script entry guard](app/simple-ai-agent-maf-short-term-memory.py#L138-L142)
   runs the coroutine only when the file is launched directly.

## Prerequisites and setup

- Python compatible with the installed framework packages; Python 3.12.3 was
  verified here.
- An existing Microsoft Foundry project with a deployed model that supports the
  Responses API and tool calling.
- An identity available to `DefaultAzureCredential` with permission to invoke
  the selected deployment. Authentication and authorization are separate.
- Network access for dependency installation and the three live model requests.

**Linux, zsh or bash; start in the repository root.** These commands are
instructional and use this stage's own environment:

```sh
cd ai-agents/microsoft-agent-framework/06_simple-maf-short-term-memory
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Select this stage's `.venv/bin/python` in VS Code. Explicit interpreter paths
avoid accidentally using a system Python without the required packages.

## Configuration

Create `app/.env` beside the entry-point file, or set the values in the process
environment. The names intentionally retain the repository's historical
`FOUNDARY_*` spelling.

| Setting | Required? | Meaning and precedence |
| --- | --- | --- |
| `FOUNDARY_MODEL` | Yes | Deployed model name passed as `model`; it is not an agent ID |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | Foundry project endpoint passed as `project_endpoint`, not a guessed full API route |

A nonempty process environment value wins over the matching `.env` value. A
missing or empty result raises `ValueError` before authentication or model use.
Placeholder configuration only:

```dotenv
FOUNDARY_MODEL=<your-model-deployment-name>
FOUNDARY_PROJECT_ENDPOINT=https://<your-foundry-project-endpoint>
```

Do not commit credentials, tokens, private endpoints, or identity configuration.
The dotenv dictionary is not exported into `os.environ`, and the script does
not print configuration values.

## Run and expected output

**Linux, zsh or bash; working directory: this stage folder after setup.** This
command makes three live, potentially billable model requests and was not run
during this documentation update:

```sh
./.venv/bin/python app/simple-ai-agent-maf-short-term-memory.py
```

The script accepts no command-line input. It prints three labeled response
blocks. The second request asks for descriptions of "those bullet points," and
the third asks for a summary of "all the above information"; a correctly
reused session gives the model the conversation context needed for those
references. Exact wording, tool selection, and response length are
nondeterministic. Configuration, credential, authorization, network, or
provider failures produce a nonzero process exit.

## Validation and troubleshooting

The stage's test directory is an empty placeholder, so no automated behavior
suite is claimed. Safe offline checks for this update use the stage interpreter
and do not call Foundry:

```sh
./ai-agents/microsoft-agent-framework/06_simple-maf-short-term-memory/.venv/bin/python \
  -m py_compile \
  ai-agents/microsoft-agent-framework/06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py

./ai-agents/microsoft-agent-framework/06_simple-maf-short-term-memory/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/microsoft-agent-framework/06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py
```

The comment placement check and syntax compilation were run for this update.
Live model, Azure identity, and tool-selection behavior were deliberately not
run. Workspace-level import diagnostics can appear when the editor uses a
system interpreter instead of this stage's `.venv/bin/python`.

| Symptom | First check |
| --- | --- |
| Missing setting | Use the exact `FOUNDARY_*` names in `app/.env` or the process environment |
| Import error | Select this stage's interpreter and install this stage's manifest |
| Follow-up lacks earlier context | Confirm every follow-up passes the same `agent_session` object; creating a new session starts another context |
| Context disappears after restart | Expected for this sample; add an application-owned persistence strategy rather than treating `AgentSession` as a database |
| Authentication or authorization failure | Check the credential source and its separate Foundry project/deployment permissions |
| Deployment or endpoint error | Confirm the project endpoint, deployment name, and installed client compatibility |

## Learning links and progression

- Python: [coroutines and `async def`](../../../docs/python-concepts.md#coroutines-and-async-def), [await](../../../docs/python-concepts.md#await), and [async context managers](../../../docs/python-concepts.md#async-context-managers).
- AI architecture: [client versus local agent](../../../docs/ai-concepts.md#foundry-client-versus-local-agent), [structured messages](../../../docs/ai-concepts.md#messages-as-structured-conversation-items), [short-term sessions](../../../docs/ai-concepts.md#short-term-conversation-sessions), and [tool calling](../../../docs/ai-concepts.md#function-tools-and-the-tool-decorator).
- Azure: [Foundry project endpoints and deployments](../../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments) and [async credentials](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).

The course progression is conceptual and uses separate folders: [simple
agent](../03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py) ->
[structured messages](../04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py)
-> [local tools](../05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py)
-> this short-term session stage -> [long-term memory](../07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py)
-> [MCP](../08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py). These stages are
separate samples; later folders are not evidence that this sample implements
persistent memory or MCP.

This is a learning script rather than a production service. It has no
interactive input loop, persistent memory, retrieval index, custom retry policy,
conversation cleanup command, or application telemetry configuration.
