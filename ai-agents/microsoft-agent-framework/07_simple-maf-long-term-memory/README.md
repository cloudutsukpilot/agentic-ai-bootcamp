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
| Memory location | `app/memory_store/demo_user/` (created on first write, gitignored) |
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

```text
Stage 06: one session -> turn 1 -> turn 2 -> turn 3          (context in RAM only)
Stage 07: session A -> write memory files -> session B/C -> read memory files
                                 \-> app/memory_store/demo_user/*.md (on disk)
```

## Technical benefits of the new construct

1. **Context provider plug-in.** A *context provider* runs before and after
   every `agent.run(...)`. Before each run, `FileMemoryProvider` adds memory
   instructions, the current memory index (`memories.md`) and these tools:
   `file_memory_write`, `file_memory_read`, `file_memory_ls`,
   `file_memory_grep`, `file_memory_delete`, `file_memory_replace` and
   `file_memory_replace_lines`.
2. **Scope decides who shares memory.** With `scope=USER_ID`, every session
   for that user reads and writes the same folder. Without `scope`, the
   provider uses the session id, so each session would get its own empty
   folder and session B would recall nothing.
3. **Inspectable storage.** Memories are readable Markdown files, so you can
   open them, edit them, or delete them to reset the agent.

Limits: the model chooses whether to call the memory tools, so recall is not
guaranteed. The files are plaintext and unencrypted, and the store does not lock
files across processes. `FileSystemAgentFileStore` is marked experimental in
`agent-framework-core` 1.21.0 and prints an `ExperimentalWarning`.

## Supported capabilities and activation requirements

| Capability | API and mechanism | Current sample status |
| --- | --- | --- |
| File-based long-term memory | `FileMemoryProvider(store=..., scope=...)` | Implemented |
| Per-user memory scope | `scope="demo_user"` (fixed demo value) | Implemented; a real app would use the signed-in user's ID |
| Local function tool | `@tool get_weather` | Registered; not used by the demo prompts |
| Automatic memory extraction | `MemoryContextProvider` uses extra LLM calls to pull facts out of transcripts | Available, experimental, not configured |
| Persisted transcripts | `FileHistoryProvider` stores one message file per session | Available, experimental, not configured |
| Database or vector memory | Custom store or vector-store providers | Not implemented |
| MCP tools | MCP client/server configuration | Not implemented; stage 08 covers MCP |

## How it works

