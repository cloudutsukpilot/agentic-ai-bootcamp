# This module gives a Pydantic AI agent durable, file-based memory.
# Pydantic AI has no built-in file memory provider, so this mirrors the Microsoft Agent
# Framework FileMemoryProvider used by the matching MAF stage: file_memory_* tools,
# a <name>_description.md sidecar per file, and a memories.md index injected into instructions.

# pathlib is Python's built-in library for filesystem paths.
# Import Path to build the per-user memory folder and file paths.
from pathlib import Path

# Pydantic AI is the third-party agent framework used by this stage.
# Import FunctionToolset, a container that groups Python tools plus optional instructions.
from pydantic_ai import FunctionToolset

# Create MEMORY_INSTRUCTIONS, the guidance added to the agent so it knows how to use the tools.
MEMORY_INSTRUCTIONS = (
    # Give the instructions a heading so they are easy to spot in the combined prompt.
    "## File Based Memory\n"
    # Explain that the tools store information that survives across conversations.
    "You have access to a file-based memory system via the `file_memory_*` tools for storing and "
    # Finish the sentence and state that memory is shared across sessions for this user.
    "retrieving information across interactions. These files are shared by every session for this user.\n\n"
    # Ask for descriptive file names so the index stays readable.
    '- Use descriptive file names (e.g., "userpreferences.md").\n'
    # Ask for descriptions, which feed the memories.md index.
    "- Include a description when writing a file to help with future discovery.\n"
    # Ask the model to check existing memory before answering.
    "- Before starting new tasks, use file_memory_ls and file_memory_read to check for relevant memories.\n"
    # Ask the model to overwrite files when facts change.
    "- Keep memories up-to-date by overwriting files when information changes."
)
# Create INDEX_FILE_NAME, the generated file that lists every memory and its description.
INDEX_FILE_NAME = "memories.md"
# Create DESCRIPTION_SUFFIX, the ending used for each memory's description sidecar file.
DESCRIPTION_SUFFIX = "_description.md"


# A function is reusable code; this one names the description sidecar for a memory file.
# Define description_file_name taking a memory file name and returning the sidecar's name.
def description_file_name(file_name: str) -> str:
    # Return "notes_description.md" for "notes.md" by replacing the extension with the suffix.
    return f"{Path(file_name).stem}{DESCRIPTION_SUFFIX}"


# Define is_internal_file, returning True for the index and sidecars that the tools manage themselves.
def is_internal_file(file_name: str) -> bool:
    # Return whether the name is the index file or ends with the description suffix.
    return file_name == INDEX_FILE_NAME or file_name.endswith(DESCRIPTION_SUFFIX)


# Define is_flat_file_name, returning True only for a plain file name with no folder parts.
def is_flat_file_name(file_name: str) -> bool:
    # Reject empty names, "." and "..", and names such as "../x" that would escape the memory folder.
    return bool(file_name) and file_name not in {".", ".."} and Path(file_name).name == file_name


