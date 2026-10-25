# Simple Long-Term Memory - Microsoft Agent Framework

<!-- markdownlint-configure-file {"MD013": false} -->

This is the seventh learning stage in the Microsoft Agent Framework course. It
gives the agent memory that survives **across sessions and process restarts**.
The user shares personal facts in one session, and a completely separate
session later recalls them, even though the two sessions share no message
history.

Long-term memory here means plain files on disk that the model reads and
writes through framework-provided memory tools. It is not a database, a vector
index, or a stored transcript of every conversation.

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Recall user facts in a new session through file-based memory |
| Framework | Microsoft Agent Framework for Python |
| Model provider | Microsoft Foundry project with a deployed model |
| Provider client | `FoundryChatClient` from `agent_framework.foundry` |
| Authentication | Async `DefaultAzureCredential` and Entra authorization |
| Memory | `FileMemoryProvider` + `FileSystemAgentFileStore`, scoped with `scope="demo_user"` |
| Memory location | `app/memory_store/demo_user/` (directory created before a run; memory files written by tools; gitignored) |
| Local tool | `get_weather(location: str)`, kept from stage 05 |
| Conversation input | Three sessions (A, B, C), one `Message` each |
| Output | Three responses plus a list of memory files on disk |
| Current status | Implemented file-based long-term memory |

## Previous implementation and technical delta

[Stage 06](../06_simple-maf-short-term-memory/README.md) reused **one**
`AgentSession` for three turns. That context lived only in the running process
and disappeared when the session or script ended. Stage 07 creates a **new**
session for each message, so any recall must come from somewhere other than
the session.

