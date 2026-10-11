
import re


def parse_conversation(text: str) -> list[dict]:
    """Convert a chat export into structured messages."""

    messages = []

    # Supports formats such as:
    # Monday 09:10 — Aisha: The demo is Friday.
    # [09:10] Aisha: The demo is Friday.
    # Aisha: The demo is Friday.
    pattern = re.compile(
        r"^(?:\[([^\]]+)\]\s*)?"
        r"(?:(.*?)\s+[—–-]\s*)?"
        r"([^:\n]+):\s*(.*)$"
    )

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        match = pattern.match(line)

        if match:
            bracket_time, prefix, sender, content = match.groups()

            # Avoid treating an empty sender or malformed line as valid.
            if content.strip():
                timestamp = bracket_time or (prefix or "").strip()

                messages.append({
                    "timestamp": timestamp,
                    "sender": sender.strip(),
                    "text": content.strip(),
                })
                continue

        # Preserve messages that do not match a known chat format.
        messages.append({
            "timestamp": "",
            "sender": "Unknown",
            "text": line,
        })

    return messages
