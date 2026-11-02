# Simple Foundry Agent - Pydantic AI

<!-- markdownlint-configure-file {"MD013": false} -->

This is the second learning stage in the Pydantic AI course. It keeps the
one-prompt agent from stage 01 but reaches the model through a **Microsoft
Foundry project** using **Entra ID** (`DefaultAzureCredential`) instead of an
API key. It is the counterpart of the
[Microsoft Agent Framework stage 02](../../microsoft-agent-framework/02_simple-maf-foundary/README.md).

## Overview and sample identity

| Dimension | This stage |
| --- | --- |
| Learning objective | Authenticate with Entra ID and call a Foundry project deployment |
| Framework | Pydantic AI (`pydantic-ai-slim`) |
| Model provider | Microsoft Foundry project with a deployed model |
| Provider / model classes | `AIProjectClient.get_openai_client()` → `OpenAIProvider` → `OpenAIResponsesModel` |
| Authentication | Async `DefaultAzureCredential` (Entra ID bearer tokens) |
| Input | One hard-coded text prompt |
| Output | `response.output` |
| Current status | Implemented one-shot prompt/response |

## Previous implementation and technical delta

Stage 01 built an `AzureProvider` from an API key. Pydantic AI has no
Foundry-specific provider, so this stage asks the Azure AI Projects SDK for an
OpenAI client that is already authenticated for the project, then hands that
client to Pydantic AI's generic `OpenAIProvider`.

