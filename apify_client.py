import json
import os
import requests
from urllib.parse import quote

APIFY_API = "https://api.apify.com/v2"

def _actor_input(template_env: str, profile_url: str):
    raw = os.getenv(template_env, "").strip()
    if not raw:
        raise ValueError(f"Missing {template_env}. Configure the input JSON for your chosen Apify Actor.")
    raw = raw.replace("__PROFILE_URL__", profile_url)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{template_env} is not valid JSON: {exc}") from exc

def run_actor(actor_id: str, template_env: str, profile_url: str, timeout: int = 300):
    token = os.getenv("APIFY_API_TOKEN", "").strip()
    if not token:
        raise ValueError("APIFY_API_TOKEN is missing. Add it to your local .env file.")
    if not actor_id:
        raise ValueError(f"Actor ID is missing. Configure the relevant Apify Actor ID in .env.")
    payload = _actor_input(template_env, profile_url)
    encoded_actor = quote(actor_id, safe="~")
    url = f"{APIFY_API}/acts/{encoded_actor}/run-sync-get-dataset-items"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=timeout
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Apify Actor failed ({response.status_code}): {response.text[:1200]}")
    data = response.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Expected dataset items from Apify, received: {type(data).__name__}")
    return data

def scrape_two_sources(linkedin_url: str, instagram_url: str):
    li_actor = os.getenv("LINKEDIN_ACTOR_ID", "").strip()
    ig_actor = os.getenv("INSTAGRAM_ACTOR_ID", "").strip()
    linkedin_items = run_actor(li_actor, "LINKEDIN_ACTOR_INPUT_TEMPLATE", linkedin_url)
    instagram_items = run_actor(ig_actor, "INSTAGRAM_ACTOR_INPUT_TEMPLATE", instagram_url)
    return {"linkedin": linkedin_items, "instagram": instagram_items}