# Define create_file_memory_toolset, which builds the memory tools for one storage folder and scope.
# root_directory is where memory lives on disk; scope (for example a user ID) selects a subfolder.
def create_file_memory_toolset(root_directory: Path, scope: str) -> FunctionToolset:
    # Create working_folder, the per-scope folder so different users would not share files.
    working_folder = root_directory / scope

    # Define a nested helper; nested functions can use working_folder from the enclosing function.
    # rebuild_index rewrites memories.md from the current memory files and their descriptions.
    def rebuild_index() -> None:
        # Create lines, starting with the index heading and a blank line.
        lines = ["# Memory Index", ""]
        # Loop over regular files in the folder in case-insensitive alphabetical order.
        for path in sorted(working_folder.iterdir(), key=lambda item: item.name.lower()):
            # Skip folders and internal files, which are not memories themselves.
            if not path.is_file() or is_internal_file(path.name):
                # Move to the next path without adding it to the index.
                continue
            # Create description_path, the sidecar that may describe this memory file.
            description_path = working_folder / description_file_name(path.name)
            # Check whether a description sidecar exists for this memory file.
            if description_path.exists():
                # Add a bullet with the file name and its stored description.
                lines.append(f"- **{path.name}**: {description_path.read_text(encoding='utf-8').strip()}")
            # Otherwise the memory file has no description.
            else:
                # Add a bullet with only the file name.
                lines.append(f"- **{path.name}**")
        # Write the finished index text, ending with a newline.
        (working_folder / INDEX_FILE_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Define memory_instructions; Pydantic AI calls it before every model request to add fresh memory context.
    def memory_instructions() -> str:
        # Create the per-scope folder on first use; existing folders are left untouched.
        working_folder.mkdir(parents=True, exist_ok=True)
        # Create index_path pointing at the generated memories.md file.
        index_path = working_folder / INDEX_FILE_NAME
        # Create index containing the saved index text, or a placeholder when nothing is saved yet.
        index = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Memory Index\n\n(empty)"
        # Return the usage guidance followed by the current index so the model sees what exists.
        return f"{MEMORY_INSTRUCTIONS}\n\n{index}"

    # Create toolset, whose instructions callable runs before each model request in a run.
    toolset = FunctionToolset(
        # Pass the callable that adds the usage guidance and current memory index to the prompt.
        instructions=memory_instructions,
        # Run these tools one at a time, so parallel calls cannot read a file while another deletes it.
        sequential=True,
    )

    # A decorator wraps a function; tool_plain registers it as a model-callable tool on this toolset.
    @toolset.tool_plain
    # Define file_memory_write with a file name, full content, and optional description.
    def file_memory_write(file_name: str, content: str, description: str | None = None) -> str:
        # Document the tool so the model knows when and how to call it.
        """Write a memory file with the given name and content, overwriting any existing file.

        Args:
            file_name: Flat file name to write under; must not contain path separators.
            content: Full text content to write to the file.
            description: Optional summary used to aid future discovery.
        """
        # Reject names that are not plain file names, protecting files outside the memory folder.
        if not is_flat_file_name(file_name):
            # Return an error message to the model instead of raising, so it can retry.
            return f"Could not write file '{file_name}': use a flat file name without path separators."
        # Reject the reserved index and sidecar names, which only the tools should manage.
        if is_internal_file(file_name):
            # Return an error message to the model so it can choose a different name.
            return f"Could not write file '{file_name}': the file name is reserved for internal use."
        # Create the per-scope folder if this is the first write.
        working_folder.mkdir(parents=True, exist_ok=True)
        # Write the memory content to disk, replacing any earlier version.
        (working_folder / file_name).write_text(content, encoding="utf-8")
        # Create description_path for this file's description sidecar.
        description_path = working_folder / description_file_name(file_name)
        # Check whether the model supplied a nonblank description.
        if description and description.strip():
            # Save the description so the index can show it.
            description_path.write_text(description, encoding="utf-8")
        # Otherwise no description was supplied.
        else:
            # Remove any stale description; missing_ok avoids an error when none exists.
            description_path.unlink(missing_ok=True)
        # Refresh memories.md so later runs see the change.
        rebuild_index()
        # Return a confirmation that the model can report or act on.
        return f"File '{file_name}' written."

    # Register file_memory_read as a model-callable tool on this toolset.
    @toolset.tool_plain
    # Define file_memory_read taking a memory file name and returning its text.
    def file_memory_read(file_name: str) -> str:
        # Document the tool so the model knows when and how to call it.
        """Read the content of a memory file by name.

        Args:
            file_name: Name of the memory file to read.
        """
        # Create path for the requested file inside the memory folder.
        path = working_folder / file_name
        # Return a not-found message for unsafe names or files that do not exist.
        if not is_flat_file_name(file_name) or not path.is_file():
            # Tell the model the file is missing so it does not invent content.
            return f"File '{file_name}' not found."
        # Return the saved text so the model can use it in its answer.
        return path.read_text(encoding="utf-8")

    # Register file_memory_delete as a model-callable tool on this toolset.
    @toolset.tool_plain
    # Define file_memory_delete taking a memory file name and returning a status message.
    def file_memory_delete(file_name: str) -> str:
        # Document the tool so the model knows when and how to call it.
        """Delete a memory file by name, including its description file.

        Args:
            file_name: Name of the memory file to delete.
        """
        # Create path for the file the model wants to delete.
        path = working_folder / file_name
        # Refuse unsafe, internal, or missing files.
        if not is_flat_file_name(file_name) or is_internal_file(file_name) or not path.is_file():
            # Tell the model nothing was deleted.
            return f"File '{file_name}' not found."
        # Delete the memory file from disk.
        path.unlink()
        # Delete its description sidecar too, ignoring a missing sidecar.
        (working_folder / description_file_name(file_name)).unlink(missing_ok=True)
        # Refresh memories.md so the deleted file disappears from the index.
        rebuild_index()
        # Return a confirmation for the model.
        return f"File '{file_name}' deleted."

    # Register file_memory_ls as a model-callable tool on this toolset.
    @toolset.tool_plain
    # Define file_memory_ls returning a list of dictionaries, one per memory file.
    def file_memory_ls() -> list[dict[str, str | None]]:
        # Document the tool so the model knows what it returns.
        """List all memory files with their descriptions (if available)."""
        # Create the per-scope folder so listing an empty memory works.
        working_folder.mkdir(parents=True, exist_ok=True)
        # Create results, an empty list that will collect one entry per memory file.
        results: list[dict[str, str | None]] = []
        # Loop over the folder's entries in alphabetical order.
        for path in sorted(working_folder.iterdir()):
            # Skip folders and internal files.
            if not path.is_file() or is_internal_file(path.name):
                # Move to the next entry.
                continue
            # Create description_path for this file's optional sidecar.
            description_path = working_folder / description_file_name(path.name)
            # Create description from the sidecar text, or None if there is no sidecar.
            description = description_path.read_text(encoding="utf-8") if description_path.exists() else None
            # Add this file's name and description to the results.
            results.append({"name": path.name, "description": description})
        # Return the list; Pydantic AI serializes it to JSON for the model.
        return results

    # Return the finished toolset so the caller can register it with an agent.
    return toolset
