# Agent guidance — Python learning mode

This repository is a Python learning workspace. Preserve behavior while making
the code understandable to a beginner.

## Repository map and scope

- Microsoft Agent Framework lessons are separate numbered folders under
   [ai-agents/microsoft-agent-framework](ai-agents/microsoft-agent-framework/).
   Use the [learning recap](ai-agents/microsoft-agent-framework/README.md) to
   navigate; verify current capabilities in the selected sample's source rather
   than inferring implementation or prerequisites from its folder name.
- The [FastAPI sample](ai-agents/pydantic-framework/simple-pydantic-openai/)
   uses the OpenAI SDK directly. Do not assume its dependencies, HTTP test setup,
   or application layout apply to the MAF lessons.
- Before editing, run `git status --short` and inspect target-file diffs;
   read untracked targets directly. Preserve current pre-edit contents, including
   user changes, rather than treating `HEAD` as the only baseline.
- For combined README/comment work, start with
   [update-docs](.github/skills/update-docs/SKILL.md), which delegates to the two
   owning skills below. Customization-only requests do not authorize application,
   dependency, README, or concept-guide edits.

## Environment and validation pitfalls

- Use the target sample's interpreter and dependency manifest. Root
   [requirements.txt](requirements.txt) and
   [requirements-dev.txt](requirements-dev.txt) describe the FastAPI stack, not
   the MAF SDKs. Inspect installed package versions before relying on API names;
   unpinned manifests do not prove the version installed in a sample environment.
- Derive configuration names and file locations from source, not private
   environment files. Preserve the existing `FOUNDARY_*` spelling where used;
   silently changing it to `FOUNDRY_*` breaks configuration compatibility.
- Root [README.md](README.md) and [Makefile](Makefile) describe a release
   template whose root application, test directory, and Dockerfile are absent.
   Do not assume `make test` or `make build` validates the learning samples.
- Use scoped checks with the selected interpreter: `python -m ruff check <paths>`
   when Ruff is installed. For the FastAPI sample, run `python -m pytest tests/ -q`
   from its own folder. Inspect tests and required configuration first; empty
   lesson test folders are not evidence of coverage. Run the comment checker
   separately as required below; report unavailable tools or blocked checks.

## Required workflow for every Python change

1. Before creating, editing, refactoring, or fixing Python code, read and follow
   [.github/skills/python-learning-comments/SKILL.md](.github/skills/python-learning-comments/SKILL.md).
2. Add a short, plain-English `#` comment immediately above every meaningful
   code line in each Python file you change. Explain imports/libraries,
   variables, functions, parameters, control flow, asynchronous operations, and
   decorators as specified in the skill. Also explain agent logic and concepts:
   framework/provider/client/agent roles, authentication and permissions,
   execution flow, tools, MCP, memory, and observability when used. Verify SDK
   names and behavior, and label optional integrations as not implemented.
   Keep comments accurate after edits.
3. Run the skill's comment checker on every Python file changed in this task
   (including helper scripts and tests), using the project's interpreter.
   Fix missing comments before reporting success; also validate syntax/types
   and relevant behavior separately.
4. Review comments manually for educational accuracy. The checker checks
   placement, not meaning. Never claim it proves comment quality or correctness.
5. When introducing or explaining concepts, including questions without code
   edits, use the same skill's topic routing:
   [Python concepts](docs/python-concepts.md) for Python language/runtime,
   [AI concepts](docs/ai-concepts.md) for AI agent/framework behavior, and
   [Azure concepts](docs/azure-concepts.md) for Azure services and identity. Create other
   populated topic guides only when needed. Give each concept one canonical
   home and cross-link overlaps rather than duplicating them. Include a simple
   example, verified source links, official references, and why the concept is
   used here. Preserve incoming anchors when moving concepts. Refresh examples
   and line links after code changes; validate cross-guide links separately
   from comment placement. Respect requests not to update docs.

## README guidance for agent samples

Before creating or updating a sample README, read and follow
[.github/skills/agent-sample-readme/SKILL.md](.github/skills/agent-sample-readme/SKILL.md).
Use separate folders for learning stages and distinguish framework, provider,
implemented capabilities, planned stages, and package versions. Keep README
configuration and commands aligned with the sample's actual source.
Preserve existing wording and structure; enrich in place rather than regenerate.
Follow the skill's what/why comparison gate: name exact APIs, mechanisms,
practical uses, and activation requirements. Verify earlier-API feature parity;
separate implemented changes from SDK support and design benefits instead of
claiming that explicit construction automatically unlocks new capabilities.

Do not mass-edit unrelated Python files, dependencies, generated code, or virtual
environments. Do not print secrets or make paid model requests for comment-only
changes. These rules are instructions for coding agents, not an automatic editor
hook or CI gate; agents must explicitly run validation.
