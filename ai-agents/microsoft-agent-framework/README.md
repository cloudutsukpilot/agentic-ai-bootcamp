# Microsoft Agent Framework — return-to-learning recap

Use this page when returning after a break. It summarizes the learning stages in
this folder, not a transcript of earlier chat sessions. For complete setup and
deeper explanations, follow the linked sample READMEs and concept guides.

## Start here: the two-minute recap

1. **Client connects; agent coordinates.** The client communicates with the model
   service. The local `Agent` combines that client with instructions and any
   configured tools or memory providers.
2. **Instructions are reusable behavior; a prompt is this run's request.**
   Naming an agent or describing an action does not implement that action.
3. **`as_agent(...)` and `Agent(client=...)` create the same kind of agent.**
   Direct construction exposes the composition boundary; it does not unlock
   otherwise unavailable tools or memory.
4. **`Message` makes input structure explicit.** `role` identifies the speaker;
   `contents` carries the input. A message is not a memory store.
5. **Tools let the model request application code.** `@tool` exposes a function;
   `tools=[...]` registers it. The framework executes requested tool calls and
   returns results to the model. Registration alone does not guarantee a call.
6. **Reusing a session preserves conversation context.** Stage 06 passes the
   same session to three runs so follow-up requests can refer to earlier turns.
7. **Persistent memory needs storage.** Stage 07 shares disk-backed memory across
   fresh sessions. Only saved information persists—not automatically every chat.
8. **Folder names are not proof of implementation.** Stage 08 does not yet use
   MCP; stage 09 is a placeholder.

## Learning map: what changed at each stage?

| Stage | Main API or change | Why it matters | Current status |
| --- | --- | --- | --- |
| [01 — Azure OpenAI](./01_simple-maf-openai/README.md) | `OpenAIChatClient` → `as_agent(...)` → `run(...)` | Establishes a single prompt/response using an Azure OpenAI endpoint and API key. | Implemented |
| [02 — Foundry](./02_simple-maf-foundary/README.md) | `FoundryChatClient` + async `DefaultAzureCredential` | Changes service access to a Foundry project and Entra authentication; the basic agent interaction stays similar. | Implemented |
| [03 — Agent class](./03_simple-maf-agentclass/README.md) | `Agent(client=chat_client, ...)` | Makes the client/agent composition explicit, useful when separating connection setup from agent configuration. | Implemented; same agent capabilities as the factory |
| [04 — Message class](./04_simple-maf-messageclass/README.md) | `Message(role="user", contents=[...])` | Represents speaker and content explicitly instead of passing only a string. | Implemented; one text content item |
| [05 — Tool decorator](./05_simple-maf-tool-decorator/README.md) | `@tool` + `tools=[get_weather]` | Lets the model request a Python function to obtain information beyond generated text. | Implemented; simulated weather only |
| [06 — Short-term memory](./06_simple-maf-short-term-memory/README.md) | `create_session()` + `run(..., session=...)` | Makes related turns share context so “those bullet points” refers to the earlier answer. | Implemented; in-process conversation |
| [07 — Long-term memory](./07_simple-maf-long-term-memory/README.md) | `FileMemoryProvider` + `FileSystemAgentFileStore` | Lets fresh sessions access durable facts and preferences saved in files. | Implemented; local file-backed demo |
| [08 — MCP source](./08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py) | Currently repeats stage 07's memory pattern | A future protocol-based tool integration needs actual MCP client/server wiring. | No MCP integration yet |
| [09 — A2A source](./09_simple-maf-A2A/app/simple-ai-agent-maf-a2a.py) | Comment-only placeholder | Agent-to-agent integration remains future work. | Not implemented |

These are separate runnable learning folders, not successive edits to one app.
Stage numbering is not an SDK version or model version.

## Stage-by-stage memory joggers

### 01–02: connect to the service, then run the agent

- **Execution order:** read configuration → construct client → construct local
  agent → await `agent.run(...)` → print `response.text`.
- Stage 01 uses an API key and an Azure OpenAI resource endpoint. Stage 02 uses a
  Foundry project endpoint and an asynchronous Entra credential.
