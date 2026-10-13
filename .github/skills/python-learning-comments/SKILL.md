---
name: python-learning-comments
description: 'Use whenever creating, editing, fixing, refactoring, reviewing, or explaining Python or AI agent code in this repository. Add beginner-friendly what-and-why comments and route concepts to canonical guides. After every Python edit, reread saved files, verify comment meaning and behavior preservation, run the existing placement checker, and report validation evidence and blocked checks.'
---

# Learn Python as you code

## Required workflow

1. Read repository instructions and the affected code. Use the project's
   installed interpreter and verified library APIs; do not guess behavior.
2. Preserve functionality unless the task requests a behavior change.
3. Annotate the full Python files touched in this task, not unrelated files.
  Follow both the Python and AI agent rules below, including helper scripts
  and tests you add. Explain what an operation does in the agent workflow,
  not just its Python syntax.
4. Run the [comment checker](./scripts/check_comments.py) from the repository
   root with the project's Python interpreter and explicit paths to **all**
   Python files changed in this task:
   `python .github/skills/python-learning-comments/scripts/check_comments.py path/to/changed.py path/to/another.py`.
   A nonzero exit status means syntax/tokenization errors or missing comments.
   Fix failures and rerun; do not suppress them by inserting empty comments.
5. Manually review every new/changed comment for accuracy and the concept
   requirements below. Then run syntax, type, and relevant behavior checks.
   Do not execute Azure/model requests just to validate comments.
6. When introducing or explaining a concept, maintain the repository's
  topic-specific concept guides using the routing rules below.
   This also applies to concept-explanation questions without a code change.
7. Report validation results and any blocked checks honestly.

### Scope and preservation baseline

Inspect current files and relevant worktree differences before editing. Record
the exact Python paths and whether the task is comment-only or behavior-changing.
Preserve user edits; compare against current pre-edit contents, not just `HEAD`.
If Git is unavailable, use direct inspection and report the limitation.

Keep accurate existing comments; add/update missing or stale explanations.
Full-file coverage remains required for touched Python files, but do not rewrite
correct comments merely for style or expand scope to unrelated files. Apply the
user's documentation scope before updating guides. Existing sample READMEs follow
the preservation rules in
[agent-sample-readme](../agent-sample-readme/SKILL.md); do not regenerate them
as a side effect of Python comment work.

### Teach intent without repetitive boilerplate

Each meaningful line still needs its preceding comment. Explain **what** the
line does and connect significant operations to **why** this sample needs them.
Define concepts at first relevant use; later comments can explain the specific
action without repeating the entire definition. Avoid generic explanations
such as "call the function" when a concrete responsibility can be named.

For agent setup and execution, identify actual responsibility boundaries:
configuration supplies values, credentials authenticate, clients communicate,
agents coordinate behavior, and invocation produces output when supported by
the code. Do not imply every constructor makes a network call. For a new
abstraction, explain its concrete mechanism and purpose, or label it an
educational alternative rather than an automatic capability gain.

## Concept guides: explain, demonstrate, connect to real code

Store shared learnings under repository-root `docs/`, not in each sample folder.
Separate subjects into these canonical guides; create a guide only when there
is a verified concept to document, never an empty placeholder.

| Guide | Owns | Example concepts |
| --- | --- | --- |
| `docs/python-concepts.md` | Python language and runtime behavior | Functions, types, objects, imports, exceptions, coroutines, `async with`, environment lookup |
| `docs/ai-concepts.md` | AI and agent behavior, frameworks, and model interaction | Client versus agent, instructions versus prompts, tool calling, MCP, sessions, memory, RAG, orchestration |
| `docs/azure-concepts.md` | Azure-specific SDKs, services, configuration, and access | Foundry project endpoints/deployments, Azure OpenAI, Entra tokens, `DefaultAzureCredential`, managed identity, RBAC, Application Insights |

For another substantial subject, first reuse an appropriate existing guide;
otherwise create `docs/<topic>-concepts.md` with a clear scope and populated
concepts. For example, provider-neutral spans, exporters, and sampling belong
in an observability guide, while Azure Monitor configuration belongs in the
Azure guide. Avoid a new file per class, sample, framework version, or question.

### Overlap, ownership, and cross-links

