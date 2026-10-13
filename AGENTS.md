# Agent guidance — Python learning mode

This repository is a Python learning workspace. Preserve behavior while making
the code understandable to a beginner.

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
   edits, use the same skill's topic routing: `docs/python-concepts.md` for
   Python language/runtime, `docs/ai-concepts.md` for AI agent/framework behavior,
   and `docs/azure-concepts.md` for Azure services and identity. Create other
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

Do not mass-edit unrelated Python files, dependencies, generated code, or virtual
environments. Do not print secrets or make paid model requests for comment-only
changes. These rules are instructions for coding agents, not an automatic editor
hook or CI gate; agents must explicitly run validation.
