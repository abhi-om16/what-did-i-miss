
import re


TASK_PATTERNS = [
    r"\bneed(?:s)? to\b",
    r"\bmust\b",
    r"\bplease\b",
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bwill you\b",
    r"\bassigned to\b",
    r"\baction item\b",
    r"\bto[- ]do\b",
    r"\bI(?:'ll| will)\b",
    r"\bwe(?:'ll| will) need to\b",
]

DECISION_PATTERNS = [
    r"\bdecision\s*:",
    r"\bwe decided\b",
    r"\bdecided that\b",
    r"\bagreed that\b",
    r"\bwe agreed\b",
    r"\bagreed to\b",
    r"\bfinal decision\b",
    r"\bwe will use\b",
    r"\bwe'll use\b",
    r"\blet's use\b",
]

DEADLINE_PATTERN = re.compile(
    r"\b(today|tonight|tomorrow|"
    r"this evening|this afternoon|"
    r"monday|tuesday|wednesday|thursday|"
    r"friday|saturday|sunday|next week|"
    r"\d{1,2}\s*(?:am|pm)|"
    r"\d{1,2}(?:st|nd|rd|th)?\s+"
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
    r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
    r"nov(?:ember)?|dec(?:ember)?)"
    r")\b",
    re.IGNORECASE,
)

CONFIRMATION_PATTERN = re.compile(
    r"^\s*(?:yes|yep|yeah|sure|okay|ok|got it|"
    r"i will|i'll|i can)\b",
    re.IGNORECASE,
)


def find_deadline(text: str) -> str | None:
    match = DEADLINE_PATTERN.search(text)
    return match.group(0) if match else None


def detect_urgency(text: str) -> int:
    text_lower = text.lower()
    score = 0

    if any(word in text_lower for word in [
        "urgent", "asap", "immediately", "overdue"
    ]):
        score += 2

    if any(word in text_lower for word in [
        "today", "tonight", "tomorrow", "deadline"
    ]):
        score += 1

    return min(score, 3)


def is_task(text: str) -> bool:
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in TASK_PATTERNS
    )


def is_decision(text: str) -> bool:
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in DECISION_PATTERNS
    )


def is_confirmation(text: str) -> bool:
    return bool(CONFIRMATION_PATTERN.search(text))


def extract_mentions(text: str) -> list[str]:
    return list(dict.fromkeys(
        re.findall(r"(?<!\w)@([A-Za-z][A-Za-z0-9_.-]*)", text)
    ))


def extract_owner(text: str, sender: str) -> str:
    patterns = [
        r"^\s*([A-Z][A-Za-z0-9_-]*),\s*can you\b",
        r"^\s*([A-Z][A-Za-z0-9_-]*),\s*please\b",
        r"\bassigned to\s+([A-Z][A-Za-z0-9_-]*)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    if re.search(r"\bI(?:'ll| will)\b", text, re.IGNORECASE):
        return sender if sender != "Unknown" else "Unspecified"

    return "Unspecified"


def extract_task_description(text: str) -> str:
    """Normalize common request and confirmation wording."""
    text = re.sub(
        r"^\s*[A-Z][A-Za-z0-9_-]*,\s*",
        "",
        text,
    )
    text = re.sub(
        r"^\s*(?:yes|yep|yeah|sure|okay|ok|got it)[,! ]*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^\s*(?:can you|could you|please)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^\s*(?:I'll|I will)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", text).strip(" .,!?")


def analyze_messages(messages: list[dict]) -> dict:
    tasks = []
    decisions = []
    key_points = []
    seen_decisions = set()

    for index, message in enumerate(messages):
        text = message["text"]
        sender = message["sender"]

        if is_decision(text):
            key = text.casefold()
            if key not in seen_decisions:
                decisions.append({
                    **message,
                    "index": index,
                    "deadline": find_deadline(text),
                    "urgency": detect_urgency(text),
                    "mentions": extract_mentions(text),
                })
                seen_decisions.add(key)

        # Requests such as "Can you finish X?" create tasks.
        # Confirmation messages are attached to existing tasks below.
        if is_task(text) and not is_confirmation(text):
            owner = extract_owner(text, sender)
            deadline = find_deadline(text)

            task = {
                **message,
                "index": index,
                "owner": owner,
                "deadline": deadline,
                "urgency": detect_urgency(text),
                "mentions": extract_mentions(text),
                "status": "Open",
                "evidence": [message],
                "description": extract_task_description(text),
            }

            # Merge repeated requests for the same owner and work.
            duplicate = next(
                (
                    existing for existing in tasks
                    if existing["owner"].casefold() == owner.casefold()
                    and existing["description"].casefold()
                    == task["description"].casefold()
                ),
                None,
            )

            if duplicate:
                if message not in duplicate["evidence"]:
                    duplicate["evidence"].append(message)
                if not duplicate["deadline"] and deadline:
                    duplicate["deadline"] = deadline
            else:
                tasks.append(task)

    # Match confirmations to an earlier task from the same owner.
    for index, message in enumerate(messages):
        text = message["text"]
        sender = message["sender"]

        if not is_confirmation(text):
            continue

        for task in tasks:
            if task["index"] >= index:
                continue

            if task["owner"].casefold() != sender.casefold():
                continue

            confirmation_deadline = find_deadline(text)

            # If both messages specify a deadline, they must agree.
            if (
                task["deadline"]
                and confirmation_deadline
                and task["deadline"].casefold()
                != confirmation_deadline.casefold()
            ):
                continue

            if message not in task["evidence"]:
                task["evidence"].append(message)

            task["status"] = "Confirmed"

            if not task["deadline"] and confirmation_deadline:
                task["deadline"] = confirmation_deadline

            break

    task_indexes = {task["index"] for task in tasks}

    # Include task records once, not their confirmation messages separately.
    for task in tasks:
        if (
            task["deadline"]
            or task["urgency"] >= 2
            or task["mentions"]
        ):
            key_points.append(task)

    # Keep urgent non-task messages and explicit mentions.
    for index, message in enumerate(messages):
        if index in task_indexes:
            continue

        text = message["text"]
        urgency = detect_urgency(text)
        mentions = extract_mentions(text)

        if urgency >= 2 or mentions:
            key_points.append({
                **message,
                "index": index,
                "deadline": find_deadline(text),
                "urgency": urgency,
                "mentions": mentions,
            })

    return {
        "message_count": len(messages),
        "tasks": tasks,
        "decisions": decisions,
        "key_points": key_points,
    }


def build_summary(messages: list[dict], analysis: dict) -> list[str]:
    if not messages:
        return ["No readable messages were found."]

    summary = [
        f"Conversation contains {len(messages)} messages."
    ]

    for decision in analysis["decisions"][:3]:
        summary.append(f"Decision: {decision['text']}")

    for task in analysis["tasks"][:3]:
        deadline_text = (
            f" — deadline: {task['deadline']}"
            if task["deadline"]
            else ""
        )
        summary.append(
            f"Action: {task['description']}{deadline_text}"
        )

    if len(summary) == 1:
        summary.append(
            "No explicit decisions or recognizable action items "
            "were detected. Review the original messages."
        )

    return summary
