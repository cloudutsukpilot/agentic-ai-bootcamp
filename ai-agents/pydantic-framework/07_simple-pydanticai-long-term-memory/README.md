# Simple Long-Term Memory - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the seventh learning stage in the Pydantic AI course. It lets **fresh
conversations** use facts saved by earlier ones, by giving the agent tools that
read and write Markdown files on disk. It is the counterpart of the
[Microsoft Agent Framework stage 07](../../microsoft-agent-framework/07_simple-maf-long-term-memory/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Persist selected facts so later, unrelated conversations can use them |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a deployed model |
| Memory mechanism | Local [`file_memory.py`](app/file_memory.py) → `FunctionToolset` with `file_memory_*` tools and dynamic instructions |
| Storage | `app/memory_store/demo_user/*.md` (created on first run, git-ignored) |
| Sessions | A: share facts → B: personalized greeting → C: "summarize past conversations" |
| Current status | Implemented local file-backed demo |

## Why this stage has its own memory module

MAF ships `FileMemoryProvider` + `FileSystemAgentFileStore`. **Pydantic AI 2.64
has no built-in equivalent.** Its `MemoryTool` is a *native* tool that only
Anthropic models support, and a separate "Pydantic AI Harness" package documents
a memory feature; neither is installed or used here. So this stage includes a
small module, [`file_memory.py`](app/file_memory.py), that reproduces the MAF
provider's behavior with ordinary Pydantic AI building blocks:

| MAF `FileMemoryProvider` | This stage's `create_file_memory_toolset(...)` |
| --- | --- |
| `file_memory_write`, `file_memory_read`, `file_memory_delete`, `file_memory_ls` tools | The [same four tools](app/file_memory.py#L105-L211), registered with `@toolset.tool_plain` |
| (also `file_memory_replace`, `_replace_lines`, `_grep`) | Not reproduced; overwrite with `file_memory_write` instead |
| `<name>_description.md` sidecar per file | [Same](app/file_memory.py#L37-L41) |
| Auto-maintained `memories.md` index | [`rebuild_index()`](app/file_memory.py#L62-L84) after every write and delete |
| Index and guidance injected before each model request | [`memory_instructions()`](app/file_memory.py#L86-L95) passed as the toolset's `instructions` |
| Store-wide write lock | [`sequential=True`](app/file_memory.py#L97-L103): the memory tools run one at a time |
| `scope=USER_ID` | `scope=USER_ID` selects the `demo_user/` subfolder |
| `context_providers=[memory_provider]` | `toolsets=[memory_tools, weather_tools]` |

The folder layout matches the MAF stage, so the same `memory_store/demo_user/`
files would make sense to either implementation.

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 06](../06_simple-pydanticai-short-term-memory/app/simple-ai-agent-pydanticai-short-term-memory.py#L122-L125) carries context by passing `conversation=`; it disappears when the script ends. | [`memory_tools`](app/simple-ai-agent-pydanticai-long-term-memory.py#L105-L106) is added to the [agent's toolsets](app/simple-ai-agent-pydanticai-long-term-memory.py#L121-L138); each session is a fresh `run(...)` with no `conversation`. | Keep selected facts on disk so new conversations, and new script runs, can use them. |

Sessions in this stage deliberately do **not** share a conversation. Session B
can only know your name because session A saved it to a file.

## How it works

1. [`MEMORY_DIR` and `USER_ID`](app/simple-ai-agent-pydanticai-long-term-memory.py#L37-L40)
   choose `app/memory_store/demo_user/` as the storage folder.
2. [`create_file_memory_toolset(...)`](app/simple-ai-agent-pydanticai-long-term-memory.py#L105-L106)
   builds the memory toolset. Nothing is written yet.
3. [`Agent(...)`](app/simple-ai-agent-pydanticai-long-term-memory.py#L121-L138)
   gets instructions to save durable facts and check memory first, plus both
   toolsets. Before each model request, Pydantic AI calls `memory_instructions()`,
   which appends the current `memories.md` index to the agent's instructions.
4. [Session A](app/simple-ai-agent-pydanticai-long-term-memory.py#L140-L156)
   shares a name, a vegetarian diet, and a format preference. The model may call
   `file_memory_write`, which saves the file and its description and rebuilds
   the index. [`print_memory_files()`](app/simple-ai-agent-pydanticai-long-term-memory.py#L59-L70)
   then lists what is on disk (names only, not contents).
5. [Session B](app/simple-ai-agent-pydanticai-long-term-memory.py#L158-L168) is
   a new conversation. The model sees the index in its instructions and can call
   `file_memory_read` to get the details.
6. [Session C](app/simple-ai-agent-pydanticai-long-term-memory.py#L170-L183)
   asks for a summary of past conversations. See the next section.

## Why session C cannot summarize past conversations

Memory files contain only what the model chose to save, usually a few facts. No
code here saves conversation transcripts, so a good answer to session C lists the
saved preferences and says it has no record of the full conversations. A
confident "summary" of past chats would be invented.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Persistent memory across sessions and restarts | Implemented | Markdown files under `app/memory_store/` |
| Memory index in the prompt | Implemented | `memory_instructions()` runs before each model request |
| Saving is guaranteed | No | The model decides whether to call `file_memory_write`; inspect the files |
| Conversation transcripts | Not implemented | Only saved facts persist |
| Search or retrieval (RAG) | Not implemented | No embeddings or vector search |
| Per-user isolation | Demo only | `USER_ID` is fixed to `demo_user` |
| MCP, streaming | Not implemented | Stages 08, 10 |

## Folder contents

```text
07_simple-pydanticai-long-term-memory/
├── README.md
├── app/
│   ├── file_memory.py                                  # memory toolset module
│   ├── simple-ai-agent-pydanticai-long-term-memory.py  # entry point
│   └── memory_store/                                   # created at run time, git-ignored
│       └── demo_user/
│           ├── memories.md                             # generated index
│           ├── <name>.md
│           └── <name>_description.md
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks, setup, and configuration

Same as [stage 05](../05_simple-pydanticai-tool-decorator/README.md#frameworks-setup-and-configuration).
Memory needs no extra packages or settings; it uses Python's built-in `pathlib`.
References: [Pydantic AI function tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/),
[parallel tool calls and `sequential`](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#parallel-tool-calls-concurrency),
[agent instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions).

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Makes three or more live,
potentially billable requests (tool calls add model turns); not run while
writing this README:

```sh
./.venv/bin/python 07_simple-pydanticai-long-term-memory/app/simple-ai-agent-pydanticai-long-term-memory.py
```

Expected shape: session A's acknowledgement, a list of memory files such as
`demo_user/memories.md` and `demo_user/userpreferences.md`, a greeting for Alex
with a vegetarian dinner idea, then session C's overview of preferences.
Wording and file names are chosen by the model.

## Exercises to try

1. Run the script twice. On the second run, session A may update the existing
   file instead of creating another; read `memories.md` to check.
2. Delete `app/memory_store/` and run only session B (comment out session A).
   Without saved facts the agent cannot know your name.
3. Change session A to "I am allergic to peanuts" and see whether session B's
   dinner idea reflects it.

## Validation and troubleshooting

`tests/` is an empty placeholder. From the repository root, check both Python files:

```sh
./ai-agents/pydantic-framework/.venv/bin/python \
  .github/skills/python-learning-comments/scripts/check_comments.py \
  ai-agents/pydantic-framework/07_simple-pydanticai-long-term-memory/app/*.py
```

| Symptom | First check |
| --- | --- |
| `ModuleNotFoundError: file_memory` | Run the script by path as shown; Python then adds `app/` to the import path |
| No memory files after session A | The model chose not to save; strengthen the instructions or rerun |
| Session B ignores saved facts | Read `memories.md`; the index must describe the file usefully |

Do not store secrets or sensitive personal data: memory files are plain text.
Delete `app/memory_store/` to reset; a new conversation alone does not.

## Learning links and progression

- [AI concepts: Pydantic AI toolsets and file memory](../../../docs/ai-concepts.md#pydantic-ai-toolsets-and-file-memory)
- [AI concepts: Pydantic AI user content and conversations](../../../docs/ai-concepts.md#pydantic-ai-user-content-and-conversations) (short-term memory, for contrast)

Next, [stage 08](../08_simple-pydanticai-mcp/README.md) keeps this memory and
adds tools from an external MCP server.
