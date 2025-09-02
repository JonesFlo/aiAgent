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
system_prompt = system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
available_functions = types.Tool(
    function_declarations=[schema_get_files_info,schema_get_file_content,schema_write_file,schema_run_python_file]
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

    get_response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt)
    )

    if verbose:
        print(f'User prompt: {prompt}')
        print(f"Prompt tokens: {get_response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {get_response.usage_metadata.candidates_token_count}")

    # python
    if get_response.function_calls:
        fc = get_response.function_calls[0]
        function_response = call_function(fc, verbose=verbose)
        
        

        has_function_response = bool(
            function_response.parts
            and getattr(function_response.parts[0], "function_response", None)
            and function_response.parts[0].function_response.response
    )
        if not has_function_response:
            raise ValueError("Function response is missing or malformed.")  
        
        # python
        resp = function_response.parts[0].function_response.response
        result_text = resp.get("result") if isinstance(resp, dict) else resp
        if verbose:
            print(f"-> {result_text}")


    else:
        print(get_response.text)


if __name__ == "__main__":
    main()
