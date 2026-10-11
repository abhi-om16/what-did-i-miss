
import streamlit as st

from src.parser import parse_conversation
from src.analyzer import analyze_messages, build_summary
from src.prioritizer import prioritize_items


# --------------------------------------------------
# CONFIGURATION AND DEMO DATA
# --------------------------------------------------

st.set_page_config(
    page_title="MIA — What Did I Miss?",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEMO_CONVERSATION = (
    "Monday 09:10 — Aisha: The project demo is Friday at 3 PM.\n"
    "Monday 09:12 — Rahul: I'll finish the slides by Thursday.\n"
    "Monday 09:15 — Meera: We still need someone to test the app.\n"
    "Monday 09:20 — Aisha: Abhi, can you test the app by Thursday "
    "evening and report any bugs?\n"
    "Monday 09:24 — Rahul: Decision: we'll use the new dashboard "
    "design for the demo.\n"
    "Monday 09:30 — Meera: I'll send the test checklist tomorrow."
)


def load_demo_conversation():
    st.session_state["conversation_input"] = DEMO_CONVERSATION


def analyze_current_conversation():
    conversation = st.session_state.get("conversation_input", "")

    if not conversation.strip():
        st.session_state["analysis_error"] = (
            "Paste a conversation or load the demo first."
        )
        return

    messages = parse_conversation(conversation)
    analysis = analyze_messages(messages)

    analysis["summary"] = build_summary(messages, analysis)
    analysis["priority_items"] = prioritize_items(
        analysis["key_points"]
    )

    st.session_state["analysis_result"] = analysis
    st.session_state.pop("analysis_error", None)


def render_task(task):
    """Display a task with its status, deadline, and evidence."""

    description = (
        task.get("description")
        or task.get("text")
        or "Task description unavailable"
    )

    owner = task.get("owner", "Unspecified")
    deadline = task.get("deadline")
    status = task.get("status", "Open")
    evidence = task.get("evidence", [])

    with st.container(border=True):
        st.markdown(f"**{description}**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Owner:** {owner}")

        with col2:
            if status.casefold() == "confirmed":
                st.success("✓ Confirmed")
            else:
                st.info("○ Open")

        if deadline:
            st.caption(f"📅 Detected deadline: {deadline}")
        else:
            st.caption("📅 No deadline detected")

        if evidence:
            with st.expander("View supporting messages"):
                for index, message in enumerate(evidence, start=1):
                    sender = message.get("sender", "Unknown")
                    message_text = message.get("text", "")

                    st.markdown(f"**{index}. {sender}**")
                    st.write(message_text)
        else:
            st.caption("No supporting messages were recorded.")


# --------------------------------------------------
# CUSTOM LIGHT-THEME STYLING
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --paper: #F7F6F0;
    --green: #245B45;
    --ink: #26352C;
    --muted: #7B8279;
    --line: #E6E5DC;
    --coral: #D8795B;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--paper);
}

.block-container {
    padding-top: 2.1rem;
    padding-bottom: 4rem;
    max-width: 1250px;
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--green);
    letter-spacing: -1.5px;
}

.brand-mark {
    color: var(--coral);
}

.eyebrow {
    color: var(--green);
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(2.3rem, 4.5vw, 3.7rem);
    line-height: 1.12;
    letter-spacing: -2px;
    font-weight: 800;
    color: var(--ink);
    margin: 0.6rem 0 0.8rem 0;
}

.hero-title span {
    color: var(--green);
}

.hero-subtitle {
    color: var(--muted);
    font-size: 1.05rem;
    line-height: 1.8;
    max-width: 660px;
}

.section-title {
    font-family: 'Manrope', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--ink);
    margin-bottom: 0.25rem;
}

.section-subtitle {
    color: var(--muted);
    font-size: 0.9rem;
}

.panel {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1.3rem;
}

.metric-label {
    color: var(--muted);
    font-size: 0.82rem;
}

.metric-number {
    font-family: 'Manrope', sans-serif;
    color: var(--ink);
    font-size: 1.8rem;
    font-weight: 800;
}

.priority {
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin: 0.65rem 0;
    background: #FFFFFF;
    border: 1px solid var(--line);
}

.priority-critical {
    border-left: 4px solid var(--coral);
}

.priority-normal {
    border-left: 4px solid #78A78A;
}

.priority-title {
    font-weight: 700;
    color: var(--ink);
}

.priority-meta {
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: 0.25rem;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 2.8rem;
    transition: all 0.15s ease;
}

.stButton > button[kind="primary"] {
    background: var(--green);
    border: 1px solid var(--green);
    color: white;
}

.stButton > button[kind="primary"]:hover {
    background: #17432F;
    border-color: #17432F;
}

div[data-testid="stTextArea"] textarea {
    background: #FFFFFF;
    border-radius: 12px;
    border-color: var(--line);
    line-height: 1.7;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--green);
}

hr {
    border-color: var(--line);
}

