import os, json
import streamlit as st
import json
from pathlib import Path
from dotenv import load_dotenv
from apify_client import scrape_two_sources
from research_agent import build_person_knowledge, build_from_participant_text
from orchestrator import run_date

load_dotenv()

# Permanent local storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STORE_PATH = DATA_DIR / "knowledge_bases.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
def create_demo_profiles():
    profiles = {
        "demo_alex": {
            "name": "Alex (Demo)",
            "linkedin_url": "Synthetic demo profile",
            "instagram_url": "Synthetic demo profile",
            "source_status": "Synthetic demo data — not real research",
            "knowledge": {
                "name": "Alex (Demo)",
                "professional_background": [
                    {"fact": "Works as a software developer", "source": "Demo data", "evidence": "Synthetic example"}
                ],
                "interests": [
                    {"fact": "Technology and artificial intelligence", "source": "Demo data", "evidence": "Synthetic example"},
                    {"fact": "Photography", "source": "Demo data", "evidence": "Synthetic example"}
                ],
                "hobbies": [
                    {"fact": "Hiking and landscape photography", "source": "Demo data", "evidence": "Synthetic example"}
                ],
                "lifestyle_signals": [],
                "values_explicitly_stated": [],
                "dating_preferences_explicitly_stated": [],
                "conversation_topics": ["Technology", "Photography", "Travel"],
                "unknown_information": ["Actual dating preferences are unknown"],
                "short_summary": "Fictional software developer interested in technology, photography and hiking."
            }
        },
        "demo_sam": {
            "name": "Sam (Demo)",
            "linkedin_url": "Synthetic demo profile",
            "instagram_url": "Synthetic demo profile",
            "source_status": "Synthetic demo data — not real research",
            "knowledge": {
                "name": "Sam (Demo)",
                "professional_background": [
                    {"fact": "Works in digital marketing", "source": "Demo data", "evidence": "Synthetic example"}
                ],
                "interests": [
                    {"fact": "Creative writing and travel", "source": "Demo data", "evidence": "Synthetic example"},
                    {"fact": "Food and culture", "source": "Demo data", "evidence": "Synthetic example"}
                ],
                "hobbies": [
                    {"fact": "Reading novels and exploring new cafes", "source": "Demo data", "evidence": "Synthetic example"}
                ],
                "lifestyle_signals": [],
                "values_explicitly_stated": [],
                "dating_preferences_explicitly_stated": [],
                "conversation_topics": ["Travel", "Books", "Food", "Culture"],
                "unknown_information": ["Actual dating preferences are unknown"],
                "short_summary": "Fictional digital marketer interested in writing, travel, food and culture."
            }
        }
    }

    st.session_state.profiles.update(profiles)
    save_profiles(st.session_state.profiles)

def load_profiles():
    if not STORE_PATH.exists():
        return {}

    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError) as e:
        st.error(f"Could not load saved profiles: {e}")
        return {}


def save_profiles(profiles):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temp_path = STORE_PATH.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

    temp_path.replace(STORE_PATH)

    return STORE_PATH

st.set_page_config(page_title="Personal AI Dating Agents", page_icon="💬", layout="wide")
st.title("💬 Personal AI Dating Agents")
st.caption("One research agent learns each person's profile; two independent dating agents use those knowledge bases to converse.")

if "profiles" not in st.session_state:
    st.session_state.profiles = load_profiles()
if "last_date" not in st.session_state:
    st.session_state.last_date = None

with st.sidebar:
    st.subheader("Configuration")
    st.write("Gemini API:", "Configured" if os.getenv("GEMINI_API_KEY") else "Missing")
    st.write("Apify token:", "Configured" if os.getenv("APIFY_API_TOKEN") else "Missing")
    st.caption("Keep API keys in .env. Never paste them into the app or commit them.")

tab1, tab2, tab3 = st.tabs(["1 · Research agent", "2 · Knowledge profiles", "3 · Dating room"])

