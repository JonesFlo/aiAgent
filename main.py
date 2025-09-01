import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types



load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


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

    get_first_response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages
    )

    if verbose:
        print(f'User prompt: {prompt}')
        print(f"Prompt tokens: {get_first_response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {get_first_response.usage_metadata.candidates_token_count}")

    print(get_first_response.text)


if __name__ == "__main__":
    main()
