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
  - [Explicit agent composition](#explicit-agent-composition)

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
- [Microsoft Agent Framework source](https://github.com/microsoft/agent-framework) (upstream may differ from installed versions).
- [Project endpoints and deployments](./azure-concepts.md#foundry-project-endpoints-and-deployments).

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
response = await agent.run("Explain what the Microsoft Agent Framework is in one sentence.")
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
