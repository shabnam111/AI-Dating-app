import json
from llm import generate_json

RESEARCH_SYSTEM = """
You are a careful personal-profile research assistant. Analyse ONLY the supplied
LinkedIn and Instagram public-profile data that the adult participant has authorized
for this dating experiment. Do not infer sensitive traits, protected characteristics,
health, religion, politics, sexuality, finances, or intimate preferences.
Distinguish explicit facts from cautious observations. Never invent information.
Return only valid JSON matching the requested schema. Every non-empty claim must
include a source label (LinkedIn or Instagram) and a short evidence excerpt.
Dating preferences must be included only if explicitly stated by the participant.
"""

def _compact(items, max_chars=10000):
    raw = json.dumps(items, ensure_ascii=False, default=str)

    if len(raw) <= max_chars:
        return raw

    return raw[:max_chars] + "\n[DATA TRUNCATED]"

def build_person_knowledge(name, linkedin_data, instagram_data):
    prompt = f"""
Create a structured knowledge profile for {name} from exactly these two sources.

LINKEDIN DATA:
{_compact(linkedin_data)}

INSTAGRAM DATA:
{_compact(instagram_data)}

Return JSON with this exact structure:
{{
  "name": "{name}",
  "professional_background": [{{"fact":"...", "source":"LinkedIn", "evidence":"..."}}],
  "interests": [{{"fact":"...", "source":"LinkedIn or Instagram", "evidence":"..."}}],
  "hobbies": [{{"fact":"...", "source":"LinkedIn or Instagram", "evidence":"..."}}],
  "lifestyle_signals": [{{"fact":"...", "source":"Instagram", "evidence":"..."}}],
  "values_explicitly_stated": [{{"fact":"...", "source":"LinkedIn or Instagram", "evidence":"..."}}],
  "dating_preferences_explicitly_stated": [],
  "conversation_topics": [],
  "unknown_information": [],
  "short_summary": "A concise evidence-grounded summary"
}}
Do not guess dating preferences from photos, likes, follows, appearance, or lifestyle.
If evidence is missing, return an empty list and explain the gap in unknown_information.
"""
    return generate_json(RESEARCH_SYSTEM, prompt)

def build_from_participant_text(name, linkedin_text, instagram_text):
    # Same research-agent workflow when Actor extraction is unavailable.
    return build_person_knowledge(
        name,
        [{"participant_supplied_excerpt": linkedin_text}],
        [{"participant_supplied_excerpt": instagram_text}]
    )
