# Simple Short-Term Memory - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the sixth learning stage in the Pydantic AI course. It sends three
related requests and carries the conversation from each run into the next, so
"those bullet points" refers to the earlier answer. It is the counterpart of
the [Microsoft Agent Framework stage 06](../../microsoft-agent-framework/06_simple-maf-short-term-memory/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Keep context across turns of one conversation |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a deployed model |
| Mechanism | `agent.run(..., conversation=previous_response.conversation)` |
| Turns | 5 bullet points about India → add a description to each → summarize |
| Storage | In process memory only; lost when the script exits |
| Current status | Implemented three-turn conversation |

Models do not remember earlier requests by themselves. "Memory" in a chat is the
application sending earlier messages again with the new one. Pydantic AI's
`Conversation` object holds those messages (plus running token usage and a
conversation ID).

## How this maps to MAF sessions

| MAF stage 06 | This stage | Notes |
| --- | --- | --- |
| `agent_session = agent.create_session()` once, up front | No setup; the first `run(...)` starts a new conversation | |
| `agent.run(msg2, session=agent_session)` | `agent.run(msg2, conversation=response1.conversation)` | Each result returns a **new** `Conversation` that includes that run's messages. |
| The same session object for every turn | The latest result's `conversation` for the next turn | |

Important detail verified with the installed version: passing the *same*
`Conversation` object to every run does **not** accumulate history. The object
you pass in is not modified; the updated conversation comes back on the result.
That is why turn 3 uses `response2.conversation`, not `response1.conversation`.

`message_history=response.all_messages()` is the older way to continue a
conversation and still works, but it carries only the messages, not the running
usage or conversation ID.

## Previous implementation and technical delta

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [Stage 05](../05_simple-pydanticai-tool-decorator/app/simple-ai-agent-pydanticai-tool-decorator.py#L111-L118) makes one independent run. | [Turn 1](app/simple-ai-agent-pydanticai-short-term-memory.py#L111-L114) starts a conversation; [turn 2](app/simple-ai-agent-pydanticai-short-term-memory.py#L122-L125) and [turn 3](app/simple-ai-agent-pydanticai-short-term-memory.py#L133-L137) continue it. | Follow-up requests can refer to earlier answers. |

The weather toolset is still registered (as in MAF stage 06) but these prompts
do not ask about weather.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Short-term conversation memory | Implemented | `conversation=` on turns 2 and 3 |
| Persistence across restarts | Not implemented | The conversation lives only in memory; stage 07 adds files |
| Local tool | Registered | `get_weather` is available but not needed by these prompts |
| MCP, streaming | Not implemented | Stages 08, 10 |

Every turn resends the whole conversation, so input tokens (and cost) grow with
each turn.

## How it works

1. Tool, configuration, and Foundry setup are the same as
   [stage 05](../05_simple-pydanticai-tool-decorator/README.md#how-it-works).
2. [Turn 1](app/simple-ai-agent-pydanticai-short-term-memory.py#L111-L120) runs
   without a conversation and prints the answer.
3. [Turn 2](app/simple-ai-agent-pydanticai-short-term-memory.py#L122-L131) passes
   `response1.conversation`, so the model sees turn 1's question and answer.
4. [Turn 3](app/simple-ai-agent-pydanticai-short-term-memory.py#L133-L139) passes
   `response2.conversation`, which contains all earlier turns, and prints the summary.

## Folder contents

```text
06_simple-pydanticai-short-term-memory/
├── README.md
├── app/
│   └── simple-ai-agent-pydanticai-short-term-memory.py
└── tests/
    └── .gitkeep        # empty placeholder, not a test suite
```

## Frameworks, setup, and configuration

Same as [stage 05](../05_simple-pydanticai-tool-decorator/README.md#frameworks-setup-and-configuration).
Reference: [Pydantic AI message history](https://pydantic.dev/docs/ai/core-concepts/message-history/).

## Run and expected output

**Working directory: `ai-agents/pydantic-framework`.** Makes three live,
potentially billable requests; not run while writing this README:

```sh
./.venv/bin/python 06_simple-pydanticai-short-term-memory/app/simple-ai-agent-pydanticai-short-term-memory.py
```

Prints "Response 1" (five bullet points), "Response 2" (the same points with
descriptions), then a one-paragraph summary.

## Exercises to try

1. **Break the memory.** Remove `conversation=response1.conversation` from turn 2.
   The model no longer knows which bullet points you mean.
2. **Watch it grow.** Print `len(response3.all_messages())` and
   `response3.usage` at the end to see how much context the last turn carried.
3. **Pass the wrong one.** Use `response1.conversation` for turn 3. The summary
   misses turn 2's descriptions, showing that each result holds its own snapshot.

## Validation and troubleshooting

`tests/` is an empty placeholder. Use the comment checker and troubleshooting
from [stage 02](../02_simple-pydanticai-foundary/README.md#validation-and-troubleshooting).

## Learning links and progression

- [AI concepts: Pydantic AI user content and conversations](../../../docs/ai-concepts.md#pydantic-ai-user-content-and-conversations)
- [AI concepts: short-term conversation sessions](../../../docs/ai-concepts.md#short-term-conversation-sessions) (MAF view)

Next, [stage 07](../07_simple-pydanticai-long-term-memory/README.md) saves
selected facts to files so fresh conversations can use them.
