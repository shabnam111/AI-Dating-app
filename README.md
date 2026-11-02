# Personal AI Dating Agents — MVP v2

## Architecture

1. Apify Actors (one LinkedIn Actor + one Instagram Actor) collect data only where permitted and with participant consent.
2. Research Agent (Gemini) reads those two datasets and creates one structured, evidence-backed knowledge base per participant.
3. Dating Agent A receives only Person A's knowledge base.
4. Dating Agent B receives only Person B's knowledge base.
5. The two dating agents alternate messages. Each agent's own knowledge and conversation history shape its messages.
6. Each agent independently evaluates whether it recommends exploring a first meeting.

## Setup (VS Code)

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
```

Add your own `GEMINI_API_KEY` and `APIFY_API_TOKEN` to `.env`.

Run:
```bash
streamlit run app.py
```

## Configure Apify

The Apify API can run Actors and return their default dataset items. Each Actor has its own input schema, so this app deliberately does not hardcode a third-party Actor ID or pretend every scraper uses the same input.

1. In Apify Store, choose an Actor appropriate for each source.
2. Review its permissions, terms, data handling, and input schema.
3. Test the Actor manually with an authorized participant profile.
4. Copy its Actor ID into `LINKEDIN_ACTOR_ID` or `INSTAGRAM_ACTOR_ID`.
5. Set the corresponding JSON input template in `.env`, replacing the target URL with `__PROFILE_URL__`.

Example templates are only examples; change them to match the exact Actor input schema:
```env
LINKEDIN_ACTOR_INPUT_TEMPLATE={"profileUrls":["__PROFILE_URL__"]}
INSTAGRAM_ACTOR_INPUT_TEMPLATE={"directUrls":["__PROFILE_URL__"]}
```

The app runs Actors through Apify's synchronous dataset endpoint (up to the API's synchronous wait limit). If your Actor takes longer, it will need an asynchronous run-and-poll implementation.

If you cannot configure an Actor in time, choose "Use participant-provided excerpts". This still exercises the research-agent and dating-agent architecture, but it is not an Apify scraping demonstration.

## Important constraints

- Use consenting adults only.
- Publicly viewable does not automatically mean unrestricted scraping or permission to reuse personal data.
- Do not bypass login walls, access private accounts, evade platform controls, or scrape data contrary to platform terms.
- Only use the participant's LinkedIn and Instagram as source inputs. The participant's consent checkbox is an authorization confirmation, not a substitute for platform permission.
- Do not infer sensitive traits or intimate preferences.
- A generated agent message is not evidence that the human actually said or believes something.
- This is an experimental prototype, not a validated dating or psychological assessment.

## Time-saving demo flow

1. Create two participant profiles with consent and authorized source data.
2. Show each research agent's JSON knowledge base.
3. Start the two-agent date.
4. Show alternating personalized messages.
5. Show both independent decisions and the mutual-interest result.
