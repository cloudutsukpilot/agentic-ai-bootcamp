# Azure concepts — Foundry access and identity

<!-- markdownlint-configure-file {"MD024": {"siblings_only": true}} -->

This guide owns Azure configuration and access. Read [AI concepts](./ai-concepts.md)
for client/agent responsibilities and [Python concepts](./python-concepts.md)
for language syntax. Stage 02 facts were checked on 2026-10-13 against installed
`agent-framework-foundry` 1.14.1 and `azure-identity` 1.26.0.

## Contents

- [Foundry services](#foundry-services)
  - [Foundry project endpoints and deployments](#foundry-project-endpoints-and-deployments)
- [Identity and access](#identity-and-access)
  - [Async credentials and resource cleanup](#async-credentials-and-resource-cleanup)

## Foundry services

Choose configuration for the actual service-access pattern; a project endpoint
and a standalone Azure OpenAI resource endpoint are not interchangeable.

### Foundry project endpoints and deployments

#### What it means

A Foundry project endpoint identifies the project, for example
`https://<your-account>.services.ai.azure.com/api/projects/<your-project>`.
Supply that project URL to `project_endpoint`, not a full Responses request URL.
The SDK obtains its OpenAI client through the Azure project client. The `model`
argument selects an existing deployment; its name may differ from a model family
name. Client construction does not provision that project, model, or hosted agent.

#### Example

**Project configuration excerpt; assumes the helper is defined:**

```python
# Create model from this sample's required deployment setting.
model = required_setting("FOUNDARY_MODEL")
# Create project_endpoint from this sample's required project URL setting.
project_endpoint = required_setting("FOUNDARY_PROJECT_ENDPOINT")
```

The sample retains the historical **`FOUNDARY_*`** names and passes the resulting
values explicitly. SDK defaults use **`FOUNDRY_*`**, but this helper does not read
those alternative names. `FOUNDARY_ENDPOINT` is not a supported setting here.
The excerpt does not make a network request; configuration lookup was tested
offline with synthetic values.

#### Where it is used

- [Parse and validate configuration](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L22-L37).
- [Read both settings](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L44-L47).
- [Pass deployment, endpoint, and credential to the adapter](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L53-L59).

#### Why it is used here

Stage 02 teaches project-backed inference instead of stage 01's resource endpoint
and API key. Neither stage guarantees a particular model family or price.
Nonempty process environment values override parsed file settings; see the
[Python helper explanation](./python-concepts.md#helper-functions-and-required-settings)
for the language mechanism.

#### Common misunderstanding

An endpoint does not identify your agent, and a deployment name is not an agent
resource ID. Configuring a project URL does not make this local Python process
a hosted Foundry agent. See [client versus agent](./ai-concepts.md#foundry-client-versus-local-agent).

#### References

- [Official Foundry provider configuration](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python).

## Identity and access

Authentication establishes identity; authorization determines which operations
that identity can perform. Cleanup releases resources but grants no access.

### Async credentials and resource cleanup

#### What it means

`azure.identity.aio.DefaultAzureCredential` is a concrete async credential that
tries supported identity sources when a token is requested. The installed version
includes environment/service-principal, workload identity, managed identity, and
developer credential sources; availability depends on OS, installed tooling,
configuration, and exclusions. It is not a promise that any source will succeed.
Constructing it neither signs in, grants RBAC, nor creates a managed identity.

The sample passes it to the Foundry client for Entra token authentication. Access
to the project/deployment still requires appropriate authorization. No service
API key is read by this sample. Since `dotenv_values` does not export values,
identity environment variables placed only in the parsed app-local file are
not automatically available to the credential chain.

#### Example

**Illustrative offline lifecycle example; no token request:**

```python
# Import the third-party Azure Identity asynchronous credential.
from azure.identity.aio import DefaultAzureCredential

# Define a reusable coroutine demonstrating cleanup, returning no useful value.
async def credential_lifecycle() -> None:
    # Create credential and close its transports when the scope exits.
    async with DefaultAzureCredential() as credential:
        # Verify that it exposes token acquisition without calling that method.
        assert callable(credential.get_token)
```

Calling this coroutine through `asyncio.run` was checked offline; it does not
prove sign-in or service permissions. The Python semantics of `async with` are
explained in [async context managers](./python-concepts.md#async-context-managers).

#### Where it is used

- [Import the async credential](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L14-L16).
- [Enter its lifetime scope](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L49-L51).
- [Supply it and manage client lifetimes](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L58-L62).

#### Why it is used here

The async credential matches asynchronous SDK operations. Nested scopes close
the OpenAI HTTP client first, the Azure project client next, and the credential
last, including when agent execution fails. This is explicit lifecycle management,
not a remote agent create/delete workflow.

#### Common misunderstanding

Successful authentication does not guarantee authorization to invoke a model.
Neither a credential nor a Foundry client configures Application Insights.
The sample has no application telemetry setup. For production, deliberately
choose credential sources rather than assuming a development fallback chain
is always the right identity policy.

#### References

- [Async DefaultAzureCredential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python).
- [Azure Identity credential chains](https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/credential-chains).
- [Foundry model-provider guidance](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry?pivots=programming-language-python).
