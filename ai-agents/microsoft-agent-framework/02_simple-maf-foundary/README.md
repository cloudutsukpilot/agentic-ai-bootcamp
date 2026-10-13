# Stage 02 — a simple MAF agent through Microsoft Foundry

## Overview and sample identity

Run one fixed prompt through a locally constructed Microsoft Agent Framework
agent, using a deployed model in a Microsoft Foundry project. Learn project
configuration, token-based authentication, and asynchronous resource cleanup.
The folder keeps its historical `foundary` spelling; the SDK uses **Foundry**.

| Item | This sample |
| --- | --- |
| Learning stage | 02, following [stage 01](../01_simple-maf-openai/README.md) |
| Framework | Microsoft Agent Framework (MAF), running in this Python process |
| Hosting service | Microsoft Foundry project; model vendor/family depends on your deployment |
| Client/API | `agent_framework.foundry.FoundryChatClient`, project-backed OpenAI Responses API |
| Authentication | Async `azure.identity.aio.DefaultAzureCredential`; authorization is separate |
| Agent | Local `Agent` returned by `client.as_agent(...)`, not a provisioned hosted agent |
| Input/output | Fixed one-sentence explanation prompt; prints `response.text` |

## Why stage 02 follows stage 01

| Previous stage/topic | Current stage | Practical reason for the change |
| --- | --- | --- |
| [Stage 01 `OpenAIChatClient(...)`](../01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L40-L48) receives an Azure OpenAI resource endpoint and API key. | [Stage 02 `FoundryChatClient(...)`](app/simple-ai-agent-maf-foundary.py#L51-L62) receives a project endpoint and async token credential. | Learn which adapter and configuration belong to Foundry project inference, without embedding a service API key in this sample. |
| [Stage 01 `client.as_agent(...)` and `agent.run(...)`](../01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L50-L62) already create and run a local agent. | [Stage 02 keeps that agent/run boundary](app/simple-ai-agent-maf-foundary.py#L63-L75), inside managed client lifetimes. | Change the service-access boundary while retaining a familiar agent execution path; explicitly close the transports this sample creates. |

### What the previous stage already did

Stage 01 already sent the same fixed user prompt and printed a model-generated
explanation. Its client owned model communication; its local agent carried its
name and instructions. It did not actually generate files despite its instruction
wording. Foundry is **not required** just to obtain a similar answer.

### What this stage adds

`FoundryChatClient` connects through a Foundry project rather than a standalone
Azure OpenAI resource endpoint. `DefaultAzureCredential` supplies Entra access
tokens when requested, instead of passing a service API key. Nested `async with`
scopes close the credential, Azure project client, and OpenAI HTTP client.

Construction paths (arrows describe local setup, not extra network requests):

```text
Previous: OpenAIChatClient(resource endpoint, API key) -> as_agent(...) -> agent -> run(prompt)
Current:  FoundryChatClient(project endpoint, credential) -> as_agent(...) -> agent -> run(prompt)
```

In both paths `as_agent(...)` hides direct `Agent(...)` construction. The installed
SDK's factory returns an `Agent` with `client=self`. The client talks to the model;
the agent owns local behavior and orchestration; the awaited `run` initiates the
model interaction. Neither the factory nor client construction deploys an agent.

### What does not change

Both use MAF, `as_agent`, the exact same user prompt, one non-streaming run, and
text output. Neither sample explicitly reuses a conversation session or adds
persistent storage. The system instructions and agent name differ in stage 02.
The model deployment is independently configured, so identical model/output or
cost cannot be assumed. Both live runs require network access and may incur
charges; exact request details depend on the adapter and SDK.

### Why this matters

If stage 02 were removed, stage 01 could still answer the prompt with an
appropriate Azure OpenAI deployment. What would be lost is this demonstration
of project-backed inference, Entra credentials, and explicit cleanup. Later,
the same local agent boundary can accept tools or reused sessions, but those
features are not enabled here. [Stage 03](../03_simple-maf-agentclass/README.md)
makes direct `Agent(...)` construction visible as a separate learning step.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Single local agent and fixed prompt | Implemented | [Factory, run, and output](app/simple-ai-agent-maf-foundary.py#L63-L77) |
| Foundry project inference / Entra credential | Implemented | [Client setup](app/simple-ai-agent-maf-foundary.py#L44-L62) |
| Local tools / MCP | Not implemented | No tool registration or MCP connection |
| Reused short-term conversation memory | Not implemented | One run; no explicit session creation/reuse |
| Persistent memory / retrieval or RAG | Not implemented | No storage or retrieval provider |
| Streaming / multi-agent orchestration | Not implemented | Awaits one completed result |
| Application Insights instrumentation | Not implemented | No telemetry setup/exporter in application code; SDK internals are separate |
| Hosted agent provisioning | Not implemented | This is direct model inference, not `FoundryAgent` |

## Folder contents

| Item | Purpose |
| --- | --- |
| [app/simple-ai-agent-maf-foundary.py](app/simple-ai-agent-maf-foundary.py) | Script and required-setting helper |
| [requirements.txt](requirements.txt) | This sample's unpinned dependencies |
| [README.md](README.md) | Setup and learning notes |
| tests folder | Currently empty placeholder, not a test suite |
| app-local dotenv file | Optional private configuration you create; not a shipped example |
| Local virtual environment / bytecode | Generated artifacts, not sample source |

## Frameworks and libraries

Observed on **2026-10-13**, using this sample's Linux virtual-environment
interpreter, Python **3.12.3**. These are installed versions, not pins or a
guarantee that a fresh install will resolve identically.

| Package / library | Import / purpose | Observed version / reference |
| --- | --- | --- |
| `agent-framework` | MAF umbrella package | 1.21.0; [official documentation](https://learn.microsoft.com/en-us/agent-framework/) |
| `agent-framework-core` | Core agent factory/orchestration dependency | 1.21.0, transitively installed |
| `agent-framework-foundry` | `agent_framework.foundry.FoundryChatClient` | 1.14.1; [Foundry provider](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python) |
| `azure-identity` | Async `DefaultAzureCredential` | 1.26.0; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) |
| `python-dotenv` | `dotenv.dotenv_values` parses a settings dictionary | 1.2.4; [library documentation](https://bbc2.github.io/python-dotenv/) |
| Python standard library | `asyncio` runs coroutines; `os` reads environment; `Path` locates configuration | [asyncio](https://docs.python.org/3/library/asyncio.html), [os.getenv](https://docs.python.org/3/library/os.html#os.getenv), [pathlib](https://docs.python.org/3/library/pathlib.html) |

The installed framework packages declare Python **>=3.10**. This sample's
manifest sets no upper bound and does not certify every Python version. Current
online documentation may differ from these installed APIs.

## How it works

1. [Parse the app-local dotenv file](app/simple-ai-agent-maf-foundary.py#L22-L24)
   relative to the script, not the shell's working directory. File values are
   not exported into the process environment.
2. [Look up required settings](app/simple-ai-agent-maf-foundary.py#L27-L37): a
   nonempty environment value wins, then the file value; missing/empty values
   raise `ValueError` before client or credential construction.
3. [Create the async credential and client](app/simple-ai-agent-maf-foundary.py#L49-L62).
   Construction is local; credential creation neither signs in nor grants access.
4. [Create the local agent](app/simple-ai-agent-maf-foundary.py#L63-L69), giving
   behavior instructions separately from the user prompt.
5. [Await the fixed prompt and print the text](app/simple-ai-agent-maf-foundary.py#L71-L77).
   `await` permits cooperative waiting; it does not start a thread.
6. Exit the nested scopes to close the HTTP/project clients and credential,
   including on errors. [The entry guard](app/simple-ai-agent-maf-foundary.py#L78-L82)
   runs `main` only when the script is launched directly.

## Prerequisites and setup

- Python >=3.10 compatible with the resolved dependencies; verified here with 3.12.3.
- An existing Foundry project and model deployment supporting the Responses API.
  The script does not create either resource.
- An authenticated identity available to `DefaultAzureCredential`, with permission
  to invoke that deployment. Authentication and Foundry authorization/RBAC are
  separate; obtain the appropriate access from your administrator.
- HTTPS access to the configured service and identity endpoints for a live run.

**Linux, zsh or bash; start in the repository root.** The following setup commands
are instructional, not executed during this documentation update. Installation
downloads packages; use this sample's manifest rather than another stage's.

```sh
cd ai-agents/microsoft-agent-framework/02_simple-maf-foundary
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

In VS Code select this sample's virtual-environment Python interpreter. The
system interpreter may not have its packages. No activation is needed for the
explicit interpreter commands shown here.

## Configuration

| Setting | Required? | Meaning / precedence |
| --- | --- | --- |
| `FOUNDARY_MODEL` | Yes | Actual deployment name, not an agent ID or necessarily a model family name |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | Project URL, not a standalone Azure OpenAI resource endpoint or full Responses API URL |

Both settings use nonempty process environment first, then the app-local dotenv
dictionary. Empty environment values fall back to the file. Whitespace-only
values are not rejected. The helper checks presence, not URL format or deployment
availability. Create a private file named `.env` beside the entry script or set
the two variables in the process launching it. Placeholder-only file contents:

```dotenv
FOUNDARY_MODEL=<your-model-deployment-name>
FOUNDARY_PROJECT_ENDPOINT=https://<your-account>.services.ai.azure.com/api/projects/<your-project>
```

Keep the literal **`FOUNDARY_*`** names: they are this sample's compatibility
names, passed explicitly as `model` and `project_endpoint`. SDK documentation
uses `FOUNDRY_*`; setting only those SDK names does not satisfy this helper.
`FOUNDARY_ENDPOINT` is not read by this script.

No service API key is read here. Credential sources depend on the environment
and installed Azure Identity version. A developer sign-in can be a source;
creating `DefaultAzureCredential` alone is not a sign-in operation. The parsed
dotenv dictionary is not exported, so putting identity environment variables
only in that file does not configure environment-based credentials.

## Run and expected output

**Linux, zsh or bash; working directory: the stage 02 sample folder after setup.**
This is a live, potentially billable model call; it was not run for documentation.

```sh
./.venv/bin/python app/simple-ai-agent-maf-foundary.py
```

There is no interactive input or command-line prompt argument. The prompt is
`Explain what the Microsoft Agent Framework is in one sentence.` Successful
completion prints generated text and exits normally; unhandled configuration,
identity, or service errors produce a traceback and nonzero exit. A one-sentence
explanation is illustrative expected output, not an observed live result or
guaranteed exact text. Model output is nondeterministic.

## Validation and troubleshooting

Offline checks for this update used the sample interpreter: comment placement,
AST/syntax preservation, imports and installed signatures, required-setting
precedence/errors, and mocked main execution/cleanup. These checks do not prove
deployment availability, permissions, or a live response. Local documentation
links/anchors and cited source ranges were checked separately. The tests folder
is empty; no existing automated test suite is claimed. No standalone `pyright`
or `mypy` is installed in this environment, and no runnable `ty` command was
available. Editor `ty` diagnostics currently report three unresolved imports
while searching system site-packages; all three imports succeed with the sample
interpreter. Static type validation therefore remains incomplete. Select/configure
this sample's environment for the checker; editor settings were not changed.

**Linux, repository root:** the repeatable comment-check command is:

```sh
./ai-agents/microsoft-agent-framework/02_simple-maf-foundary/.venv/bin/python .github/skills/python-learning-comments/scripts/check_comments.py ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py
```

| Symptom | Check |
| --- | --- |
| Missing required Foundry setting | Exact `FOUNDARY_*` spelling, app-local file placement, and empty values |
| Import error / unresolved editor import | Select this sample's interpreter and install its own manifest |
| Credential unavailable / authentication failure | Available credential source and its sign-in/configuration; never print tokens |
| Service permission error | Identity's authorization to the project/deployment, independently of authentication |
| Endpoint / deployment / API error | Project URL, actual deployment name, Responses compatibility, and installed SDK version |
| Rate limit / quota / network failure | Service limits, connectivity, retry guidance; this script adds no custom recovery |

## Learning links and progression

- Python: [required-setting helpers](../../../docs/python-concepts.md#helper-functions-and-required-settings),
  [await](../../../docs/python-concepts.md#await),
  [async context managers](../../../docs/python-concepts.md#async-context-managers).
- AI: [client versus local agent](../../../docs/ai-concepts.md#foundry-client-versus-local-agent),
  [instructions versus prompts](../../../docs/ai-concepts.md#instructions-versus-user-prompts).
- Azure: [project configuration](../../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments),
  [async credentials and cleanup](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).

Keep lessons in separate folders. Existing next-stage topics are
[direct Agent construction](../03_simple-maf-agentclass/README.md),
[messages](../04_simple-maf-messageclass/app/simple-ai-agent-maf-messageclass.py),
[local tools](../05_simple-maf-tool-decorator/app/simple-ai-agent-maf-tool-decorator.py),
[short-term memory](../06_simple-maf-short-term-memory/app/simple-ai-agent-maf-short-term-memory.py),
[long-term memory](../07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py),
and [MCP](../08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py).
These links identify learning topics, not certification of sibling implementations
or capabilities in stage 02. Tools add callable actions; sessions allow history
reuse; persistent storage addresses restart retention; MCP supplies protocol-based
tools, **not conversation memory**. These are future extensions for this sample.

This is a learning script, not a production deployment: no interactive loop,
custom recovery, persistent memory, hosted agent lifecycle, or application
telemetry configuration is implemented.
