
import json
import os
import re
from google import genai
from google.genai import types
import time
import threading
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# Gemini free-tier rate limiter
_last_request_time = 0
_request_lock = threading.Lock()

def wait_for_gemini():
    global _last_request_time

    with _request_lock:
        elapsed = time.monotonic() - _last_request_time
        wait_time = max(0, 13.2 - elapsed)

        if wait_time > 0:
            print(f"Gemini rate limit: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)

        _last_request_time = time.monotonic()

def _client():
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if not key:
        raise ValueError("GEMINI_API_KEY is missing.")

    return genai.Client(api_key=key)


def generate_text(system_instruction, user_prompt, temperature=0.5):
    client = _client()
    wait_for_gemini()
    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=2500
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")
    
    return response.text.strip()


def generate_json(system_instruction, user_prompt):
    client = _client()

    def call_model(prompt):
        wait_for_gemini()
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=4096
            )
        )

        return (response.text or "").strip()

    raw = call_model(user_prompt)

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        print("Invalid JSON received. Attempting repair...")

    repair_prompt = f"""
    Convert the following response into valid JSON.

    IMPORTANT:
    - Preserve the original information.
    - Do not invent facts.
    - Escape quotation marks correctly.
    - Remove markdown formatting.
    - Do not truncate the response.
    - Return only valid JSON.

    ORIGINAL RESPONSE:
    {raw[:12000]}
    """

    repaired = call_model(repair_prompt)

    try:
        return json.loads(repaired)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON repair failed: {error}. "
            f"Repaired response preview: {repaired[:1000]}"
        )
