---
name: agent-sample-readme
description: 'Create, enrich, or review an AI agent sample README. Preserve existing content while adding concise beginner explanations of what the code does and why, with source-grounded stage comparisons, setup, tools, MCP, and memory. Verify saved files, links, claims, and preservation after every edit; keep planned features separate from implemented capabilities.'
---

# Agent sample README

## Purpose and scope

Document independently runnable learning samples across frameworks and model
providers. Each learning stage is a **separate folder** with its own README and
dependency manifest; do not turn all stages into one evolving sample. Preserve
existing folder names. Prefer `README.md` unless the folder already uses another
case; never create a second README differing only in case.

Learning stage, SDK package version, and model/deployment identity are different
things. Record them separately. Never invent model names, tested versions, sibling
folders, tests, or capabilities.

## Existing READMEs — preserve and enrich

- Inspect current contents and relevant worktree differences before editing,
   including uncommitted user changes. Use the current pre-edit file, not only
   `HEAD`, as the preservation baseline. For untracked files, inspect contents
   directly; Git diffs omit them. If Git is unavailable, report the limitation.
- Keep existing wording, headings, order, tables, examples, and working commands.
   Add missing explanations in the closest relevant section; add a short section
   only when none fits. Do not regenerate, reformat, or restructure for consistency.
- Small source-verified factual corrections and affected stale links are allowed.
   Record the correction and evidence. Ask before substantial removal,
   restructuring, changes to learning intent, or uncertain corrections. Follow
   stricter user requests such as append-only or exact-wording preservation.
- The required sections below are a coverage guide, not a layout migration for
   existing READMEs. Reuse equivalent sections; do not duplicate explanations.
   New READMEs should use applicable sections without inventing filler.
- Editing this skill alone does not authorize sample README or concept-guide
   edits. Leave application code, dependencies, and unrelated docs untouched.

## Workflow — inspect, write, verify

1. Read repository instructions. Inspect the target folder, source entry point,
   manifests, example configuration, test files, and available run tasks. Do not
   read secret files or print their values. Derive required configuration from
   code, not a private environment file. Leave application code/dependencies
   untouched unless the user requests changes.
2. Establish the framework, provider/hosting service, API/client, authentication,
   prompt/input, output, and learning stage. Ask only for facts that cannot be
   established and materially affect the document (for example, desired stage
   layout). Provider adapters are not necessarily the hosting provider.
3. Verify version requirements from manifests and installed metadata. Cite
   first-party framework/provider documentation and official standard-library
   or library documentation. Treat upstream main/latest APIs as potentially
   different from the installed version. Record the date and interpreter for
   validation evidence; distinguish observed versions from unpinned requirements.
4. Create or enrich the README using the preservation rules and coverage guide.
   Explain what and why from source evidence, not irrelevant stage templates.
   Use beginner-friendly explanations and relative local links.
5. Validate local links, heading anchors, source line ranges, command working
   directories, and configuration names. Inspect syntax of shell examples and
   run safe checks with the sample interpreter. Do not reinstall dependencies,
   overwrite private configuration, execute tools/MCP servers, or make paid
   model requests merely to validate documentation. Label checks not executed.
6. Report files written, verified checks, and any remaining limitations. Review
   README accuracy after later changes to this sample's code or manifest.

## Explain what we are doing and why

For each new learning objective or significant construct, add concise answers
in the relevant existing section, with verified source links:

1. **What:** the operation, its input, and its observable result.
2. **How:** the actual responsible symbol and its place in execution order.
   Distinguish local setup from network requests and potentially paid operations.
3. **Why here:** the concrete problem/responsibility it addresses in this sample,
   not only a generic definition. Briefly define new jargon.
4. **Benefit and limits:** explain the technical mechanism and one practical use
   case. State whether the benefit is a runtime capability, design choice, or
   educational step; do not invent exclusive gains or unsupported benefits.
5. **Status:** distinguish implemented behavior, SDK-supported but unconfigured
   extensions, and future plans. State relevant prerequisites and boundaries.

When comparing stages, inspect the relevant prerequisite/comparison sample;
folder numbering alone does not establish a dependency. Explain what it already
did, what changed, the new responsibility, and a concrete reason for the change.
Use the counterfactual internally: could the earlier API do the same thing?
Acknowledge parity concisely when supported, rather than inventing improvements.
Use a compact previous/current/reason table when helpful; preserve equivalent
existing explanations. For standalone samples, explain the objective without
inventing a previous stage. The capabilities table describes implementation
status; the what/why explanation describes learning and design intent.

## Required README sections

1. **Overview and sample identity:** objective, framework, provider, API/client,
   auth, learning stage, and what the user should learn.
2. **Capabilities:** table with implemented/not implemented/not applicable
   status and source-grounded notes. Consider single-agent prompt, local tools,
   MCP, short-term conversation memory, persistent memory, streaming,
   multi-agent orchestration, and retrieval/RAG. SDK support is not evidence
   that a capability is enabled in the sample.
