# Simple Tool Decorator - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the fifth learning stage in the Pydantic AI course. It adds a local
Python function that the model can request during a run. The weather function
returns randomized demo data, so the lesson focuses on the tool-calling flow
without calling a real weather API. It is the counterpart of the
[Microsoft Agent Framework stage 05](../../microsoft-agent-framework/05_simple-maf-tool-decorator/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Register a Python function as a model-selectable tool |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a deployed model |
| Tool | `get_weather(location: str) -> str`, decorated with `@weather_tools.tool_plain` |
| Registration | `Agent(..., toolsets=[weather_tools])` |
| Input / output | A question about weather in India / `response.output` |
| Current status | Implemented one-shot local-tool demonstration |

A **tool** is application code that the model may ask to run. The model only
sends a request ("call `get_weather` with `location='India'`"); Pydantic AI
validates the arguments, runs the Python function, and sends the result back to
the model so it can write the final answer.

## How this maps to MAF's `@tool`

| MAF stage 05 | This stage | Notes |
| --- | --- | --- |
| `@tool` on a module-level function | `weather_tools = FunctionToolset()` then `@weather_tools.tool_plain` | Pydantic AI has no standalone `@tool`; a decorator on a toolset (or on an agent) registers the function. |
| `Agent(tools=[get_weather])` | `Agent(toolsets=[weather_tools])` | A toolset is a reusable group of tools. |
| Schema from signature + docstring | Same | `location: str` becomes the JSON schema; the docstring's `Args:` section becomes the parameter description. |

Pydantic AI also offers `@agent.tool_plain` / `@agent.tool`, which register a
tool directly on an agent. That needs the agent to exist before the function is
defined. This course creates the agent inside `main()` (after authentication),
so a module-level `FunctionToolset` keeps the MAF shape: define the tool at the
top of the file, attach it when building the agent. `tool_plain` is for tools
that do not need `RunContext`; `tool` passes a `RunContext` as the first argument.

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 04](../04_simple-pydanticai-messageclass/app/simple-ai-agent-pydanticai-messageclass.py#L69-L77) builds an agent with no tools. | [`weather_tools`](app/simple-ai-agent-pydanticai-tool-decorator.py#L34-L35) plus the [decorated `get_weather`](app/simple-ai-agent-pydanticai-tool-decorator.py#L51-L72). | Give the model a typed, described action instead of text-only answers. |
| Agent without `toolsets`. | [`Agent(..., toolsets=[weather_tools])`](app/simple-ai-agent-pydanticai-tool-decorator.py#L97-L109). | Enable the tool for this agent; registration does not force the model to use it. |

```text
Previous: model + Agent(...)                        -> run(user content) -> text
Current:  model + Agent(toolsets=[weather_tools])  -> run -> optional tool call -> text
```

A tool-enabled run may need more than one model request (one to ask for the
tool, one to use its result), so cost and latency can be higher.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Local function tool | Implemented | `get_weather` in `weather_tools` |
| Live weather data | Not implemented | Returns random demo values |
| Approval before running a tool | Supported, not configured | `requires_approval=True` exists on `tool_plain` |
| MCP tools | Not implemented | Stage 08 |
| Conversation memory, persistent memory, streaming | Not implemented | Stages 06, 07, 10 |

## How it works

1. [`weather_tools = FunctionToolset()`](app/simple-ai-agent-pydanticai-tool-decorator.py#L34-L35)
   creates an empty tool container at import time.
2. [`@weather_tools.tool_plain`](app/simple-ai-agent-pydanticai-tool-decorator.py#L51-L72)
   adds `get_weather` to it. The signature and docstring become the tool's
   name, JSON schema, and description; the function itself is unchanged.
3. [The Foundry `async with` block](app/simple-ai-agent-pydanticai-tool-decorator.py#L84-L94)
   and [`chat_model`](app/simple-ai-agent-pydanticai-tool-decorator.py#L95-L96)
   are the same as earlier stages.
4. [`Agent(...)`](app/simple-ai-agent-pydanticai-tool-decorator.py#L97-L109)
   receives a description and `toolsets=[weather_tools]`.
5. [`await agent.run(user_message)`](app/simple-ai-agent-pydanticai-tool-decorator.py#L111-L118)
   starts the run. If the model requests `get_weather`, Pydantic AI calls it and
   continues the run with the result. `main()` never calls `get_weather` itself.

## Folder contents

```text
05_simple-pydanticai-tool-decorator/
├── README.md
├── app/
│   └── simple-ai-agent-pydanticai-tool-decorator.py
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks, setup, and configuration

Same as [stage 02](../02_simple-pydanticai-foundary/README.md#frameworks-and-libraries),
plus Python's built-in `random.randint`. Reference:
[Pydantic AI function tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/).
Requires a deployment that supports tool calling.

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Live, potentially billable
request; not run while writing this README:

```sh
./.venv/bin/python 05_simple-pydanticai-tool-decorator/app/simple-ai-agent-pydanticai-tool-decorator.py
```

Prints generated text that usually includes the random temperature and
condition from `get_weather`. Whether the model calls the tool, and the wording,
are nondeterministic.

## Exercises to try

1. **See when the tool runs.** Add `print(f"get_weather called for {location}")`
   as the first line inside `get_weather`, then ask about Pune and Delhi.
2. **The model decides.** Ask "What is the capital of France?" The print from
   exercise 1 does not appear: registering a tool does not force its use.
3. **Inspect the exchange.** Print `response.all_messages()` and find the
   `ToolCallPart` (the model's request) and the `ToolReturnPart` (your result).
4. **Add a second tool.** Decorate `get_time(city: str) -> str` with
   `@weather_tools.tool_plain` and ask for the time and weather in Pune.

## Validation and troubleshooting

`tests/` is an empty placeholder. Use the comment checker and troubleshooting
from [stage 02](../02_simple-pydanticai-foundary/README.md#validation-and-troubleshooting).

| Symptom | First check |
| --- | --- |
| Tool never called | The deployment supports tool calling; the question needs weather |
| Unexpected weather values | Intentional: the function returns random demo data |

## Learning links and progression

- [AI concepts: Pydantic AI toolsets and file memory](../../../docs/ai-concepts.md#pydantic-ai-toolsets-and-file-memory)
- [AI concepts: function tools and the `@tool` decorator](../../../docs/ai-concepts.md#function-tools-and-the-tool-decorator) (MAF view)
- [Python concepts: functions and typing](../../../docs/python-concepts.md#functions-and-typing)

Next, [stage 06](../06_simple-pydanticai-short-term-memory/README.md) continues
one conversation across several runs.