1. [`MEMORY_DIR` and `USER_ID`](app/simple-ai-agent-maf-long-term-memory.py#L34-L39)
   set where memories live and which user they belong to.
2. [`print_memory_files`](app/simple-ai-agent-maf-long-term-memory.py#L54-L68)
   lists every file under `MEMORY_DIR` so you can see what the agent saved.
3. [`FileSystemAgentFileStore` and `FileMemoryProvider`](app/simple-ai-agent-maf-long-term-memory.py#L104-L109)
   are created locally. No file is written until the model calls a memory tool.
4. [`DefaultAzureCredential` and `FoundryChatClient`](app/simple-ai-agent-maf-long-term-memory.py#L111-L124)
   prepare authenticated model communication, as in earlier stages.
5. [`Agent(...)`](app/simple-ai-agent-maf-long-term-memory.py#L126-L144)
   registers the memory provider and the weather tool.
6. [Session A](app/simple-ai-agent-maf-long-term-memory.py#L146-L166) shares
   facts. The model usually calls `file_memory_write`, then the script prints
   the memory files.
7. [Session B](app/simple-ai-agent-maf-long-term-memory.py#L171-L189) is a new
   session. The model reads memory to greet Alex and suggest a vegetarian dinner.
8. [Session C](app/simple-ai-agent-maf-long-term-memory.py#L191-L209) asks for a
   summary of past conversations. It shows what memory does **not** store (see
   [Why session C cannot summarize past conversations](#why-session-c-cannot-summarize-past-conversations)).

## Why session C cannot summarize past conversations

A typical run prints something like:

```text
- I don't have a record of earlier conversation topics in the available memory.
- Your name is Alex, and you're vegetarian.
- You prefer answers in 3 short bullet points.
```

That answer is correct behavior, not a bug:

- **Sessions do not share history.** Session C is new, so it cannot see the
  messages from sessions A or B.
- **Memory holds only what the model chose to save.** Following its
  instructions, the model saved *durable facts* (name, diet, answer style) to
  `userpreferences.md`. It did not save "Alex asked about dinner" or the
  chickpea curry suggestion, because those are one-off events, not durable facts.
- **Nothing stores transcripts.** This sample has no history provider such as
  `FileHistoryProvider`. Even that provider stores history per session, so a
  new session would not load it automatically.

The model therefore reports the preferences it found and honestly says it has
no record of past conversation topics. Exercise 5 below shows one way to change that.

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

Observed on **2026-10-13** with this stage's Linux virtual-environment
interpreter, Python **3.12.3**. The manifest is unpinned, so a fresh install
may resolve different versions.

| Package / library | Purpose in this sample | Observed version / reference |
| --- | --- | --- |
| `agent-framework-foundry` | Provides `FoundryChatClient` and installs the core framework | 1.14.1; [Foundry provider docs](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python) |
| `agent-framework-core` | `Agent`, `Message`, `tool`, `FileMemoryProvider`, `FileSystemAgentFileStore` | 1.21.0; [Agent Framework docs](https://learn.microsoft.com/en-us/agent-framework/) |
| `azure-identity` | Async `DefaultAzureCredential` for Entra token acquisition | 1.26.0; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) |
| `python-dotenv` | Parses the app-local dotenv file into a dictionary | 1.2.4; [python-dotenv docs](https://bbc2.github.io/python-dotenv/) |
| Python standard library | `asyncio`, `os`, `pathlib`, and `random` | [Python docs](https://docs.python.org/3/) |

## Prerequisites and setup

- Python compatible with the installed framework packages; 3.12.3 was verified here.
- A Microsoft Foundry project with a deployed model that supports the
  Responses API and tool calling (the memory tools are function tools).
- An identity available to `DefaultAzureCredential` with permission to invoke
  the deployment.

**Linux, zsh or bash; start in the repository root:**

```sh
cd ai-agents/microsoft-agent-framework/07_simple-maf-long-term-memory
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## Configuration

Create `app/.env` beside the script, or set the values in the process
environment. A nonempty environment value wins over the `.env` value.

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

- `memories.md` is an index that the provider rebuilds after every write.
- `*_description.md` holds the short description the model gave a file.
- Reset all memory with `rm -rf app/memory_store`.

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

## Validation and troubleshooting

The test folder is an empty placeholder. Safe offline checks are the comment
placement checker, Python compilation, and imports; they do not prove model
behavior. From the repository root:

```sh
./ai-agents/microsoft-agent-framework/07_simple-maf-long-term-memory/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/microsoft-agent-framework/07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py
```

| Symptom | First check |
| --- | --- |
| `ExperimentalWarning` printed | Expected; `FileSystemAgentFileStore` is experimental |
| Memory file list is empty after session A | The model did not call `file_memory_write`; make the instructions more explicit |
| Session B does not recall facts | Check that `scope` is set and that the files exist under `app/memory_store/demo_user/` |
| Session C cannot summarize past topics | Expected; see [Why session C cannot summarize past conversations](#why-session-c-cannot-summarize-past-conversations) |
| Old facts keep appearing | Memory persists by design; delete `app/memory_store` to reset |
| Missing setting / auth failure | Same checks as earlier stages: `FOUNDARY_*` names, credential, and RBAC |

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

Progression: simple model response, explicit agent, structured messages,
local tools, [short-term sessions](../06_simple-maf-short-term-memory/README.md),
**persistent memory (this stage)**, then MCP. MCP supplies protocol-based tools
and does not itself provide memory.

This is a learning sample, not a production memory system. It has no real
user identity, encryption, retention policy, concurrency control, or tests.
