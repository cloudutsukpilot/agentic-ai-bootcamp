# Simple Message Structure - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the fourth learning stage in the Pydantic AI course. It sends the user's
request as a **list of content items** (`list[UserContent]`) instead of a plain
string. It is the counterpart of the
[Microsoft Agent Framework stage 04](../../microsoft-agent-framework/04_simple-maf-messageclass/README.md),
which introduced `Message(role="user", contents=[...])`.

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Represent the user's input as structured content |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a deployed model |
| Input | `user_message: list[UserContent]` with one text item |
| Output | `response.output` |
| Current status | Implemented; one text content item |

## How this maps to MAF's `Message` class

Pydantic AI does **not** have a public `Message(role=..., contents=...)` input
class. Its design is:

| Concept | MAF | Pydantic AI |
| --- | --- | --- |
| The user's turn | `Message(role="user", contents=[...])` | The `user_prompt` argument of `agent.run(...)`: a `str` or a sequence of `UserContent` items |
| Role | Explicit `role="user"` | Implicit: whatever you pass to `run(...)` is the user's turn |
| Content items | `contents=[...]` (text, `Content.from_data(...)`) | `str`, `BinaryContent`, `ImageUrl`, `DocumentUrl`, and other `UserContent` types |
| Stored history | `Message` objects in a session | `ModelRequest` (containing a `UserPromptPart`) and `ModelResponse` objects |

So the direct equivalent of `contents=[...]` is the list passed to
[`agent.run(user_message)`](app/simple-ai-agent-pydanticai-messageclass.py#L79-L88).
Internally, Pydantic AI wraps it in a `UserPromptPart` inside a `ModelRequest`;
you see those classes when you inspect `response.all_messages()`.

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 03](../03_simple-pydanticai-agentclass/app/simple-ai-agent-pydanticai-agentclass.py#L81-L86) passes a plain string to `agent.run(...)`. | [`user_message: list[UserContent]`](app/simple-ai-agent-pydanticai-messageclass.py#L79-L84) is a list with one text item. | A list can later hold several items of different types, such as an image plus a question in stage 09. |

**This stage has the same capabilities as stage 03.** A one-item text list and a
plain string produce the same request. The list form matters once you add
non-text content. A content list is also not memory: each `run(...)` without a
conversation is still independent (stage 06 changes that).

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Structured user content | Implemented | One text item in `list[UserContent]` |
| Multimodal input | Not implemented | Supported by `UserContent`; stage 09 sends an image |
| Conversation memory | Not implemented | Stage 06 |
| Tools, MCP, streaming | Not implemented | Stages 05, 08, 10 |

## How it works

1. [Configuration](app/simple-ai-agent-pydanticai-messageclass.py#L29-L54) and
   the [Foundry `async with` block](app/simple-ai-agent-pydanticai-messageclass.py#L56-L66)
   are the same as stage 03.
2. [`chat_model` and `Agent(...)`](app/simple-ai-agent-pydanticai-messageclass.py#L67-L77)
   are created as before (provider inlined in the model call).
3. [`user_message`](app/simple-ai-agent-pydanticai-messageclass.py#L79-L84) is
   annotated `list[UserContent]` so editors and type checkers know what it may hold.
4. [`await agent.run(user_message)`](app/simple-ai-agent-pydanticai-messageclass.py#L86-L88)
   sends the structured input and prints the output.

## Folder contents

```text
04_simple-pydanticai-messageclass/
├── README.md
├── app/
│   └── simple-ai-agent-pydanticai-messageclass.py
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks, setup, and configuration

Same as [stage 02](../02_simple-pydanticai-foundary/README.md#frameworks-and-libraries).
`UserContent` is imported from `pydantic_ai`. Uses the shared `.venv` and the
`FOUNDARY_*` settings in the shared `.env`.

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Live, potentially billable
request; not run while writing this README:

```sh
./.venv/bin/python 04_simple-pydanticai-messageclass/app/simple-ai-agent-pydanticai-messageclass.py
```

Prints a generated explanation of Pydantic AI's message structure.

## Exercises to try

1. Add a second text item to `user_message`, for example
   `"Answer in exactly three sentences."`, and see both items influence the answer.
2. After the print, add `print(response.all_messages())` to see the
   `ModelRequest`/`UserPromptPart` and `ModelResponse`/`TextPart` objects that
   Pydantic AI recorded for this run.

## Validation and troubleshooting

`tests/` is an empty placeholder. Use the comment checker and troubleshooting
table from [stage 02](../02_simple-pydanticai-foundary/README.md#validation-and-troubleshooting).

## Learning links and progression

- [AI concepts: Pydantic AI user content and conversations](../../../docs/ai-concepts.md#pydantic-ai-user-content-and-conversations)
- [AI concepts: messages as structured conversation items](../../../docs/ai-concepts.md#messages-as-structured-conversation-items) (MAF view)
- [Pydantic AI message history](https://pydantic.dev/docs/ai/core-concepts/message-history/)

Next, [stage 05](../05_simple-pydanticai-tool-decorator/README.md) adds a Python
function the model can call.
