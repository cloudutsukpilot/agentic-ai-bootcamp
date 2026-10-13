---
description: 'Beginner Python and AI agent learning comments: explain language syntax, agent logic, clients, authentication, tools, memory, and observability; use the learning skill and validate coverage.'
applyTo: '**/*.py'
---

Read and follow `.github/skills/python-learning-comments/SKILL.md` before changing
Python code. Explain each meaningful line with a concise comment immediately
above it; add extra explanations for libraries and beginner concepts.
Explain AI agent intent as well as syntax: framework/provider/client/agent roles,
authentication versus authorization, configuration, execution flow, and tools,
MCP, memory, or observability when present. Verify SDK names and behavior; do not
describe optional integrations as implemented or add features for comments.
Run
`.github/skills/python-learning-comments/scripts/check_comments.py` on every
Python file changed in the task and fix missing comments. Review meaning manually
and validate syntax/types independently. Exclude generated and dependency code.

Route concepts introduced or explained into repository-root topic guides:
`docs/python-concepts.md` for Python language/runtime, `docs/ai-concepts.md` for
AI agent/framework behavior, and `docs/azure-concepts.md` for Azure services,
identity, and configuration. Reuse other subject guides or create populated
`docs/<topic>-concepts.md` guides only when needed. Give each concept one canonical
home, a beginner definition, commented example, verified source links, official
references, and a project-specific rationale. Cross-link overlapping concepts
instead of duplicating them; preserve old anchors with forwarding notes when
moving content. Refresh affected examples/source links and validate cross-guide
links separately. Respect explicit requests not to update documentation.