- Choose one canonical home for each concept based on what is being explained,
  not merely which Python file contains it. Do not put every library concept
  into the Python guide just because its example uses Python syntax.
- Split mixed explanations into focused concepts and link them. For example,
  explain `async with` semantics in the Python guide, async Entra credential
  acquisition in the Azure guide, and agent client roles in the AI guide.
- Keep the full explanation in its owning guide; other guides may include a
  brief project-specific bridge and a relative link to that concept's anchor.
  Use sibling links such as `./python-concepts.md#await` and
  `./azure-concepts.md#<actual-heading-anchor>`. Verify the destination exists;
  never publish the illustrative placeholder anchor as a real link.
- Link related guides in their introduction or a **Related concepts** section
  and add links back where they help a beginner follow prerequisites. Sample
  READMEs should link to the relevant topic guides, not assume Python owns all
  learning material.
- When revisiting a misplaced existing concept, move its full explanation to
  the owning guide rather than duplicating it. Leave a short forwarding note
  under the original heading to preserve inbound anchors; update the contents
  and known incoming links. Do not mass-migrate unrelated concepts unless asked.
- Respect explicit requests not to update documentation. Updating this skill
  alone does not require creating guides or migrating existing content.

### Content and validation rules for every guide

- Add or update a section whenever a task introduces a beginner concept or
  the user asks what a concept means (for example, event loops, coroutines,
  `await`, functions, tool calling, agent memory, or credential chains).
  Reuse existing sections rather than duplicating them.
- Group concepts by learning topic: use `## Category`, `### Concept`, and
  `#### What it means` / `#### Example` / `#### Where it is used` /
  `#### Why it is used here` / `#### Common misunderstanding` headings.
  Keep `## Contents` as a nested linked list of categories and their concepts.
- Reuse these categories when appropriate: **Python fundamentals** (variables,
  values, types, assignment), **Control flow and errors** (conditions, loops,
  exceptions), **Functions and typing** (parameters, return values, annotations,
  decorators), **Objects and methods** (objects, classes, attributes, method
  calls), **Modules and program entry** (imports, `__name__`, script-entry guard),
  **Configuration and file handling** (environment variables, paths, files),
  and **Asynchronous programming** (coroutines, event loops, `await`, tasks)
  within the Python guide. Use subject-appropriate categories in other guides,
  such as **Agent architecture**, **Tools and orchestration**, **Memory and
  retrieval**, **Foundry services**, **Identity and access**, or **Monitoring**.
  Create a category only when it has a documented concept; avoid empty headings.
- Put each concept in one primary category, use cross-links for related topics,
  and order concepts from prerequisites to more advanced ideas where practical.
  Explain briefly how concepts within each category relate. Preserve existing
  concept anchors when reorganizing; validate links after heading changes.
- Give each concept a descriptive heading and include:
  1. **What it means:** a short plain-English definition; explain any new jargon.
  2. **Example:** a small commented Python example or exact relevant excerpt.
     Label illustrative examples versus project excerpts. Include expected
     behavior/output when useful, without claiming untested output was observed.
  3. **Where it is used:** relative Markdown links from the guide to real source
     files with verified `#Lx` or `#Lx-Ly` fragments. Link to each relevant
     non-contiguous location separately, not just the file's beginning.
  4. **Why it is used here:** connect the concept to this project's behavior,
     rather than giving only a generic definition.
  5. **Common misunderstanding:** explain a relevant pitfall when applicable.
    6. **References:** verified official language, SDK, framework, or service
      documentation relevant to the concept and the sample's installed version.
- Keep a linked contents list and cross-link related concepts using heading
  anchors. Never include API keys, credentials, or sensitive configuration.
- On later code edits, refresh affected examples and source line references
  so the guide stays accurate as comments move code lines. Do not add unrelated
  concepts just to fill a glossary or change application behavior for examples.
- Before completion, check that local file links, heading anchors, and source
  line ranges exist and point to the claimed symbols, including cross-guide
  links and forwarding anchors after moves. Review the explanations
  against the actual code. Validate runnable examples with the project
  interpreter when safe; otherwise label them as illustrative and unexecuted.
  Avoid live Azure/model calls solely for documentation validation.
- The comment checker does not validate Markdown examples or guide coverage;
  concept documentation and link validation are separate required checks.

## Comment rules

