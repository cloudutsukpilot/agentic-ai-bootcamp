---
name: update-docs
description: 'Coordinate sample README enrichment and Python learning-comment updates. Use for combined requests needing worktree awareness, preservation of existing READMEs, beginner what-and-why explanations, and post-edit verification. Delegate to the owning skills and report automated checks separately from model review and blocked validation.'
---

# Update docs and Python comments

## Purpose and delegation

This skill coordinates two existing repository skills; it does not replace
their detailed rules:

- [agent-sample-readme](../agent-sample-readme/SKILL.md) owns AI agent sample
  README structure, source-grounded claims, configuration, setup, progression,
  links, and documentation validation.
- [python-learning-comments](../python-learning-comments/SKILL.md) owns
  beginner-friendly Python comments, agent-concept explanations, topic-guide
  routing, comment placement, and Python validation.

Load and follow both skills before acting when a request involves both a sample
README and Python source. Load the relevant one when a request involves only
one of those surfaces. Preserve the narrower rules from either skill when this
workflow summarizes them.

README preservation and its what/why acceptance gate belong to
`agent-sample-readme` and apply to README-only tasks too. Python comment meaning,
behavior preservation, and its acceptance gate belong to
`python-learning-comments`. The comparison guidance below elaborates on these
rules; it does not authorize restructuring existing docs. Skill-only updates
do not authorize sample or guide edits.

## Required workflow

### 1. Check existing worktree differences first

Before updating any requested file or document, inspect the repository state so
existing user, formatter, or automation changes are understood and preserved.
Run this from the repository root:

```sh
# Check the worktree so existing changes are understood before editing.
git status --short
```

Inspect the current contents and relevant diff for every target file before
editing. Do not revert unrelated changes. If `git` is unavailable, report that
limitation and continue with direct file inspection; do not claim that the
worktree was checked.

Use current pre-edit files as the task baseline, including user changes. Inspect
untracked files directly; `git diff` alone omits them. Record approved edit scope
and distinguish existing changes from task-created changes in the final review.

### 2. Read instructions and route the request

1. Read the repository `AGENTS.md` and any matching instruction files.
2. Read [agent-sample-readme](../agent-sample-readme/SKILL.md) for README work.
3. Read [python-learning-comments](../python-learning-comments/SKILL.md) for
   Python work, including tests or helper scripts.
4. Identify the exact sample folder, README, Python files, manifests, tests,
   and concept guides involved. Do not read or print secret configuration.
5. Separate implementation changes from documentation changes. Preserve
   behavior unless the user explicitly requests a behavior change.

### 3. Inspect before editing

For README work, establish facts from the current source, manifest,
configuration names, tests, and safe project metadata. Do not invent provider,
model, version, capability, or roadmap claims.

For Python work, verify imports, constructors, authentication, client and agent
roles, configuration precedence, lifecycle, and execution flow against the
installed interpreter and source. Explain only behavior that the code actually
implements. Keep optional tools, MCP, memory, retrieval, observability, and
deployment features clearly labeled as unimplemented unless verified in code.

### Explain why each new construct exists

Whenever a sample introduces a class, component, abstraction, or feature, the
README must teach the reason for the change, not only name the new API. Compare
the current sample with the relevant verified prerequisite stage or topic using
source evidence; numbering alone does not prove a dependency. For standalone
samples, explain the objective without inventing a previous stage. When a
comparison applies, it is incomplete unless a beginner can answer all of
these questions:

1. **What could the previous stage already do?** Describe its input, main API
   call, responsibility boundaries, and observable result. Say explicitly if
   it could already produce the same or a similar response.
2. **What was added or changed?** Name the exact class, method, component, or
   feature and show where the current source constructs or uses it.
3. **What does the new construct own?** Explain its concrete responsibilities,
   such as holding instructions, carrying an identity, coordinating a run,
   selecting tools, maintaining state, or managing a lifecycle. Do not use
   "more flexible," "more reusable," or "more extensible" without explaining
   what code can now be organized or added differently.
4. **What remains the same?** Separate architectural change from runtime
   behavior. State whether the model, prompt, output, network request, cost,
   authentication, and persistence behavior changed or stayed the same.
5. **What are the technical benefits and capabilities?** Explain the mechanism
   behind each benefit, the exact API or configuration needed, and a concrete
   application scenario. For example, describe how registered tools let a model
   request application functions, how a reused session carries conversation
   context, or how middleware intercepts execution. "Educational progression"
   or "makes the boundary visible" alone is not an adequate technical rationale.
   Verify whether the previous API already exposes each capability before
   presenting it as an improvement over that API.
