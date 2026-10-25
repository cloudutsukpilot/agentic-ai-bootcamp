# Simple Tool Decorator - Microsoft Agent Framework

<!-- markdownlint-configure-file {"MD013": false} -->

This is the fifth learning stage in the Microsoft Agent Framework course. It
adds a local Python function that the model can request during an agent run.
The sample uses a weather function with randomized demo data, so it teaches the
tool-calling boundary without calling a weather API or another external system.

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Register a Python callable as a model-selectable tool |
| Framework | Microsoft Agent Framework for Python |
| Model provider | Microsoft Foundry project with a deployed model |
| Provider client | `FoundryChatClient` from `agent_framework.foundry` |
| Authentication | Async `DefaultAzureCredential` and Entra authorization |
| Tool | `get_weather(location: str)`, decorated with `@tool` |
| Input | One structured user message asking about weather in India |
| Output | Model-generated text that may include the tool's randomized result |
| Current status | Implemented one-shot local-tool demonstration |

A **tool** is application-owned code that an agent can request while answering a
user. The model does not become Python code and the tool decorator does not
make an arbitrary operation safe. The application still owns the function's
implementation, permissions, validation, side effects, and error handling.

## Previous implementation and technical delta

Stage 04 already constructed an `Agent`, represented the request with a
structured `Message`, awaited `agent.run(...)`, and printed `response.text`.
It could already produce a normal model answer. Stage 05 keeps that client,
agent, message, authentication, and output boundary, then adds one callable
operation that the model can request.

