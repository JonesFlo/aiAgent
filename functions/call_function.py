from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file_content import write_file
from functions.run_python import run_python_file
import json

FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}

def call_function(function_call_part, verbose=False):
    kwargs = dict(function_call_part.args)
    kwargs['working_directory'] = './calculator'  # Set your working directory here
    function_name = function_call_part.name

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}()")

    if function_name not in FUNCTION_MAP:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    else:
        result = FUNCTION_MAP[function_name](**kwargs)

    if isinstance(result, (dict, list)):
        result_str = json.dumps(result)
    elif isinstance(result, bytes):
        try:
            result_str = result.decode("utf-8", errors="replace")
        except Exception:
            result_str = str(result)
    else:
        try:
            result_str = result if isinstance(result, str) else str(result)
        except Exception as e:
            result_str = f"<non-string result; coercion failed: {e}>"
   
   

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result_str},
            )
        ],
    )



    
 
    
