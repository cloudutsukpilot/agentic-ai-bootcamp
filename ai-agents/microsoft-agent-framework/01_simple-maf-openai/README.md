# Simple agent — Microsoft Agent Framework + Azure OpenAI

A beginner-friendly Python script that creates one agent, sends one prompt to
Azure OpenAI, and prints the generated text. Use this as the baseline before
building separate examples with tools, MCP, or memory.

## Sample identity

| Dimension | This sample |
| --- | --- |
| Learning stage | Simple single-agent prompt; baseline stage |
| Framework | Microsoft Agent Framework (Python) |
| Model provider/hosting | Azure OpenAI; not the public OpenAI service |
| Provider adapter | `agent-framework-openai` |
| Client/API | `OpenAIChatClient`, using the Responses API |
| Authentication | Azure resource endpoint and API key |
| Interface | Command-line script with a hardcoded prompt |
| Output | Completed response text on standard output |

The configured deployment determines the actual model; no specific model family
is hardcoded. A learning stage is **not** an SDK version or model version.

## Capabilities

| Capability | Status | Details |
| --- | --- | --- |
| Single-agent prompt/response | Implemented | One `agent.run(...)` call |
| Local function tools | Not implemented | No tools registered |
| MCP tools | Not implemented | No MCP server/client configuration |
| Short-term conversation memory | Not implemented | No reusable session or multi-turn conversation configured |
| Persistent memory | Not implemented | No memory store configured |
| Streaming | Not implemented | Prints after the complete response arrives |
| Multi-agent orchestration | Not implemented | One agent only |
| Retrieval/RAG | Not implemented | No retrieval or document index |

The SDK may support more features, but installing it does not enable those
features in this script. No explicit persistence policy is configured here;
absence of an application memory store is not a guarantee of provider-side
data retention behavior.

## Folder contents

```text
simple-maf-openai/
├── README.md                  # This guide
├── requirements.txt           # This sample's dependency manifest
├── app/
│   ├── simple-ai-agent.py      # Python entry point with learning comments
│   ├── .env                   # Private local configuration; create locally
│   └── __pycache__/           # Generated Python bytecode, if present
├── tests/                     # Currently empty; no automated test suite
└── .venv/                     # Local virtual environment; create locally
```

- [app/simple-ai-agent.py](app/simple-ai-agent.py): configuration, agent setup,
  prompt execution, and script-entry guard.
- [requirements.txt](requirements.txt): dependencies to install for this folder,
  not the repository's unrelated root manifest.
- The private configuration, virtual environment, and bytecode are local or
  generated artifacts excluded by the [repository ignore rules](../../../.gitignore).
  Do not commit credentials or copy another machine's virtual environment.
- The empty test folder is only a placeholder and may be absent in a fresh
  checkout because Git does not track empty directories.

## Frameworks and libraries

