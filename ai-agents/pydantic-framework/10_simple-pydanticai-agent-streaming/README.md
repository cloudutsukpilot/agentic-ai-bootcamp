# Simple Agent Streaming - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the tenth learning stage in the Pydantic AI course. It prints the
model's answer **while it is being generated** instead of waiting for the
complete response. It is the counterpart of the MAF stage
[`10_simple-maf-agent-streaming`](../../microsoft-agent-framework/10_simple-maf-agent-streaming/app/simple-ai-agent-maf-agent-streaming.py),
which has no README yet.

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Stream text output token-by-token to the terminal |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a deployed model |
| Mechanism | `async with agent.run_stream(...) as stream:` + `async for chunk in stream.stream_text(delta=True)` |
| Input | One structured user message asking for a longer answer |
| Output | Text printed incrementally, then a newline |
| Current status | Implemented |

## How this maps to MAF streaming

| MAF stage 10 | This stage | Notes |
| --- | --- | --- |
| `stream = agent.run(user_message, stream=True)` | `async with agent.run_stream(user_message) as stream:` | Pydantic AI uses a separate method and an async context manager. |
| `async for chunk in stream:` then loop over `chunk.contents` | `async for chunk in stream.stream_text(delta=True):` | `stream_text` yields only text, so no content-type filtering is needed. |
| Skip `merge_mode == "replace"` snapshots | `delta=True` | With `delta=True` each item is only the new text; with `delta=False` each item is the full text so far. |

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 04](../04_simple-pydanticai-messageclass/app/simple-ai-agent-pydanticai-messageclass.py#L86-L88) awaits `agent.run(...)` and prints the full output at the end. | [`agent.run_stream(...)`](app/simple-ai-agent-pydanticai-agent-streaming.py#L86-L94) prints each new piece as it arrives. | Long answers feel responsive; users see progress immediately. |

Streaming changes **when** text is shown, not what the model generates or what it
costs. Like the MAF stage, this one has no tools or memory, so it isolates the
streaming lesson.

## How it works

1. Configuration, Foundry setup, and [`Agent(...)`](app/simple-ai-agent-pydanticai-agent-streaming.py#L68-L78)
   are the same as stage 04.
2. [`user_message`](app/simple-ai-agent-pydanticai-agent-streaming.py#L80-L84)
   asks for ten bullet points, long enough to see streaming happen.
3. [Entering `agent.run_stream(...)`](app/simple-ai-agent-pydanticai-agent-streaming.py#L86-L88)
   sends the request and returns a `StreamedRunResult` once the model starts
   producing its final text.
4. [`stream.stream_text(delta=True)`](app/simple-ai-agent-pydanticai-agent-streaming.py#L89-L92)
   yields new text fragments. Each is printed with `end=""` (no newline) and
   `flush=True` (show it now). Fragments are grouped by up to 0.1 seconds by
   default (`debounce_by=0.1`).
5. A final [`print()`](app/simple-ai-agent-pydanticai-agent-streaming.py#L93-L94)
   ends the line after the stream finishes.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Streaming text output | Implemented | `run_stream` + `stream_text(delta=True)` |
| Streaming tool-call events | Not implemented | `agent.run_stream_events(...)` exposes every event, including tool calls |
| Tools, memory, MCP | Not configured | Intentionally omitted to focus on streaming |

## Folder contents

```text
10_simple-pydanticai-agent-streaming/
├── README.md
├── app/
│   └── simple-ai-agent-pydanticai-agent-streaming.py
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks, setup, and configuration

Same as [stage 02](../02_simple-pydanticai-foundary/README.md#frameworks-and-libraries).
Reference: [Pydantic AI streaming](https://pydantic.dev/docs/ai/core-concepts/agent/#streaming-events-and-final-output).

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Live, potentially billable
request; not run while writing this README:

```sh
./.venv/bin/python 10_simple-pydanticai-agent-streaming/app/simple-ai-agent-pydanticai-agent-streaming.py
```

Text appears in small pieces until the explanation and ten bullet points are complete.

## Exercises to try

1. Change `delta=True` to `delta=False` and see each print repeat the whole text so far.
2. Pass `debounce_by=None` to `stream_text(...)` to print every fragment as soon as it arrives.
3. After the `async for` loop (still inside the `async with`), print
   `stream.usage` to see token counts once streaming has finished.

## Validation and troubleshooting

`tests/` is an empty placeholder. Use the comment checker and troubleshooting
from [stage 02](../02_simple-pydanticai-foundary/README.md#validation-and-troubleshooting).
If the text appears all at once, your terminal or a pipe may be buffering
output; run the script directly in a terminal.

## Learning links and progression

- [AI concepts: Pydantic AI streamed runs](../../../docs/ai-concepts.md#pydantic-ai-streamed-runs)
- [AI concepts: streaming text updates and replacement snapshots](../../../docs/ai-concepts.md#streaming-text-updates-and-replacement-snapshots) (MAF view)
- [Python concepts: async context managers](../../../docs/python-concepts.md#async-context-managers)

This is the last implemented stage. See the [course recap](../README.md) for the
full map.
