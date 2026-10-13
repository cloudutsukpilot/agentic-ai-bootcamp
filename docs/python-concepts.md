# Python concepts — learn from the code

<!-- markdownlint-configure-file {"MD024": {"siblings_only": true}} -->

This guide connects Python concepts to the code in this repository. Read the
explanation, follow the source links, and see why the concept is used there.
Examples marked **illustrative** are small learning examples, not application
code; they do not require Azure credentials or make model requests.

Agent behavior belongs in [AI concepts](./ai-concepts.md); service configuration
and identity belong in [Azure concepts](./azure-concepts.md).

## Contents

- [Functions and typing](#functions-and-typing)
  - [Helper functions and required settings](#helper-functions-and-required-settings)
- [Asynchronous programming](#asynchronous-programming)
  - [Event loop](#event-loop)
  - [Coroutines and async def](#coroutines-and-async-def)
  - [async def versus asyncio.run](#async-def-versus-asynciorun)
  - [Await](#await)
  - [Async context managers](#async-context-managers)
- [Objects and methods](#objects-and-methods)
  - [Objects, methods, and assignment](#objects-methods-and-assignment)
- [AI agent architecture](#ai-agent-architecture)
  - [Foundry client versus local agent](#foundry-client-versus-local-agent)
- [Identity and access](#identity-and-access)
  - [Async credentials and resource cleanup](#async-credentials-and-resource-cleanup)

## AI agent architecture

The framework coordinates the agent while the provider serves model requests.
Client configuration and agent behavior are separate responsibilities.

### Foundry client versus local agent

This heading is retained for existing links. The canonical explanation is now
[Foundry client versus local agent](./ai-concepts.md#foundry-client-versus-local-agent).
For Python method-call syntax, see [objects and methods](#objects-methods-and-assignment).

## Identity and access

Authentication establishes identity; authorization determines what that identity
may access. Client lifetime management releases resources after the work ends.

### Async credentials and resource cleanup

This heading is retained for existing links. Azure credential behavior now lives
in [async credentials and resource cleanup](./azure-concepts.md#async-credentials-and-resource-cleanup).
Python lifecycle syntax lives in [async context managers](#async-context-managers).

## Functions and typing

Functions give repeated operations a name and a reusable implementation. Type
annotations describe the inputs and outputs; runtime checks enforce the actual
conditions we need.

### Helper functions and required settings

#### What it means

A **helper function** is an ordinary function that packages a small reusable
task. This is abstraction: callers ask for a required setting without repeating
how it is looked up and checked. `required_setting` is our own helper, not a
Python built-in or a framework requirement.

`os.getenv(name)` reads the process environment and returns a string if the
variable exists, otherwise `None` unless a default was supplied. It can also
return an empty string. The name is `getenv`, not `get_env`.

#### Example

**Project excerpt; assumes the module's imports and settings dictionary exist:**

```python
# Define a reusable helper taking a setting name and returning a nonempty string.
def required_setting(name: str) -> str:
    # Create value from a nonempty environment value or the parsed file value.
    value = os.getenv(name) or settings.get(name)
    # Check whether both lookup attempts failed to produce a nonempty value.
    if not value:
        # Stop with a clear error that identifies the setting, not its secret value.
        raise RuntimeError(f"Missing required Azure OpenAI setting: {name}")
    # Return the validated value to the caller.
    return value
```

The `or` expression chooses the first truthy operand; it does not always return
a Boolean. Here a nonempty environment string wins; otherwise the file lookup
is used. `if not value` rejects `None` and empty strings, but not whitespace-only
strings. The helper does not validate endpoint format, credential validity, or
whether a deployment exists.

#### Where it is used

- [Parse file configuration without exporting environment variables](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L19-L21).
- [Define the helper and its validation](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L24-L34).
- [Reuse it for three client settings](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L40-L48).
- [Stage 02 uses the same fallback policy with ValueError](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L27-L37).

#### Why it is used here

The file is parsed using `dotenv_values`, so its values live in `settings`, not
automatically in `os.environ`. Using only `os.getenv` would miss file-only
configuration. The helper centralizes file fallback, precedence, and immediate
missing-setting errors for all three required values. Successful calls return
a string, making client setup clearer for both readers and type checkers.

References: [os.getenv](https://docs.python.org/3/library/os.html#os.getenv),
[Boolean operations](https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not),
and [python-dotenv](https://bbc2.github.io/python-dotenv/).

#### Common misunderstanding

A helper is optional: callers could repeat these checks inline. It is useful
when several values share the same policy, not because every environment lookup
needs its own function. For optional settings, `os.getenv(name, default)` may be
enough. That default applies when the variable is absent, not when it is set to
an empty string. A `-> str` annotation alone does not enforce validation at
runtime; the explicit check does.

## Asynchronous programming

These concepts work together: a coroutine defines asynchronous work, the event
loop coordinates its execution, and `await` lets it wait for a result. Start
with the event-loop overview, then relate it to coroutines and waiting.

### Event loop

#### What it means

An **event loop** coordinates asynchronous work: it runs tasks that are ready,
tracks tasks waiting for something, and resumes them when they can continue.
An asynchronous task can pause while waiting for a network response so that
other scheduled tasks can run on the same thread.

Think of a waiter taking an order, serving another table while the kitchen
prepares the food, then returning when it is ready. The waiter does not need
to stand idle at the kitchen. The kitchen's work is separate; the waiter
coordinates what to do next.

#### Example

**Illustrative, no network calls:**

```python
# asyncio is Python's built-in library for asynchronous tasks and event loops.
# Import asyncio to coordinate tasks and simulate waiting.
import asyncio

# A function is reusable code; this async function creates a coroutine when called.
# Define describe_task with a string parameter named name and no return value.
async def describe_task(name: str) -> None:
    # Print which task has started its work.
    print(f"{name}: start")
    # Pause this task for a timer without blocking other tasks on the event loop.
    await asyncio.sleep(0.01)
    # Print which task resumed after its timer finished.
    print(f"{name}: finish")

# Define the main coroutine, a reusable async function that coordinates this example.
async def main() -> None:
    # Schedule both coroutines and wait until both have finished.
    await asyncio.gather(describe_task("A"), describe_task("B"))

# Run only when this example is launched directly, not when it is imported.
if __name__ == "__main__":
    # Create an event loop, run main to completion, and close the loop afterward.
    asyncio.run(main())
```

Both tasks can start before either finishes because waiting for a timer lets
the other task run. Do not rely on finish-order timing as a general guarantee.

#### Where it is used

- [Start the sample's event loop](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L67-L69).
- [Define the main coroutine](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L37-L39).
- [Wait for the agent response](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L58-L62).

#### Why it is used here

`asyncio.run(main())` provides the event loop needed by the agent's asynchronous
network operations. The sample sends a prompt to Azure OpenAI and waits for its
response. When the underlying asynchronous network operations suspend, the loop
can process other ready work. This sample makes one agent call; it does not
schedule two independent application tasks like the example above.

#### Common misunderstanding

An event loop does **not** automatically create a thread for each task, or make
CPU-heavy calculations faster. Tasks cooperate by yielding control. Blocking
operations such as `time.sleep(...)` inside a coroutine still block its event
loop thread. Related: [coroutines](#coroutines-and-async-def) and [await](#await).

### Coroutines and async def

#### What it means

A **function** is a reusable block of code. A function declared with `async def`
is a **coroutine function**. Calling it creates a **coroutine object**: a unit
of asynchronous work that has not yet run its body. It needs to be awaited,
scheduled as a task, or passed to a runner such as `asyncio.run(...)`.

#### Example

**Project excerpt:**

```python
# Define a coroutine function named main; None means it returns no useful value.
async def main() -> None:
    # The real function configures the client, creates the agent, and awaits its response.
    ...
```

The `...` is a placeholder in this shortened excerpt, not a replacement for
the actual application body. Calling `main()` alone creates its coroutine
object; `asyncio.run(main())` drives that object to completion.

#### Where it is used

- [The actual main definition and client setup](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L37-L48).
- [Pass main's coroutine to asyncio.run](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L67-L69).

#### Why it is used here

The sample needs to await `agent.run(...)`. Declaring `main` with `async def`
allows `await` in its body, and `asyncio.run` connects that asynchronous body
to a normal command-line script.

#### Common misunderstanding

`async def` does not start work in the background by itself. Calling a coroutine
function without running/awaiting the resulting coroutine does not execute
its body. See the runnable [event-loop example](#event-loop) for the full flow.

### async def versus asyncio.run

#### What it means

`async def` is Python syntax that **defines a coroutine function**; it describes
the asynchronous work. `asyncio.run(...)` is a standard-library function that
**runs asynchronous work from synchronous code**, managing an event loop until
the supplied work completes and closing the loop afterward.

| Expression | What happens |
| --- | --- |
| `async def main(): ...` | Defines a coroutine function; its body does not run yet. |
| `main()` | Creates a coroutine object; its body still does not run. |
| `asyncio.run(main())` | Runs that coroutine to completion and returns its result. |

#### Example

**Illustrative, no network calls:**

```python
# asyncio is the built-in library providing event-loop runners.
# Import asyncio so synchronous script code can run a coroutine.
import asyncio

# A function is reusable code; define an async function with a string return annotation.
async def greeting() -> str:
    # Return the greeting when this coroutine is actually executed.
    return "Hello from async code!"

# Create result by running the greeting coroutine to completion.
result = asyncio.run(greeting())
# Print the string returned by the coroutine.
print(result)
```

Output: `Hello from async code!`. The inner `greeting()` creates the coroutine
object first, then `asyncio.run` runs it. An async function does not need an
`await` statement to be a coroutine function, although asynchronous I/O often
requires one.

#### Where it is used

- [Define the sample's asynchronous main function](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L37-L39).
- [Run main from the script-entry guard](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L67-L69).

#### Why it is used here

The agent response is obtained using [await](#await), so `main` is defined with
`async def`. The script starts in normal synchronous Python code, so
`asyncio.run(main())` supplies the [event loop](#event-loop) to run that work.
One defines what to do; the other starts and manages its execution.

#### Common misunderstanding

Do not call `asyncio.run(...)` from a thread that already has a running event
loop. Inside async code, normally use `await greeting()` instead. Environments
such as notebooks may already manage a loop and support top-level `await`.
`asyncio.run` is usually the outer entry point of a standalone async script,
not something to call for each operation inside it.

### Await

#### What it means

`await` gets the result of an **awaitable**—an object representing asynchronous
work. If the operation is not ready and suspends, the current coroutine pauses
and the event loop can run other ready tasks. Execution resumes after that
operation completes, or an exception is raised if it fails.

#### Example

**Project excerpt, not a standalone example:**

```python
# Create response by waiting for the agent's answer to this prompt.
response = await agent.run("Explain what the Microsoft Agent Framework is in one sentence.")
# Print the text after the awaited operation completes successfully.
print(response.text)
```

This excerpt belongs inside the async `main` function and assumes `agent` has
already been created. `print` runs after the response is available, not while
the request is still pending. A live run uses Azure credentials and may incur
model charges; it is not needed for learning the control flow.

#### Where it is used

- [Create the agent used by the awaited call](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L50-L56).
- [Await the response, then print its text](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L58-L62).
- [Stage 02's awaited run and text output](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L71-L77).

#### Why it is used here

The agent call returns an awaitable response. `await` lets the sample obtain
the completed response before reading its `text` attribute, while supporting
the library's asynchronous network operations.

#### Common misunderstanding

`await` pauses **this coroutine**, not necessarily the entire program. It does
not automatically run the next line concurrently or create another thread.
Awaiting an operation that is already complete may not yield control at all.
Related: [event loop](#event-loop) and [coroutines](#coroutines-and-async-def).

### Async context managers

#### What it means

`async with` enters an asynchronous context manager, runs its body, then awaits
its exit operation even when the body raises an exception. For these SDK clients,
exit releases network transports. Multiple managers enter left to right and exit
right to left; it is resource management, not parallel execution.

#### Example

**Project excerpt; assumes the configured client exists:**

```python
# Enter project and HTTP client scopes; exit closes HTTP first, then project.
async with client.project_client, client.client:
  # The real body creates and runs the local agent before these scopes exit.
  ...
```

This shortened excerpt is illustrative and unexecuted on its own. The outer
credential scope surrounds this one and exits last.

#### Where it is used

- [Credential scope](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L49-L51).
- [Client scopes](../ai-agents/microsoft-agent-framework/02_simple-maf-foundary/app/simple-ai-agent-maf-foundary.py#L61-L62).

#### Why it is used here

The script must release the clients after its single run, including if the run
fails. It avoids repeating cleanup in success and error paths. Azure-specific
identity behavior belongs in [the Azure guide](./azure-concepts.md#async-credentials-and-resource-cleanup).

#### Common misunderstanding

A context manager does not itself authenticate or grant permissions, and not
every object supports this protocol. See the official
[async with specification](https://docs.python.org/3/reference/compound_stmts.html#the-async-with-statement)
and [asyncio runners](https://docs.python.org/3/library/asyncio-runner.html).

## Objects and methods

These concepts explain how we use library objects: variables name objects,
attribute access finds their operations, and method calls return results that
can be assigned to other variables.

### Objects, methods, and assignment

#### What it means

An **object** is a value that can hold data and provide operations. A **method**
is a function associated with an object or class. The dot in `client.as_agent`
looks up the `as_agent` attribute on the client object; here that attribute is
a method. Parentheses call it. The assignment operator `=` binds a variable
name to the returned value.

#### Example

**Project excerpt, not standalone:**

```python
# Create agent by calling the client object's as_agent method and storing its returned object.
agent = client.as_agent(
    # Supply a readable name as a keyword argument to the method.
    name="Sample MAF Azure OpenAI Agent",
    # Supply instructions that guide the agent's behavior.
    instructions="You are a helpful assistant that generates MAF files based on user input.",
)
```

Read it from right to left: use `client`, call its `as_agent` method with the
specified arguments, then bind the returned agent object to the variable
`agent`. The variable names are chosen by us; `as_agent` is a library method,
not a Python keyword. This method creates a configured agent using the client;
it does not turn the existing client variable into an agent or send the prompt.

#### Where it is used

- [Create the client object](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L40-L48).
- [Call as_agent and assign its result](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L50-L56).
- [Run the resulting agent](../ai-agents/microsoft-agent-framework/01_simple-maf-openai/app/simple-ai-agent-maf-azopenai.py#L58-L62).

#### Why it is used here

The client supplies model communication and authentication configuration. The
agent uses that client and adds instructions and agent behavior. Keeping both
names makes these responsibilities visible instead of hiding them in one
chained expression. The actual prompt is submitted later using `agent.run`;
see [await](#await).

#### Common misunderstanding

`agent = client.as_agent` **without parentheses** would store the bound method
itself, not its result. A bound method remembers the object it belongs to and
can be called later. `agent = client.as_agent(...)` calls the method now and
stores the returned agent. Assignment names an object; it does not automatically
copy it or convert its type.