with tab1:
    st.subheader("Create a person's knowledge base")
    st.info("Use only consenting adults who explicitly authorize this profile analysis. The app does not bypass logins, private accounts, or platform restrictions.")
    with st.form("research_form"):
        name = st.text_input("Participant display name")
        li_url = st.text_input("LinkedIn public profile URL")
        ig_url = st.text_input("Instagram public profile URL")
        consent = st.checkbox("I confirm this adult participant has consented to this analysis and use in the dating-agent demo.")
        mode = st.radio("How will source information be provided?", ["Run configured Apify Actors", "Use participant-provided excerpts"], horizontal=False)
        li_text = ""
        ig_text = ""
        if mode == "Use participant-provided excerpts":
            li_text = st.text_area("LinkedIn information (participant-provided excerpt)", height=120)
            ig_text = st.text_area("Instagram information (participant-provided public captions/bio excerpt)", height=120)
        submitted = st.form_submit_button("Run research agent", type="primary")

    if submitted:
        if not name.strip() or not consent:
            st.error("Enter a name and confirm consent.")
        elif not li_url.startswith("https://www.linkedin.com/") or not ig_url.startswith("https://www.instagram.com/"):
            st.error("Enter the participant's official LinkedIn and Instagram profile URLs.")
        else:
            try:
                with st.spinner("Research agent is collecting and analysing the two authorized sources..."):
                    if mode == "Run configured Apify Actors":
                        raw = scrape_two_sources(li_url, ig_url)
                        knowledge = build_person_knowledge(name.strip(), raw["linkedin"], raw["instagram"])
                        source_status = "Apify extraction"
                    else:
                        if not li_text.strip() or not ig_text.strip():
                            raise ValueError("Provide excerpts from both sources.")
                        knowledge = build_from_participant_text(name.strip(), li_text, ig_text)
                        source_status = "Participant-provided excerpts"
                    pid = f"{name.strip()}::{li_url}"
                    st.session_state.profiles[pid] = {
                        "name": name.strip(), "linkedin_url": li_url, "instagram_url": ig_url,
                        "knowledge": knowledge, "source_status": source_status
                    }
                
                save_profiles(st.session_state.profiles)
                st.success(f"Research agent created a knowledge base for {name}.")
            except Exception as e:
                st.error(str(e))

with tab2:
    st.divider()
    st.subheader("Emergency demo setup")

    if st.button(
            "Create two fictional demo participants",
            key="create_demo_profiles"
    ):
            create_demo_profiles()
            st.success("Two fictional demo profiles saved locally!")
            st.rerun()
    st.subheader("Research agent memory")
    if not st.session_state.profiles:
        st.info("Create at least two participant knowledge bases first.")
    else:
        keys = list(st.session_state.profiles.keys())
        chosen = st.selectbox("Choose profile", keys, format_func=lambda k: st.session_state.profiles[k]["name"])
        p = st.session_state.profiles[chosen]
        st.markdown(f"### {p['name']}")
        st.caption(f"Source mode: {p['source_status']}")
        st.json(p["knowledge"])
        st.download_button("Download knowledge base JSON", json.dumps(p["knowledge"], indent=2), file_name="knowledge_base.json", mime="application/json")
        st.divider()
   

with tab3:
    st.subheader("Two agents dating")
    if len(st.session_state.profiles) < 2:
        st.warning("Create two participant knowledge bases before starting a date.")
    else:
        keys = list(st.session_state.profiles.keys())
        col1, col2 = st.columns(2)
        with col1:
            key_a = st.selectbox("Dating Agent A represents", keys, format_func=lambda k: st.session_state.profiles[k]["name"], key="agent_a")
        with col2:
            key_b = st.selectbox("Dating Agent B represents", keys, index=1, format_func=lambda k: st.session_state.profiles[k]["name"], key="agent_b")
        turns = st.slider("Conversation rounds", 1, 3, 2)
        if st.button("▶ Start agent-to-agent date", type="primary"):
            if key_a == key_b:
                st.error("Choose two different participants.")
            else:
                a, b = st.session_state.profiles[key_a], st.session_state.profiles[key_b]
                try:
                    with st.spinner("Two independent agents are conversing using their own research-agent knowledge bases..."):
                        result = run_date(
    a["name"],
    a["knowledge"],
    b["name"],
    b["knowledge"],
    turns=turns,
    demo_mode=True
)
                    st.session_state.last_date = result
                except Exception as e:
                    st.error(f"Dating session failed: {e}")

    result = st.session_state.last_date
    if result:
        if result.get("demo_mode"):
            st.warning("DEMO MODE — Conversation generated locally using fictional participant profiles. No Gemini API calls were made.")
        st.markdown(f"### {result['participant_a']} × {result['participant_b']}")
        for line in result["transcript"].split("\n\n"):
            if ": " in line:
                who, msg = line.split(": ", 1)
            else:
                who = "Agent"
                msg = line
            with st.chat_message("assistant" if who == result["participant_a"] + "'s agent" else "user"):
                st.markdown(f"**{who}**")
                st.write(msg)
        st.divider()
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(f"**{result['participant_a']}'s independent decision**")
            st.json(result["decision_a"])
        with c2:
            st.markdown(f"**{result['participant_b']}'s independent decision**")
            st.json(result["decision_b"])
        if result["mutual_interest"]:
            st.success("Both agents independently indicated interest.")
        else:
            st.info("This is not a mutual-interest match. Review each agent's independent decision.")
        st.download_button("Download conversation and decisions", json.dumps(result, indent=2), file_name="dating_session.json", mime="application/json")

st.divider()
st.caption("Important: Agent conclusions are experimental suggestions, not verified statements about a person. Participants should review their profiles and consent to any use of the results. The system does not infer sensitive traits.")
