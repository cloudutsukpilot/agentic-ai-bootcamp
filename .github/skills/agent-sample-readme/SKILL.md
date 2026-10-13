---
name: agent-sample-readme
description: 'Create or update a README for an AI agent learning sample in this repository. Use for documenting sample folders, framework/provider comparisons, setup and run commands, tools, MCP, short-term or persistent memory, and learning-stage progression. Ground every claim in the sample source and keep planned features separate from implemented capabilities.'
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
4. Write the README in the target sample folder using the sections below. Adapt
   to the implementation rather than copying irrelevant instructions from other
   stages. Use beginner-friendly explanations and relative local links.
5. Validate local links, heading anchors, source line ranges, command working
   directories, and configuration names. Inspect syntax of shell examples and
   run safe checks with the sample interpreter. Do not reinstall dependencies,
   overwrite private configuration, execute tools/MCP servers, or make paid
   model requests merely to validate documentation. Label checks not executed.
6. Report files written, verified checks, and any remaining limitations. Review
   README accuracy after later changes to this sample's code or manifest.

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