6. **What terminology is correct?** Use the symbol that exists in the source.
   For example, call `Agent` a class or agent object only when the code imports
   and constructs `Agent`; do not invent an `AgentClass` symbol because it is
   the lesson's folder name or informal title.

Use the counterfactual test internally to prevent false claims: **Would the
previous API still support this behavior or extension?** If yes, summarize that
parity in one concise qualification, then focus on the verified technical
mechanisms and design trade-offs. Do not make hypothetical removal or repeated
"nothing changes" paragraphs the main explanation. If the new construct adds
exclusive behavior, name the operation and verify why the old API lacks it.

Distinguish three levels throughout the comparison:

- **Implemented delta:** what the current sample actually changes or enables.
- **SDK capability:** what the abstraction supports when explicitly configured,
   even if neither sample enables it yet.
- **Construction/design benefit:** what explicit composition changes in code
   organization, dependency injection, testing, or configuration ownership.

For a capability-focused lesson, include a technical matrix:

| Capability / benefit | API and mechanism | Concrete use case | Previous API support | Current sample status |
| --- | --- | --- | --- | --- |
| Verified capability or design benefit | Exact constructor argument, method, or extension contract | Specific operation it enables and why useful | Already supported, newly supported, or not verified | Implemented or available but not configured |

Keep additions concise and relevant to the lesson. For an explicitly
capability-focused request, cover at least three relevant verified mechanisms
when the SDK offers them; do not add an exhaustive SDK catalog to every README.
Explain prerequisites and limits: tools need registration and compatible model
support, sessions need deliberate reuse, persistence needs a storage strategy,
and middleware needs explicit attachment. Do not turn a capability list into a
promise that the sample already implements those features.

For a new comparison section, prefer a compact table with these columns:

| Previous stage/topic | Current stage | Practical reason for the change |
| --- | --- | --- |
| Existing API and responsibility, linked to source | New API and responsibility, linked to source | Specific learning, design, reuse, lifecycle, orchestration, or future-extension benefit |

For new READMEs, use short subsections titled **Previous implementation and technical
delta**, **Technical benefits of the new construct**, and **Supported
capabilities and activation requirements**. Prefer mechanism-driven explanations
and the capability matrix to lengthy unchanged-behavior sections.
For existing READMEs, reuse equivalent explanations and add only missing answers;
do not force new headings or tables that duplicate content or change structure.
Use a minimal code excerpt only when it makes the construction difference
obvious. Explain the execution path in plain language: identify the object
that talks to the model, the object that carries agent behavior, and the call
that actually sends the request.

When the change is a construction-path change, show the paths in a compact
before/after form, using the repository's actual symbols:

```text
Previous: client -> convenience/factory method -> agent -> run(prompt)
Current:  client + explicit Agent(...) -> agent -> run(prompt)
```

Explain what is hidden in the previous path and what is explicit in the
current path. Do not imply that an arrow means a separate network call; the
README must distinguish local object construction from the later model request.

For example, when documenting direct `Agent(...)` construction after a stage
that uses `client.as_agent(...)`, say all of the following when supported by
the source:

- The earlier stage already creates an agent and can run a prompt, so the
  direct constructor is not being added because the old stage could not answer.
- `as_agent(...)` is a client convenience/factory path in the earlier sample,
  while `Agent(...)` makes the agent object and its inputs visible in the new
  sample. Verify the installed SDK before describing their exact relationship.
- The client remains responsible for model communication; the agent object
  represents local orchestration and behavior such as its name and
  instructions. Do not describe the agent as the model or as a hosted Foundry
  resource unless the source actually provisions one.
- Explain direct construction as explicit dependency injection: agent creation
   accepts a compatible client without calling that client's factory. Give a
   concrete scenario, such as injecting a fake client to test agent configuration
   offline, or centralizing agent configuration while selecting a provider adapter
   separately. Do not imply the factory-created agent cannot be tested or reused.
- Inspect `Agent` and `as_agent` signatures and factory implementation before
   claiming feature differences. When both create the same class, say that tools,
   middleware, sessions, streaming, or context providers are capabilities of
   `Agent` accessible through either path, not constructor-exclusive upgrades.