| Previous stage | This stage | Reason for the change |
| --- | --- | --- |
| [`AzureProvider(azure_endpoint=..., api_key=...)`](../01_simple-pydanticai-openai/app/simple-ai-agent-pydanticai-azopenai.py#L47-L53) | [`AIProjectClient(...).get_openai_client()`](app/simple-ai-agent-pydanticai-foundary.py#L56-L66) | Use a Foundry project endpoint and Entra ID instead of a shared secret key. |
| `OpenAIResponsesModel(..., provider=AzureProvider(...))` | [`OpenAIResponsesModel(..., provider=OpenAIProvider(openai_client=...))`](app/simple-ai-agent-pydanticai-foundary.py#L67-L75) | Reuse the project's authenticated client; the agent and run call are unchanged. |

This mirrors what MAF's `FoundryChatClient` does internally: it also creates an
`AIProjectClient` and calls `get_openai_client()`. The difference is that this
Pydantic AI sample makes those steps visible.

`get_openai_client()` returns an `AsyncOpenAI` client whose base URL is the
project endpoint plus `/openai/v1` and whose "API key" is a token provider that
requests Entra tokens for the `https://ai.azure.com/.default` scope. Tokens are
requested when the first model call happens, not at construction.

### What remains the same

The prompt, the `Agent(...)` construction, `await agent.run(...)`, and printing
`response.output` are the same as stage 01. In MAF, stage 02 used the
`client.as_agent(...)` factory; Pydantic AI has no such factory, so this stage
passes the model straight into `Agent(...)`.

## Capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Single local agent and fixed prompt | Implemented | One `Agent` and one run |
| Entra ID authentication | Implemented | `DefaultAzureCredential` passed to `AIProjectClient` |
| Hosted Foundry agent | Not implemented | The agent object is local; nothing is created in Foundry |
| Tools, MCP, memory, streaming | Not implemented | Added in stages 05–10 |

## How it works

1. [`dotenv_values`](app/simple-ai-agent-pydanticai-foundary.py#L29-L31) reads
   the shared `.env` file, and [`required_setting`](app/simple-ai-agent-pydanticai-foundary.py#L34-L44)
   validates each value (environment first, then file).
2. [`model_name` and `project_endpoint`](app/simple-ai-agent-pydanticai-foundary.py#L50-L54)
   are read using the course's `FOUNDARY_*` names.
3. [One `async with` statement](app/simple-ai-agent-pydanticai-foundary.py#L56-L66)
   enters three context managers in order: the credential, the project client
   (which needs the credential), and the OpenAI client (which comes from the
   project client). Leaving the block closes them in reverse order.
4. [`Agent(...)`](app/simple-ai-agent-pydanticai-foundary.py#L67-L75) receives
   an `OpenAIResponsesModel` wired to that OpenAI client.
5. [`await agent.run(...)`](app/simple-ai-agent-pydanticai-foundary.py#L77-L81)
   triggers token acquisition and the model request, then prints the output.

## Folder contents

```text
02_simple-pydanticai-foundary/
├── README.md
└── app/
    └── simple-ai-agent-pydanticai-foundary.py
```

Dependencies are in the shared [requirements.txt](../requirements.txt);
configuration is in the shared, private `ai-agents/pydantic-framework/.env`.

## Frameworks and libraries

Observed on **2026-11-02**, shared environment, Python **3.12.3**.

| Package / library | Purpose in this sample | Observed version / reference |
| --- | --- | --- |
| `pydantic-ai-slim[openai]` | `Agent`, `OpenAIResponsesModel`, `OpenAIProvider` | 2.64.0; [OpenAI models](https://pydantic.dev/docs/ai/models/openai/) |
| `azure-ai-projects` (import `azure.ai.projects.aio`) | `AIProjectClient` and its `get_openai_client()` | 2.10.0; [Azure AI Projects client library](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python) |
| `azure-identity` (import `azure.identity.aio`) | Async `DefaultAzureCredential` | 1.27.0; [credential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python) |
| `aiohttp` | Async HTTP transport needed by the `.aio` Azure clients | 3.14.5 |
| `python-dotenv` | Parses the shared `.env` file | 1.2.4 |

## Prerequisites and setup

- The shared environment from the [course recap](../README.md#shared-environment-setup).
- A Foundry project with a deployed model that supports the Responses API.
- An identity that `DefaultAzureCredential` can find (for local work, usually
  `az login`) **and** a role on the project that allows model inference, such as
  *Azure AI User*. Signing in proves who you are; the role decides what you may do.

## Configuration

Set these in `ai-agents/pydantic-framework/.env` (see [`.env.example`](../.env.example)):

| Setting | Required? | Meaning |
| --- | --- | --- |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | Project URL, such as `https://<resource>.services.ai.azure.com/api/projects/<project>` |
| `FOUNDARY_MODEL` | Yes | Deployment name in that project |

The `FOUNDARY_*` spelling is intentional and matches the MAF stages, so one set
of values works for both courses. Do not use an Azure OpenAI resource endpoint
here; see [endpoints and deployments](../../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments).

## Run and expected output

**Linux, zsh or bash; working directory: `ai-agents/pydantic-framework`.** Live,
potentially billable request; not run while writing this README:

```sh
./.venv/bin/python 02_simple-pydanticai-foundary/app/simple-ai-agent-pydanticai-foundary.py
```

Prints one generated sentence. Credential, permission, or network problems end
the process with a traceback and a nonzero exit code.

## Exercises to try

1. Run `az logout` and run the script again to see which credential sources
   `DefaultAzureCredential` tried before failing. Run `az login` afterwards.
2. Temporarily set `FOUNDARY_MODEL` to a name that does not exist and observe
   the error: authentication succeeded, but the deployment lookup failed.

## Validation and troubleshooting

No test folder exists for this stage. Run the comment checker from the
repository root with `ai-agents/pydantic-framework/.venv/bin/python`
(see [stage 01](../01_simple-pydanticai-openai/README.md#validation-and-troubleshooting)).

| Symptom | First check |
| --- | --- |
| `Missing required Foundry setting` | Exact `FOUNDARY_*` names in the shared `.env` |
| `CredentialUnavailableError` | Sign in with `az login` or another supported source |
| 401 / 403 | Your identity's role assignment on the Foundry project |
| 404 | Endpoint is a project URL and `FOUNDARY_MODEL` is a deployment in that project |

## Learning links and progression

- [AI concepts: Pydantic AI provider, model, and agent](../../../docs/ai-concepts.md#pydantic-ai-provider-model-and-agent)
- [Azure concepts: Foundry project OpenAI client](../../../docs/azure-concepts.md#foundry-project-openai-client)
- [Azure concepts: async credentials and resource cleanup](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup)
- [Python concepts: async context managers](../../../docs/python-concepts.md#async-context-managers)

Next, [stage 03](../03_simple-pydanticai-agentclass/README.md) separates the
provider, model, and agent into named variables to make the composition explicit.
