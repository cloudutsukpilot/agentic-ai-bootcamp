# Simple Image Analysis - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the ninth learning stage in the Pydantic AI course. It sends a PNG image
together with a question in one user message, asks the agent to save what it
sees to file memory, and then asks follow-up questions in **fresh**
conversations that never receive the image. It is the counterpart of the
[Microsoft Agent Framework stage 09](../../microsoft-agent-framework/09_simple-maf-image-analysis/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Send image + text input, and reuse what the model saw through memory |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a vision-capable deployed model |
| Image input | `BinaryContent(data=image_data, media_type="image/png")` |
| Memory | Same `file_memory.py` toolset as stage 07 |
| Tools | Memory tools only (no weather tool, no MCP) |
| Sessions | A: image + "What does this image contain?" → B: superhero? → C: user's interpretation → D: character name |
| Current status | Implemented |

## How this maps to MAF's `Content` items

| MAF stage 09 | This stage |
| --- | --- |
| `Content.from_data(data=image_data, media_type="image/png")` | `BinaryContent(data=image_data, media_type="image/png")` |
| `Content.from_text("What does this image contain?")` | A plain string item in the same list |
| `Message(role="user", contents=[...])` | `message_a: list[UserContent] = [...]` passed to `agent.run(...)` |
| `FileMemoryProvider` via `context_providers` | `create_file_memory_toolset(...)` via `toolsets` |
| `print_session_text(...)` colored output | Same helper, same colors and `NO_COLOR` handling |

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 04](../04_simple-pydanticai-messageclass/app/simple-ai-agent-pydanticai-messageclass.py#L79-L84) sends a one-item text list. | [`message_a`](app/simple-ai-agent-pydanticai-image-analysis.py#L131-L138) holds image bytes **and** text. | Show why the list form of user content exists. |
| [Stage 07](../07_simple-pydanticai-long-term-memory/app/simple-ai-agent-pydanticai-long-term-memory.py#L121-L138) remembers facts the user typed. | The [agent](app/simple-ai-agent-pydanticai-image-analysis.py#L114-L129) is told to store image details in memory. | Later sessions answer questions about an image they never received. |

## How it works

1. [`image_path` and `image_data`](app/simple-ai-agent-pydanticai-image-analysis.py#L96-L99)
   load `sample-image.png` from beside the script as raw bytes.
2. [`memory_tools`](app/simple-ai-agent-pydanticai-image-analysis.py#L93-L94)
   uses `app/memory_store/demo_user/`.
3. [`Agent(...)`](app/simple-ai-agent-pydanticai-image-analysis.py#L114-L129)
   registers only the memory toolset.
4. [Session A](app/simple-ai-agent-pydanticai-image-analysis.py#L131-L149)
   sends the image and question. `BinaryContent` tells Pydantic AI the bytes are
   a PNG; the OpenAI Responses adapter sends them to the model as an image. The
   model may save a description with `file_memory_write`.
5. Sessions [B](app/simple-ai-agent-pydanticai-image-analysis.py#L151-L164),
   [C](app/simple-ai-agent-pydanticai-image-analysis.py#L166-L179), and
   [D](app/simple-ai-agent-pydanticai-image-analysis.py#L181-L194) are fresh
   runs with text only. They depend on what earlier sessions saved; session C
   may add the user's interpretation to memory, which session D can then use.
6. [`print_session_text`](app/simple-ai-agent-pydanticai-image-analysis.py#L71-L81)
   colors prompts cyan and responses green only in an interactive terminal when
   `NO_COLOR` is not set.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Image input | Implemented | One PNG via `BinaryContent` |
| Persistent file memory | Implemented | Same module as stage 07 |
| Image re-sent in later sessions | No | Only saved text descriptions carry over |
| Other local tools or MCP | Not configured | Only the memory toolset is registered |
| Streaming | Not implemented | Stage 10 |

## Folder contents

```text
09_simple-pydanticai-image-analysis/
├── README.md
├── app/
│   ├── file_memory.py                               # same memory module as stage 07
│   ├── sample-image.png                             # copied from the MAF stage
│   ├── simple-ai-agent-pydanticai-image-analysis.py # entry point
│   └── memory_store/                                # created at run time, git-ignored
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks, setup, and configuration

Same as [stage 07](../07_simple-pydanticai-long-term-memory/README.md#frameworks-setup-and-configuration),
plus Python's built-in `sys` module. The deployment must accept image input
(a vision-capable model); text-only deployments return an error for session A.

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Sends the image and makes
several live, potentially billable requests; not run while writing this README:

```sh
./.venv/bin/python 09_simple-pydanticai-image-analysis/app/simple-ai-agent-pydanticai-image-analysis.py
```

Output alternates "Session X Prompt" and "Session X Response" blocks, with a
memory-file listing after session A. Answers depend on the model and on any
memory left from earlier runs.

## Exercises to try

1. Delete `app/memory_store/` and comment out session A. Sessions B–D can no
   longer answer, because nothing describes the image.
2. Replace `sample-image.png` with your own PNG and change session B's question.
3. Change `media_type` to `"image/jpeg"` and use a JPEG file to see that the
   media type must match the bytes.

## Validation and troubleshooting

`tests/` is an empty placeholder. Check both Python files with the comment
checker (see [stage 07](../07_simple-pydanticai-long-term-memory/README.md#validation-and-troubleshooting)).

| Symptom | First check |
| --- | --- |
| Error in session A about image input | The deployment must be vision-capable |
| `FileNotFoundError: sample-image.png` | The image must stay beside the script |
| Later sessions do not know the image | Read `memory_store/demo_user/memories.md`; the model may not have saved anything |

## Learning links and progression

- [AI concepts: Pydantic AI user content and conversations](../../../docs/ai-concepts.md#pydantic-ai-user-content-and-conversations)
- [AI concepts: Pydantic AI toolsets and file memory](../../../docs/ai-concepts.md#pydantic-ai-toolsets-and-file-memory)
- [Python concepts: script-relative paths and binary image data](../../../docs/python-concepts.md#script-relative-paths-and-binary-image-data)

Next, [stage 10](../10_simple-pydanticai-agent-streaming/README.md) prints the
answer while the model is still generating it.
