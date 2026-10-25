# Stage 09 — Image analysis with file-based memory

## Overview

This independently runnable learning sample sends a local PNG and a text question
to a vision-capable model through Microsoft Foundry, then asks three follow-up
questions in **fresh sessions**. It demonstrates both multimodal input (image and
text together) and the difference between conversation history and saved memory.

| Identity | This sample |
| --- | --- |
| Learning stage | 09: image analysis; not an SDK version |
| Framework | Microsoft Agent Framework, running orchestration locally |
| Provider/service | A model deployment in a Microsoft Foundry project |
| API adapter | `agent_framework.foundry.FoundryChatClient`, using the Responses API |
| Agent | Local `Agent`; construction does not deploy a hosted agent |
| Authentication | Asynchronous `DefaultAzureCredential`; permissions are separate |
| Input | PNG bytes plus hard-coded text in A; text only in B–D |
| Output | Four completed text responses and a memory-file listing after A |

See the [entry point](./app/simple-ai-agent-maf-image-analysis.py#L75-L242).
The configured deployment is supplied by the user; no particular model name is
hard-coded or guaranteed to work.

## What changes from earlier stages, and why?

| Earlier implementation | This sample | Mechanism and practical reason |
| --- | --- | --- |
| [Stage 07](../07_simple-maf-long-term-memory/app/simple-ai-agent-maf-long-term-memory.py#L152-L162) sends text facts and shares file memory across sessions | A supplies a PNG and a text question | `Content.from_data()` and `Content.from_text()` form one multimodal `Message`; useful for describing screenshots, illustrations, or other visual inputs |
| Stage 07 registers a simulated weather function | No weather function is registered here | Focuses the example on visual input and memory rather than unrelated tool output |
| [Stage 08](../08_simple-maf-mcp/app/simple-ai-agent-maf-mcp.py#L127-L165) adds an MCP subprocess and weather tool | No MCP connection or custom application tool | Removes Node.js/server requirements from this lesson; memory tools still come from `FileMemoryProvider` |
| Earlier persistent-memory examples ask about user facts | B asks for a character identity, C adds an Indian-TV clue, D asks for the name | Tests whether newly inferred details were actually saved, rather than assuming a response becomes durable memory |

Image input is not an exclusive benefit of constructing `Agent` directly: it
depends on message content and a compatible model/client. This is a new sample
input and learning objective, not a claim that the earlier API could not do it.
No earlier sample needs to be run first.

## Capabilities

| Capability | Status | Boundary |
| --- | --- | --- |
| Single-agent prompt execution | Implemented | One local agent, four sequential `agent.run()` calls |
| Image analysis | Implemented | Only A receives the original PNG; requires a compatible vision deployment |
| Structured image/text message | Implemented | Inline PNG bytes and a text question in one `Message` |
| Short-term session objects | Implemented | A–D each create a new session; no cross-turn conversation reuse in this script |
| Persistent file memory | Implemented | Shared `demo_user` scope on local disk; writes/reads depend on tool calls |
| Local memory tools | Implemented | Provider supplies file reading, writing, searching, editing, and deletion |
| Custom tools / weather | Not implemented | Explicit `tools=[]`; provider tools are added separately |
| MCP | Not implemented | No MCP server, transport, or tool discovery |
| Streaming | Not implemented | Prints `response.text` only after each run completes |
| Multi-agent / A2A orchestration | Not implemented | No handoffs or second agent |
| Vector retrieval / RAG | Not implemented | No embeddings, vector database, or document retrieval pipeline |
| Image generation / editing | Not implemented | Reads an existing image; does not generate an image |
| Telemetry export | Not implemented | No Application Insights or explicit tracing/export configuration |

## Folder contents

| Location | Purpose |
| --- | --- |
| [app/simple-ai-agent-maf-image-analysis.py](./app/simple-ai-agent-maf-image-analysis.py) | Executable lesson and its four prompts |
| [requirements.txt](./requirements.txt) | Sample-specific, unpinned package requirements |
| [app/sample-image.png](./app/sample-image.png) | Local PNG read by the current script; keep/provide this file before running |
| [app/memory_store/demo_user/](./app/memory_store/demo_user/) | Local memory artifacts; may contain output from previous runs |
| [tests/.gitkeep](./tests/.gitkeep) | Empty-directory placeholder, not a test suite |

The app-local `.env` is private configuration, not a shipped credential asset.
The local `.venv` and any `__pycache__` files are generated environment artifacts,
not application source. Memory filenames and contents are model-produced and can
change; they are not a fixed schema or verified reference answers.

## Frameworks and libraries

| Package / standard library | Role and first-party reference |
| --- | --- |
| `agent-framework-foundry` → `agent_framework.foundry` | [Foundry model adapter](https://learn.microsoft.com/agent-framework/integrations/by-component/model-providers/microsoft-foundry) for model requests |
| Transitive `agent-framework-core` → `agent_framework` | `Agent`, `Message`, `Content`, and file-memory components; [framework source](https://github.com/microsoft/agent-framework/tree/main/python) |
| `azure-identity` → `azure.identity.aio` | [Asynchronous Entra credential chain](https://learn.microsoft.com/python/api/azure-identity/azure.identity.aio.defaultazurecredential); obtains tokens, not permissions |
| `python-dotenv` → `dotenv` | [`dotenv_values`](https://bbc2.github.io/python-dotenv/) parses the local configuration into a dictionary |
| `pathlib` | [Filesystem paths and `read_bytes()`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.read_bytes); no extra installation |
| `asyncio` / `os` | [Event-loop execution](https://docs.python.org/3.12/library/asyncio-runner.html#asyncio.run) and [environment lookup](https://docs.python.org/3.12/library/os.html#os.getenv) |

Installed versions observed while preparing this README: Foundry adapter **1.15.0**,
core **1.23.0**, Azure Identity **1.26.0**, python-dotenv **1.2.4**. These are
observations, not pinned requirements or a guarantee that a fresh install resolves
the same versions. Package metadata for this set requires Python **3.10+**;
the locally inspected interpreter is **Python 3.12.3**. Other Python versions
were not tested. Latest online documentation can differ from installed APIs;
memory behavior below was checked against installed core 1.23.0.

## How it works

1. [Parse configuration](./app/simple-ai-agent-maf-image-analysis.py#L31-L52):
   `dotenv_values()` reads the file beside the script without exporting settings.
   `required_setting()` selects a nonempty process value first, then a file value,
   and raises `ValueError` if both are absent or empty.
2. [Configure local memory](./app/simple-ai-agent-maf-image-analysis.py#L82-L87):
   `FileSystemAgentFileStore` is the disk backend; `FileMemoryProvider` supplies
   tools and context. The fixed `USER_ID` shares one memory scope across sessions.
3. [Read the image](./app/simple-ai-agent-maf-image-analysis.py#L89-L92):
   `Path(__file__).resolve().with_name(...)` finds the PNG beside the script,
   independent of the terminal working directory. `read_bytes()` opens it in
   binary mode, reads the whole file, and closes it automatically. This is a
   concise alternative to `with open(path, "rb")` followed by `.read()`.
4. [Create credential, client, and agent](./app/simple-ai-agent-maf-image-analysis.py#L94-L125):
   credentials authenticate; the client communicates with Foundry; the local
   agent coordinates instructions and tools. These constructors do not deploy a
   hosted agent. Async context managers release credential/client resources.
5. [Run A](./app/simple-ai-agent-maf-image-analysis.py#L128-L156):
   `Content.from_data(data=image_data, media_type="image/png")` supplies inline
   image content. `Content.from_text()` supplies “What does this image contain?”
   The run can make paid network requests and model-selected local memory calls.
6. [Run B](./app/simple-ai-agent-maf-image-analysis.py#L158-L182):
   a new session asks whether the image depicts a famous superhero and requests
   a memory update if identified. It receives no PNG or A transcript.
7. [Run C](./app/simple-ai-agent-maf-image-analysis.py#L185-L209):
   another fresh session supplies the Indian television clue and requests an
   update if the association is true. This is a clue, not verified ground truth.
8. [Run D](./app/simple-ai-agent-maf-image-analysis.py#L211-L235):
   a fourth session asks the character's name. It tests persisted recall, not
   continuation of C. The program exits after D and closes its resources.

### What persistent memory does—and does not—save

The [shared storage configuration](./app/simple-ai-agent-maf-image-analysis.py#L35-L40)
places memory under the app-local `memory_store/demo_user` directory. In installed
core 1.23.0, `FileMemoryProvider.before_run()` registers memory tools and injects
instructions plus the `memories.md` index when available. The index helps discover
files; it is not all their full contents or a replay of earlier conversations.
The model can read relevant files through the tools.

| Provider tool | Input / effect |
| --- | --- |
| `file_memory_write` | Filename, full text, optional description; creates or overwrites a memory and refreshes the index |
| `file_memory_read` | Filename; returns stored text |
| `file_memory_ls` / `file_memory_grep` | Optional filename filter / search pattern; discover stored information |
| `file_memory_replace` / `file_memory_replace_lines` | Filename and edit arguments; change existing text |
| `file_memory_delete` | Filename; removes memory and its description, refreshes index |

The installed provider does **not** override `after_run()` to automatically save
every answer. Saying a character name is not the same as calling a persistence
tool. B/C request updates, but natural-language instructions do not guarantee
tool selection, a successful write, or a correct identification. For example, C
could answer “Shaktimaan” while D still lacks that name if it was not saved or
retrieved. Inspect saved content and tool-call evidence rather than relying on
response wording. Reusing a session would preserve conversational context, but
that is a different experiment from the current fresh-session test.

Memory is plain text: content files, optional `_description.md` companions, and
the generated `memories.md` discovery index. The original image is not copied
into memory by this script; only text explicitly written through tools persists.
The folder survives restarts until removed. There is no expiry, consent flow,
encryption configuration, or authenticated user isolation implemented here.
The installed tools do not require human approval for writes/edits/deletes.
Use only non-sensitive demo data. Before resetting the experiment, stop the app,
review/back up what is needed, and manually remove this sample's `demo_user`
memory directory. Do not delete other lessons' memory folders.

## Prerequisites and setup

- Python 3.10+ for the inspected dependency versions; Python 3.12.3 was inspected.
- A reachable Foundry project and deployment supporting **image input, Responses
  API requests, and function tools**. An OpenAI-compatible endpoint alone does not
  establish support for these capabilities.
- An identity available to `DefaultAzureCredential` with inference permissions
  for that project/deployment. Signing in and assigning access are separate;
  follow the [identity guide](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).
- Network access for package installation, identity/token acquisition, and model
  requests. This lesson does not need Node.js, npm, or an MCP server.
- A readable PNG at the image path in the source. Use an image you are authorized
  to send to the configured provider; image and prompt data leave the machine.

**Linux, zsh/bash; start from the repository root.** These instructions create a
new environment only when one is not already present; do not recreate a working
environment just to read this lesson.

```sh
cd ai-agents/microsoft-agent-framework/09_simple-maf-image-analysis
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Use this sample's manifest, not the repository-root FastAPI requirements. In VS
Code, select this lesson's `.venv/bin/python` with **Python: Select Interpreter**;
the explicit command paths below also avoid shell aliases/wrappers. Windows
virtual-environment paths differ; these commands are for Linux.

## Configuration

Create a private `.env` beside the Python script (inside the app directory), or
set the following variables in the launching process. Do not commit credentials.

| Setting | Required | Meaning / precedence |
| --- | --- | --- |
| `FOUNDARY_PROJECT_ENDPOINT` | Yes | Full Foundry project endpoint; nonempty process value overrides file value |
| `FOUNDARY_MODEL` | Yes | Deployed model's deployment name; nonempty process value overrides file value |

**Placeholder-only file contents:**

```dotenv
FOUNDARY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
FOUNDARY_MODEL=<vision-capable-deployment-name>
```

The spelling **`FOUNDARY_*` is intentional compatibility with this source**;
the SDK's standard `FOUNDRY_*` names do not replace this helper's required keys.
The helper passes the resolved values explicitly to `FoundryChatClient`.
Use the project endpoint, not a standalone Azure OpenAI resource URL or an
endpoint with `/responses` appended. A deployment name is not necessarily its
underlying model-family name. No API-key setting is consumed by this script;
authentication uses the credential chain, not keys in this example file.

## Run and expected output

**Linux, zsh/bash; working directory: this lesson's folder.**

```sh
./.venv/bin/python ./app/simple-ai-agent-maf-image-analysis.py
```

There is no interactive input or command-line image selector. Change prompts or
the image in the source/location deliberately for another experiment. Keep the
declared media type consistent with the actual file format; renaming a JPEG to
PNG does not convert it.

**Illustrative output shape, not a guaranteed model answer:**

```text
---------- Session A Response ----------
<visual description>
---------- End of Session A Response ----------
------- Memory files on disk -------
<files present after A, if any>
-------- End of memory files ------------
---------- Session B Response ----------
<identification attempt based on saved text>
---------- End of Session B Response ----------
---------- Session C Response ----------
<answer using the clue and available memory>
---------- End of Session C Response ----------
---------- Session D Response ----------
<remembered name, uncertainty, or another guess>
---------- End of Session D Response ----------
```

The user's supplied run showed four response blocks, but that is not an automated
assertion of character identity or memory correctness. Responses, formatting,
filenames, and successful recall vary by model and existing memory. The file
listing runs **only after A**, not after B/C/D. Four agent runs can produce more
than four model requests when tool calls require additional inference rounds;
expect network use and provider charges. Unhandled errors stop later sessions.

## Validation and troubleshooting

The test folder contains only a placeholder; there is no working sample test
suite or dedicated run task. Root release-template commands are not evidence
that this lesson passes tests.

**Linux, zsh/bash; working directory: this lesson's folder.** These safe checks
do not invoke the agent, authenticate, or make model requests:

```sh
./.venv/bin/python -c 'import ast; from pathlib import Path; ast.parse(Path("app/simple-ai-agent-maf-image-analysis.py").read_text()); print("Syntax OK")'
./.venv/bin/python -c 'from agent_framework import Agent, Content, Message, FileMemoryProvider, FileSystemAgentFileStore; from agent_framework.foundry import FoundryChatClient; from azure.identity.aio import DefaultAzureCredential; from dotenv import dotenv_values; print("Imports OK")'
```

After Python edits, the repository's separate comment-placement check is run
from the **repository root** with the sample interpreter:

```sh
ai-agents/microsoft-agent-framework/09_simple-maf-image-analysis/.venv/bin/python .github/skills/python-learning-comments/scripts/check_comments.py ai-agents/microsoft-agent-framework/09_simple-maf-image-analysis/app/simple-ai-agent-maf-image-analysis.py
```

Comment placement is not a behavioral test or proof of educational accuracy.

| Symptom | Explanation / next check |
| --- | --- |
| `ExperimentalWarning` for `FileSystemAgentFileStore` | Installed SDK labels the file-store API experimental; warning alone is not a crash. APIs may change across upgrades |
| `NameError: image_file` in an older edit | `.read()` needs a previously opened file object; current source uses `Path.read_bytes()` instead |
| `FileNotFoundError` | Check the PNG beside the script; changing the working directory does not supply a missing image |
| Missing required Foundry setting | Check exact `FOUNDARY_*` spelling, nonempty values, and app-local file location; never print secrets to debug |
| Editor cannot resolve imports | Select the sample interpreter; packages in a lesson environment need not exist in system Python |
| Authentication / permission failure | Verify credential availability, tenant/project access, and assigned permissions; constructing credentials grants no access |
| Model rejects image, tools, or request API | Verify deployment capabilities, project endpoint, media type, size limits, and compatible installed SDK versions |
| D forgets C's character name | Sessions are fresh; inspect saved memory and tool results. B/C's update requests do not force a write |
| Wrong character identification | Treat visual resemblance and user clues as uncertain evidence; ask for confirmation before persisting an inference as fact |
| Results influenced by older experiments | Existing memory persists; inspect/back up/reset only this sample's scope as described above |

## Learning links

- **Python:** [script-relative paths and binary reads](../../../docs/python-concepts.md#script-relative-paths-and-binary-image-data),
  [required-setting helpers](../../../docs/python-concepts.md#helper-functions-and-required-settings),
  [async context managers](../../../docs/python-concepts.md#async-context-managers).
- **Agent concepts:** [client versus agent](../../../docs/ai-concepts.md#foundry-client-versus-local-agent),
  [structured messages](../../../docs/ai-concepts.md#messages-as-structured-conversation-items),
  [short-term sessions](../../../docs/ai-concepts.md#short-term-conversation-sessions).
- **Azure:** [project endpoints and deployments](../../../docs/azure-concepts.md#foundry-project-endpoints-and-deployments),
  [credentials and cleanup](../../../docs/azure-concepts.md#async-credentials-and-resource-cleanup).
- **Official multimodal walkthrough:** [using images with an agent](https://learn.microsoft.com/agent-framework/agents/multimodal).
  Its client example may differ; this lesson uses the Foundry adapter and local PNG bytes.

## Progression and limitations

Each stage is a separate folder, not a migration to perform in place. The current
sequence introduces [simple Azure OpenAI inference](../01_simple-maf-openai/README.md),
[Foundry inference](../02_simple-maf-foundary/README.md),
[explicit agent composition](../03_simple-maf-agentclass/README.md),
[structured messages](../04_simple-maf-messageclass/README.md),
[local tools](../05_simple-maf-tool-decorator/README.md),
[short-term sessions](../06_simple-maf-short-term-memory/README.md),
[persistent memory](../07_simple-maf-long-term-memory/README.md), and
[MCP tools](../08_simple-maf-mcp/README.md), followed by this image-input lesson.
MCP supplies a protocol for external tools; it does not itself provide memory.
The Azure OpenAI/Foundry variants share orchestration concepts but have different
client, endpoint, and configuration requirements; they are not interchangeable
solely because an endpoint is OpenAI-compatible.

This is a demo, not an identity verifier or production memory system. B–D rely on
stored descriptions rather than fresh visual inspection, and no stable image ID
ties a remembered name to a specific image. The fixed user scope can mix repeated
experiments. Reliable confirmed-fact persistence, per-image identifiers, real
user isolation, approval/retention controls, tests, and telemetry would be future
extensions—not implemented guarantees of this sample.