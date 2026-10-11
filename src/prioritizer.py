
def priority_score(item: dict) -> int:
    text = item["text"].lower()
    score = 0

    # Explicit urgency
    score += item.get("urgency", 0) * 3

    # Deadlines and time sensitivity
    if item.get("deadline"):
        score += 3

    if any(word in text for word in [
        "today", "tonight", "asap", "immediately", "overdue",
    ]):
        score += 3

    # Directly relevant information
    if item.get("mentions"):
        score += 2

    if item.get("owner") not in (None, "", "Unspecified"):
        score += 1

    # Decisions can affect multiple people
    if any(word in text for word in [
        "decision:", "decided", "agreed", "final decision",
    ]):
        score += 2

    return score


def prioritize_items(items: list[dict]) -> list[dict]:
    ranked = []

    for item in items:
        ranked_item = dict(item)
        ranked_item["priority_score"] = priority_score(item)

        score = ranked_item["priority_score"]

        if score >= 9:
            ranked_item["priority"] = "High"
        elif score >= 4:
            ranked_item["priority"] = "Medium"
        else:
            ranked_item["priority"] = "Low"

        ranked.append(ranked_item)

    return sorted(
        ranked,
        key=lambda item: (
            -item["priority_score"],
            item.get("index", 0),
        ),
    )
