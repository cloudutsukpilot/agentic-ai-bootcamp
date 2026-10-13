# argparse is a built-in library for reading command-line arguments.
# Import argparse so callers can pass the Python files they want to check.
import argparse
# ast is a built-in library for parsing Python into an abstract syntax tree.
# Import ast to reject invalid Python before checking its comments.
import ast
# io is a built-in library that provides file-like objects in memory.
# Import io to give the tokenizer a text stream without creating a file.
import io
# pathlib is a built-in library for working with filesystem paths.
# Import Path to represent and read the files supplied by the caller.
from pathlib import Path
# tokenize is a built-in library that separates Python source into tokens.
# Import tokenize to distinguish executable code from comments and string contents.
import tokenize


# A function is a reusable block of code; this one returns missing-comment line numbers.
# Define missing_comments with a text parameter and a return type of list[int].
def missing_comments(source: str) -> list[int]:
    # Create the lines variable containing each physical source line without its newline.
    lines = source.splitlines()
    # Create the code_lines dictionary mapping line numbers to meaningful tokens.
    code_lines: dict[int, list[tokenize.TokenInfo]] = {}
    # Create the ignored set containing token kinds that do not represent code operations.
    ignored = {tokenize.ENCODING, tokenize.ENDMARKER, tokenize.INDENT, tokenize.DEDENT,
               # Include comments and newlines because they do not need their own explanations.
               tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE}
    # A loop repeats work; inspect each token produced from the in-memory source stream.
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        # Only collect tokens representing code, rather than indentation or comments.
        if token.type not in ignored:
            # Add this token to the list for its starting line, creating that list if needed.
            code_lines.setdefault(token.start[0], []).append(token)
    # Create the missing variable as an empty list of lines that need explanations.
    missing: list[int] = []
    # Inspect each code line and the tokens that start on it.
    for number, tokens in sorted(code_lines.items()):
        # Skip lines made entirely of closing brackets and commas, which are formatting only.
        if all(token.type == tokenize.OP and token.string in {')', ']', '}', ','} for token in tokens):
            # Continue jumps to the next loop iteration without checking this formatting line.
            continue
        # Create the current variable holding this code line using Python's zero-based indexing.
        current = lines[number - 1]
        # Create the indent variable holding the whitespace before this code line.
        indent = current[:len(current) - len(current.lstrip())]
        # Create the previous variable holding the preceding line, or empty text for line one.
        previous = lines[number - 2] if number > 1 else ''
        # Create the explanation variable after removing the expected indentation from that line.
        explanation = previous[len(indent):] if previous.startswith(indent) else ''
        # Flag lines without an immediately preceding, equally indented, nonempty explanation.
        if not explanation.startswith('# ') or not explanation[2:].strip():
            # Append this line number so the caller can report the missing comment.
            missing.append(number)
    # Return the list of missing-comment line numbers to the caller.
    return missing


# A function is a reusable block of code; this one runs the command-line validation.
# Define main without parameters and annotate its returned exit code as an integer.
def main() -> int:
    # Create the parser variable to describe this command-line tool and its arguments.
    parser = argparse.ArgumentParser(description='Check beginner-comment placement in Python files.')
    # Register one or more required file arguments and convert each supplied path into a Path object.
    parser.add_argument('files', nargs='+', type=Path)
    # Create the args variable holding the parsed command-line arguments.
    args = parser.parse_args()
    # Create the failed variable to record whether any file fails validation.
    failed = False
    # Check every file supplied by the caller.
    for path in args.files:
        # A try block lets us report expected file/parsing errors instead of crashing without context.
        try:
            # Open Python source with encoding detection so coding declarations are respected.
            with tokenize.open(path) as handle:
                # Create the source variable containing this file's Python text.
                source = handle.read()
            # Parse the code to check syntax without executing imports or application behavior.
            ast.parse(source, filename=str(path))
            # Create the missing variable containing lines without the required comments.
            missing = missing_comments(source)
        # Handle unreadable files, bad encodings, invalid syntax, and malformed tokens.
        except (OSError, UnicodeError, SyntaxError, tokenize.TokenError) as error:
            # Print the file and validation error without printing its source or any secrets.
            print(f'{path}: validation error: {error}')
            # Update failed to remember that validation did not pass.
            failed = True
            # Skip further work on this file and proceed to the next one.
            continue
        # Report each code line that needs an explanatory comment.
        for number in missing:
            # Print a navigable file/line diagnostic identifying the missing comment.
            print(f'{path}:{number}: missing explanatory comment immediately above code')
        # Update failed while preserving any failure from a previously checked file.
        failed = failed or bool(missing)
    # Print a success message only when every supplied file passes.
    if not failed:
        # Tell the caller that comment placement passed, without claiming semantic quality.
        print('Comment placement checks passed.')
    # Return zero for success or one for failure, following command-line exit-code conventions.
    return int(failed)


# __name__ identifies how Python loaded this module; run only when launched as a script.
if __name__ == '__main__':
    # Raise SystemExit with the checker result so shells and automation can detect failures.
    raise SystemExit(main())