- Put a single short plain-English `#` explanation immediately **before** each
  meaningful physical code line, at the same indentation. Describe what the
  next line actually does and why when useful. Comments are not shell commands.
- Extra consecutive explanation lines are welcome for libraries and concepts;
  the last line of the block must still describe the next code line.
- Imports: explain whether a library is built into Python or third-party,
  its purpose, and what the imported symbol contributes. Explain each library
  when first introduced; never assert an API behavior without verification.
- New variables: say explicitly that a variable is being created, identify
  its name, and describe the stored value. Assignments to existing variables
  should explain the update, not incorrectly call it a new variable.
- Functions: briefly explain that a function is a reusable block of code,
  then describe this function's purpose. Explain parameters and return type
  annotations. For `async def`, explain a coroutine and `await` in beginner
  terms: waiting without blocking the event loop, not creating a new thread.
- Decorators: explain that a decorator wraps/modifies a function or class;
  explain the specific decorator's purpose directly above each `@...` line.
  Do not add decorators merely to demonstrate them.
- Explain calls, returns, raises, conditions, loops, context managers, classes,
  attributes, type annotations and the script-entry guard when encountered.
- In multiline calls/signatures/collections, comment each argument/parameter/
  item line. Explain keyword arguments without calling them new variables.
- Exempt blank lines, existing comments, closing-only delimiters (such as `)`
  or `},`), and interior lines of multiline strings/docstrings. They are
  formatting/data, not separate Python operations. Explain the opening string
  line if it is a meaningful assignment or docstring.
- Preserve valid Python: never put comments into string data or unsafe
  backslash continuations. Convert explicit backslash continuations to
  parenthesized continuation when needed and verify behavior is unchanged.
- Keep explanations readable and current; avoid unexplained jargon, secrets,
  repeated boilerplate, and comments that merely restate punctuation.

## AI agent logic and concepts

Apply these rules alongside the line-by-line Python comments. Stay neutral
across frameworks and providers; explain the actual sample, not a presumed
architecture. A short comment can cover both language and agent purpose;
add another comment when a concept needs context.

- **Verify SDK names and behavior first:** inspect the sample's dependencies,
  installed APIs, and first-party documentation. Class names, import paths,
  constructor arguments, and remote-resource behavior vary by SDK version.
  Correct misconceptions in explanations; report invalid imports rather than
  adding comments that imply they work. Do not silently upgrade dependencies
  or implement missing features during a comment-only task.
- **Framework, provider, client, and agent:** explain each imported library's
  role and distinguish the orchestration framework from the model provider.
  A chat client is an adapter for model/service communication, not automatically
  a remotely persisted agent. Explain what the particular constructor and
  agent factory actually create, and where the agent executes. For example,
  verify `FoundryChatClient` under `agent_framework.foundry`, not the misspelled
  `FoundaryChatClient` under `agent_framework.foundary`. Do not infer that client
  construction provisions a Foundry Agent Service resource.
- **Authentication and authorization:** explain how the configured credential
  supplies authentication and why it is passed to this client. The Azure class
  is `DefaultAzureCredential` (singular): it attempts supported credential
  sources to obtain Entra access tokens. Constructing it does not grant access,
  create a managed identity, or guarantee sign-in. Permissions/RBAC are separate.
  Verify the credential chain for the installed version and distinguish sync
  and async imports, token acquisition, and cleanup. Never expose token/key values.
- **Configuration and lifecycle:** explain endpoint versus model/deployment
  versus project/agent identifiers, required configuration, precedence,
  resource creation/reuse/deletion, and client/context-manager cleanup wherever
  used. Identify local setup separately from remote calls and their costs.
- **Instructions and execution flow:** explain instructions versus user input,
  tool registration, agent invocation, model output, streaming, and response
  processing. Explain why each argument or operation is needed at this stage.
  Do not imply instructions alone implement file generation or external actions.
- **Tools, MCP, and orchestration:** when present, explain tool schemas and
  model-selected invocation versus direct Python calls, permissions and side
  effects, MCP transport/session lifecycle, and handoffs or workflow control.
- **Memory and retrieval:** when present, distinguish conversation history,
  short-term sessions, persistent storage, and RAG. Explain lifetime, storage,
  isolation, and cleanup; neither MCP nor a client object automatically gives
  an agent persistent memory.