3. **Folder contents:** compact tree/table, real entry-point/manifest links,
   and each item's purpose. Distinguish tracked source, local secret config,
   generated virtual environment/bytecode, and empty test placeholders.
   Never link to private or nonexistent files as if they were shipped assets.
4. **Frameworks and libraries:** purpose in this sample, package names versus
   import names, first-party documentation links, and verified version notes.
   Include relevant standard libraries, but do not call all libraries frameworks.
5. **How it works:** numbered execution flow with source links, explaining
   configuration precedence, client versus agent, execution, and output.
6. **Prerequisites and setup:** supported Python range versus verified Python,
   provider access and model/API compatibility, network requirements, isolated
   `.venv`, installation from this sample's own manifest, and editor interpreter
   selection. Use explicit interpreter paths to avoid user shell wrappers.
   State the shell/OS and working directory before command blocks; do not imply
   Linux commands work unchanged on Windows.
7. **Configuration:** table of required/optional settings, meaning, precedence,
   location, and placeholder-only example. Explain resource endpoint versus full
   API base URL and deployment name versus model family when relevant. Never
   include real credentials, personal endpoints, tenant IDs, or secret output.
8. **Run and expected output:** exact command, input mechanism, exit behavior,
   output shape, cost/network warning, and nondeterministic model output.
   Distinguish instructional expected output from observed live output.
9. **Validation and troubleshooting:** existing tests versus syntax/import/
   comment checks, commands, validation evidence, missing configuration,
   unresolved imports/interpreter mismatch, and provider errors where relevant.
   Do not describe an empty test folder as a functioning test suite.
10. **Learning links:** categorized links to the relevant repository topic guides
   and source code: `docs/python-concepts.md` for language/runtime,
   `docs/ai-concepts.md` for agent/framework concepts, `docs/azure-concepts.md`
   for Azure-specific concepts, and other populated subject guides as needed.
   Use the `python-learning-comments` skill's ownership and cross-link rules
   when introducing concepts instead of building a duplicate glossary. Link
   only to guides/anchors that exist; do not create empty guides for a README.
11. **Progression and limitations:** conceptual separate-folder roadmap from
    simple agent → local tools → MCP → short-term memory → persistent memory,
    with an objective/delta for each. Adjust for framework support and the user's
    actual sequence; it is a plan, not a claim of implemented folders. Add links
    only to stages that exist. Explain that MCP supplies protocol-based tools
    and does not itself provide conversation memory. Compare framework/provider
    variants along the same capability axes. State learning/demo limitations.

## Conditional details for later stages

- **Tools:** signatures and purpose, permissions, side effects, safe inputs,
  tool-selection flow, and mock versus live behavior.
- **MCP:** transport, server command or endpoint, prerequisites, authentication,
  server lifecycle, exposed tools, and network/permission boundaries.
- **Short-term memory:** session creation/reuse, reset behavior, conversation
  scope, and token implications; do not equate it with persistent storage.
- **Persistent memory:** storage backend, schema/location, retention, sensitive
  data, restart persistence, cleanup, and the difference from retrieval/RAG.
- **Other framework/provider variants:** what changed and what stayed the same,
  separate authentication/configuration/API requirements, and actual supported
  capabilities. Do not assume an OpenAI-compatible endpoint supports every API.

## Post-edit acceptance gate — review the saved file

After every creation/update, reread the saved README and inspect its task diff
against the pre-edit contents. Repeat affected checks after corrections; intended
edits or an earlier draft are not evidence about the final file.

| Check | Required verification |
| --- | --- |
| Preservation and scope | Retain existing content and user edits; justify factual corrections/removals. No unrelated edits or layout churn. |
| What and why | Model review: explain each new objective's operation, responsible symbol, concrete rationale, practical use case, and relevant limits. Define jargon for beginners. |
| Source grounding | Model review against source/manifests: verify roles, capabilities, configuration precedence, commands, versions, and stage deltas. Mark unknowns rather than guessing. |
| Local links | Resolve relative to the README; check files, heading anchors including duplicate headings, and source line-range bounds. Inspect target lines for the claimed symbol, not just range existence. |
| Examples and safety | Check shell, working directory, interpreter and placeholder configuration. Distinguish illustrative output from observed output. Do not run setup, side-effecting imports, or live requests just to validate prose. |
| Markdown and consistency | Check fences, headings, lists, tables, contradictions, and duplicated explanations. Review rendering when available; state when only source was inspected. |

These are mandatory agent checks, not automatic editor-save hooks or CI gates.
Use available safe tools for mechanical checks; otherwise inspect explicitly and
label the evidence as manual/model review. Link checks do not prove educational
quality, SDK semantics, or runtime success.

Report **Check / Result / Evidence** using `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`,
or `N/A` with a reason, affected paths, and actual commands/inspections. Fix
task-introduced failures before completion; separate pre-existing problems.
Blocked required verification means qualified completion, not a full pass.
Keep volatile validation logs in the task response, not the README, unless asked.