| Previous stage | Current stage | Practical reason for the change |
| --- | --- | --- |
| One session reused for every turn | [Three separate sessions](app/simple-ai-agent-maf-long-term-memory.py#L146-L203) | Prove that recall does not depend on shared conversation history |
| No storage | [`FileSystemAgentFileStore` and `FileMemoryProvider`](app/simple-ai-agent-maf-long-term-memory.py#L104-L109) | Keep facts on disk after the process exits |
| `Agent(tools=[get_weather])` | [`Agent(context_providers=[memory_provider], tools=[get_weather])`](app/simple-ai-agent-maf-long-term-memory.py#L126-L144) | Plug the memory provider into every agent run |
| Generic instructions | Instructions that ask the model to save durable facts and check memory first | The model decides when to use memory tools, so it needs explicit guidance |

The shared pieces remain the Foundry Responses API client, Entra credential,
local `Agent`, structured `Message` inputs, and simulated weather tool. See
[stage 06's shared-session calls](../06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py#L111-L141).
Stage 06's `Agent` can also accept `context_providers`; stage 07 **configures**
persistence rather than unlocking a capability unavailable to the earlier API.
For example, a returning dinner assistant can reuse a diet preference without
replaying the previous conversation. The same user scope and disk directory
must be retained; three fresh sessions alone do not provide that benefit.

```text
Stage 06: one session -> turn 1 -> turn 2 -> turn 3          (context in RAM only)
Stage 07: session A -> write memory files -> session B/C -> read memory files
                                 \-> app/memory_store/demo_user/*.md (on disk)
```

## Technical benefits of the new construct

1. **Context provider plug-in.** A *context provider* participates in an agent's
   run lifecycle. Here, `FileMemoryProvider.before_run` adds memory
   instructions, the current memory index (`memories.md`, if present) and these tools:
   `file_memory_write`, `file_memory_read`, `file_memory_ls`,
   `file_memory_grep`, `file_memory_delete`, `file_memory_replace` and
   `file_memory_replace_lines`.
2. **Scope decides who shares memory.** With `scope=USER_ID`, every session
   for that user reads and writes the same folder. Without `scope`, the
   provider uses the session id, so each session would get its own empty
   folder and session B would recall nothing.
3. **Inspectable storage.** Memories are readable Markdown files, so you can
   open them, edit them, or delete them to reset the agent.

**Automatic context is not automatic extraction.** In installed core 1.21.0,
`before_run` creates the scoped directory and injects the existing index;
`FileMemoryProvider` has no custom after-run extraction step. The model selects
`file_memory_read`/`file_memory_grep` to retrieve facts and `file_memory_write`
to save them during the ordinary tool-calling loop. The framework executes a
requested tool, sends its result back to the model, and continues the response.
An index description can itself contain useful facts, but full memory files
are not all loaded automatically. There is no separate background summarizer.

The disk schema is a flat set of UTF-8 text files per scope: model-named content
files, optional description sidecars, and the generated index. The installed
index lists at most 50 content files; it is not an unlimited context window.
Index text and retrieved content consume model input tokens, and tool turns
can add latency and billable requests. Regex search over local files is not
semantic/vector retrieval or a configured retrieval-augmented generation (RAG)
pipeline.

Limits: the model chooses whether to call the memory tools, so recall is not
guaranteed. The files are plaintext and unencrypted, and the store does not lock
files across processes. `FileSystemAgentFileStore` is marked experimental in
`agent-framework-core` 1.21.0 and prints an `ExperimentalWarning`.

**Isolation and retention are application responsibilities.** The fixed
`demo_user` scope shares memory with every run using this store and scope;
it does not authenticate a person. Derive and authorize scopes from a trusted
signed-in identity in a real app. Storage path checks do not replace access
control, OS permissions, or protection against other host processes. Memory
tools run with this Python process's filesystem permissions and, in this SDK,
do not require user approval before writing, replacing, or deleting content.
Do not supply secrets or sensitive personal data: index descriptions and tool
results may be sent to the remote model. Gitignore is not encryption or a
retention policy. There is no automatic expiry; delete unwanted data explicitly
and consider backups separately. SDK in-process mutation locks do not provide
cross-process coordination.

## Supported capabilities and activation requirements

| Capability | API and mechanism | Current sample status |
| --- | --- | --- |
| File-based long-term memory | `FileMemoryProvider(store=..., scope=...)` | Implemented |
| Per-user memory scope | `scope="demo_user"` (fixed demo value) | Implemented; a real app would use the signed-in user's ID |
| Local function tool | `@tool get_weather` | Registered; not used by the demo prompts |
| Automatic memory extraction | `MemoryContextProvider` uses extra LLM calls to pull facts out of transcripts | Available, experimental, not configured |
| Persisted transcripts | `FileHistoryProvider` stores one append-only history file per session | Available, experimental, not configured |
| Database or vector memory | Custom store or vector-store providers | Not implemented |
| MCP tools | MCP client/server configuration | Not implemented; stage 08 covers MCP |
| Single-agent prompts | Three `Message` inputs and awaited `agent.run` calls | Implemented; hard-coded, not an interactive chat loop |
| Short-term history | A fresh `AgentSession` for each run | Sessions implemented; shared multi-turn history is not demonstrated here |
| Streaming | Completed `response.text`, not `run_stream` | Not implemented |
| Multi-agent orchestration | One local `Agent`; no workflow/handoffs | Not implemented |
| Retrieval/RAG | No embeddings, vector index, or document retrieval pipeline | Not implemented; file lookup is the memory mechanism |
| Telemetry export | No tracing/exporter configuration | Not implemented; terminal output is not Application Insights integration |

The optional providers above are different SDK mechanisms, not enabled modes
of this `FileMemoryProvider`. Changing provider or storage backend requires
application configuration/code changes; it is not a switch in this sample.

The registered local tool is
[`get_weather(location: str) -> str`](app/simple-ai-agent-maf-long-term-memory.py#L72-L93).
Its signature/docstring describe the model-facing input; it returns random
conditions and a temperature from -10 to 35 °C, not live weather. A harmless
test input would be a city name, but the supplied prompts do not request weather
and registration does not guarantee invocation. It needs no weather API key,
makes no weather-service call, and has no disk side effects.

Memory tool inputs and effects in installed core 1.21.0:

| Tool / input shape | Result and side effect |
| --- | --- |
| `file_memory_write(file_name, content, description=None)` | Writes/overwrites full text, updates optional description, rebuilds index |
| `file_memory_read(file_name)` | Returns file text or not-found text; no write |
| `file_memory_ls(glob_pattern=None)` | Lists content file names and descriptions; no write |
| `file_memory_grep(regex_pattern, glob_pattern=None)` | Case-insensitive search with snippets/line numbers; regex length at most 256 characters; no write |
| `file_memory_delete(file_name)` | Deletes content and description, rebuilds index |
| `file_memory_replace(file_name, old_string, new_string, replace_all=False)` | Edits matching text; default requires exactly one occurrence |
| `file_memory_replace_lines(file_name, edits)` | Edits 1-based lines; each edit has `line_number`, `new_line`, optional `expected_line` |

Use flat names such as `preferences.md`, not absolute paths or nested paths.
Writes reserve the index/description filenames for framework bookkeeping.
Read before editing; overwrite and delete are real, potentially destructive
local actions. Never treat model-generated file content as trusted policy.

## How it works

Before these steps, [`dotenv_values` and `required_setting`](app/simple-ai-agent-maf-long-term-memory.py#L30-L51)
parse configuration locally and validate required values. Neither operation
authenticates or invokes a model. The client communicates with the deployment;
the local agent coordinates instructions, tools, and the memory provider—it
does not create a hosted Foundry agent resource.

1. [`MEMORY_DIR` and `USER_ID`](app/simple-ai-agent-maf-long-term-memory.py#L34-L39)
   set where memories live and which user they belong to.
2. [`print_memory_files`](app/simple-ai-agent-maf-long-term-memory.py#L54-L68)
   lists every file under `MEMORY_DIR` so you can see what the agent saved.
3. [`FileSystemAgentFileStore` and `FileMemoryProvider`](app/simple-ai-agent-maf-long-term-memory.py#L104-L109)
   are constructed locally without disk writes. Before a run, the provider
   creates the scope directory; memory content is written by mutating tools.
4. [`DefaultAzureCredential` and `FoundryChatClient`](app/simple-ai-agent-maf-long-term-memory.py#L111-L124)
   prepare authenticated model communication, as in earlier stages.
5. [`Agent(...)`](app/simple-ai-agent-maf-long-term-memory.py#L126-L144)
   registers the memory provider and the weather tool.
6. [Session A](app/simple-ai-agent-maf-long-term-memory.py#L146-L166) shares
   facts. The instructions request `file_memory_write`, then the script prints
   the memory files.
7. [Session B](app/simple-ai-agent-maf-long-term-memory.py#L171-L189) is a new
   session. The model reads memory to greet Alex and suggest a vegetarian dinner.
8. [Session C](app/simple-ai-agent-maf-long-term-memory.py#L191-L209) asks for a
   summary of past conversations. It shows what memory does **not** store (see
   [Why session C cannot summarize past conversations](#why-session-c-cannot-summarize-past-conversations)).

The three runs are awaited sequentially; B starts after A finishes. Session
objects still hold their own run histories, but are never reused across A/B/C.
The file listing is printed once after A and lists **all scopes** under
`MEMORY_DIR`, not just this user. The three response blocks print only
`response_a.text`, `response_b.text`, and `response_c.text`. On successful
completion, nested async context managers close the HTTP/project clients and
credential, then `asyncio.run(main())` exits. There is no stdin prompt loop or
session reload on restart.

## Why session C cannot summarize past conversations

A typical run prints something like:

```text
- I don't have a record of earlier conversation topics in the available memory.
- Your name is Alex, and you're vegetarian.
- You prefer answers in 3 short bullet points.
```

That answer is appropriate when only preferences were saved, not a bug:

- **Sessions do not share history.** Session C is new, so it cannot see the
  messages from sessions A or B.
- **Memory holds only what the model chose to save.** Following its
   instructions, the model may save *durable facts* (name, diet, answer style) to
   a file such as `userpreferences.md`. It is not instructed to save "Alex asked
   about dinner" or the chickpea curry suggestion as a conversation log.
- **Nothing stores transcripts.** This sample has no history provider such as
  `FileHistoryProvider`. Even that provider stores history per session, so a
  new session would not load it automatically.

The model therefore reports the preferences it found and honestly says it has
no record of past conversation topics. Exercise 5 below shows one way to change that.

This describes the intended illustration, not a guaranteed observed response.
Existing files from earlier runs, model-selected extra notes, or hallucination
can change the answer. A new session proves there is no shared A/B message
history; it does not prove that a claimed recollection is accurate. Session C
cannot reliably reconstruct conversations that were never recorded.

## Folder contents

```text
07_simple-maf-long-term-memory/
├── README.md
├── requirements.txt
├── app/
│   ├── simple-ai-agent-maf-long-term-memory.py
│   ├── .env                  # local private configuration, not shipped
│   └── memory_store/         # generated by runs, gitignored
├── tests/
│   └── .gitkeep
└── .venv/                    # local generated environment, not source
```

- [app/simple-ai-agent-maf-long-term-memory.py](app/simple-ai-agent-maf-long-term-memory.py)
  contains configuration, the memory provider, agent setup, and the three sessions.
- [requirements.txt](requirements.txt) lists this stage's unpinned dependencies.
  No new package is needed for memory; it ships in `agent-framework-core`.
- `tests/.gitkeep` preserves an empty test placeholder; it is not a test suite.

## Frameworks and libraries

Observed on **2026-10-13**, with the same versions rechecked on **2026-10-25**
using this stage's Linux virtual-environment
interpreter, Python **3.12.3**. The manifest is unpinned, so a fresh install
may resolve different versions.

| Package / library | Purpose in this sample | Observed version / reference |
| --- | --- | --- |
| `agent-framework-foundry` | Provides `FoundryChatClient` and installs the core framework | 1.14.1; [Foundry provider docs](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python) |
| `agent-framework-core` | `Agent`, `Message`, `tool`, `FileMemoryProvider`, `FileSystemAgentFileStore` | 1.21.0; [Agent Framework docs](https://learn.microsoft.com/en-us/agent-framework/) |
| `azure-identity` | Async `DefaultAzureCredential` for Entra token acquisition | 1.26.0; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) |
| `python-dotenv` | Parses the app-local dotenv file into a dictionary | 1.2.4; [python-dotenv docs](https://bbc2.github.io/python-dotenv/) |
| Python standard library | `asyncio`, `os`, `pathlib`, and `random` | [Python docs](https://docs.python.org/3/) |

Package names differ from imports: `agent-framework-foundry` supplies
`agent_framework.foundry` (backed by `agent_framework_foundry`), core supplies
`agent_framework`, `azure-identity` supplies `azure.identity.aio`, and
`python-dotenv` supplies `dotenv`. Core is a transitive dependency, not a
separate line in this stage's manifest. Observed OpenAI SDK **3.29.0** is also
transitive; the Foundry adapter uses it for Responses API communication. Package
versions are not the learning-stage number or the model/deployment version.
Installed implementation was used for the memory semantics above; current
online documentation may describe newer APIs.

## Prerequisites and setup

- Installed framework package metadata requires Python **>=3.10** (no upper
   bound declared); **3.12.3** was verified here. This is not certification of
   every newer Python release or future unpinned dependency resolution.
- A Microsoft Foundry project with a deployed model that supports the
  Responses API and tool calling (the memory tools are function tools).
- An identity available to `DefaultAzureCredential` with permission to invoke
  the deployment.
- Outbound HTTPS/DNS access to identity and Foundry services, package-index
   access for installation, and a writable local memory directory. Constructing
   a credential does not sign you in or grant RBAC permissions.

**Linux, zsh or bash; start in the repository root:**

```sh
cd ai-agents/microsoft-agent-framework/07_simple-maf-long-term-memory
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

These are first-time setup instructions, not validation commands to rerun over
an existing environment. Resolve `python3` to the intended executable (for
example `/usr/bin/python3.12` on this Linux host) before creating the virtual
environment; use its explicit executable if a shell function/alias intervenes.
Subsequent commands use the environment's interpreter directly, so activation
is unnecessary. In VS Code, run **Python: Select Interpreter** and select this
stage's virtual-environment Python, not the repository root environment.
See the [official virtual-environment guide](https://docs.python.org/3/library/venv.html).
Windows uses different executable paths/shell commands; the blocks here target
Linux only. Do not substitute the root dependency manifest for this stage's.

## Configuration

Create `app/.env` beside the script, or set the values in the process
environment. A nonempty environment value wins over the `.env` value.

[`required_setting`](app/simple-ai-agent-maf-long-term-memory.py#L43-L51)
implements that precedence using `os.getenv(name) or settings.get(name)`.
Empty environment values fall back to the file; a missing/empty value in both
places raises `ValueError` before client creation. `dotenv_values` returns a
dictionary and does not export file settings to `os.environ`. The file path
is relative to the script, not the shell's working directory. Keep the existing
`FOUNDARY_*` spelling: these are this sample's names, not the SDK's differently
spelled defaults. No API key setting is read by this entry point.

| Setting | Required? | Meaning |
| --- | --- | --- |
| `FOUNDARY_MODEL` | Yes | The deployed model name passed as `model` |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | The Foundry project endpoint passed as `project_endpoint` |

```dotenv
FOUNDARY_MODEL=<your-model-deployment-name>
FOUNDARY_PROJECT_ENDPOINT=https://<your-foundry-project-endpoint>
```

The memory folder and user scope are code constants (`MEMORY_DIR`, `USER_ID`),
not settings.

Use the **project endpoint** shown by your Foundry project, not an Azure OpenAI
resource endpoint and not a manually extended `/openai/v1` or `/responses` URL.
The installed adapter obtains its OpenAI client through
`project_client.get_openai_client()`. `FOUNDARY_MODEL` is the deployment name
accepted by that project, not necessarily a model-family label and not an agent
ID. The values above are placeholders, not working credentials or a real URL.
Keep local configuration private and out of commits; the async credential
obtains tokens independently of these two settings.

## Run and expected output

**Linux, zsh or bash; working directory: this stage folder.** This makes
several live, potentially billable model requests (three runs, plus extra
model turns when memory tools are called):

```sh
./.venv/bin/python app/simple-ai-agent-maf-long-term-memory.py
```

Illustrative output shape; wording and file names vary because the model
chooses them:

```text
ExperimentalWarning: FileSystemAgentFileStore is experimental ...
---------- Session A Response ----------
- Got it, Alex. ...
------- Memory files on disk -------
demo_user/memories.md
demo_user/userpreferences.md
demo_user/userpreferences_description.md
-------- End of memory files ------------
---------- Session B Response ----------
- Hi, Alex! ... (vegetarian dinner suggestion)
---------- Session C Response ----------
- I don't have a record of earlier conversation topics ...
```

- `memories.md` is an index rebuilt by `file_memory_write` and `file_memory_delete`; direct file edits do not rebuild it.
- `*_description.md` holds the short description the model gave a file.
- Reset all memory with `rm -rf app/memory_store`.

**Reset warning:** run that deletion only from this stage folder and only for
disposable demo data. It recursively removes **every user scope** in this
sample's store, not just `demo_user`, without confirmation. Stop concurrent
runs first. Deleting only the demo user's directory resets that scope; a fresh
session or process alone does not. The script never runs a reset automatically.

## Exercises to try

Each exercise needs a live run, so each one costs a few model calls. Start
each from a clean memory folder unless the exercise says otherwise.

1. **Restart persistence.** Run the script once. Then change `message_a` to
   something unrelated (for example `"What is 2 + 2?"`) and run again *without*
   deleting `app/memory_store`. Session B should still greet Alex, which shows
   the memory came from the files on disk, not from this process.
2. **Per-user isolation.** After a normal run, change `USER_ID = "other_user"`,
   change `message_a` to something unrelated, and run again. Session B should
   no longer know the name, because `other_user` has its own empty folder.
3. **Session-scoped memory.** Delete `app/memory_store`, remove `scope=USER_ID`
   from `FileMemoryProvider(...)` and run. Each session now writes into a folder
   named after its own session id (list them with `ls app/memory_store`), so
   session B cannot see session A's facts.
4. **Inspect and edit memory.** Run `cat app/memory_store/demo_user/*.md`. Edit
   `userpreferences.md` (for example change "vegetarian" to "vegan"), comment
   out session A, and run again. Session B now follows the edited fact. Memory
   is plain text, so never store secrets in it.
5. **Make session C summarize past conversations.** Session C fails today
   because nothing records conversation topics (see the section above). Append
   this sentence to the agent `instructions`: `"At the end of every answer,
   append a one-line summary of the user's request to a memory file named
   conversation_log.md."` Delete `app/memory_store` and run again. Session C
   can now read `conversation_log.md` and summarize earlier topics. Discuss the
   trade-off: more stored data means more privacy and retention decisions.
6. **Weak instructions.** Remove the instruction sentences about saving and
   checking memory, delete `app/memory_store`, and run. Compare how often the
   model still calls the memory tools. This shows that recall depends on the
   model's choices, not on the provider alone.

Treat these as optional source-edit experiments, not implemented guarantees.
For exercise 4, use the content filename the model actually created, and remove
the whole session A block if testing without it. Direct edits can leave the
description/index stale, so update related metadata consistently or use memory
tools to rewrite the file. Exercise 5's instruction does not implement a
reliable append operation: `file_memory_write` overwrites, so the model must
read/retain earlier entries and write during tool execution **before** its
final response. Verify that A/B topics were actually recorded; a selective
summary log is still not a full transcript. None of these exercises was run
for this documentation update.

## Validation and troubleshooting

The test folder is an empty placeholder. Safe offline checks are the comment
placement checker, Python compilation, and imports; they do not prove model
behavior. Import checks should target SDK symbols only, not the app module,
which reads its private configuration at import time. No workspace run task
is provided for this stage. **Linux, zsh or bash; repository root:**

```sh
./ai-agents/microsoft-agent-framework/07_simple-maf-long-term-memory/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/microsoft-agent-framework/07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py
```

The checker tests comment placement/syntax, not comment meaning, SDK behavior,
or persistence. For an offline syntax check without writing bytecode, use the
same interpreter's `ast.parse` on the entry-point source; importing SDK classes
alone does not authenticate or test a deployment. Empty tests are not coverage;
the root template's `make test`/`make build` do not validate this exercise.

| Symptom | First check |
| --- | --- |
| `ExperimentalWarning` printed | Expected; `FileSystemAgentFileStore` is experimental |
| Memory file list is empty after session A | The model did not call `file_memory_write`; make the instructions more explicit |
| Session B does not recall facts | Check that `scope` is set and that the files exist under `app/memory_store/demo_user/` |
| Session C cannot summarize past topics | Expected; see [Why session C cannot summarize past conversations](#why-session-c-cannot-summarize-past-conversations) |
| Old facts keep appearing | Memory persists by design; delete `app/memory_store` to reset |
| Missing setting / auth failure | Same checks as earlier stages: `FOUNDARY_*` names, credential, and RBAC |
| Unresolved imports / missing memory classes | Select this stage's interpreter; compare installed metadata with the unpinned manifest rather than assuming every version exposes these APIs |
| Permission denied / missing memory after restart | Check filesystem write permissions and reuse the same store/scope; an empty directory is not evidence of saved facts |
| Endpoint/deployment error or unsupported tool calls | Verify project endpoint, deployment name, Responses API/tool support, and network access |
| Authentication/authorization error | Verify the intended credential source and project permissions privately; credential construction does not grant access |

If writing failed or existing memory was deleted, an empty list does not prove
the model simply skipped the write; inspect the tool result/errors as well.
Do not paste credentials, environment contents, or personal memory into logs.

## Learning links and progression

- [AI concepts: short-term conversation sessions](../../../docs/ai-concepts.md#short-term-conversation-sessions)
  explains the stage 06 session model that this stage builds on.
- [AI concepts: function tools](../../../docs/ai-concepts.md#function-tools-and-the-tool-decorator)
  explains the tool mechanism that the memory provider's `file_memory_*` tools use.
- [Python concepts](../../../docs/python-concepts.md) and
  [Azure concepts](../../../docs/azure-concepts.md) cover async code,
  configuration, credentials, and authorization.
- [Official Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/)
  covers context providers and memory options.

Focused learning links reuse the existing canonical guides rather than adding
a second glossary here:

- **Python/runtime:** [configuration helper](../../../docs/python-concepts.md#helper-functions-and-required-settings),
   [await](../../../docs/python-concepts.md#await), and
   [async context managers](../../../docs/python-concepts.md#async-context-managers).
- **Agent/framework:** [client versus agent](../../../docs/ai-concepts.md#foundry-client-versus-local-agent),
   [instructions versus prompts](../../../docs/ai-concepts.md#instructions-versus-user-prompts),
   and [structured messages](../../../docs/ai-concepts.md#messages-as-structured-conversation-items).
- **Azure service/identity:** [project endpoints/deployments](../../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments)
   and [credentials and cleanup](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).

Progression: simple model response, explicit agent, structured messages,
local tools, [short-term sessions](../06_simple-maf-short-term-memory/README.md),
**persistent memory (this stage)**, then MCP. MCP supplies protocol-based tools
and does not itself provide memory.

These are separate exercises, not imports or mandatory runtime dependencies:

| Exercise | Objective / delta |
| --- | --- |
| [01: simple response](../01_simple-maf-openai/README.md) | Azure OpenAI `OpenAIChatClient`, API-key access, and a single prompt; no configured persistent memory |
| [02: Foundry provider](../02_simple-maf-foundary/README.md) | Foundry project Responses API and Entra credential instead of the Azure OpenAI endpoint/key configuration; still a simple response |
| [03: explicit agent](../03_simple-maf-agentclass/README.md) | Compose `Agent(client=...)` explicitly; not an exclusive capability gain over `as_agent(...)` |
| [04: messages](../04_simple-maf-messageclass/README.md) | Make role/content explicit with `Message` |
| [05: local tools](../05_simple-maf-tool-decorator/README.md) | Register model-selected Python execution; simulated weather, not live data |
| [06: short-term sessions](../06_simple-maf-short-term-memory/README.md) | Reuse one session for related turns; no configured disk persistence |
| 07: persistent memory (here) | Share selected disk-backed facts across fresh sessions; no transcript reconstruction |
| [08: MCP source](../08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py#L127-L165) | Adds `MCPStdioTool` for external protocol-based tools alongside memory; separate process, installation/authentication/permission concerns, not required to run stage 07 |

The provider variants change endpoint, API, and authentication requirements;
neither a provider change nor an OpenAI-compatible URL automatically enables
tools, sessions, or persistence. Stage 07 adds no MCP process or external MCP
permissions. Future production work would require authenticated user mapping,
retention/deletion rules, controlled tool execution, and actual behavioral tests.

This is a learning sample, not a production memory system. It has no real
user identity, encryption, retention policy, cross-process concurrency control, or tests.
