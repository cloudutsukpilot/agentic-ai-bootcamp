# Pydantic AI — learning recap

<!-- markdownlint-configure-file {"MD013": false} -->

This folder replicates the [Microsoft Agent Framework course](../microsoft-agent-framework/README.md)
stage by stage, using [Pydantic AI](https://pydantic.dev/docs/ai/core-concepts/agent/)
instead of MAF. Every stage talks to the same Azure services with the same
`AZURE_OPENAI_*` / `FOUNDARY_*` settings, so you can compare the two frameworks
side by side.

The one structural difference: **all stages share one virtual environment and
one `.env` file** at this folder's root, instead of one per stage.

## Start here: the two-minute recap

1. **Provider connects, model selects, agent coordinates.** A provider owns the
   authenticated client, a model adapter names the deployment and API, and the
   local `Agent` adds instructions, tools, and output handling.
2. **Instructions are reusable behavior; the prompt is this run's request.**
3. **There is only one way to build an agent: `Agent(...)`.** Stage 03 names the
   provider and model separately to make the composition visible; it adds no capability.
4. **User input is a list of content items.** Text, `BinaryContent` images, and
   other `UserContent` items go into `agent.run([...])`; the role is implicit.
5. **Tools are functions in a toolset.** `@toolset.tool_plain` registers a function;
   `toolsets=[...]` attaches it. The model decides whether to call it.
6. **A conversation continues through results.** Pass `response.conversation`
   to the next `run(...)`; the conversation you pass in is not modified.
7. **Persistent memory needs storage you control.** Pydantic AI has no built-in
   file memory, so stages 07–09 include a small `file_memory.py` toolset that
   mirrors MAF's `FileMemoryProvider`.
8. **MCP servers are just another toolset.** `MCPToolset(StdioTransport(...))`
   starts a server process and offers its tools to the model.

## Learning map: what changed at each stage?

| Stage | Main API or change | MAF counterpart | Status |
| --- | --- | --- | --- |
| [01 — Azure OpenAI](./01_simple-pydanticai-openai/README.md) | `AzureProvider` → `OpenAIResponsesModel` → `Agent(...)` → `run(...)` | `OpenAIChatClient` → `as_agent` | Implemented |
| [02 — Foundry](./02_simple-pydanticai-foundary/README.md) | `AIProjectClient.get_openai_client()` → `OpenAIProvider` + async `DefaultAzureCredential` | `FoundryChatClient` | Implemented |
| [03 — Agent class](./03_simple-pydanticai-agentclass/README.md) | Named `provider` / `chat_model` → `Agent(model=...)` | `Agent(client=...)` | Implemented; same capabilities as 02 |
| [04 — Message structure](./04_simple-pydanticai-messageclass/README.md) | `user_message: list[UserContent]` | `Message(role="user", contents=[...])` | Implemented; one text item |
| [05 — Tool decorator](./05_simple-pydanticai-tool-decorator/README.md) | `FunctionToolset` + `@weather_tools.tool_plain` + `toolsets=[...]` | `@tool` + `tools=[...]` | Implemented; simulated weather |
| [06 — Short-term memory](./06_simple-pydanticai-short-term-memory/README.md) | `run(..., conversation=previous.conversation)` | `create_session()` + `session=` | Implemented; in-process only |
| [07 — Long-term memory](./07_simple-pydanticai-long-term-memory/README.md) | Local `file_memory.py` toolset with dynamic instructions | `FileMemoryProvider` | Implemented; local files |
| [08 — MCP](./08_simple-pydanticai-mcp/README.md) | `MCPToolset(StdioTransport("npx", [...@azure/mcp...]))` | `MCPStdioTool` | Implemented |
| [09 — Image analysis](./09_simple-pydanticai-image-analysis/README.md) | `BinaryContent(data=..., media_type="image/png")` + file memory | `Content.from_data(...)` | Implemented |
| [10 — Streaming](./10_simple-pydanticai-agent-streaming/README.md) | `run_stream(...)` + `stream_text(delta=True)` | `run(..., stream=True)` | Implemented |

The MAF folder also contains two `10_simple-maf-A2A copy …` folders with a
one-line placeholder; they are not replicated here. These are separate runnable
folders, not successive edits to one app.

## Shared environment setup

**Linux, zsh or bash; start in the repository root.** Run once for all stages:

```sh
cd ai-agents/pydantic-framework
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env    # then edit .env with your values
```

- [requirements.txt](./requirements.txt) lists the shared dependencies.
  Observed on 2026-11-02 with Python 3.12.3: `pydantic-ai-slim` 2.64.0,
  `azure-ai-projects` 2.10.0, `azure-identity` 1.27.0, `python-dotenv` 1.2.4.
- In VS Code, select `ai-agents/pydantic-framework/.venv/bin/python` once; it
  works for every stage.
- Each script finds the shared `.env` with `Path(__file__).resolve().parents[2]`,
  so it works from any working directory. A nonempty process environment value
  wins over the file.
- Stage 08 also needs Node.js (`npx`) for the Azure MCP server.

Run any stage from this folder, for example:

```sh
./.venv/bin/python 05_simple-pydanticai-tool-decorator/app/simple-ai-agent-pydanticai-tool-decorator.py
```

Pydantic AI prints an informational banner to standard error; set
`PYDANTIC_AI_NO_BANNER=1` in your shell to hide it.

### Configuration

| Setting | Used by | Meaning |
| --- | --- | --- |
| `AZURE_OPENAI_ENDPOINT` | 01 | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | 01 | Key for that resource |
| `AZURE_OPENAI_MODEL` | 01 | Deployment name |
| `FOUNDARY_PROJECT_ENDPOINT` | 02–10 | Foundry project URL (`.../api/projects/<project>`) |
| `FOUNDARY_MODEL` | 02–10 | Deployment name in that project |

Keep the `FOUNDARY_*` spelling: it matches the MAF stages, so the same values
work in both courses. Stages 02–10 also need an Entra identity (for example via
`az login`) with permission to use the project.

### Not part of this course

[`simple-pydantic-openai/`](./simple-pydantic-openai/) is an older, separate
FastAPI sample that uses the OpenAI SDK directly. It keeps its own setup and does
not use this shared environment.

## Do not confuse these capabilities

| Concept | What it provides here | What it does not automatically provide |
| --- | --- | --- |
| Provider | An authenticated client for a service | A choice of deployment or API |
| Model | Deployment name + API shape | Instructions, tools, or memory |
| Agent | Local coordination of model, instructions, toolsets | A hosted Foundry agent or Azure permissions |
| `list[UserContent]` | Structured user input, including images | Conversation memory |
| Toolset | Model-requested Python execution | Live data unless the function fetches it |
| `Conversation` | Context carried across related runs | Survival across restarts |
| `file_memory.py` | Durable facts saved through tools | Transcripts or vector search |
| `MCPToolset` | Tools from another process | Memory of any kind |
| `run_stream` | Earlier display of text | Different content or lower cost |

## Quick self-check

- Can I explain provider vs. model vs. agent, and why stage 03 adds no capability?
- Can I explain why the role is implicit in `agent.run([...])`?
- Can I trace a tool call from the model to Python and back?
- Why does turn 3 in stage 06 use `response2.conversation`, not `response1.conversation`?
- Why can stage 07's session B greet me by name, but session C cannot summarize past chats?
- What runs where in stage 08, and whose identity does the Azure MCP server use?

## Deeper reference shelf

- **Agent/framework:** [AI concepts — Pydantic AI course](../../docs/ai-concepts.md#pydantic-ai-course)
- **Azure:** [Foundry project OpenAI client](../../docs/azure-concepts.md#foundry-project-openai-client),
  [credentials and cleanup](../../docs/azure-concepts.md#async-credentials-and-resource-cleanup)
- **Python:** [Python concepts](../../docs/python-concepts.md), especially
  [`await`](../../docs/python-concepts.md#await) and
  [async context managers](../../docs/python-concepts.md#async-context-managers)
- **Official:** [Pydantic AI agents](https://pydantic.dev/docs/ai/core-concepts/agent/),
  [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/),
  [message history](https://pydantic.dev/docs/ai/core-concepts/message-history/),
  [MCP client](https://pydantic.dev/docs/ai/mcp/client/),
  [OpenAI models](https://pydantic.dev/docs/ai/models/openai/),
  [testing with `TestModel`](https://pydantic.dev/docs/ai/guides/testing/)

Pydantic AI changes quickly. Check the installed version before adopting an API
from newer documentation.
