import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions.get_files_info import *
from functions.get_file_content import *
from functions.write_file_content import *
from functions.run_python import *
from functions.call_function import *

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

 “When you need context, first call get_files_info on '.' or './calculator' to discover files, then read relevant files with get_file_content.”

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
available_functions = types.Tool(
    function_declarations=[schema_get_files_info, schema_get_file_content, schema_write_file, schema_run_python_file]
)

def main():
    args = sys.argv[1:]
    if not args:
        print("Missing Prompt")
        sys.exit(1)

    verbose = False
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")

    if not args:
        print("Missing Prompt")
        sys.exit(1)

    prompt = args[0]
    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    max_iterations = 20
    try:
        for iteration in range(max_iterations):
            get_response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt)
            )

            # Always append all candidates' content to messages before inspecting function_calls
            for candidate in get_response.candidates:
                messages.append(candidate.content)

            if verbose:
                print(f'User prompt: {prompt}')
                print(f"Prompt tokens: {get_response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {get_response.usage_metadata.candidates_token_count}")

            # Handle function calls first, regardless of get_response.text
            if get_response.function_calls:
                for fc in get_response.function_calls:
                    function_response = call_function(fc, verbose=verbose)
                    # Instead of appending the whole Content object as a part, extract the result string
                    resp = function_response.parts[0].function_response.response
                    result_text = resp.get("result") if isinstance(resp, dict) else resp
                    user_message = types.Content(
                        role="user",
                        parts=[types.Part(text=result_text)]
                    )
                    messages.append(user_message)

                    if verbose:
                        print(f"-> {result_text}")
                continue  # Go to next iteration after handling function calls

            # Only treat .text as final when there are no tool calls to handle
            if getattr(get_response, "text", None):
                print(get_response.text)
                break

            # No function calls and no text, break to avoid infinite loop
            print("No response or function call from model.")
            break
        else:
            print("Max iterations reached without final response.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