| Previous stage/topic | Current stage | Practical reason for the change |
| --- | --- | --- |
| [Stage 04 message construction](../04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py#L76-L88) sends a `Message` directly to `agent.run(...)`. | [Stage 05 tool declaration](app/simple-ai-agent-maf-tool-decorator.py#L46-L67) uses `@tool` on `get_weather`. | Give the model a typed, described application action instead of limiting the run to generated text. |
| [Stage 03 `Agent(...)` construction](../03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py#L67-L80) already creates and runs an `Agent`. | [Stage 05 tool registration](app/simple-ai-agent-maf-tool-decorator.py#L93-L111) passes `tools=[get_weather]` and runs the same agent API. | Configure the agent with a callable it may select during the run; this is an enabled capability, not a new agent class. |

The installed SDK already exposed the `tools` parameter on `Agent` in the
previous stage. The implemented delta is that this sample creates a decorated
`FunctionTool` and supplies it to that parameter. In other words, the tool
feature was available at the agent boundary; this lesson makes its registration
and execution path concrete.

```text
Previous: client + Agent(...) -> Message -> agent.run(message) -> model text
Current:  client + @tool function + Agent(tools=[...]) -> Message -> run -> optional tool call -> model text
```

The arrows describe local object composition and the later invocation flow, not
separate network calls. Constructing `Agent` and decorating `get_weather` are
local operations. `agent.run(...)` initiates model communication. If the model
requests the tool, the framework invokes the local function and can send its
result into the remaining response flow; the exact number of model requests is
provider- and model-dependent.

### What remains the same

The Foundry project endpoint, deployment setting, Entra credential, async
resource cleanup, one-shot run, and `response.text` output shape remain in
place. The function itself is local and does not add a weather-service network
request. A tool-enabled run can require an additional model turn when the model
requests the function, so network usage and cost may differ from a plain
text-only run. Output wording and whether a compatible model selects the tool
are nondeterministic.

## Technical benefits of the new construct

The transcript's three motivations map to specific SDK mechanisms:

1. **Less schema boilerplate.** The installed `@tool` implementation wraps the
   callable as a `FunctionTool` and infers an input model and JSON schema from
   its signature. Here, `location: str` supplies the input type and `-> str`
   describes the result type. An explicit Pydantic or mapping schema is also
   supported when inference is not enough, but this sample does not configure
   one.
2. **Model discoverability.** `Agent(tools=[get_weather])` registers the
   generated tool with the model-facing agent configuration. The function's
   name and docstring describe the operation, so a compatible model can compare
   it with other registered tools and request it when the user's question
   needs that operation. Registration does not guarantee selection.
3. **Framework-managed invocation flow.** `agent.run(user_message)` starts the
   normal agent flow. If the model returns a tool request, the framework maps
   the requested arguments to the typed function, invokes it, and makes the
   result available for the response. The sample does not call
   `get_weather(...)` directly from `main`; the model-selected path is the
   lesson's point.

A practical production-shaped example would replace the randomized body with a
permission-checked order lookup or weather API call. That would require
explicit credentials, input validation, timeout/error handling, and a policy
for which identities may invoke the operation. None of those external
integrations are implemented here.

## Supported capabilities and activation requirements

This matrix separates the current sample from capabilities supported by the
installed SDK but not configured here.

| Capability / benefit | API and mechanism | Concrete use case | Previous API support | Current sample status |
| --- | --- | --- | --- | --- |
| Decorated local function | `@tool` creates a `FunctionTool` from a callable | Expose a safe application operation to the model | Agent already accepted tools, but no tool was registered | Implemented with `get_weather` |
| Inferred input schema | Function annotations such as `location: str`; the decorator builds the input model/schema | Validate and describe simple JSON arguments without a separate schema class | Available in the same installed SDK | Implemented |
| Tool description | Function docstring, or explicit `@tool(description=...)` | Tell the model what an operation does and when it is relevant | Available through the same agent boundary | Docstring implemented; explicit description not used |
| Agent registration | `Agent(tools=[get_weather])` | Let the model choose among multiple application functions | `Agent` accepted `tools` in stage 03, but that sample left it empty | Implemented with one tool |
| Explicit schema | `@tool(schema=WeatherInput)` with a Pydantic model or mapping | Add defaults, richer validation, or parameter descriptions | Available, not demonstrated previously in this course | Available but not configured |
| Approval and invocation limits | `approval_mode`, `max_invocations`, and related tool options | Require review before a side-effecting action or cap repeated calls | Available in the installed decorator API | Available but not configured |
| Streaming | `agent.run(..., stream=True)` | Display response updates in a chat UI | Available on `Agent` | Not implemented |
| Conversation session | `agent.create_session()` and reuse through `run(..., session=session)` | Preserve earlier turns for follow-up questions | Available on `Agent` | Not implemented |
| MCP tools | MCP client/server configuration | Use protocol-based tools outside this local function | Not part of this sample's registration path | Not implemented; stage 08 covers MCP |

Tool calling requires a provider/model combination that supports the framework's
tool-invocation contract. A session requires deliberate reuse and is not
persistent memory. Approval settings are not authorization by themselves; the
application still needs an authorization policy. MCP supplies protocol-based
tool access and does not automatically provide conversation memory.

## How it works

1. [`dotenv_values`](app/simple-ai-agent-maf-tool-decorator.py#L28-L30) reads an
   app-local `.env` file beside the script without exporting its values.
2. [`required_setting`](app/simple-ai-agent-maf-tool-decorator.py#L33-L43)
   resolves each setting from a nonempty process environment value first, then
   the dotenv dictionary, and raises `ValueError` if neither exists.
3. [`get_weather`](app/simple-ai-agent-maf-tool-decorator.py#L46-L67) is wrapped
   locally by `@tool`. Its signature and docstring become tool metadata; its
   body returns randomized demo data.
4. [`DefaultAzureCredential` and `FoundryChatClient`](app/simple-ai-agent-maf-tool-decorator.py#L78-L91)
   prepare authenticated model communication. Construction does not provision
   a hosted Foundry agent.
5. [`Agent`](app/simple-ai-agent-maf-tool-decorator.py#L92-L104) receives the
   client, behavior instructions, description, and the registered tool.
6. [`Message`](app/simple-ai-agent-maf-tool-decorator.py#L106-L107) carries the
   user's weather question. [`agent.run(...)`](app/simple-ai-agent-maf-tool-decorator.py#L109-L113)
   sends it through the configured agent; the model may request the registered
   function before producing final text.
7. The nested async context managers close credential and client resources, and
   the [script entry guard](app/simple-ai-agent-maf-tool-decorator.py#L116-L120)
   runs the coroutine only when the file is launched directly.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Single local agent and fixed prompt | Implemented | One `Agent` and one `Message` run |
| Local function tool | Implemented | `get_weather` is decorated and registered |
| Live external weather API | Not implemented | The function returns randomized local data |
| MCP tools | Not implemented | No MCP transport or server is configured |
| Short-term conversation memory | Not implemented | No session is created or reused |
| Persistent memory | Not implemented | No database, file store, or durable state exists |
| Streaming | Not implemented | The script awaits one completed response |
| Multi-agent orchestration | Not implemented | One local agent is configured |
| Retrieval or RAG | Not implemented | No retrieval source or index exists |
| Observability | Not implemented | No application telemetry setup is included |

## Folder contents

```text
05_simple-maf-tool-decorator/
├── README.md
├── requirements.txt
├── app/
│   └── simple-ai-agent-maf-tool-decorator.py
├── tests/
│   └── .gitkeep
└── .venv/                    # local generated environment, not source
```

- [app/simple-ai-agent-maf-tool-decorator.py](app/simple-ai-agent-maf-tool-decorator.py)
  contains configuration, the decorated tool, agent setup, and execution.
- [requirements.txt](requirements.txt) lists this stage's unpinned dependencies.
- `tests/.gitkeep` preserves an empty test placeholder; it is not an automated
  test suite.
- `app/.env`, `.venv/`, `__pycache__/`, and credentials are local/private or
  generated artifacts and are not shipped sample files.

## Frameworks and libraries

Observed on **2026-10-13** with this sample's Linux virtual-environment
interpreter, Python **3.12.3**. The manifest is unpinned, so a fresh install
may resolve different versions.

| Package / library | Purpose in this sample | Observed version / reference |
| --- | --- | --- |
| `agent-framework-foundry` | Provides `FoundryChatClient`; the installed dependency set also supplies the core `Agent`, `Message`, and `tool` imports | 1.14.1; [Foundry provider docs](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python) |
| `agent-framework-core` | Installed core framework package used by the imported agent and tool APIs | 1.21.0; [Agent Framework docs](https://learn.microsoft.com/en-us/agent-framework/) |
| `azure-identity` | Async `DefaultAzureCredential` for Entra token acquisition | 1.26.0; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) |
| `python-dotenv` | Parses the app-local dotenv file into a dictionary | 1.2.4; [python-dotenv docs](https://bbc2.github.io/python-dotenv/) |
| Python standard library | `asyncio`, `os`, `pathlib`, and `random` support the event loop, configuration, paths, and demo values | [Python docs](https://docs.python.org/3/) |

## Prerequisites and setup

- Python compatible with the installed framework packages; Python 3.12.3 was
  verified here.
- An existing Microsoft Foundry project with a deployed model that supports the
  Responses API and tool calling.
- An identity available to `DefaultAzureCredential` with permission to invoke
  the selected deployment. Authentication and authorization are separate.
- Network access for dependency installation and the live model request.

**Linux, zsh or bash; start in the repository root.** These commands are
instructional and use this stage's own environment:

```sh
cd ai-agents/microsoft-agent-framework/05_simple-maf-tool-decorator
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
| `FOUNDARY_MODEL` | Yes | The deployed model name passed as `model`; it is not an agent ID |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | The Foundry project endpoint passed as `project_endpoint`, not a guessed full API route |

A nonempty process environment value wins over the matching `.env` value. A
missing or empty result raises `ValueError` before the model request. Placeholder
configuration only:

```dotenv
FOUNDARY_MODEL=<your-model-deployment-name>
FOUNDARY_PROJECT_ENDPOINT=https://<your-foundry-project-endpoint>
```

Do not commit credentials, tokens, private endpoints, or identity configuration.
The dotenv dictionary is not exported into `os.environ`, and the script does
not print configuration values.

## Run and expected output

**Linux, zsh or bash; working directory: this stage folder after setup.** This
command makes a live, potentially billable model request and was not run during
this documentation update:

```sh
./.venv/bin/python app/simple-ai-agent-maf-tool-decorator.py
```

The script accepts no command-line input. A successful run prints generated
text, possibly describing the randomized temperature and condition returned by
`get_weather`; the exact wording and tool-selection behavior are nondeterministic.
The local function does not contact a weather service. Configuration,
credential, authorization, network, or provider failures produce a nonzero
process exit.

## Exercises to try

Each exercise makes a live, potentially billable model request. Undo your
edits afterwards.

1. **See when the tool runs.** Add `print(f"get_weather called for {location}")`
   as the first line inside `get_weather`. Ask `"What is the weather in Pune and Delhi?"`
   The print shows the framework calling your function, often once per city.
2. **The model decides.** Ask a question unrelated to weather, such as
   `"What is the capital of France?"` The print from exercise 1 does not
   appear: registering a tool does not force the model to use it.
3. **Descriptions matter.** Replace the docstring's first line with
   `"Does something."` and repeat the weather question. The model may stop
   choosing the tool, because the docstring is how it learns what the tool is for.
4. **Add a second tool.** Write a `@tool` function such as
   `get_time(city: str) -> str` that returns a fixed demo time, add it to
   `tools=[get_weather, get_time]`, and ask `"What is the time and weather in Pune?"`
   The model can pick and combine several tools in one run.
5. **Explicit description.** Use `@tool(description="Get the current weather for a city.")`
   instead of relying on the docstring, and confirm the tool is still selected.

## Validation and troubleshooting

The stage's test directory is an empty placeholder, so no automated behavior
suite is claimed. Safe offline checks for this update include the comment
placement checker, Python compilation, imports, installed API signatures, and
local decorated-tool metadata. They do not prove Foundry availability,
permissions, model tool-calling support, or a successful live response.

From the repository root, run the comment check with the stage interpreter:

```sh
./ai-agents/microsoft-agent-framework/05_simple-maf-tool-decorator/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/microsoft-agent-framework/05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py
```

| Symptom | First check |
| --- | --- |
| Missing setting | Use the exact `FOUNDARY_*` spelling and place `.env` beside the script |
| Import error | Select this stage's interpreter and install this stage's manifest |
| Authentication failure | Check the credential sources available to `DefaultAzureCredential` |
| Authorization failure | Check the identity's permission to the Foundry project/deployment |
| Tool is not selected | Confirm model/provider tool-calling support; selection is model-controlled |
| Unexpected weather | The function intentionally returns randomized demo data, not live weather |

## Learning links and progression

- [AI concepts: function tools and `@tool`](../../../docs/ai-concepts.md#function-tools-and-the-tool-decorator)
  explains schema inference, descriptions, registration, invocation, and limits.
- [AI concepts: client versus local agent](../../../docs/ai-concepts.md#foundry-client-versus-local-agent)
  separates model communication from local orchestration.
- [Python concepts](../../../docs/python-concepts.md) covers coroutines,
  `await`, context managers, imports, and configuration helpers.
- [Azure concepts](../../../docs/azure-concepts.md) covers project endpoints,
  deployments, credentials, and authorization.
- [Official tool documentation](https://learn.microsoft.com/en-us/agent-framework/agents/tools/)
  describes additional tool configuration options.

The separate-folder progression is conceptual: simple model response, explicit
agent construction, structured messages, local tools, short-term sessions,
persistent storage, and MCP. This stage implements only the local-tool step.
MCP is a protocol-based tool integration, not conversation memory. Later
stages must add sessions or storage explicitly if they need those capabilities.

This sample is a learning aid, not a production agent. It has no live weather
integration, authorization policy around the demo function, retries,
observability, persistence, interactive loop, or hosted-agent lifecycle.
