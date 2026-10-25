# AI concepts — agents and model interaction

<!-- markdownlint-configure-file {"MD024": {"siblings_only": true}} -->

This guide owns agent/framework behavior. Python syntax belongs in
[Python concepts](./python-concepts.md); service endpoints and credentials belong
in [Azure concepts](./azure-concepts.md). Facts below were checked against stage
02's installed `agent-framework-core` 1.21.0 and `agent-framework-foundry` 1.14.1
on 2026-10-13. Online documentation can evolve independently.

## Contents

- [Agent architecture](#agent-architecture)
  - [Foundry client versus local agent](#foundry-client-versus-local-agent)
  - [Instructions versus user prompts](#instructions-versus-user-prompts)
    - [Streaming text updates and replacement snapshots](#streaming-text-updates-and-replacement-snapshots)
  - [Messages as structured conversation items](#messages-as-structured-conversation-items)
    - [Short-term conversation sessions](#short-term-conversation-sessions)
  - [Explicit agent composition](#explicit-agent-composition)
  - [Tools and orchestration](#tools-and-orchestration)
  - [Function tools and the `@tool` decorator](#function-tools-and-the-tool-decorator)
- [MCP connections](#mcp-connections)
    - [Stdio server lifecycle](#stdio-server-lifecycle)

## Agent architecture

Separate the adapter that communicates with a model from the object that carries
agent behavior. Then distinguish reusable behavior instructions from a run's input.

### Foundry client versus local agent

#### What it means

Microsoft Agent Framework is the orchestration library, not the model itself.
`FoundryChatClient` is an adapter to a Foundry project's OpenAI Responses API.
The configured deployment determines the model; a client class alone does not
identify its vendor or family. `client.as_agent(...)` locally constructs an
`Agent` using that client. In the installed SDK, the factory ends with
`Agent(**agent_kwargs)` and supplies `client=self`.

The client owns service communication. The agent holds its name, instructions,
and local run orchestration. Neither object is automatically a service-managed
Foundry agent resource. The awaited `agent.run(...)` triggers model interaction,
not the earlier factory call.

#### Example

**Exact stage 02 construction excerpt; not standalone:**

```python
# Create a local agent through the client's convenience factory.
agent = client.as_agent(
    # Set the local agent's readable name, not a hosted resource identifier.
    name="Sample MAF Foundry Agent",
    # Supply behavior instructions independently of the prompt passed to run.
    instructions="You are a helpful agent that explains the Microsoft Agent Framework.",
)
```

Expected result is a configured local agent object; no prompt is sent by this
excerpt. It assumes an existing configured client and was not run live.

#### Where it is used

- [Configure the Foundry client](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L51-L60).
- [Create the local agent](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L63-L69).
- [Invoke it and print text](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L71-L77).

#### Why it is used here

Stage 02 changes the service-access adapter and authentication while keeping the
same local agent boundary as stage 01. Its [README comparison](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/README.md#why-stage-02-follows-stage-01)
explains why this is not a new ability to answer questions. Later tools or session
reuse could be configured at this boundary; neither is configured here.

#### Common misunderstanding

`as_agent` does not mutate the client into an agent, provision a hosted agent,
or supply persistent memory. Application Insights instrumentation is not enabled
by this factory. For Python method-call semantics see
[objects and methods](./python-concepts.md#objects-methods-and-assignment).

#### References

- [Official Foundry model-provider documentation](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python).
<!-- markdownlint-disable-next-line MD013 -->
- [Microsoft Agent Framework source](https://github.com/microsoft/agent-framework) (upstream may differ from installed versions).
- [Project endpoints and deployments](./azure-concepts.md#foundry-project-endpoints-and-deployments).

### Streaming text updates and replacement snapshots

#### What it means

A streaming update is not always new text to append. In stage 10's installed
`agent-framework-core` 1.23.0, the Responses API adapter converts
`response.output_text.delta` into text content with `merge_mode="append"`.
It also converts `response.output_text.done` into the full text with
`merge_mode="replace"`. That snapshot replaces the corresponding accumulated
content; it is not a second answer. `AgentResponseUpdate.text` concatenates its
text contents without interpreting their merge modes.

#### Example

**Illustrative event sequence, reproduced offline with SDK content objects:**

1. Append `Hello` followed by a space.
2. Append `world`.
3. Replace the accumulated content with `Hello world`.

Printing every update's `.text` with no separator produces
`Hello worldHello world`. A terminal renderer that displays only new text can
print append contents and skip replacement snapshots when those snapshots
repeat the streamed text. A general renderer must instead honor replacements
per content item, since a replacement may revise earlier text.

#### Where it is used

- [Stage 10's stream and merge-mode-aware text printing](../ai-agents/microsoft-agent-framework/10_simple-maf-agent-streaming/app/simple-ai-agent-maf-agent-streaming.py#L84-L96).

#### Why it is used here

Streaming displays output before the whole response completes. Distinguishing
incremental text from final snapshots prevents the terminal from displaying
the entire answer twice. This diagnosis was checked against installed SDK
source and an offline reproduction; no paid model request was made. The terminal
loop now skips replacement snapshots and prints only incremental text. This
simple demo does not redraw earlier output if a provider revises a snapshot.

#### Common misunderstanding

`chunk.text` does not guarantee that its text has never appeared before.
Duplicated terminal output does not by itself prove two agent invocations.

#### References

- [Official Responses API streaming events](https://platform.openai.com/docs/api-reference/responses-streaming).
- [Microsoft Agent Framework source](https://github.com/microsoft/agent-framework) (compare with the installed version).

### Instructions versus user prompts

#### What it means

Instructions describe the agent's intended behavior; a user prompt is the task
for a particular run. Neither is Python code that creates files or invokes
external tools automatically. Model output is generated text, not guaranteed
compliance with every instruction.

#### Example

**Project excerpt; requires an already configured agent, unexecuted live:**

```python
# Ask this run's specific question and await its completed response.
response = await agent.run(
    "Explain what the Microsoft Agent Framework is in one sentence."
)
# Display the generated text after the run completes.
print(response.text)
```

The desired output is a short explanation, not a deterministic exact string.

#### Where it is used

- [Stage 02 behavior instructions](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L67-L68).
- [Stage 02 prompt and output](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L71-L77).
- [Stage 01's different instructions and same prompt](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L54-L62).

#### Why it is used here

Separating behavior from the run input makes it clear why both stages can answer
the same question even though their instruction wording differs.

#### Common misunderstanding

Stage 01 mentions generating MAF files in its instructions, but implements no
file-writing tool. Stage 02 implements no tools, MCP, retrieval, persistent
storage, streaming, or multi-agent workflow either. SDK support is not proof
that the application enables a capability.

#### References

- [Your first Agent Framework agent](https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent).
- [Python await](./python-concepts.md#await).

### Messages as structured conversation items

#### What it means

`Message` is the installed framework's structured representation of one chat
item. Its `role` identifies the author, such as `user`, `assistant`, `system`,
or `tool`; its `contents` sequence stores text or other supported content
objects. The `text` property joins the text content items. Optional
`author_name`, `message_id`, and `additional_properties` carry attribution and
local workflow metadata.

#### Example

**Project excerpt; it constructs a local object and does not call the model:**

```python
# Import the framework's message value object.
from agent_framework import Message

# Represent one human request with an explicit role and text content item.
user_message = Message(
    # Identify the speaker for this conversation item.
    role="user",
    # Store text in the content sequence used by the framework.
    contents=["Explain structured messages."],
)
```

The earlier string shorthand, `await agent.run("Explain structured messages.")`,
can still produce a response. The structured form makes the conversation
boundary explicit and leaves room for roles, mixed content, metadata, and
serialization. Those extensions require explicit application code and suitable
model/provider support.

#### Where it is used

- [Import `Message`](../ai-agents/microsoft-agent-framework/04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py#L16).
- [Construct the user message](../ai-agents/microsoft-agent-framework/04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py#L77).
- [Pass the message to the agent](../ai-agents/microsoft-agent-framework/04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py#L86).
- [Compare with stage 03's string input](../ai-agents/microsoft-agent-framework/03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py#L78).

#### Why it is used here

Stage 04 teaches the input data model while preserving stage 03's client,
agent, authentication, one-shot execution, and text output. A structured
message is useful when an application must distinguish human input from system
instructions or tool results, attach correlation metadata, or pass more than
one supported content item. It does not itself provide conversation memory:
history requires deliberate session reuse, and restart persistence requires a
separate storage strategy.

#### Common misunderstanding

`Message` is a local value object, not the model, a hosted agent resource, or a
durable database record. A bare string remains a valid run input in the
installed API, so constructing `Message` is not an exclusive requirement for
getting an answer. Likewise, a content object such as an image reference needs
compatible model/provider support and does not upload or authorize access by
itself.

#### References

- [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/).
<!-- markdownlint-disable-next-line MD013 -->
- [Microsoft Agent Framework source repository](https://github.com/microsoft/agent-framework) (installed APIs may differ from upstream).

### Short-term conversation sessions

#### What it means

`agent.create_session()` creates an `AgentSession` value that an application
can pass to later `agent.run(..., session=session)` calls. Reusing the same
session gives those runs a shared conversation context for the lifetime of the
configured workflow. The session is an application-held object; creating it
does not provision a hosted agent or automatically write a durable transcript.

#### Example

**Project excerpt; it requires a configured agent and makes live model calls:**

```python
# Create one local session for this conversation.
session = agent.create_session()
# Send the first turn through the session.
first_response = await agent.run(Message(role="user", contents=["List five facts about India."]), session=session)
# Reuse the same session so the follow-up can refer to the first turn.
second_response = await agent.run(Message(role="user", contents=["Summarize those facts."]), session=session)
```

The application controls the session lifetime. Creating a different session
isolates another conversation; omitting the session from a later run does not
select the earlier session. Context limits, history handling, and model token
cost still apply. Restart persistence, retention, user-to-session mapping, and
database storage require additional application design and are not supplied by
`create_session()` alone.

#### Where it is used

- [Create the short-term session](../ai-agents/microsoft-agent-framework/06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py#L106-L107).
- [Reuse the session for three messages](../ai-agents/microsoft-agent-framework/06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py#L109-L135).

#### Why it is used here

Stage 06 uses one session so the second prompt can refer to "those bullet
points" and the third can summarize "all the above information." The earlier
stages already supported the `Agent` and `Message` APIs; this stage activates
the session mechanism and makes its lifetime visible. This is short-term
conversation context, not long-term memory, retrieval, MCP, or an observability
store.

#### Common misunderstanding

Session support is an `Agent` capability, not a benefit exclusive to direct
construction or to a convenience factory. Both construction paths can create
an `Agent` that supports sessions when the installed SDK exposes that API.
Sharing a `FoundryChatClient` is not the same as sharing an `AgentSession`, and
sharing a session is not permission to access another user's data. The
application must choose the correct session boundary and persistence policy.

#### References

- [Agent Framework sessions documentation](https://learn.microsoft.com/en-us/agent-framework/agents/).
- [Microsoft Agent Framework source repository](https://github.com/microsoft/agent-framework) (installed APIs may differ from upstream).

## Tools and orchestration

Tools give a model a controlled way to request application-owned work. The
model proposes a tool call from the registered name and input schema; the
framework invokes the Python function and makes its result available for the
agent's response. The function is still application code, so its permissions,
side effects, validation, and error handling remain the application's
responsibility.

### Function tools and the `@tool` decorator

#### What it means

The installed `agent_framework.tool` decorator wraps a Python callable as a
`FunctionTool`. With `@tool`, the framework infers an input model and JSON
schema from the function signature. If no explicit description is supplied,
the decorated function's docstring becomes the tool description. The
`Agent(tools=[...])` argument registers that object with the agent; it does
not call the function during local construction.

#### Example

**Project excerpt; the live model request is not made by this excerpt:**

```python
# Register a callable function as a model-discoverable framework tool.
@tool
# The annotation supplies the input and result types used for tool metadata.
async def get_weather(location: str) -> str:
    """Get weather for a location."""
    # Return application data that the framework can pass back to the model.
    return f"Weather for {location}"

# Attach the tool to the local agent configuration.
agent = Agent(client=chat_client, tools=[get_weather])
# Start the run; the model may request the tool before producing final text.
response = await agent.run("What is the weather in London?")
```

In stage 05, the function returns randomized demo data rather than calling a
weather service. The `location: str` annotation supplies the input shape, the
docstring supplies the description, and the returned string is the tool result.
The model can select the tool because it is registered in `tools`; the Python
function is executed only when the framework's invocation flow receives a tool
request.

#### Where it is used

- [Import the decorator](../ai-agents/microsoft-agent-framework/05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py#L15-L17).
- [Declare and implement the decorated weather tool](../ai-agents/microsoft-agent-framework/05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py#L46-L67).
- [Register the tool with the agent](../ai-agents/microsoft-agent-framework/05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py#L93-L104).
- [Run the structured weather request](../ai-agents/microsoft-agent-framework/05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py#L106-L113).

#### Why it is used here

Stage 04 already creates a `Message`, runs an `Agent`, and prints model text.
Stage 05 adds an application action to that same run boundary. The decorator
removes the need to construct a separate schema object for this simple
signature, while the agent's tool list makes the function available to the
model. This is useful for operations such as looking up an order, querying a
permitted database, or calling a weather API, where the model should request
an application function instead of inventing the result.

The decorator is not the only supported construction path. The installed
`tool(...)` API also accepts an explicit `description`, a Pydantic or mapping
`schema`, approval settings, invocation limits, and a result parser. Those
options are SDK capabilities; this sample uses none of them. Likewise, stage
03's direct `Agent(...)` already accepted `tools`; stage 05 implements the
tool-registration path rather than adding a new agent class.

#### Common misunderstanding

Tool registration does not grant permissions, make arbitrary external systems
safe, or guarantee that a model will call the function. A compatible model and
provider must support tool calling, and the application must implement and
authorize the operation. This sample's weather function has no external side
effect and no live API; its randomized result is only a teaching stand-in.
Tool calling is also different from MCP: MCP can expose protocol-based tools
through a server, while this example registers a local Python callable.

#### References

- [Microsoft Agent Framework tool documentation](https://learn.microsoft.com/en-us/agent-framework/agents/tools/).
- [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/).
- [Python function annotations](https://docs.python.org/3/library/typing.html).

Composition connects separately configured components into an application.
An agent's behavior and its model connection can be configured independently.

### Explicit agent composition

#### What it means

**Dependency injection** means supplying an object that a component needs rather
than constructing that dependency internally. `Agent(client=...)` receives a
compatible chat client; instructions and optional execution components belong
to the agent configuration. This lets application code assemble behavior without
hardcoding the provider's client-construction or factory call in that assembly.

#### Example

**Illustrative design pattern, not implemented in the samples.** This helper
only constructs an agent; it does not invoke a model. It has not been executed.

```python
# Import the framework's local agent execution class.
from agent_framework import Agent

# Define a helper that receives a compatible client and returns a configured agent.
def build_support_agent(client) -> Agent:
    # Return an agent whose connection dependency is supplied by the caller.
    return Agent(
        # Use the caller's real adapter or protocol-compatible offline fake client.
        client=client,
        # Give this role a readable label.
        name="SupportAgent",
        # Configure role guidance independently of individual user requests.
        instructions="Explain support policies clearly; do not invent order status.",
    )
```

#### Where it is used

- [Stage 03 explicitly injects its client](../ai-agents/microsoft-agent-framework/03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py#L67-L74).
- [Stage 02 uses the client factory](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L64-L69).

#### Why it is used here

The constructor provides a composition point for role instructions and future
tools, middleware, or context providers. A caller could select a real adapter
or compatible fake client without changing role assembly, allowing offline
configuration/execution tests with a properly implemented fake. Separate agents
can also carry different roles using a shared client. Neither helper extraction,
fake-client tests, nor multiple roles are implemented in Stage 03.

#### Common misunderstanding

The preceding factory already creates the same `Agent` class. Direct
construction does not uniquely enable tools, streaming, sessions, or middleware;
those are agent capabilities accessible through either construction path.
Register tools explicitly, reuse a session explicitly for conversation context,
and configure persistence separately for durable state. Supplying a client does
not provision a hosted agent, and sharing a client is not sharing a session.

#### References

- [Agent Framework capabilities](https://learn.microsoft.com/en-us/agent-framework/agents/).
- [Tool mechanisms and provider support](https://learn.microsoft.com/en-us/agent-framework/agents/tools/).
- [Framework source repository](https://github.com/microsoft/agent-framework).

Constructor and factory behavior was verified from the installed Stage 03
environment (`agent-framework` 1.21.0, Python 3.12.3) on 2026-10-13. The README's
[technical comparison](../ai-agents/microsoft-agent-framework/03_simple-maf-agentclass/README.md#why-this-stage-adds-agent)
connects these principles to supported extension APIs and their sample status.

## MCP connections

MCP separates the agent's tool client from a server that implements operations.

### Stdio server lifecycle

#### What it means

`MCPStdioTool` connects to a local server subprocess using standard input/output.
Entering its async context launches the process and discovers tools; registering
the adapter with the agent makes those tools available for model-selected calls.
Exiting the context cleans up the connection and subprocess. This protocol does
not itself provide memory or grant permissions.

#### Example

**Illustrative lifecycle excerpt; assumes the adapter is already configured:**

```python
# Start the configured MCP server and initialize its protocol connection.
async with azure_mcp:
    # Keep this scope open while the agent uses the server's tools.
    print("MCP connection initialized")
```

The stage 08 connection was smoke-tested through startup, tool discovery, and
cleanup without invoking tools, making model requests, or operating on Azure resources.

#### Where it is used

- [Configure and enter the stage 08 MCP connection](../ai-agents/microsoft-agent-framework/08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py#L128-L144).
- [Register local and MCP tools](../ai-agents/microsoft-agent-framework/08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py#L164-L165).

#### Why it is used here

Stage 08 adds Azure operations through an external server while retaining its
existing local weather function and file-memory provider.

#### Common misunderstanding

The Python `mcp` package supplies client support, not the Azure server executable.
Framework 1.23.0 also requires `tenacity` for MCP subscription recovery; stage 08
declares both optional dependencies explicitly using the framework's version ranges.
The subprocess has its own authentication context; it does not receive the
Python credential object. See [Azure MCP launch configuration](./azure-concepts.md#azure-mcp-server-launch).

#### References

- [Official Agent Framework MCP tools guide](https://learn.microsoft.com/en-us/agent-framework/agents/tools/).
- [MCP standard transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).