- Authentication proves identity; authorization/RBAC determines what that
  identity may access. Constructing `DefaultAzureCredential` does not grant access.
- Constructing the local agent does not deploy or register a hosted Foundry agent.
- The samples send hard-coded prompts, print completed text, and exit. They are
  not interactive chat loops, streaming apps, or file generators.

**Revisit:** [stage 01 source](./01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py),
[stage 02 source](./02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py),
[client versus agent](../../docs/ai-concepts.md#foundry-client-versus-local-agent),
[Azure identity and cleanup](../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).

### 03–04: make agent composition and message structure explicit

- `Agent(client=chat_client, ...)` makes it clear which object supplies model
  communication and which object supplies the agent's behavior.
- A reusable builder could accept a compatible client from outside, but stage 03
  does not itself add builders, fake-client tests, or multiple agents.
- `Message(role="user", contents=[...])` packages input as a structured item.
  This is useful when working with explicit speakers or richer conversation data.
- The current stage 04 still sends a single text request. Structured input does
  not automatically enable multimodal input, conversation storage, or persistence.

**Revisit:** [stage 03 source](./03_simple-maf-agentclass/app/simple-ai-agent-maf-agentclass.py),
[stage 04 source](./04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py),
[explicit composition](../../docs/ai-concepts.md#explicit-agent-composition),
[message structure](../../docs/ai-concepts.md#messages-as-structured-conversation-items).

### 05: let the model request a local function

- `get_weather(location: str) -> str` accepts a location and returns text.
  Its signature and docstring help describe the tool's inputs and purpose.
- `@tool` exposes the function to the framework; `tools=[get_weather]` attaches
  it to this agent. These are different responsibilities.
- **Possible run flow:** user asks about weather → model requests the tool →
  framework calls Python → tool result returns to the model → final answer.
- The function generates random conditions and temperature. **It does not query
  a weather service.** Its output must not be treated as real weather information.
- Tools run with the application's permissions. A real integration would need
  appropriate validation, access controls, error handling, and side-effect review.

**Revisit:** [stage 05 source](./05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py)
and [function tools](../../docs/ai-concepts.md#function-tools-and-the-tool-decorator).

### 06: remember earlier turns within one conversation

- Create `agent_session` once with `agent.create_session()`.
- Pass it to all three calls through `session=agent_session`.
- The sequence is: five bullet points about India → add descriptions to those
  points → summarize the information. Later turns depend on earlier context.
- The weather tool remains registered, but these prompts do not demonstrate
  weather-tool use.
- A fresh session starts a separate conversation. This sample does not save the
  session to durable storage; restarting the script loses its conversation state.
- More history can increase the input context and token cost; memory is not free
  or unlimited.

**Revisit:** [stage 06 source](./06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py)
and [short-term sessions](../../docs/ai-concepts.md#short-term-conversation-sessions).

### 07: remember selected facts across fresh sessions

- `FileSystemAgentFileStore(root_directory=MEMORY_DIR)` supplies disk storage.
- `FileMemoryProvider(store=memory_store, scope=USER_ID)` supplies file-memory
  tools and instructions. `context_providers=[memory_provider]` connects it to
  the agent's run lifecycle.
- The shared scope is `demo_user`; files live under the sample's
  [memory store](./07_simple-maf-long-term-memory/app/memory_store/).
- **Session A** shares a name, vegetarian preference, and short-answer preference.
  The model is instructed to save durable facts using its memory tools.
- **Session B** is fresh but asks for a personalized greeting and dinner idea.
  It can use the shared files rather than session A's conversation history.
- **Session C** asks about past conversations. Saved preferences are not a full
  transcript: the sample has no conversation-history persistence provider.
- Files survive a restart if written, but actual saving and recall depend on
  tool use. Inspect the files rather than assuming a successful memory write.
- This is a learning demo, not production user isolation: the user scope is fixed
  and local files are plaintext. Do not store secrets or sensitive personal data.
  Removing saved memory files resets durable facts; a new session alone does not.

**Revisit:** [stage 07 source](./07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py)
and [its detailed README](./07_simple-maf-long-term-memory/README.md).

## Do not confuse these capabilities

| Concept | What it provides here | What it does not automatically provide |
| --- | --- | --- |
| Client | Model-service communication | A deployed agent or stored conversation |
| Agent | Local coordination of instructions, client, and configured extensions | Permission to access Azure resources |
| Message | Explicit speaker/content structure | Conversation memory |
| Local tool | Model-requested Python execution | Live external data unless the function fetches it |
| Session | Context shared across related runs | Restart persistence in stage 06 |
| File memory | Durable facts saved/read through memory tools | A complete chat transcript or vector-search/RAG pipeline |
| MCP — planned | Protocol-based access to external tools/resources | Automatic conversation memory; no MCP wiring exists here yet |
| A2A — planned | Agent-to-agent communication | An implemented workflow just because a folder exists |

No current stage configures streaming, a retrieval/RAG pipeline, multi-agent
orchestration, or Application Insights telemetry export. SDK support is not the
same as a capability enabled in these scripts.

## Restart checklist

1. Pick one stage and open its README. Use that folder's own dependency manifest
   and Python environment, not an unrelated environment from another sample.
2. In VS Code, select the intended stage's virtual-environment interpreter.
   Dependencies are unpinned: reinstalling later can produce different SDK APIs.
3. Check configuration privately. Each implemented script reads a local
   configuration file beside itself; a **nonempty process environment value wins**
   over the file. `dotenv_values(...)` parses settings; it does not export them.
4. Stage 01 requires `AZURE_OPENAI_MODEL`, `AZURE_OPENAI_ENDPOINT`, and
   `AZURE_OPENAI_API_KEY`. Here `MODEL` identifies the deployment to call.
5. Stages 02–07 require `FOUNDARY_MODEL` and `FOUNDARY_PROJECT_ENDPOINT`, plus a
   usable Entra identity with the required permissions. Keep the code's existing
   `FOUNDARY_*` spelling even though the service name is **Foundry**.
6. Do not substitute an Azure OpenAI resource endpoint for a Foundry project URL.
   See [endpoints and deployments](../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments).
7. Read the hard-coded prompt before running. Awaited runs contact the remote
   service and may incur charges; tool use can add model interactions. Output is
   generated, not a deterministic expected string.
8. For stage 07, remember that old memory files affect later runs. Never commit
   credentials or sensitive memory content.
9. Test folders are placeholders, not evidence of a working automated test suite.
   A printed answer also does not prove tools were called or facts were persisted.

## Quick self-check before moving on

- Can I explain the difference between the client and the agent?
- Can I explain why direct `Agent(...)` construction is not a new capability?
- Can I distinguish instructions, a user `Message`, and a session?
- Can I trace a tool request from the model to Python and back?
- Can I explain why stage 06 loses context after restart but stage 07 can keep facts?
- Can I explain why saved facts cannot reliably reconstruct every past conversation?
- Can I identify which stages are implemented without relying on their names?

If these answers feel clear, continue with the MCP implementation rather than
re-reading every earlier file.

## Deeper reference shelf

Keep detailed definitions in the canonical guides; this page is a revision index.

- **Python/runtime:** [Python concepts](../../docs/python-concepts.md), especially
  [event loops](../../docs/python-concepts.md#event-loop),
  [`await`](../../docs/python-concepts.md#await), and
  [async context managers](../../docs/python-concepts.md#async-context-managers).
- **Agent/framework:** [AI concepts](../../docs/ai-concepts.md) for client/agent
  roles, instructions, messages, tools, composition, and short-term sessions.
- **Azure/services/identity:** [Azure concepts](../../docs/azure-concepts.md) for
  Foundry endpoints, deployments, credentials, permissions, and cleanup.
- **Official:** [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/),
  [framework source](https://github.com/microsoft/agent-framework),
  [Azure Identity](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python),
  and [Python asyncio](https://docs.python.org/3/library/asyncio.html).

Treat online examples as version-dependent. Check the selected environment and
the sample source before adopting an API from newer documentation.