- Explain relevant supported mechanisms with exact APIs, practical examples,
   activation requirements, and sample status. For example, verify `tools`,
   `middleware`, `context_providers`, `create_session`, and `run(stream=True)`
   against the installed version rather than assuming their names or behavior.

### Comparison quality gate

Before finishing a README that introduces a new construct, review the section
against this checklist:

- The previous and current source files, symbols, and relevant line links are
  named.
- The comparison states whether the observable output is actually different.
- Responsibilities are assigned to the correct object or component.
- Technical benefits identify an API, its mechanism, and a concrete use case;
   educational visibility alone is not used as the conclusion.
- When a capability matrix is included, it separates implemented changes,
   SDK-supported extensions, and construction/design benefits, and states
   previous-API support for each. Otherwise review those distinctions in prose.
- Feature parity is acknowledged concisely without inventing exclusive gains
   or overwhelming the technical explanation with unchanged-behavior prose.
- Activation requirements and unimplemented capabilities are called out.
- No vague benefit claim remains without a specific example or consequence.
- The wording does not imply provisioning, persistence, tools, memory,
  observability, or other capabilities that the source does not implement.

If any checklist item cannot be supported from the repository, inspect the
preceding sample or installed API metadata before editing. If it still cannot
be established, state the uncertainty in the README instead of guessing.

### 4. Apply the smallest coordinated edit

1. Update Python comments according to the full `python-learning-comments`
   rules. Add comments immediately before meaningful Python lines and explain
   both Python syntax and the actual agent workflow.
2. Update the README according to the full `agent-sample-readme` rules. Keep
   source links, line references, configuration names, commands, capabilities,
   and limitations aligned with the resulting code.
   Preserve existing wording and structure; add concise explanations in place.
   Allow small source-verified factual corrections without asking. Ask before
   substantial removals, restructuring, or uncertain corrections.
3. Route new concepts to the canonical guide from the Python skill:
   `docs/python-concepts.md`, `docs/ai-concepts.md`, or
   `docs/azure-concepts.md`. Cross-link overlapping concepts instead of
   duplicating them. Do not create empty guides.
4. Keep edits limited to requested files and required learning documentation.
   Never expose secrets, add paid model calls, or modify dependencies merely to
   improve comments or README prose.

### 5. Validate each affected surface

For every changed Python file, run the comment checker from the repository
root with the project interpreter, using explicit paths for all changed files:

```sh
python .github/skills/python-learning-comments/scripts/check_comments.py \
  path/to/changed.py
```

Also run syntax, type, and relevant safe behavior checks. Do not make live
Azure or model requests solely for comment or documentation validation.

For every changed README or concept guide:

- Check local file links and source line references.
- Check heading anchors and command working directories.
- Confirm configuration examples contain placeholders only.
- Search for stale claims left by the previous implementation.
- Distinguish observed validation from illustrative or unexecuted commands.
- Confirm empty test folders are not described as test suites.

When both Python and README files change, complete both validation paths before
reporting success. Report unavailable commands, skipped live checks, and
remaining test gaps honestly.

### 6. Review saved files and close the verification loop

Run each owning skill's acceptance gate on the saved final files. Check README
preservation against the current pre-edit baseline, not a generated template.
Review source-linked explanations after final Python edits so shifted line
numbers and stage comparisons do not leave stale claims.

Separate evidence for automated placement/syntax checks, explicit link/Markdown
inspection, model review of meaning and what/why rationale, and configured
type/behavior checks. Model review is mandatory, not an automated proof of
correctness. No new scripts, hooks, or CI are implied by these instructions.

Fix task-introduced failures and repeat affected checks after corrections.
Report existing failures and unavailable checks separately; do not turn
`BLOCKED` or `NOT RUN` into `PASS`. Respect the repository's three-attempt limit
for fixing errors in one file; report unresolved issues when that limit is reached.

## Completion report

Report:

- Files changed and why.
- Existing worktree differences considered before editing.
- Python comment, syntax, type, and behavior checks run.
- README and guide link/content checks run.
- Live model, Azure, MCP, or other external checks deliberately not run.
- Any remaining limitations or follow-up work.

Use a concise **Check / Result / Evidence** summary (`PASS`, `FAIL`, `BLOCKED`,
`NOT RUN`, or `N/A` with a reason). Include preservation findings and any
source-verified corrections. Do not say "all checks passed" when only placement
was checked or required review remains blocked.