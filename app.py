
import csv
import io
import re
from datetime import datetime

import streamlit as st


# ============================================================
# MIA — Message Intelligence Assistant
# ============================================================

st.set_page_config(
    page_title="MIA | Message Intelligence Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    "Catch-up",
    "Action items",
    "Decisions",
    "Messages",
    "History",
    "Privacy",
]

DEMO_CONVERSATION = """Aisha: The project demo is Friday at 3 PM.
Rahul: I will finish the login page by tomorrow.
Priya: We need to test the dashboard before the demo.
Aisha: Let's use Streamlit for the final prototype.
Rahul: Agreed. I'll push the updated code to GitHub tonight.
Priya: I will prepare the presentation by Thursday.
Aisha: Please share the final slides in the group.
Rahul: We decided to keep the first version simple and add authentication later.
Priya: The testing meeting is scheduled for Thursday at 5 PM.
Aisha: Everyone should review the final prototype before Friday."""


# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    defaults = {
        "page": "Catch-up",
        "conversation_input": "",
        "messages": [],
        "summary": "",
        "tasks": [],
        "decisions": [],
        "history": [],
        "analysis_complete": False,
        "analysis_error": "",
        "analysis_id": 0,
        "message_search": "",
        "history_search": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ============================================================
# CALLBACKS
# ============================================================

def navigate(page):
    st.session_state.page = page


def load_demo():
    st.session_state.conversation_input = DEMO_CONVERSATION
    st.session_state.analysis_error = ""


def load_uploaded_text():
    uploaded = st.session_state.get("conversation_file")

    if uploaded is None:
        return

    try:
        raw = uploaded.getvalue()
        st.session_state.conversation_input = raw.decode("utf-8-sig")
        st.session_state.analysis_error = ""

    except (UnicodeDecodeError, AttributeError):
        st.session_state.analysis_error = (
            "Couldn't read this file as UTF-8 text. "
            "Please upload a UTF-8 encoded .txt file."
        )


def clear_current_analysis():
    st.session_state.conversation_input = ""
    st.session_state.messages = []
    st.session_state.summary = ""
    st.session_state.tasks = []
    st.session_state.decisions = []
    st.session_state.analysis_complete = False
    st.session_state.analysis_error = ""
    st.session_state.analysis_id += 1
    st.session_state.message_search = ""


def clear_history():
    st.session_state.history = []
    st.session_state.history_search = ""


# ============================================================
# CONVERSATION PARSING
# ============================================================

def parse_conversation(text):
    """Parse messages in Sender: message format."""

    messages = []
    current = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        match = re.match(r"^([^:\n]{1,80}):\s*(.*)$", line)

        if match:
            if current:
                messages.append(current)

            current = {
                "sender": match.group(1).strip() or "Unknown",
                "text": match.group(2).strip(),
            }

        elif current:
            current["text"] = (
                current["text"] + " " + line
            ).strip()

        else:
            current = {
                "sender": "Unknown",
                "text": line,
            }

    if current:
        messages.append(current)

    return [
        message
        for message in messages
        if message["text"]
    ]


# ============================================================
# DEADLINE AND PRIORITY DETECTION
# ============================================================

DEADLINE_PATTERNS = [
    r"\bday after tomorrow\b",
    r"\b(?:today|tonight|tomorrow)\b",
    r"\b(?:this|next)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|week|month)\b",
    r"\bby\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|EOD|end of day|end of week|tonight|tomorrow)\b",
    r"\b(?:at|by|on)\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM)\b",
    r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\b",
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
]


def find_deadline(text):
    for pattern in DEADLINE_PATTERNS:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(0)

    return "Not specified"


def get_priority(text):
    if re.search(
        r"\b(urgent|asap|immediately|critical|high priority)\b",
        text,
        re.IGNORECASE,
    ):
        return "High"

    if re.search(
        r"\b(important|soon|before the demo|before the deadline)\b",
        text,
        re.IGNORECASE,
    ):
        return "Medium"

    return "Normal"


