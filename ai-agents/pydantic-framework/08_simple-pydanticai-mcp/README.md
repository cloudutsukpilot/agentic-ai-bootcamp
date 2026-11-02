# Simple MCP Tools - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the eighth learning stage in the Pydantic AI course. It keeps stage 07's
file memory and weather tool, and adds the **Azure MCP server** as a third
toolset, so the agent can answer "List all the subscriptions in my Azure
account." It is the counterpart of the
[Microsoft Agent Framework stage 08](../../microsoft-agent-framework/08_simple-maf-mcp/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Use tools provided by a separate process through the Model Context Protocol |
| Framework | Pydantic AI (`pydantic-ai-slim[mcp]`) |
| Model provider | Microsoft Foundry project with a deployed model |
| MCP client | `MCPToolset(StdioTransport(command="npx", args=[...]), id="azure_mcp")` |
| MCP server | `@azure/mcp@latest`, started with `npx -y @azure/mcp@latest server start` |
| Transport | stdio (the server is a child process; messages go over stdin/stdout) |
| Other toolsets | File memory (stage 07) and `get_weather` (stage 05) |
| Sessions | A, B, C as in stage 07, plus D: list Azure subscriptions |
| Current status | Implemented |

**MCP (Model Context Protocol)** is a standard way for an application to offer
tools to an agent from another process or service. The agent does not know how
the Azure MCP server talks to Azure; it only sees a list of tools with schemas,
the same as local tools. MCP provides tools, not memory.

## How this maps to MAF's `MCPStdioTool`

| MAF stage 08 | This stage | Notes |
| --- | --- | --- |
| `MCPStdioTool(name="Azure MCP Server", command="npx", args=[...], load_prompts=False)` | [`MCPToolset(StdioTransport(command="npx", args=[...]), id="azure_mcp")`](app/simple-ai-agent-pydanticai-mcp.py#L112-L118) | `MCPToolset` is the recommended MCP client in Pydantic AI 2.x and is built on the FastMCP client. MCP prompts are never turned into tools here, so no `load_prompts` option is needed. |
| `async with ..., azure_mcp:` | [Same idea](app/simple-ai-agent-pydanticai-mcp.py#L120-L132): `azure_mcp` is the last item in the `async with` | Entering starts the server process and the MCP session; leaving stops it. |
| `tools=[get_weather, azure_mcp]` | [`toolsets=[memory_tools, weather_tools, azure_mcp]`](app/simple-ai-agent-pydanticai-mcp.py#L135-L154) | Every source of tools is a toolset. |

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 07](../07_simple-pydanticai-long-term-memory/app/simple-ai-agent-pydanticai-long-term-memory.py#L121-L138) has only in-process Python tools. | Adds [`azure_mcp`](app/simple-ai-agent-pydanticai-mcp.py#L112-L118) and [session D](app/simple-ai-agent-pydanticai-mcp.py#L201-L211). | Reach Azure through a maintained tool server instead of writing Azure SDK code yourself. |

## Security and permissions

- `npx -y @azure/mcp@latest` downloads and runs the latest published package
  without asking. Pin a version (for example `@azure/mcp@<version>`) if you need
  repeatable runs.
- The Azure MCP server authenticates **as you**, using its own credential chain
  (for local work, your `az login` session). It is separate from the
  `DefaultAzureCredential` this script uses for Foundry. Its tools can read, and
  in some cases change, anything your identity can access.
- The model chooses which MCP tools to call. Review the tools the server exposes
  before using it with a privileged account.

## How it works

1. Memory, weather tool, and Foundry configuration are the same as stage 07.
2. [`azure_mcp = MCPToolset(...)`](app/simple-ai-agent-pydanticai-mcp.py#L112-L118)
   describes how to launch the server. No process starts yet.
3. [The `async with` block](app/simple-ai-agent-pydanticai-mcp.py#L120-L132)
   opens the credential, project client, and OpenAI client, and finally enters
   `azure_mcp`, which runs `npx`, starts the server, and opens an MCP session.
4. [`Agent(...)`](app/simple-ai-agent-pydanticai-mcp.py#L135-L154) adds an
   instruction to use the Azure MCP tools and registers all three toolsets.
   Pydantic AI fetches the MCP server's tool list (cached after the first
   request by default) and offers those tools to the model next to the local ones.
5. Sessions [A](app/simple-ai-agent-pydanticai-mcp.py#L156-L172),
   [B](app/simple-ai-agent-pydanticai-mcp.py#L174-L184), and
   [C](app/simple-ai-agent-pydanticai-mcp.py#L186-L199) repeat stage 07.
6. [Session D](app/simple-ai-agent-pydanticai-mcp.py#L201-L211) asks for Azure
   subscriptions. The model may call a subscription-listing tool; Pydantic AI
   forwards the call to the server and returns its result to the model.
7. Leaving the `async with` block stops the MCP server and closes the clients.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| MCP tools over stdio | Implemented | `MCPToolset` + `StdioTransport` |
| Persistent file memory | Implemented | Same module as stage 07 |
| Local weather tool | Implemented | Same as stage 05 |
| Remote (HTTP) MCP servers | Supported, not configured | `MCPToolset("https://.../mcp")` |
| Tool approval | Supported, not configured | Pydantic AI deferred/approval tools |
| Streaming | Not implemented | Stage 10 |

## Folder contents

```text
08_simple-pydanticai-mcp/
├── README.md
├── app/
│   ├── file_memory.py                    # same memory module as stage 07
│   ├── simple-ai-agent-pydanticai-mcp.py # entry point
│   └── memory_store/                     # created at run time, git-ignored
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks and libraries

Observed on **2026-11-02**, shared environment, Python **3.12.3**. In addition to
[stage 02's packages](../02_simple-pydanticai-foundary/README.md#frameworks-and-libraries):

| Package / tool | Purpose in this sample | Observed version / reference |
| --- | --- | --- |
| `pydantic-ai-slim[mcp]` (import `pydantic_ai.mcp`) | `MCPToolset`, `StdioTransport` | 2.64.0; [Pydantic AI MCP client](https://pydantic.dev/docs/ai/mcp/client/) |
| `mcp`, `fastmcp-slim` | Protocol implementation and client used by `MCPToolset` | 2.3.0, 4.1.5 (installed by the `mcp` extra) |
| Node.js `npx` | Downloads and runs the Azure MCP server | Not pinned; [Azure MCP Server](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/) |

## Prerequisites and setup

- Everything from [stage 02](../02_simple-pydanticai-foundary/README.md#prerequisites-and-setup).
- Node.js with `npx` on your `PATH`, and network access to download `@azure/mcp`.
- `az login` so the Azure MCP server can authenticate, and a deployment that
  supports tool calling.

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Starts a Node.js process
and makes several live, potentially billable model requests; not run while
writing this README:

```sh
./.venv/bin/python 08_simple-pydanticai-mcp/app/simple-ai-agent-pydanticai-mcp.py
```

The first run can be slow while `npx` downloads the server. Output shows
sessions A–C as in stage 07, then session D with your subscription names or an
explanation of why they could not be listed.

## Exercises to try

1. Add a session that asks "Which Azure tools can you use?" to see how the model
   describes the tools the MCP server offered it.
2. Run `az logout` and rerun session D to see the MCP server's authentication error.
3. Remove `azure_mcp` from `toolsets` and rerun session D: the model has no way
   to list subscriptions.

## Validation and troubleshooting

`tests/` is an empty placeholder. Check both Python files with the comment
checker (see [stage 07](../07_simple-pydanticai-long-term-memory/README.md#validation-and-troubleshooting)).

| Symptom | First check |
| --- | --- |
| `FileNotFoundError: npx` | Install Node.js and make sure `npx` is on `PATH` |
| Timeout while starting the server | First download can be slow; check network/proxy access to the npm registry |
| Session D reports an authentication error | Run `az login`; the MCP server uses its own credential chain |
| Model does not call an MCP tool | Deployment supports tool calling; the request clearly needs Azure data |

## Learning links and progression

- [AI concepts: Pydantic AI MCP toolsets](../../../docs/ai-concepts.md#pydantic-ai-mcp-toolsets)
- [AI concepts: stdio server lifecycle](../../../docs/ai-concepts.md#stdio-server-lifecycle) (MAF view)
- [Azure concepts: Azure MCP server launch](../../../docs/azure-concepts.md#azure-mcp-server-launch)

Next, [stage 09](../09_simple-pydanticai-image-analysis/README.md) sends an
image to the model and saves what it learns to memory.
