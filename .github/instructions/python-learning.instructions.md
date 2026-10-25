---
description: 'Beginner Python and AI agent learning comments: explain language syntax, agent logic, clients, authentication, tools, memory, and observability; use the learning skill and validate coverage.'
applyTo: '**/*.py'
---

Before Python work, follow the repository's
[agent guidance](../../AGENTS.md) and load the
[python-learning-comments skill](../skills/python-learning-comments/SKILL.md).
The skill owns full-file comment coverage, beginner what/why explanations,
agent-concept accuracy, behavior preservation, and canonical concept-guide routing.

Run its [comment placement checker](../skills/python-learning-comments/scripts/check_comments.py)
on every Python file changed in this task with the target sample's interpreter.
Fix missing comments, reread saved files, and review meaning manually; validate
syntax/types and relevant behavior separately. Check affected documentation links
independently. Exclude generated and dependency code, respect explicit requests
not to update docs, and report blocked checks without claiming success.