# ============================================================
# ACTION ITEM EXTRACTION
# ============================================================

ACTION_PATTERNS = [
    r"\bi will\b",
    r"\bi'll\b",
    r"\bwe will\b",
    r"\bwe'll\b",
    r"\bplease\b",
    r"\bneed to\b",
    r"\bneeds to\b",
    r"\bmust\b",
    r"\bshould\b",
    r"\bhas to\b",
    r"\bhave to\b",
    r"\baction item\b",
    r"\bto[- ]do\b",
    r"\bsubmit\b",
    r"\bsend\b",
    r"\bprepare\b",
    r"\bcomplete\b",
    r"\bfinish\b",
    r"\breview\b",
    r"\bcheck\b",
    r"\bupdate\b",
    r"\bshare\b",
    r"\bbring\b",
    r"\bbook\b",
    r"\bcall\b",
    r"\bemail\b",
    r"\bupload\b",
    r"\bdeploy\b",
    r"\bfix\b",
    r"\bcreate\b",
    r"\btest\b",
    r"\bschedule\b",
    r"\bconfirm\b",
    r"\bimplement\b",
    r"\bdeliver\b",
    r"\bpush\b",
]


def is_action_item(text):
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in ACTION_PATTERNS
    )


def extract_tasks(messages):
    tasks = []
    seen = set()

    for message in messages:
        text = message["text"]

        if not is_action_item(text):
            continue

        key = text.casefold().strip()

        if key in seen:
            continue

        seen.add(key)

        cleaned = re.sub(
            r"^(please\s+|action item:\s*|todo:\s*)",
            "",
            text.strip(),
            flags=re.IGNORECASE,
        )

        tasks.append({
            "text": cleaned,
            "owner": message["sender"],
            "deadline": find_deadline(text),
            "priority": get_priority(text),
            "done": False,
            "source": text,
        })

    return tasks


# ============================================================
# DECISION EXTRACTION
# ============================================================

DECISION_PATTERNS = [
    r"\bdecided\b",
    r"\bdecision\b",
    r"\bagreed\b",
    r"\bwe'll go with\b",
    r"\bwe will use\b",
    r"\bwe are going with\b",
    r"\bselected\b",
    r"\bconfirmed\b",
    r"\bfinalized\b",
    r"\bfinalised\b",
    r"\bsettled on\b",
    r"\bapproved\b",
    r"\bwe chose\b",
    r"\bgoing with\b",
]


def extract_decisions(messages):
    decisions = []
    seen = set()

    for message in messages:
        text = message["text"]

        is_decision = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in DECISION_PATTERNS
        )

        if not is_decision:
            continue

        key = text.casefold().strip()

        if key not in seen:
            seen.add(key)

            decisions.append({
                "text": text,
                "sender": message["sender"],
            })

    return decisions


# ============================================================
# SUMMARY GENERATION
# ============================================================

def create_summary(messages, tasks, decisions):
    if not messages:
        return "No conversation content was found."

    participants = list(dict.fromkeys(
        message["sender"]
        for message in messages
    ))

    lines = [
        (
            f"The conversation contains {len(messages)} message(s) "
            f"from {len(participants)} participant(s)."
        ),
        "Participants: " + ", ".join(participants) + ".",
    ]

    important_words = [
        "meeting",
        "demo",
        "deadline",
        "important",
        "urgent",
        "schedule",
        "problem",
        "blocked",
    ]

    important = [
        message["text"]
        for message in messages
        if any(
            word in message["text"].lower()
            for word in important_words
        )
    ]

    if important:
        lines.append("\nPotentially important points:")

        lines.extend(
            f"- {item}"
            for item in list(dict.fromkeys(important))[:6]
        )

    if decisions:
        lines.append("\nLikely decisions:")

        lines.extend(
            f"- {decision['text']} "
            f"(mentioned by {decision['sender']})"
            for decision in decisions[:6]
        )

    if tasks:
        lines.append("\nLikely action items:")

        for task in tasks[:8]:
            deadline = (
                f" — Deadline: {task['deadline']}"
                if task["deadline"] != "Not specified"
                else ""
            )

            lines.append(
                f"- {task['text']} "
                f"(Owner: {task['owner']}){deadline}"
            )

    lines.append(
        "\nNote: MIA uses rule-based detection. "
        "Verify important items against the original messages."
    )

    return "\n".join(lines)


