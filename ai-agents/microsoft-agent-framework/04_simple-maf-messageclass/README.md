# Simple Message Class - Microsoft Agent Framework

This is the fourth learning stage in the Microsoft Agent Framework course. It
keeps the stage 03 local `Agent` construction and Foundry model connection, but
passes the user input as an explicit `Message` object instead of a bare string.

The sample demonstrates message structure, not a new hosted-agent resource or a
new model capability. The earlier `agent.run("...")` form could already ask the
model a question and print `response.text`; this stage makes the speaker role
and content collection visible to the application.

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Represent one user input as a structured `Message` |
| Framework | Microsoft Agent Framework for Python |
| Model provider | Microsoft Foundry project with a deployed model |
| Provider client | `FoundryChatClient` from `agent_framework.foundry` |
| Authentication | Async Entra credential from `DefaultAzureCredential` |
| Input | One `Message(role="user", contents=[...])` object |
| Output | The completed `response.text` printed to standard output |
| Current status | Implemented one-shot learning sample |

## Previous implementation and technical delta

| Previous stage/topic | Current stage | Practical reason for the change |
| --- | --- | --- |
| [Stage 03 creates an `Agent`](../03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py#L67) and passes a string to [`agent.run(...)`](../03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py#L78) | [Stage 04 imports and constructs `Message`](app/simple-ai-agent-maf-messageclass.py#L16) before passing it to [`agent.run(...)`](app/simple-ai-agent-maf-messageclass.py#L86) | Make who is speaking and what content is being sent explicit, so later conversation, multimodal content, metadata, or serialization can use a structured boundary |

Construction and execution are separate operations:

```text
Previous: Agent -> agent.run(prompt string) -> response.text
Current:  Agent -> Message(role, contents) -> agent.run(message) -> response.text
```

The arrows above describe local object construction and the later request flow;
they do not imply that constructing `Message` makes a network call. The client
still communicates with Foundry, `Agent` still coordinates the run, and the
awaited `agent.run(...)` still initiates model interaction.

The installed `Agent.run` API accepts both a string input and structured message
inputs. Therefore `Message` is not required merely to obtain an answer. Its
technical benefit is the explicit conversation data model: a message carries a
role and a sequence of content items, with optional author, ID, and application
properties. The current sample uses only a user role and one text item.

## Technical benefits of the new construct

The structured boundary makes speaker classification, content composition,
metadata, and serialization explicit. Those mechanisms matter when an
application needs to preserve more than prompt text, while the current sample
keeps the smallest useful example: one user message containing one text item.

### What a `Message` owns

`Message` represents one item in a chat conversation. In the installed SDK,
`role` can identify a `user`, `assistant`, `system`, or `tool` speaker, while
`contents` stores one or more text or other content items. The `text` property
returns the text portions joined together. Optional `author_name`, `message_id`,
and `additional_properties` support attribution, tracking, and local workflow
metadata; they are not configured by this sample.

### Supported capabilities and activation requirements

The matrix separates SDK mechanisms from what this stage actually enables.

| Capability / benefit | API and mechanism | Concrete use case | Previous API support | Current sample status |
| --- | --- | --- | --- | --- |
| Speaker classification | `Message(role="user")` stores who authored the item | Distinguish a human request from system instructions, an assistant reply, or a tool result | Stage 03 could send a string, but did not expose a role in its source | User role implemented |
| Multiple content types | `contents=[...]` accepts text and content objects; text is exposed through `message.text` | Combine a question with an image or other supported content for a multimodal model | `Agent.run` supports message inputs when the caller constructs them; stage 03 did not | One text item implemented; multimodal content not configured |
| Message metadata | `author_name`, `message_id`, and `additional_properties` carry optional local metadata | Correlate turns with a user or workflow without placing tracking data in the prompt text | Not exposed by stage 03's string input; available through a structured `Message` | Available, not configured |
| Serialization | `Message` inherits serialization helpers such as `to_dict()` and `to_json()` | Store or transport a conversation representation when an application adds a persistence strategy | Not used by stage 03 | Available, not used |
| Conversation history | Pass messages through repeated runs and explicitly reuse `Agent.create_session()` | Keep prior turns available for a follow-up question | The SDK supports sessions through either agent construction path | No session or multi-turn loop implemented |

Content items, sessions, persistence, and model support have prerequisites. A
`Message` object does not create durable memory, upload an image by itself, or
grant permission to a model service. MCP, tools, retrieval, and observability
are also not configured here.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Single local agent and fixed prompt | Implemented | One structured message is passed to one `agent.run(...)` call |
| Foundry project inference and Entra credential | Implemented | Same client, endpoint, deployment, and credential path as stage 03 |
| Structured user message | Implemented | User role plus one text content item |
| Assistant, system, or tool messages | SDK-supported, not implemented | No other message roles are constructed |
| Mixed or multimodal content | SDK-supported, not implemented | No image or other non-text content is supplied |
| Message metadata or serialization | SDK-supported, not implemented | No author, ID, additional properties, or persistence is configured |
| Local tools / MCP | Not implemented | No tool registration or MCP connection |
| Short-term conversation memory | Not implemented | No session creation, reuse, or multi-turn history |
| Persistent memory / retrieval or RAG | Not implemented | No storage or retrieval source |
| Streaming / multi-agent orchestration | Not implemented | One completed response is awaited |

## Folder contents

| Item | Purpose |
| --- | --- |
| [app/simple-ai-agent-maf-messageclass.py](app/simple-ai-agent-maf-messageclass.py) | Configuration, client and agent setup, `Message` construction, invocation, and output |
| [requirements.txt](requirements.txt) | This stage's unpinned dependencies |
| [README.md](README.md) | Setup, source-grounded explanation, and validation notes |
| `tests/` | Empty placeholder; it is not an automated test suite |
| `app/.env` | Optional private configuration created locally; not a shipped file |
| `.venv/` and `__pycache__/` | Generated local artifacts, not source files |

## Frameworks and libraries

The following versions were observed with this stage's Linux virtual-environment
interpreter on **2026-10-13**. The manifest is unpinned, so a fresh install may
resolve different versions.

| Package / library | Purpose here | Observed version / reference |
| --- | --- | --- |
| `agent-framework-foundry` | Provides `FoundryChatClient`; it installs the core framework dependency used by `Agent` and `Message` | 1.14.1; [Foundry provider documentation](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python) |
| `agent-framework-core` | Provides the local `Agent` and `Message` abstractions transitively | 1.21.0; [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/) |
| `azure-identity` | Supplies async `DefaultAzureCredential` for Entra token acquisition | 1.26.0; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) |
| `python-dotenv` | Reads the app-local `.env` file into a dictionary | 1.2.4; [library documentation](https://bbc2.github.io/python-dotenv/) |
| Python standard library | `asyncio` runs the coroutine, `os` reads process settings, and `pathlib` locates the dotenv file | [asyncio](https://docs.python.org/3/library/asyncio.html), [os.getenv](https://docs.python.org/3/library/os.html#os.getenv), [pathlib](https://docs.python.org/3/library/pathlib.html) |

Python 3.12.3 was verified here. The installed framework packages declare a
Python 3.10-or-newer floor, but this sample does not certify every supported
interpreter version.

## How it works

1. [`dotenv_values`](app/simple-ai-agent-maf-messageclass.py#L27) reads an
   app-local `.env` file without exporting its values into the process.
2. [`required_setting`](app/simple-ai-agent-maf-messageclass.py#L32) chooses a
   nonempty process environment value first, then the dotenv dictionary.
3. [`DefaultAzureCredential`](app/simple-ai-agent-maf-messageclass.py#L54)
   supplies the credential used by the client when a token is requested.
   Authentication and Foundry authorization are separate concerns.
4. [`FoundryChatClient`](app/simple-ai-agent-maf-messageclass.py#L56) is created
   with the deployment name, project endpoint, and credential. This configures
   model communication; it does not provision a hosted agent.
5. [`Agent`](app/simple-ai-agent-maf-messageclass.py#L67) is constructed locally
   with the client, name, and instructions.
6. [`Message`](app/simple-ai-agent-maf-messageclass.py#L77) stores the user role
   and prompt text before [`agent.run`](app/simple-ai-agent-maf-messageclass.py#L86)
   sends the input through the client.
7. The script prints [`response.text`](app/simple-ai-agent-maf-messageclass.py#L88)
   and exits the async context managers, which close client and credential
   resources.

## Prerequisites and setup

- Python compatible with the installed dependencies; Python 3.12.3 was checked.
- An existing Microsoft Foundry project and deployed model supporting the
  configured client/API. This script creates neither resource.
- An identity available to `DefaultAzureCredential`, with permission to invoke
  the selected deployment.
- Network access for package installation and the live model request.

**Linux, zsh or bash; start in the repository root.** These commands are
instructional and were not rerun during documentation validation:

```sh
cd ai-agents/microsoft-agent-framework/04_simple-maf-messageclass
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Select this stage's `.venv/bin/python` in VS Code. Explicit interpreter paths
avoid accidentally using a different shell environment.

## Configuration

Create a private `app/.env` beside the entry point, or set these names in the
process environment:

```dotenv
FOUNDARY_MODEL=<your-model-deployment-name>
FOUNDARY_PROJECT_ENDPOINT=https://<your-foundry-project-endpoint>
```

| Setting | Required | Meaning / precedence |
| --- | --- | --- |
| `FOUNDARY_MODEL` | Yes | The deployed model name, not an agent ID or necessarily a model family name; process environment wins over the dotenv file |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | The Foundry project URL; process environment wins over the dotenv file |

The source intentionally retains the repository's existing `FOUNDARY_*`
spelling. Missing or empty values raise `ValueError` before the client is used.
Do not commit credentials, tokens, or private endpoints.

## Run and expected output

**Linux, zsh or bash; working directory: this stage folder.** This command
makes a live model request and may incur provider charges:

```sh
./.venv/bin/python app/simple-ai-agent-maf-messageclass.py
```

The prompt is hardcoded inside the `Message`; the script is not interactive.
Successful execution prints model-generated explanatory text and exits. Exact
wording is nondeterministic and was not observed during documentation checks.
Configuration, authentication, authorization, network, or provider failures
produce an exception and nonzero exit status.

## Validation and troubleshooting

From the repository root, the following offline checks use this stage's
interpreter and do not call Foundry:

```sh
./ai-agents/microsoft-agent-framework/04_simple-maf-messageclass/.venv/bin/python \
  -m py_compile \
  ai-agents/microsoft-agent-framework/04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py

./ai-agents/microsoft-agent-framework/04_simple-maf-messageclass/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/microsoft-agent-framework/04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py
```

The local validation also constructed `Message(role="user", contents=[...])`
and checked its role and text property. The `tests/` folder is empty, so no
automated behavior suite is claimed. Live model, Azure identity, and provider
compatibility checks were deliberately not run.

| Symptom | First check |
| --- | --- |
| Missing setting | Use the exact `FOUNDARY_*` names in `app/.env` or the process environment |
| Import error | Select this stage's interpreter and install this stage's manifest |
| Authentication or authorization failure | Check the credential source and its separate Foundry project/deployment permissions |
| Deployment or endpoint error | Confirm the project endpoint, deployment name, and installed client compatibility |
| Follow-up message lacks context | This sample creates one message and does not create or reuse a session |

## Learning links and progression

- Python: [functions and required settings](../../../docs/python-concepts.md#helper-functions-and-required-settings), [await](../../../docs/python-concepts.md#await), and [async context managers](../../../docs/python-concepts.md#async-context-managers).
- AI architecture: [client versus local agent](../../../docs/ai-concepts.md#foundry-client-versus-local-agent), [instructions versus prompts](../../../docs/ai-concepts.md#instructions-versus-user-prompts), and [structured messages](../../../docs/ai-concepts.md#messages-as-structured-conversation-items).
- Azure: [Foundry project endpoints and deployments](../../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments) and [async credentials](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).

The surrounding course continues with [local tools](../05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py), [short-term memory](../06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py), [long-term memory](../07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py), and [MCP](../08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py). These are separate learning stages, not capabilities enabled by this sample. MCP supplies protocol-based tools; it does not automatically provide conversation memory.

This is a learning script rather than a production service. It has no
interactive loop, local tools, MCP connection, persistent memory, retrieval
index, custom retry policy, or application telemetry configuration.