@media (max-width: 768px) {
    .block-container {
        padding: 1.2rem 1rem 3rem;
    }

    .hero-title {
        letter-spacing: -1px;
    }
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">✳</span> mia.</div>',
        unsafe_allow_html=True,
    )

    st.caption("YOUR CONVERSATION COMPASS")
    st.divider()

    st.markdown("**WORKSPACE**")

    page = st.radio(
        "Navigation",
        [
            "✳  Catch-up",
            "☷  Action items",
            "◷  History",
            "⚙  Privacy",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("**YOUR DATA**")
    st.markdown("`SESSION-BASED`")
    st.caption("Conversations are not saved as permanent history.")

    st.divider()

    st.caption("MIA · WHAT DID I MISS?")
    st.caption("Built for the unread problem.")


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    '<div class="eyebrow">A CLEARER WAY TO CATCH UP</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">Less scrolling.<br>'
    '<span>More knowing.</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-subtitle">'
    'Your conversations move fast. MIA helps you find the decisions, '
    'deadlines and little things you cannot afford to miss.'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")


# --------------------------------------------------
# CATCH-UP PAGE
# --------------------------------------------------

if page == "✳  Catch-up":

    left, right = st.columns([1.45, 0.85], gap="large")

    with left:
        st.markdown(
            '<div class="section-title">Bring me up to speed</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Paste an unread conversation to begin your catch-up.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        st.text_area(
            "Conversation",
            height=260,
            placeholder=(
                "Paste a group chat, meeting transcript, or conversation "
                "export here...\n\n"
                "Tip: include timestamps and sender names when available."
            ),
            label_visibility="collapsed",
            key="conversation_input",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.button(
                "✳  Catch me up",
                type="primary",
                use_container_width=True,
                on_click=analyze_current_conversation,
            )

        with col2:
            st.button(
                "Load demo conversation",
                use_container_width=True,
                on_click=load_demo_conversation,
            )

        if st.session_state.get("analysis_error"):
            st.warning(st.session_state["analysis_error"])

    with right:
        st.markdown(
            '<div class="section-title">'
            'Your catch-up, at a glance</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'A preview of the information MIA will surface.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        st.markdown("""
        <div class="panel">
          <div class="metric-label">WHAT MATTERS MOST</div>
          <div class="metric-number">Your priorities</div>
          <hr>
          <div class="priority priority-critical">
            <div class="priority-title">↗ Upcoming deadline</div>
            <div class="priority-meta">Time-sensitive messages</div>
          </div>
          <div class="priority priority-normal">
            <div class="priority-title">☷ Pending action</div>
            <div class="priority-meta">Tasks and assignments</div>
          </div>
          <div class="priority priority-normal">
            <div class="priority-title">◇ Team decision</div>
            <div class="priority-meta">Agreements and changes</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.caption(
            "Illustrative preview. Actual results appear in the report below."
        )

    # --------------------------------------------------
    # ACTUAL ANALYSIS RESULTS
    # --------------------------------------------------

    result = st.session_state.get("analysis_result")

    if result:
        st.divider()
        st.markdown("## Your catch-up report")

        st.caption(
            "Rule-based analysis. Verify extracted information "
            "against the original conversation."
        )

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric("Messages read", result["message_count"])
        metric2.metric("Action items", len(result["tasks"]))
        metric3.metric("Decisions", len(result["decisions"]))

        st.markdown("### The short version")

        for point in result["summary"]:
            st.markdown(f"- {point}")

        # PRIORITY INBOX

        st.markdown("### Your priority inbox")

        if result["priority_items"]:
            for item in result["priority_items"]:
                with st.container(border=True):
                    st.markdown(
                        f"**{item['priority']} priority** · "
                        f"{item['sender']}"
                    )

                    st.write(item["text"])

                    details = []

                    if item.get("deadline"):
                        details.append(
                            f"Detected deadline: {item['deadline']}"
                        )

                    if item.get("mentions"):
                        details.append(
                            "Mentions: " + ", ".join(item["mentions"])
                        )

                    if details:
                        st.caption(" · ".join(details))
        else:
            st.info(
                "No urgent or explicitly time-sensitive messages "
                "were detected."
            )

        # ACTION ITEMS

        st.markdown("### Action items")

        if result["tasks"]:
            for task in result["tasks"]:
                render_task(task)
        else:
            st.write("No recognizable action items were detected.")

        # DECISIONS

        st.markdown("### Decisions")

        if result["decisions"]:
            for decision in result["decisions"]:
                st.markdown(f"- {decision['text']}")
        else:
            st.write("No explicit decisions were detected.")


# --------------------------------------------------
# ACTION ITEMS PAGE
# --------------------------------------------------

elif page == "☷  Action items":

    st.markdown("## Action items")
    st.caption("Tasks, ownership, deadlines, and supporting messages.")

    result = st.session_state.get("analysis_result")

    if result and result["tasks"]:
        for task in result["tasks"]:
            render_task(task)

        st.caption(
            "Owners, status, and deadlines are rule-based estimates. "
            "Verify them against the original conversation."
        )
    else:
        st.info(
            "Analyze a conversation first. Your extracted tasks "
            "will appear here."
        )


# --------------------------------------------------
# HISTORY PAGE
# --------------------------------------------------

elif page == "◷  History":

    st.markdown("## Catch-up history")

    st.info(
        "Persistent history has not been implemented. "
        "Results are held in the current Streamlit session."
    )


# --------------------------------------------------
# PRIVACY PAGE
# --------------------------------------------------

elif page == "⚙  Privacy":

    st.markdown("## Your privacy")

    st.markdown("### Current processing")

    st.write(
        "This version analyzes pasted text using Python rules. "
        "It does not send conversations to an external AI API."
    )

    st.markdown("### Storage")

    st.write(
        "The application runs on a remote server when deployed. "
        "Session-based processing is not the same as on-device processing."
    )

    st.markdown("### Before production")

    st.write(
        "Session retention, data handling, and the final privacy "
        "architecture must be tested and documented before production."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("MIA · Make room for what matters.")