# ============================================================
# ANALYSIS
# ============================================================

def run_analysis():
    source = st.session_state.conversation_input.strip()

    if not source:
        st.session_state.analysis_error = (
            "Paste a conversation or load the demo before analyzing."
        )
        st.session_state.analysis_complete = False
        return

    messages = parse_conversation(source)

    if not messages:
        st.session_state.analysis_error = (
            "No readable messages were found. "
            "Use Sender: message format."
        )
        st.session_state.analysis_complete = False
        return

    tasks = extract_tasks(messages)
    decisions = extract_decisions(messages)
    summary = create_summary(messages, tasks, decisions)

    st.session_state.messages = messages
    st.session_state.tasks = tasks
    st.session_state.decisions = decisions
    st.session_state.summary = summary
    st.session_state.analysis_complete = True
    st.session_state.analysis_error = ""
    st.session_state.analysis_id += 1

    st.session_state.history.append({
        "timestamp": datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        ),
        "source_text": source,
        "messages": [dict(m) for m in messages],
        "summary": summary,
        "tasks": [dict(t) for t in tasks],
        "decisions": [dict(d) for d in decisions],
    })


# ============================================================
# HISTORY RESTORATION
# ============================================================

def restore_history(item):
    st.session_state.conversation_input = item["source_text"]

    st.session_state.messages = [
        dict(message)
        for message in item["messages"]
    ]

    st.session_state.tasks = [
        dict(task)
        for task in item["tasks"]
    ]

    st.session_state.decisions = [
        dict(decision)
        for decision in item["decisions"]
    ]

    st.session_state.summary = item["summary"]
    st.session_state.analysis_complete = True
    st.session_state.analysis_error = ""
    st.session_state.analysis_id += 1
    st.session_state.page = "Catch-up"


# ============================================================
# REPORT EXPORT
# ============================================================

def export_report():
    lines = [
        "MIA — MESSAGE INTELLIGENCE ASSISTANT",
        "=" * 42,
        "",
        "SUMMARY",
        st.session_state.summary or "No summary available.",
        "",
        "ACTION ITEMS",
    ]

    if st.session_state.tasks:
        for task in st.session_state.tasks:
            status = "x" if task["done"] else " "

            lines.append(
                f"- [{status}] {task['text']} | "
                f"Owner: {task['owner']} | "
                f"Deadline: {task['deadline']} | "
                f"Priority: {task['priority']}"
            )
    else:
        lines.append("No action items detected.")

    lines.extend(["", "DECISIONS"])

    if st.session_state.decisions:
        lines.extend(
            f"- {decision['text']} "
            f"(mentioned by {decision['sender']})"
            for decision in st.session_state.decisions
        )
    else:
        lines.append("No decisions detected.")

    lines.extend([
        "",
        "ORIGINAL CONVERSATION",
        st.session_state.conversation_input,
    ])

    return "\n".join(lines)


def action_items_csv():
    buffer = io.StringIO()

    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "task",
            "owner",
            "deadline",
            "priority",
            "completed",
        ],
    )

    writer.writeheader()

    for task in st.session_state.tasks:
        writer.writerow({
            "task": task["text"],
            "owner": task["owner"],
            "deadline": task["deadline"],
            "priority": task["priority"],
            "completed": task["done"],
        })

    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# 💬 MIA")
    st.caption("Message Intelligence Assistant")
    st.divider()

    st.radio(
        "Navigate",
        PAGES,
        key="page",
    )

    st.divider()
    st.markdown("### Workspace")

    st.metric("Messages", len(st.session_state.messages))
    st.metric("Action items", len(st.session_state.tasks))
    st.metric("Decisions", len(st.session_state.decisions))

    st.caption("History lasts for the current Streamlit session only.")
    st.divider()

    st.button(
        "Load demo conversation",
        use_container_width=True,
        on_click=load_demo,
    )

    st.button(
        "Clear current analysis",
        use_container_width=True,
        on_click=clear_current_analysis,
    )

    if st.session_state.history:
        st.button(
            "Clear history",
            use_container_width=True,
            on_click=clear_history,
        )


