# Azure MCP tools with file memory — Microsoft Agent Framework

<!-- markdownlint-configure-file {"MD013": false} -->

## Overview and sample identity

Stage 08 adds **live Azure tools through Model Context Protocol (MCP)** to the
file-memory agent from stage 07. MCP is a protocol for discovering tool schemas
and requesting their execution. Here, a local Azure MCP Server subprocess serves
tools over standard input/output (**stdio**); Azure service requests still use
the network. MCP does not supply conversation memory.

| Dimension | This sample |
| --- | --- |
| Framework | Microsoft Agent Framework for Python; one locally orchestrated `Agent` |
| Model hosting / adapter | Microsoft Foundry project deployment / `FoundryChatClient`, using the Responses API |
| Model authentication | Python async `DefaultAzureCredential`; Entra permissions required separately |
| External tools | `MCPStdioTool`, launching Azure MCP Server through `npx` |
| Other tools / memory | Simulated `get_weather` and `FileMemoryProvider` with `FileSystemAgentFileStore` |
| Input / output | Four hard-coded messages in fresh sessions A–D; four response blocks and one memory-file listing |
| Learning objective | Connect, discover, register, invoke, and clean up protocol tools without replacing the agent or its file memory |

### Stage 07 → stage 08: what changes and why

Compare [stage07 source](../07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py#L104-L144)
and its [README](../07_simple-maf-long-term-memory/README.md) with
[stage08 MCP configuration](app/simple-ai-agent-maf-mcp.py#L130-L166).

| Stage 07 | Stage 08 | Mechanism and practical benefit |
| --- | --- | --- |
| `tools=[get_weather]` | `tools=[get_weather, azure_mcp]` | The MCP adapter discovers external tool definitions; the model can request real Azure operations instead of requiring a handwritten Python wrapper per service |
| No external tool process | `MCPStdioTool(command="npx", ...)` inside `async with` | Starts and connects a protocol server, then manages its connection/process lifetime |
| Three fresh sessions A/B/C | Adds fresh session D requesting subscriptions | Demonstrates live account inventory alongside preference recall; requires separate Azure MCP authentication and permissions |
| Foundry credential and local file access | Also needs Node/npm, npm access, and server-side Azure access | External tooling introduces installation, process, authentication, and authorization failure boundaries |

`Agent`, `Message`, `agent.create_session()`, `agent.run(..., session=...)`,
the Foundry client, weather tool, and file-memory design remain the same.
Stage07's `Agent` API already accepts tools: this stage **configures MCP**, not
an exclusive new agent API. Likewise, explicit `Agent(client=...)` is a
composition choice, not evidence that the earlier `as_agent(...)` factory
cannot configure tools. Each stage runs independently; stage08 does not import
or read stage07's memory folder.

## Capabilities

| Capability | Status | Boundary |
| --- | --- | --- |
| Single-agent prompts | Implemented | Four sequential awaited runs, no interactive input loop |
| Local function tool | Registered | Random weather, not a live weather service; no prompt explicitly asks for it |
| MCP tools | Configured | Dynamic server discovery and model-selected execution; live connection not validated by this documentation task |
| MCP prompt templates | Disabled | `load_prompts=False` disables prompt loading, **not tool discovery** |
| Short-term conversation state | Implemented per session | All four sessions are fresh; no shared A/B/C/D transcript or reused-session demonstration |
| Persistent memory | Implemented | Selected facts in plaintext local files under a fixed user scope |
| Full transcript persistence / automatic extraction | Not configured | No `FileHistoryProvider` or separate memory-extraction provider |
| Read-only enforcement / approval gate | Not configured | A listing request is not a permission boundary; exposed Azure operations can mutate resources |
| Streaming / multi-agent orchestration | Not implemented | Prints completed `response.text`; one agent, no workflow or handoffs |
| Retrieval/RAG | Not implemented | Regex file lookup is not an embeddings/vector retrieval pipeline |
| Application Insights / telemetry export | Not configured | Printed responses and server diagnostics are not instrumentation |

## Folder contents

```text
08_simple-maf-mcp/
├── README.md
├── requirements.txt
├── app/
│   ├── simple-ai-agent-maf-mcp.py
│   ├── .env                  # optional private local configuration, not shipped
│   └── memory_store/         # local persistent data, gitignored
├── tests/
│   └── .gitkeep              # placeholder only
└── .venv/                    # local generated Python environment
```

- [Entrypoint](app/simple-ai-agent-maf-mcp.py): settings, tools, memory, MCP lifecycle, and four sessions.
- [Dependency manifest](requirements.txt): this stage's packages and MCP/retry compatibility ranges.
- [Test placeholder](tests/.gitkeep): no behavioral test suite.
- [Repository ignore rules](../../../.gitignore) exclude local dotenv files,
  virtual environments, bytecode, and memory stores. Ignore rules are not data
  encryption. No workspace run task is supplied for this sample.

## Frameworks and libraries

Observed **2026-10-25** with this stage's Linux virtual-environment interpreter,
Python **3.12.3**. These are installed versions, not a lockfile or the learning
stage/model version. A future install can resolve different versions.

| Distribution / import | Responsibility | Installed version; declared Python requirement |
| --- | --- | --- |
| `agent-framework-foundry` / `agent_framework.foundry` | Foundry model adapter; [provider documentation](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python) | 1.15.0; >=3.10 |
| `agent-framework-core` / `agent_framework` | Agent, messages, function tools, file memory, MCP adapter; [MCPStdioTool reference](https://learn.microsoft.com/en-us/python/api/agent-framework-core/agent_framework.mcpstdiotool?view=agent-framework-python-latest) | 1.23.0; >=3.10; transitive |
| `mcp` / `mcp` | Python MCP protocol/session/stdio implementation; [official SDK](https://github.com/modelcontextprotocol/python-sdk) | 2.3.0; >=3.10 |
| `tenacity` / `tenacity` | Framework MCP subscription-recovery retry support; [library documentation](https://tenacity.readthedocs.io/) | 9.1.4; >=3.10; not imported directly by the app |
| `azure-identity` / `azure.identity.aio` | Python async credential; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) | 1.26.0; >=3.9 |
| `python-dotenv` / `dotenv` | Parse local settings without exporting them; [library documentation](https://bbc2.github.io/python-dotenv/) | 1.2.4; >=3.10 |
| `openai` / `openai` | Transitive Responses API transport used by the provider | 3.37.0; >=3.10 |
| Python standard library | `asyncio` coordinates coroutines; `os` reads settings; `pathlib.Path` locates files; `random.randint` simulates weather | Python 3.12.3; [standard-library documentation](https://docs.python.org/3/library/) |

The manifest explicitly requires `mcp>=2.2.0,<3` and
`tenacity>=9.1.4,<9.2.0`. Both match installed core 1.23.0's `all` extra metadata;
installing only the Foundry adapter does not imply every MCP optional dependency
is present. These existing dependency fixes avoid an incompatible MCP major or
missing retry library; they were not changed for this README. Other direct
manifest dependencies are unpinned. Stage07's documented core 1.21.0 behavior
is not a substitute for inspecting stage08's installed core 1.23.0.

The npm server is separate from Python packages: metadata-only lookup on
2026-10-25 resolved `@azure/mcp@latest` to **4.0.0-beta.3**, requiring
**Node >=22.0.0**. Local executables reported Node **v22.23.1** and npx
**10.9.8**. This does not prove the server was downloaded or launched.
`latest` is mutable; the source does not pin a server version.

## How it works

1. [Settings and scope](app/simple-ai-agent-maf-mcp.py#L34-L55) are evaluated
   locally. `required_setting` validates the two Foundry settings before client
   setup. Parsing the dotenv file does not sign in or invoke a model.
2. [Store and provider construction](app/simple-ai-agent-maf-mcp.py#L101-L113)
   configure shared disk memory. Constructors do not write memory content;
   the provider creates the scoped directory before a run.
3. [Credential and client](app/simple-ai-agent-maf-mcp.py#L115-L128) prepare
   authenticated model access. `FoundryChatClient` obtains its Responses client
   through the project client; it does not provision a hosted agent resource.
4. [MCP configuration and context entry](app/simple-ai-agent-maf-mcp.py#L130-L144)
   launch `npx -y @azure/mcp@latest server start`, initialize the stdio protocol
   connection, and discover server tool names, descriptions, and input schemas.
   `-y` accepts npm installation without prompting; it is not user approval for
   later Azure operations. No HTTP MCP endpoint/listening port is configured.
5. [Agent construction](app/simple-ai-agent-maf-mcp.py#L146-L166) registers the
   local weather tool and MCP adapter; `FileMemoryProvider.before_run` adds
   memory tools/instructions and any existing index. The exposed Azure tool set
   comes from the running server, **not a hard-coded list in Python**. No
   `allowed_tools` filter is supplied. Server versions/modes can expose different
   schemas or namespace tools, so a fixed subscription-tool signature is not
   promised here.
6. The model chooses tools and arguments during `agent.run`. The framework
   dispatches local calls or forwards MCP calls over stdio; the server performs
   authorized Azure requests and returns results. Tool results go back to the
   model before final text. Merely registering tools does not guarantee a call.
7. [Session A](app/simple-ai-agent-maf-mcp.py#L168-L191) shares Alex's name,
   vegetarian diet, and three-bullet preference; a memory-file listing follows.
   [Session B](app/simple-ai-agent-maf-mcp.py#L193-L211) requests a personalized
   greeting/dinner. [Session C](app/simple-ai-agent-maf-mcp.py#L213-L231) asks
   for past conversations and preferences, testing the limits of selective memory.
8. [Session D](app/simple-ai-agent-maf-mcp.py#L233-L251) asks
   “List all the subscriptions in my Azure account.” The model can use the MCP
   tools, subject to server authentication, permissions, and discovery behavior.
9. Async context exit closes the MCP session/subprocess, then the model HTTP
   client and project client; the outer scope closes the credential.
   [The entry guard](app/simple-ai-agent-maf-mcp.py#L257-L260) runs the coroutine
   through `asyncio.run`. There is no app-level exception recovery: a settings,
   npm/process, initialization, or discovery failure stops execution. Because
   MCP connects **before agent/session creation**, a connection failure prevents
   even sessions A–C, despite their memory-only prompts.

### Tools and safety boundaries

[`get_weather(location: str) -> str`](app/simple-ai-agent-maf-mcp.py#L77-L97)
accepts a location string (a city is a harmless example) and returns random
conditions and -10 to 35 °C. It makes no weather-service call and has no disk
side effects. Its decorator/docstring provide model-facing schema information.

Azure MCP tools are **live**, not weather-style mocks. Use only resources and
subscriptions you are authorized to inspect. The source sets neither server
read-only restrictions nor an application approval policy. Mutating tools can
be exposed throughout A–D, not only D, and a natural-language listing prompt
does not constrain their permissions. Review actual discovered schemas and
apply least privilege and explicit execution controls before production use;
those controls require changes outside this sample's current configuration.
Tool arguments, results, and retrieved memory can reach the remote model.

### Short-term and persistent memory

Each `agent.create_session()` creates independent in-process conversation state.
A/B/C/D do not share message histories; keeping all four objects alive does not
merge them. Restarting loses these histories but retains the disk store.

Installed core **1.23.0** supplies these provider tools:

| Tool / input | Effect |
| --- | --- |
| `file_memory_write(file_name, content, description=None)` | Overwrite content, update/remove description sidecar, rebuild index |
| `file_memory_read(file_name)` | Return stored text or not-found result |
| `file_memory_ls(glob_pattern=None)` | List content files and descriptions |
| `file_memory_grep(regex_pattern, glob_pattern=None)` | Case-insensitive regex search with snippets/line numbers; regex limit 256 characters |
| `file_memory_delete(file_name)` | Delete content and sidecar, rebuild index |
| `file_memory_replace(file_name, old_string, new_string, replace_all=False)` | Replace matching text; default requires one match |
| `file_memory_replace_lines(file_name, edits)` | Replace 1-based lines; edits specify `line_number`, `new_line`, optional `expected_line` |

The backend is a flat set of UTF-8 files inside this sample's app-local memory
store, scoped to `demo_user`: model-named content files, optional description
sidecars, and a generated memory index. Use flat names such as `preferences.md`,
not paths; internal index/description names are reserved. `before_run` creates
the scope directory and injects the existing index (up to 50 content entries).
It does not load every content file or extract facts after the response;
`after_run` is inherited without a custom extraction step. The model selects
read/search/write tools during its ordinary tool loop. Writes/deletes rebuild
the index; replacements or manual file edits do not refresh descriptions/index.

Session C cannot reliably reconstruct A/B transcripts that were never recorded.
It may recall saved preferences, including useful index descriptions; existing
memory or model-selected extra notes can change its answer. Memory recall and
the exact saved filenames are nondeterministic, not guaranteed assertions.
Index/history/retrieved text consumes input tokens; tool turns add latency and
potential model charges. MCP adds tools, not additional memory guarantees.

Files survive new sessions and process restarts when the same store/scope is
used. The fixed `demo_user` value is not authenticated identity isolation.
There is no automatic expiry, encryption, transcript archive, or cross-process
coordination; in-process locks do not solve concurrent-process writes. Memory
tools can overwrite/delete without user approval in this SDK. Do not store
secrets or sensitive personal information. To reset, stop concurrent runs and
manually remove only the disposable demo-user directory from this sample's
memory store; removing the whole store removes **all** its scopes. Nothing is
deleted automatically, and backups need their own retention policy.

## Prerequisites and setup

- Python **>=3.10** satisfies the inspected framework/MCP metadata (no declared
  upper bound); **3.12.3** is the observed interpreter, not certification of
  every later Python release or future dependency resolution.
- A Foundry project with a deployed Responses API/tool-calling-compatible
  model and an identity authorized to invoke it.
- Node/npm with `npx` on `PATH`; satisfy the resolved server's Node engine
  requirement, not just an older tutorial's generic “Node LTS” advice.
- Outbound access to Python/npm registries for installation and to identity,
  Foundry, and relevant Azure APIs at runtime; writable local memory storage.
- Azure MCP sign-in and least-privilege access to intended subscriptions/services
  as described under [Authentication](#authentication-two-independent-paths).

**First-time setup only; Linux bash/zsh, starting at the repository root:**

```sh
cd ai-agents/microsoft-agent-framework/08_simple-maf-mcp
/usr/bin/python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Use an existing intended Python >=3.10 executable if that Linux system does not
provide the example base executable. Do not recreate an existing environment
just to check documentation. Install from [this manifest](requirements.txt),
not the root FastAPI dependencies. Explicit environment executables avoid shell
aliases/wrappers; activation is unnecessary. In VS Code choose **Python: Select
Interpreter** and select this stage's virtual-environment Python. Windows needs
different paths/commands. See the [official venv guide](https://docs.python.org/3/library/venv.html).

## Configuration

Place the following placeholder-only settings in a private dotenv file beside
the entrypoint (its location is shown in the folder tree), or supply them through
the parent process environment. Keep the source's **`FOUNDARY_*` spelling**.

| Setting | Required | Meaning / precedence |
| --- | --- | --- |
| `FOUNDARY_MODEL` | Yes | Deployment name passed as `model`; nonempty environment value wins over file value |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | Foundry project endpoint passed as `project_endpoint`; same precedence |
| Identity settings / developer sign-in | Depends on chosen credential source | Not parsed by `required_setting`; Python and MCP have separate credential mechanisms |

```dotenv
FOUNDARY_MODEL=<your-model-deployment-name>
FOUNDARY_PROJECT_ENDPOINT=https://<your-foundry-resource>.services.ai.azure.com/api/projects/<your-project-name>
```

[`required_setting`](app/simple-ai-agent-maf-mcp.py#L46-L55) uses
`os.getenv(name) or settings.get(name)`: an empty environment value falls back
to the file, and missing/empty values in both raise `ValueError` before client
creation. File lookup is relative to the script, not the terminal directory.
`dotenv_values` returns a dictionary; it **does not export** values into
`os.environ`. No API key is read by this entrypoint. Store location and user
scope are source constants, not environment settings.

Use the endpoint supplied by the **Foundry project**, not an Azure OpenAI resource
endpoint or a manually extended full `/openai/v1` or `/responses` API URL.
The adapter obtains the appropriate client via `project_client.get_openai_client()`.
The deployment name need not equal the model-family name and is not an agent ID.
The example above is not a real endpoint or credential.

### Authentication: two independent paths

1. **Python → Foundry:** async `azure.identity.aio.DefaultAzureCredential`
   supplies tokens to `FoundryChatClient`. It tries supported credential sources
   when tokens are requested. Constructing it neither signs in nor grants access.
   Successful authentication still requires Foundry authorization for the deployment.
2. **Azure MCP subprocess → Azure:** the server uses **Azure Identity for .NET**,
   not the Python credential object. The [official Python integration guide](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/get-started/languages/python)
   documents broker mode (native OS broker with `InteractiveBrowserCredential`)
   and credential-chain mode (environment, VS Code, Visual Studio, Azure CLI,
   PowerShell, Azure Developer CLI, interactive browser). Availability and selection
   depend on platform/server configuration; this Linux sample does not select a
   broker mode or prove which account/credential succeeds.

No Python credential or token is forwarded to MCP. Installed MCP **2.3.0** uses
`get_default_environment()` when `env=None`; on this Linux host it forwards only
`HOME`, `LOGNAME`, `PATH`, `SHELL`, `TERM`, and `USER` (and filters shell-function
values). Thus this subprocess has inherited environment/user credential access,
**not a copy of every Python environment variable**. Developer credential tools
and caches may be reachable via that home/path context; custom `AZURE_*` variables
are not automatically forwarded by this configuration. Placing them only in the
app's dotenv dictionary exports them to neither credential chain. An environment-
based MCP deployment would require deliberate environment forwarding/configuration
outside this sample; do not assume exporting a variable alone fixes it here.

For local development, use a supported sign-in method from the official guide,
for example VS Code **Azure: Sign In** or an Azure CLI sign-in performed separately
by the user. These are optional authentication instructions, **not actions run
for this README**. The two processes may resolve different identities. Foundry
access does not grant Azure service RBAC, and Azure MCP subscription visibility
does not prove Foundry model access. No active account or selected credential was
verified during this documentation task.

## Run and expected output

**Linux bash/zsh; working directory: this stage folder:**

```sh
./.venv/bin/python app/simple-ai-agent-maf-mcp.py
```

Running starts npm/MCP before the first session, can download executable code,
makes at least four logical model runs plus any tool-related model turns, and
may incur charges and Azure side effects. Review the safety boundaries first.
There is no stdin prompt: the four messages are in source. On normal completion
the script prints responses and exits after cleanup; unhandled errors abort it.

Illustrative **shape only**, not output observed for this README:

```text
ExperimentalWarning: FileSystemAgentFileStore is experimental ...
---------- Session A Response ----------
<acknowledgment of facts; model may save them>
---------- End of Session A Response ----------
------- Memory files on disk -------
<zero or more relative paths, depending on existing files and tool writes>
-------- End of memory files ------------
---------- Session B Response ----------
<personalized greeting and vegetarian dinner if facts were saved/retrieved>
---------- End of Session B Response ----------
---------- Session C Response ----------
<saved preferences; no guaranteed reconstruction of previous conversations>
---------- End of Session C Response ----------
---------- Session D Response ----------
<authorized subscription results, no results, or an explanation of failure>
---------- End of Session D Response ----------
```

The file listing occurs once after A and includes every scope under this sample's
memory root, not just `demo_user`. Server diagnostics may appear separately on
stderr. Answers, tool choices, filenames, and result ordering can vary. Do not
interpret generated subscription text alone as proof that an MCP call succeeded.

## Validation and troubleshooting

This sample has only [an empty test placeholder](tests/.gitkeep), not a test suite.
No end-to-end, model, authentication, memory-write, or MCP connection check was
run for this documentation task. Safe offline checks inspect source syntax and import **SDK symbols**,
not the app module (which reads private configuration at import time).

**Linux bash/zsh; working directory: this stage folder; offline syntax/import checks:**

```sh
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -c 'import ast; from pathlib import Path; ast.parse(Path("app/simple-ai-agent-maf-mcp.py").read_text())'
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -c 'from agent_framework import Agent, Message, tool, MCPStdioTool, FileMemoryProvider, FileSystemAgentFileStore; from agent_framework.foundry import FoundryChatClient; from azure.identity.aio import DefaultAzureCredential; from dotenv import dotenv_values'
```

These checks do not construct clients, authenticate, start MCP, or prove runtime
behavior. The repository comment checker checks Python comment placement, not
Markdown accuracy or live behavior; no Python files were edited for this README.
Root template build/test commands are not sample validation.

| Symptom | Check / interpretation |
| --- | --- |
| `Missing required Foundry setting` | Preserve `FOUNDARY_*`; check nonempty environment/file values privately |
| Unresolved imports / missing `MCPStdioTool` | Select stage08's interpreter; compare installed metadata and its own manifest, not another stage's environment |
| Missing `mcp` / MCP API mismatch | Use the manifest's `mcp>=2.2.0,<3` range compatible with inspected core 1.23.0; do not substitute an old unconstrained MCP install |
| Missing `tenacity` / retry import error | The manifest explicitly includes `tenacity>=9.1.4,<9.2.0` matching core's optional dependency metadata |
| npm `E404` | Check spelling: `@azure/mcp@latest` has an `@` before the version tag; the earlier `@azure/mcplatest` typo names a different, nonexistent package |
| `npx` missing / engine mismatch | Check executable `PATH`, Node/npm installation, and the resolved package's Node requirement (>=22 for the observed server version) |
| Connection closes before session A | npm download/server initialization/discovery happens before any session; examine diagnostics, network/proxy restrictions, package compatibility |
| `ExperimentalWarning` | `FileSystemAgentFileStore` is experimental; the warning alone is nonfatal, unlike a following exception |
| MCP authorization failure but Foundry works | Separate .NET server identity/credential access and Azure RBAC from the Python credential and Foundry permissions |
| Foundry endpoint/deployment/tool error | Verify project endpoint, deployment name, Responses/tool support, network, and model authorization |
| Empty memory listing / B forgets / C lacks topics | Check tool errors and saved files/scope; model writes are discretionary, and no transcript provider is configured |
| Old facts after restart | Expected disk persistence; reset only authorized disposable data as described above |

Do not paste tokens, private configuration, personal memory, or account inventory
into troubleshooting logs. A fresh install or successful import is not evidence
that cloud permissions or protocol calls work.

## Learning links

Reuse the canonical topic guides; this README does not create a second glossary.

- **Python/runtime:** [required settings](../../../docs/python-concepts.md#helper-functions-and-required-settings),
  [await](../../../docs/python-concepts.md#await),
  [async context managers](../../../docs/python-concepts.md#async-context-managers).
- **Agent/framework:** [client versus agent](../../../docs/ai-concepts.md#foundry-client-versus-local-agent),
  [function tools](../../../docs/ai-concepts.md#function-tools-and-the-tool-decorator),
  [conversation sessions](../../../docs/ai-concepts.md#short-term-conversation-sessions),
  [stdio lifecycle](../../../docs/ai-concepts.md#stdio-server-lifecycle).
- **Azure/identity:** [server launch](../../../docs/azure-concepts.md#azure-mcp-server-launch),
  [project endpoints/deployments](../../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments),
  [async credentials and cleanup](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).
- **Official protocol reference:** [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#stdio).
  Online/latest references can describe newer APIs; installed SDK inspection
  grounds this document's version-specific behavior.

## Progression and limitations

These are separate-folder exercises, not prerequisites imported at runtime.
The repository's sequence introduces memory **before** MCP:

| Stage | Objective / technical delta |
| --- | --- |
| [01: simple response](../01_simple-maf-openai/README.md) | Azure OpenAI `OpenAIChatClient` with endpoint/key access; no configured memory/MCP |
| [02: Foundry](../02_simple-maf-foundary/README.md) | Project Responses adapter and Entra credential instead of Azure OpenAI endpoint/key configuration |
| [03: explicit agent](../03_simple-maf-agentclass/README.md) | `Agent(client=...)` composition, not exclusive capabilities over the factory |
| [04: messages](../04_simple-maf-messageclass/README.md) | Explicit role/content through `Message` |
| [05: local tools](../05_simple-maf-tool-decorator/README.md) | Model-selected Python function execution with simulated weather |
| [06: short-term memory](../06_simple-maf-short-term-memory/README.md) | Reuse one session for related turns; no configured disk persistence |
| [07: persistent memory](../07_simple-maf-long-term-memory/README.md) | Save selected facts to disk and recall across fresh sessions |
| 08: MCP (here) | Add external protocol tools and their process/auth/permission boundaries while retaining file memory |

Changing model provider changes endpoint/API/authentication requirements, not
automatically tool, memory, or orchestration support. Stage08 remains a local
single-agent demo: it does not deploy a hosted agent, enforce read-only Azure
access, authenticate memory users, provide production retention/encryption, or
include behavioral tests. Future hardening would require pinned dependencies,
restricted/approved tool execution, identity-aware scopes, safe data handling,
observability, and tests; none is claimed as implemented here.