- **Observability:** when present, explain instrumentation, spans/traces, logs,
  metrics, exporters, correlation, and the telemetry destination. Application
  Insights can receive supported OpenTelemetry telemetry via Azure Monitor,
  but neither a Foundry client nor `DefaultAzureCredential` enables it alone.
  Verify framework instrumentation and exporter setup separately; generic HTTP
  instrumentation does not guarantee agent/tool spans or token metrics.
  Explain initialization, configuration, shutdown/flush, sampling, ingestion
  costs, and prompt/output privacy at the relevant code. Never enable sensitive
  content capture, add dependencies, provision resources, or export telemetry
  merely to enrich comments.
- **Implemented versus optional:** comment current behavior as fact. Mention
  unimplemented integrations only in a clearly labeled optional learning note
  or planned README section, not as if the sample already uses them. An optional
  Application Insights note should explain its purpose and prerequisites, not
  promise telemetry from code that has no instrumentation.
- **Concept documentation and review:** route language concepts to the Python
  guide, agent/framework concepts to the AI guide, and Azure service/identity
  concepts to the Azure guide using the ownership rules above. Cross-link
  overlapping concepts rather than duplicating explanations. Include examples,
  source links, and verified first-party references; distinguish illustrative/
  planned material from implemented code.
  Respect explicit requests not to update docs. Manually check that comments
  explain both Python and agent intent; the placement checker cannot prove this.

Useful first-party references (verify APIs against the sample's SDK version):

- [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [DefaultAzureCredential reference](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python)
- [Application Insights with OpenTelemetry](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable)

## Post-edit acceptance gate — verify the final files

After every creation/update, reread the saved Python files, not just the patch.
Apply these checks to every changed Python file, including helpers and tests:

1. **Placement (automated):** run the existing checker with explicit paths to
  all task-changed Python files, using the verified project interpreter
  executable rather than an unverified shell alias. Record the command, exit
  code, and file coverage; rerun after corrections for the final versions.
2. **Meaning (model review):** check every new/changed comment against its next
  line and surrounding flow. Verify creation versus updates, parameters versus
  variables, imported library roles, async semantics, actual SDK symbols, and
  what/why explanations. Check other affected comments for newly stale claims.
  Placement success is not evidence of semantic accuracy.
3. **Behavior preservation:** for comment-only edits, compare executable code
  with the current pre-edit baseline. Use AST comparison when practical; inspect
  literals, annotations, decorators, argument values/order, indentation, and
  entry guards. AST equality does not validate comment-based type-ignore, lint,
  encoding, or coverage directives. Preserve directives; explain necessary
  continuation-format changes and verify equivalent behavior.
4. **Python validity:** the checker parses syntax but does not resolve imports
  or types. Inspect relevant editor diagnostics and run configured safe
  type/behavior checks when applicable. Separate pre-existing failures from
  task-introduced ones. Report missing tools and unsafe/skipped checks honestly;
  do not execute a model-calling sample merely to validate its comments.
5. **Learning docs (when in scope):** verify concept ownership, examples, local
  and cross-guide links, anchors, and refreshed source ranges. Inspect target
  lines for the claimed symbol. Record when no new concept was introduced or
  docs were excluded; do not create empty guides for checklist completeness.
6. **Scope and consistency:** review the task diff for preserved user changes,
  accidental code/data edits, secrets, unrelated files, and contradictions.
  Repeat affected checks after fixes; do not reuse stale validation results.

Summarize **Check / Result / Evidence** using `PASS`, `FAIL`, `BLOCKED`,
`NOT RUN`, or `N/A` with a reason. Include interpreter, changed-file coverage,
automated results, model-review findings, and intentionally skipped external
calls. Fix task-introduced failures before claiming completion; qualify results
when required checks are blocked. These rules require explicit agent review;
they do not install automatic hooks or CI.

## Validation boundaries

The checker uses the standard library AST/tokenizer to find meaningful physical
lines and checks for a nonempty, equally indented comment immediately above
each. It deliberately ignores inline trailing comments and formatting-only
lines. It does **not** validate the educational meaning, variable/library/
decorator explanations, type safety, runtime behavior, or editor configuration.
Those checks remain the agent's responsibility. Instructions route agents to
this skill; they do not guarantee automatic execution on manual editor saves.