page = st.session_state.page


# ============================================================
# PAGE 1: CATCH-UP
# ============================================================

if page == "Catch-up":
    st.title("💬 Catch up on your conversations")

    st.write(
        "Paste a group chat or meeting discussion. MIA extracts "
        "likely key points, action items, deadlines, priorities, "
        "and decisions."
    )

    st.info(
        "Expected format: one message per line, "
        "for example `Aisha: The demo is Friday.`"
    )

    st.file_uploader(
        "Or upload a plain-text conversation (.txt)",
        type=["txt"],
        key="conversation_file",
        on_change=load_uploaded_text,
        help="Use Sender: message format and UTF-8 encoding.",
    )

    st.text_area(
        "Conversation text",
        key="conversation_input",
        height=250,
        placeholder=(
            "Aisha: The demo is Friday.\n"
            "Rahul: I will finish the login page by tomorrow."
        ),
    )

    left, right = st.columns(2)

    with left:
        st.button(
            "✨ Analyze conversation",
            type="primary",
            use_container_width=True,
            on_click=run_analysis,
        )

    with right:
        st.button(
            "View action items →",
            use_container_width=True,
            on_click=navigate,
            args=("Action items",),
        )

    if st.session_state.analysis_error:
        st.error(st.session_state.analysis_error)

    if st.session_state.analysis_complete:
        st.divider()
        st.subheader("Your catch-up report")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Messages",
            len(st.session_state.messages),
        )

        col2.metric(
            "Participants",
            len(set(
                message["sender"]
                for message in st.session_state.messages
            )),
        )

        col3.metric(
            "Action items",
            len(st.session_state.tasks),
        )

        col4.metric(
            "Decisions",
            len(st.session_state.decisions),
        )

        st.markdown("### 📝 Summary")
        st.markdown(st.session_state.summary)

        left, right = st.columns(2)

        with left:
            st.markdown("### ✅ Action items")

            if st.session_state.tasks:
                for task in st.session_state.tasks[:5]:
                    st.markdown(
                        f"- **{task['text']}** — {task['owner']} · "
                        f"Deadline: {task['deadline']} · "
                        f"Priority: {task['priority']}"
                    )
            else:
                st.write("No likely action items detected.")

            st.button(
                "Open all action items →",
                on_click=navigate,
                args=("Action items",),
                use_container_width=True,
            )

        with right:
            st.markdown("### 📌 Decisions")

            if st.session_state.decisions:
                for decision in st.session_state.decisions[:5]:
                    st.markdown(
                        f"- {decision['text']} "
                        f"*(mentioned by {decision['sender']})*"
                    )
            else:
                st.write("No likely decisions detected.")

            st.button(
                "Open all decisions →",
                on_click=navigate,
                args=("Decisions",),
                use_container_width=True,
            )

        d1, d2 = st.columns(2)

        with d1:
            st.download_button(
                "⬇️ Download full report (.txt)",
                data=export_report(),
                file_name="mia_report.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with d2:
            st.download_button(
                "Download tasks (.csv)",
                data=action_items_csv(),
                file_name="mia_action_items.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with st.expander("View parsed conversation"):
            for message in st.session_state.messages:
                st.markdown(
                    f"**{message['sender']}:** {message['text']}"
                )


# ============================================================
# PAGE 2: ACTION ITEMS
# ============================================================

elif page == "Action items":
    st.title("✅ Action items")

    st.write(
        "Track tasks, owners, deadlines, and likely priority. "
        "Check off tasks as you complete them."
    )

    if not st.session_state.analysis_complete:
        st.info("Analyze a conversation first.")

        st.button(
            "Go to Catch-up",
            on_click=navigate,
            args=("Catch-up",),
        )

    elif not st.session_state.tasks:
        st.success("No likely action items were detected.")

    else:
        tasks = st.session_state.tasks

        completed = sum(
            1 for task in tasks
            if task["done"]
        )

        st.progress(completed / len(tasks))
        st.caption(
            f"{completed} of {len(tasks)} tasks completed"
        )

        f1, f2 = st.columns(2)

        with f1:
            filter_choice = st.selectbox(
                "Filter tasks",
                [
                    "All tasks",
                    "Pending only",
                    "Completed only",
                    "Deadlines identified",
                    "High priority",
                ],
            )

        with f2:
            owner_options = ["All owners"] + sorted(
                set(task["owner"] for task in tasks)
            )

            owner_choice = st.selectbox(
                "Filter by owner",
                owner_options,
            )

        for index, task in enumerate(tasks):
            if filter_choice == "Pending only" and task["done"]:
                continue

            if filter_choice == "Completed only" and not task["done"]:
                continue

            if (
                filter_choice == "Deadlines identified"
                and task["deadline"] == "Not specified"
            ):
                continue

            if (
                filter_choice == "High priority"
                and task["priority"] != "High"
            ):
                continue

            if (
                owner_choice != "All owners"
                and task["owner"] != owner_choice
            ):
                continue

            with st.container(border=True):
                checkbox_key = (
                    f"task_done_{st.session_state.analysis_id}_{index}"
                )

                def update_task(i=index, key=checkbox_key):
                    st.session_state.tasks[i]["done"] = bool(
                        st.session_state.get(key, False)
                    )

                st.checkbox(
                    task["text"],
                    value=task["done"],
                    key=checkbox_key,
                    on_change=update_task,
                )

                st.caption(
                    f"Owner: {task['owner']} · "
                    f"Deadline: {task['deadline']} · "
                    f"Priority: {task['priority']}"
                )

                with st.expander("View original message"):
                    st.write(task["source"])

        st.download_button(
            "Download action items (.csv)",
            data=action_items_csv(),
            file_name="mia_action_items.csv",
            mime="text/csv",
        )


# ============================================================
# PAGE 3: DECISIONS
# ============================================================

elif page == "Decisions":
    st.title("📌 Decisions")

    st.write(
        "Review messages that appear to record an agreement, "
        "choice, approval, or finalized plan."
    )

    if not st.session_state.analysis_complete:
        st.info("Analyze a conversation first.")

        st.button(
            "Go to Catch-up",
            on_click=navigate,
            args=("Catch-up",),
        )

    elif not st.session_state.decisions:
        st.info(
            "No likely decisions were detected. "
            "The conversation may use different wording."
        )

    else:
        st.caption(
            f"{len(st.session_state.decisions)} likely decision(s) found"
        )

        for index, decision in enumerate(
            st.session_state.decisions,
            start=1,
        ):
            with st.container(border=True):
                st.markdown(f"**Decision {index}**")
                st.write(decision["text"])
                st.caption(f"Mentioned by: {decision['sender']}")

        decisions_text = "\n".join(
            f"- {decision['text']} "
            f"(mentioned by {decision['sender']})"
            for decision in st.session_state.decisions
        )

        st.download_button(
            "Download decisions (.txt)",
            data=decisions_text,
            file_name="mia_decisions.txt",
            mime="text/plain",
        )


# ============================================================
# PAGE 4: SEARCH MESSAGES
# ============================================================

elif page == "Messages":
    st.title("🔎 Search messages")

    st.write(
        "Search the analyzed conversation for a keyword, "
        "name, deadline, or phrase."
    )

    if not st.session_state.analysis_complete:
        st.info("Analyze a conversation first.")

        st.button(
            "Go to Catch-up",
            on_click=navigate,
            args=("Catch-up",),
        )

    else:
        query = st.text_input(
            "Search messages",
            key="message_search",
            placeholder="Try: Friday, Rahul, demo...",
        ).casefold().strip()

        matching = [
            (index, message)
            for index, message in enumerate(
                st.session_state.messages,
                start=1,
            )
            if query in (
                message["sender"] + " " + message["text"]
            ).casefold()
        ]

        st.caption(
            f"{len(matching)} matching message(s) out of "
            f"{len(st.session_state.messages)}"
        )

        if matching:
            for number, message in matching:
                with st.container(border=True):
                    st.caption(
                        f"Message {number} · {message['sender']}"
                    )
                    st.write(message["text"])
        else:
            st.info("No messages match that search.")


# ============================================================
# PAGE 5: HISTORY
# ============================================================

elif page == "History":
    st.title("🕘 Conversation history")

    st.write(
        "Previous analyses are available during the current session."
    )

    history = st.session_state.history

    if not history:
        st.info(
            "No history yet. Analyze a conversation to create your first entry."
        )

        st.button(
            "Go to Catch-up",
            on_click=navigate,
            args=("Catch-up",),
        )

    else:
        query = st.text_input(
            "Search history",
            key="history_search",
            placeholder="Search conversations or summaries...",
        ).casefold().strip()

        filtered = [
            (index, item)
            for index, item in enumerate(history)
            if query in (
                item["source_text"] + " " + item["summary"]
            ).casefold()
        ]

        filtered.reverse()

        st.caption(
            f"{len(filtered)} matching conversation(s)"
        )

        for original_index, item in filtered:
            with st.container(border=True):
                st.markdown(
                    f"**Analysis from {item['timestamp']}**"
                )

                st.caption(
                    f"{len(item['messages'])} messages · "
                    f"{len(item['tasks'])} action items · "
                    f"{len(item['decisions'])} decisions"
                )

                st.write(item["summary"])

                st.button(
                    "Restore this conversation",
                    key=f"restore_history_{original_index}",
                    on_click=restore_history,
                    args=(item,),
                    use_container_width=True,
                )

                with st.expander("View original conversation"):
                    st.text(item["source_text"])

        history_export = "\n\n".join(
            (
                f"DATE: {item['timestamp']}\n"
                f"{item['summary']}\n\n"
                f"ORIGINAL CONVERSATION:\n{item['source_text']}"
            )
            for item in reversed(history)
        )

        st.download_button(
            "Export history (.txt)",
            data=history_export,
            file_name="mia_history.txt",
            mime="text/plain",
        )

        st.warning(
            "Clearing history removes entries from this active session."
        )

        st.button(
            "Clear all history",
            on_click=clear_history,
        )


# ============================================================
# PAGE 6: PRIVACY
# ============================================================

elif page == "Privacy":
    st.title("🔒 Privacy and data handling")

    st.markdown("""
### How this version of MIA works

- **Session-only storage:** conversations and history are held in
  Streamlit session state during the active session.
- **No database configured:** this version does not intentionally save
  conversations to a database or user account.
- **Rule-based analysis:** task, deadline, priority, and decision detection
  uses Python text patterns. No external AI API is required.
- **File support:** upload plain-text `.txt` conversations and download reports.
- **Search:** search messages and the current session's history.

### Important limitations

Session state is not permanent storage. Data may disappear when the
session resets, the app restarts, or the hosting environment changes.
Clearing the current analysis does not clear history; use the Clear history
button if you want to remove history from the active session.

Avoid pasting passwords, private credentials, or highly sensitive personal
information. If publicly deployed, review the hosting provider's data-handling
policies before using confidential conversations.
""")

    st.divider()
    st.subheader("Current workspace")

    st.write(
        f"- Messages loaded: {len(st.session_state.messages)}"
    )

    st.write(
        f"- Action items detected: {len(st.session_state.tasks)}"
    )

    st.write(
        f"- Saved history entries: {len(st.session_state.history)}"
    )

    st.warning(
        "MIA is a rule-based prototype. Verify important deadlines, "
        "decisions, and task ownership against the original messages."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "MIA · Message Intelligence Assistant · "
    "Rule-based prototype · Session-only history"
)
