import subprocess
import sys
import os
from google.genai import types

def run_python_file(working_directory, file_path , args=None, timeout=30):
    """
    Run a Python script in a subprocess, validating path and working dir.
    Prints STDOUT/STDERR with prefixes and warns on non-zero exit code.
    """
    if args is None:
        args = []

    # Resolve full paths
    full_path = os.path.join(working_directory, file_path)
    abs_full_path = os.path.abspath(full_path)
    abs_working_directory = os.path.abspath(working_directory)

    # Validate path constraints
    if not abs_full_path.startswith(abs_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(abs_full_path):
        return f'Error: File "{file_path}" not found.'

    if not abs_full_path.endswith('.py'):
        return f'Error: File "{file_path}" is not a Python file.'

    try:
        result = subprocess.run(
            [sys.executable, abs_full_path, *args],
            cwd=abs_working_directory,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Print STDOUT with prefix
        if result.stdout:
            for line in result.stdout.splitlines():
                print(f"STDOUT: {line}")

        # Print STDERR with prefix
        if result.stderr:
            for line in result.stderr.splitlines():
                print(f"STDERR: {line}")

        # Non-zero exit code message
        if result.returncode != 0:
            print(f"⚠️ Process exited with code {result.returncode}")

        return result

    except subprocess.TimeoutExpired as e:
        print(f"❌ Timeout: script took longer than {timeout} seconds")
        if e.stdout:
            for line in e.stdout.splitlines():
                print(f"STDOUT: {line}")
        if e.stderr:
            for line in e.stderr.splitlines():
                print(f"STDERR: {line}")
        return None
    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file that should run, relative to the working directory. If not provided it prints an error."),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of arguments to pass to the script.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)