| Component | Purpose here | Documentation |
| --- | --- | --- |
| Microsoft Agent Framework | Builds the agent and exposes `as_agent` / `run`; the `agent-framework` package is the umbrella distribution | [Framework repository](https://github.com/microsoft/agent-framework) |
| OpenAI integration | Supplies `OpenAIChatClient`, imported through `agent_framework.openai`; connects to Azure when explicitly configured with `azure_endpoint` | [Provider package and API examples](https://github.com/microsoft/agent-framework/tree/main/python/packages/openai) |
| Azure OpenAI | Hosts the deployed model and processes paid API requests | [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/overview) |
| python-dotenv | `dotenv_values` parses local configuration into a dictionary without exporting it into the process environment | [Library documentation](https://github.com/theskumar/python-dotenv#readme) |
| `asyncio` | Standard library: runs the asynchronous entry point and event loop | [Python asyncio](https://docs.python.org/3/library/asyncio.html) |
| `os` | Standard library: reads process environment variables | [Python os](https://docs.python.org/3/library/os.html) |
| `pathlib` | Standard library: locates configuration beside the script | [Python pathlib](https://docs.python.org/3/library/pathlib.html) |

**Version evidence, 2026-10-09:** the inspected local environment uses Python
3.12.3, `agent-framework` 1.21.0, `agent-framework-openai` 1.16.0, and
`python-dotenv` 1.2.4. Installed metadata for these three distributions declares
Python >=3.10. Only Python 3.12.3 was checked for this README; that is not a
certification of every supported Python version.

The manifest is **unpinned**, so a fresh install may resolve different versions.
There is no dependency lock file here. The umbrella package can install more
integrations than this sample uses; this README does not change dependencies.
Upstream documentation may describe newer APIs than your installed release.

## How the code works

1. [Read configuration beside the script](app/simple-ai-agent.py#L19-L21).
2. [Resolve required settings](app/simple-ai-agent.py#L24-L34): a nonempty
   process environment value wins; otherwise the parsed file value is used.
   Missing/empty values raise an error naming the setting, without printing it.
3. [Create the client](app/simple-ai-agent.py#L40-L48) with the deployment,
   endpoint, and API key. This configures communication with the model.
4. [Create the agent](app/simple-ai-agent.py#L50-L56) from that client, adding a
   readable name and instructions. The instructions currently describe an
   assistant that generates MAF files; the demonstration prompt merely asks
   for a one-sentence explanation and does not write a file.
5. [Run the prompt and print the text](app/simple-ai-agent.py#L58-L62).
6. [Start the event loop](app/simple-ai-agent.py#L65-L69) only when launched
   directly. Importing the module still performs its top-level imports and
   configuration-file parsing, but does not run the agent.

## Prerequisites and setup

- Python >=3.10 compatible with the versions you install; Python 3.12 is the
  locally checked version. See [virtual environment documentation](https://docs.python.org/3/library/venv.html).
- An existing Azure OpenAI resource, a valid API key, and a deployment that
  supports the **Responses API** in your region. An arbitrary OpenAI-compatible
  or Chat Completions-only endpoint is not sufficient.
- Network access to package indexes for installation and the Azure endpoint
  for the live run. This guide does not provision cloud resources.

### Create the environment and install dependencies

These commands are for **Linux/macOS with Bash or Zsh**. Start at the repository
root, then enter this sample folder:

```bash
cd ai-agents/microsoft-agent-framework/simple-maf-openai
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

If the environment already exists, skip its creation. Use the explicit
interpreter to avoid shell aliases/functions installing into a different
environment. Activation is optional:

```bash
source .venv/bin/activate
```

In VS Code, open this sample's Python file, run **Python: Select Interpreter**,
and select the sample's `.venv/bin/python`. Terminal activation and editor
interpreter selection are separate; installing packages does not guarantee
the editor is using that environment.

## Configuration

Create the private configuration file inside the sample's **app folder**, beside
the script, using your editor. The code does not search for a configuration file
at the sample root. Paste these placeholders and replace them locally:

```dotenv
AZURE_OPENAI_MODEL=your-responses-deployment-name
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=replace-with-your-private-key
```

Never paste real secrets into README files, Git, screenshots, or chat. Existing
private configuration must not be overwritten by a setup command.

| Setting | Required | Meaning |
| --- | --- | --- |
| `AZURE_OPENAI_MODEL` | Yes | **Azure deployment name**, which can differ from the model family name |
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure resource endpoint, not a project URL or full API route |
| `AZURE_OPENAI_API_KEY` | Yes | Key for that Azure resource |

These are the three settings explicitly read by this script. It passes `model=`
from `AZURE_OPENAI_MODEL`, so the adapter's fallback to `AZURE_OPENAI_CHAT_MODEL`
does not replace this requirement. No API version is explicitly passed by the
script; adapter defaults and its environment handling apply.

`dotenv_values` does not modify `os.environ`. Avoid exporting conflicting
adapter settings such as `AZURE_OPENAI_BASE_URL` alongside the resource endpoint:
the installed adapter can reject simultaneous base URL and endpoint settings.
Unrelated keys sitting in the private file are not exported by this script.

## Run and expected output

From the sample folder, after configuring credentials:

```bash
.venv/bin/python app/simple-ai-agent-maf-azopenai.py
```

**This command makes a live model request and can incur Azure charges.**

The input is currently hardcoded:
“Explain what the Microsoft Agent Framework is in one sentence.”
The script prints the generated response text, then exits. It is not an
interactive chat, web server, or file generator. Output varies by deployment
and model; no exact sentence is guaranteed. For a different prompt, edit the
[agent call](app/simple-ai-agent.py#L60) using the repository's learning-comment
workflow. Unhandled configuration/provider errors produce a traceback and a
nonzero exit status.

## Exercises to try

Each exercise edits the script and makes a live, potentially billable model
request unless it says otherwise. Undo your edits afterwards, or keep a copy
of the original file.

1. **Change the prompt.** Replace the text passed to `agent.run(...)` with your
   own question and run again. Run the same prompt twice and compare the
   answers: model output is nondeterministic.
2. **Instructions versus prompt.** Keep the prompt, but change `instructions=`
   to `"Always answer in exactly 3 bullet points."` The instructions shape
   *how* the agent answers every request; the prompt says *what* to answer.
3. **Missing configuration (no model call).** Rename `AZURE_OPENAI_MODEL` in
   `app/.env` to `AZURE_OPENAI_MODEL_X` and run. `required_setting` raises
   `RuntimeError` before any request is sent. Restore the name afterwards.
4. **Environment precedence.** Run
   `AZURE_OPENAI_MODEL=does-not-exist ./.venv/bin/python app/simple-ai-agent-maf-azopenai.py`.
   The process environment value wins over `app/.env`, so the provider rejects
   the unknown deployment name. This shows the lookup order in `required_setting`.
5. **No memory between runs.** Change the prompt to `"My name is Alex."`, run,
   then change it to `"What is my name?"` and run again. The agent cannot
   answer, because each run is independent. Stages 06 and 07 add memory.

## Validation without a model request

From this sample folder:

```bash
# Check Python syntax; does not execute the script.
.venv/bin/python -m py_compile app/simple-ai-agent.py
# Check that this interpreter can import the two third-party symbols.
.venv/bin/python -c 'from agent_framework.openai import OpenAIChatClient; from dotenv import dotenv_values; print("Imports OK")'
# Check required learning-comment placement; review comment meaning separately.
.venv/bin/python ../../../.github/skills/python-learning-comments/scripts/check_comments.py app/simple-ai-agent.py
# Check installed dependency compatibility.
.venv/bin/python -m pip check
```

There is currently no automated behavior test suite in this sample. Syntax,
imports, and comment placement do not prove a live deployment works. The README
validation checks do not call Azure; live execution requires valid credentials,
deployment availability, and API compatibility.

**Verified locally on 2026-10-09 with Python 3.12.3:** compilation, both imports,
learning-comment placement, and `pip check` passed. README local links, source
references, and shell-block syntax were also checked. Environment creation and
dependency installation were documented but not rerun; live model execution
was not performed.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Unresolved imports or `Unknown` in the editor | Select this sample's interpreter, verify imports with the command above, and refresh/reload language tooling if needed |
| Missing required Azure OpenAI setting | Confirm all three names are populated in the app-local configuration or process environment |
| Multiple endpoint/base URL settings | Remove conflicting exported base URL settings for this endpoint-based sample; do not log keys |
| Authentication failure (401/403) | Check the endpoint/key pairing, resource access policy, and network restrictions |
| Deployment not found or API unavailable (404) | Check the deployment name, resource endpoint, region, and Responses API support |
| Rate-limit/quota error (429) | Check provider quota/rate limits; this sample configures no custom retry/backoff policy |
| `asyncio.run` reports an already-running loop | Run as a standalone script; notebooks may already manage an event loop |

## Python learning links

- **Asynchronous programming:** [event loop](../../../docs/python-concepts.md#event-loop),
  [coroutines](../../../docs/python-concepts.md#coroutines-and-async-def),
  [async def versus asyncio.run](../../../docs/python-concepts.md#async-def-versus-asynciorun),
  and [await](../../../docs/python-concepts.md#await).
- **Objects and methods:** [method calls and assignment](../../../docs/python-concepts.md#objects-methods-and-assignment),
  illustrated by [client.as_agent](app/simple-ai-agent.py#L50-L56).
- [Python learning-comment skill](../../../.github/skills/python-learning-comments/SKILL.md)
  defines how code and the shared concept guide are maintained.

## Learning progression — separate sample folders

This is a **planned learning path**, not a list of implemented sibling folders.
Each future stage should have its own code, dependencies, and README using the
[sample README skill](../../../.github/skills/agent-sample-readme/SKILL.md).

| Stage | New learning objective | Status relative to this sample |
| --- | --- | --- |
| Simple agent | Configure a client, create an agent, and run one prompt | Current baseline |
| Agent with local tools | Register functions and understand tool calls and side effects | Future separate sample |
| Agent with MCP | Connect to protocol-based tool servers and manage their lifecycle/authentication | Future separate sample |
| Agent with short-term memory | Reuse conversation state/session across turns and reset it deliberately | Future separate sample |
| Agent with persistent memory | Store selected state across restarts, with retention and cleanup rules | Future separate sample |

MCP supplies a protocol for tools/context; it does not automatically add
conversation memory. Short-term memory, persistent storage, and retrieval/RAG
are distinct capabilities. Future framework/provider variants can follow the
same checklist so their differences are easy to compare. No naming convention
or new stage folders are imposed by this README.

## Limitations and safety

This is a learning example, not a production-ready service. It has no custom
observability, conversation loop, output validation, or application-level
failure recovery. SDK defaults may still apply. Treat model output as untrusted,
avoid sensitive prompts, protect keys, and review the provider's data-handling
policy. No live model call was made while authoring this guide.
