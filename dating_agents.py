import json
from llm import generate_text, generate_json

def _profile_text(profile):
    return json.dumps(profile, ensure_ascii=False, indent=2)[:9000]

def agent_speak(own_name, own_knowledge, partner_name, transcript, round_number):
    system = f"""
You are the dating representative agent for {own_name}, an adult who consented
to this matchmaking experiment. You speak on their behalf in a respectful,
curious way. Your ONLY personal knowledge about yourself comes from this profile:
{_profile_text(own_knowledge)}

Rules:
- Never invent personal facts, experiences, feelings, preferences, or intentions.
- You may discuss only facts supported by your profile.
- If something is unknown, say you would need to ask the person.
- Do not infer sensitive traits or make sexual/pressuring comments.
- Ask one natural, specific question at a time.
- Be warm but not overly flattering. Do not claim to be the human.
- You are an AI representative, not the person themselves.
"""
    prompt = f"""
You are speaking with {partner_name}'s dating agent.
Conversation so far:
{transcript if transcript else "(No messages yet.)"}

This is turn {round_number}. Write the next message from {own_name}'s agent.
Respond naturally to what the other agent actually said. Use your own profile
knowledge where relevant. Keep it to 2-4 sentences and ask at most one question.
"""
    return generate_text(system, prompt, temperature=0.8)

def agent_decision(own_name, own_knowledge, partner_name, transcript):
    system = """
You evaluate whether an AI representative has enough conversation evidence
to recommend that its consenting adult participant consider a first meeting.
Do not infer attraction, intimate preferences, or sensitive traits.
Return valid JSON only. Be conservative and explain uncertainty.
"""
    prompt = f"""
Participant represented: {own_name}
Their evidence-grounded profile:
{_profile_text(own_knowledge)}

Other participant: {partner_name}
Conversation:
{transcript}

Return:
{{
 "interest": "interested | maybe | not_interested",
 "reasons": ["specific evidence from profile or conversation"],
 "open_questions": ["important things not yet known"],
 "confidence": 0-100
}}
Do not treat an agent's generated statement as verified evidence about the human.
"""
    return generate_json(system, prompt)
