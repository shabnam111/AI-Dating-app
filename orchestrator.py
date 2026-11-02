def _facts(knowledge, section):
    items = knowledge.get(section, [])
    facts = []

    for item in items:
        if isinstance(item, dict):
            fact = item.get("fact", "")
        else:
            fact = str(item)

        if fact:
            facts.append(fact)

    return facts


def _demo_speak(own_name, own_knowledge, partner_name, transcript, turn):
    interests = _facts(own_knowledge, "interests")
    hobbies = _facts(own_knowledge, "hobbies")
    professional = _facts(own_knowledge, "professional_background")
    topics = _facts(own_knowledge, "conversation_topics")

    if turn % 2 == 1:
        if interests:
            detail = interests[0]
        elif hobbies:
            detail = hobbies[0]
        elif professional:
            detail = professional[0]
        else:
            detail = "learning new things"

        return (
            f"Hi {partner_name}! One thing about me is {detail}. "
            f"What are some interests or activities you enjoy?"
        )

    if hobbies:
        detail = hobbies[0]
        return (
            f"That sounds interesting! I also enjoy {detail}. "
            f"What would you usually choose for a relaxing weekend?"
        )

    if topics:
        return (
            f"I'd enjoy talking more about {topics[0]}. "
            f"What do you find most interesting about it?"
        )

    if interests:
        return (
            f"I'd like to know more about your interests. "
            f"What is something you've enjoyed learning recently?"
        )

    return (
        f"It's nice getting to know you, {partner_name}. "
        f"What is something you enjoy doing in your free time?"
    )


def _demo_decision(own_name, own_knowledge, partner_name, transcript):
    # The local demo cannot establish genuine human attraction or consent.
    return {
        "interest": "maybe",
        "reasons": [
            "This is a simulated demonstration, not a real participant decision.",
            "The agent used its own participant knowledge base during the conversation."
        ],
        "open_questions": [
            "Would the actual participant be interested in continuing?",
            "Are their expectations and preferences compatible?"
        ],
        "confidence": 0
    }


def run_date(
    name_a,
    knowledge_a,
    name_b,
    knowledge_b,
    turns=3,
    progress_callback=None,
    demo_mode=False
):
    """Alternating two-agent conversation."""

    transcript_lines = []

    for turn in range(1, turns + 1):

        if demo_mode:
            msg_a = _demo_speak(
                name_a, knowledge_a, name_b,
                "\n".join(transcript_lines), turn
            )
        else:
            from dating_agents import agent_speak
            msg_a = agent_speak(
                name_a, knowledge_a, name_b,
                "\n".join(transcript_lines), turn
            )

        transcript_lines.append(f"{name_a}'s agent: {msg_a}")

        if progress_callback:
            progress_callback(name_a, msg_a)

        if demo_mode:
            msg_b = _demo_speak(
                name_b, knowledge_b, name_a,
                "\n".join(transcript_lines), turn
            )
        else:
            msg_b = agent_speak(
                name_b, knowledge_b, name_a,
                "\n".join(transcript_lines), turn
            )

        transcript_lines.append(f"{name_b}'s agent: {msg_b}")

        if progress_callback:
            progress_callback(name_b, msg_b)

    transcript = "\n\n".join(transcript_lines)

    if demo_mode:
        decision_a = _demo_decision(
            name_a, knowledge_a, name_b, transcript
        )
        decision_b = _demo_decision(
            name_b, knowledge_b, name_a, transcript
        )
    else:
        from dating_agents import agent_decision
        decision_a = agent_decision(
            name_a, knowledge_a, name_b, transcript
        )
        decision_b = agent_decision(
            name_b, knowledge_b, name_a, transcript
        )

    return {
        "participant_a": name_a,
        "participant_b": name_b,
        "transcript": transcript,
        "decision_a": decision_a,
        "decision_b": decision_b,
        "demo_mode": demo_mode,
        "mutual_interest": (
            decision_a.get("interest") == "interested"
            and decision_b.get("interest") == "interested"
        )
    }
