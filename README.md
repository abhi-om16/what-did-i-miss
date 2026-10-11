
# MIA — Message Intelligence Assistant

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://what-did-i-miss-3g7jrmn8kt4v8rj8zsjguq.streamlit.app/)

**Turn long group conversations into clear summaries, decisions, and actionable tasks.**

MIA (Message Intelligence Assistant) is a Python-based web application built with Streamlit that helps users catch up on group conversations without reading every message. It analyzes conversation text and organizes potentially important information into summaries, action items, decisions, and searchable messages.

🚀 **Live Demo:** [Try MIA here](https://what-did-i-miss-3g7jrmn8kt4v8rj8zsjguq.streamlit.app/)

---

## ✨ Features

### 📝 Conversation Catch-up
- Generates a concise catch-up report from conversation messages.
- Identifies participants and counts messages.
- Highlights potentially important points.
- Displays likely decisions and action items.

### ✅ Action Item Extraction
- Detects potential tasks from messages.
- Attempts to identify task owners and deadlines.
- Assigns priority levels based on detected keywords and rules.
- Supports marking tasks as completed.
- Provides filters for task status, deadlines, priority, and owner.

### 📌 Decision Detection
- Identifies likely decisions using rule-based text analysis.
- Displays detected decisions along with the person who mentioned them.

### 🔎 Message Search
- Search analyzed conversations using keywords.
- Quickly find relevant messages without manually scanning the entire conversation.

### 📂 Conversation Input
- Paste conversation text into the application.
- Upload `.txt` files containing conversations.
- Use a built-in demo conversation to explore the app.

### 🕘 Conversation History
- View previously analyzed conversations during the current session.
- Restore a previous conversation for review.
- Clear the available session history.

### 📤 Export and Reports
- Download conversation reports as text files (`.txt`).
- Export extracted action items as CSV files (`.csv`).

### 🔐 Privacy Information
- Includes a dedicated page explaining the application's data handling.
- Conversation history is session-based rather than a permanent database.

---

## 🛠️ Tech Stack

- **Language:** Python
- **Frontend and Web Framework:** Streamlit
- **Text Processing:** Rule-based analysis and keyword matching
- **Data Export:** TXT and CSV

---

## ⚙️ How It Works

1. **Input:** Paste a conversation or upload a `.txt` file.
2. **Analyze:** MIA processes messages using predefined rules and keywords.
3. **Summarize:** View participants, message counts, and important points.
4. **Organize:** Review potential tasks, owners, deadlines, priorities, and decisions.
5. **Search:** Find specific messages using keywords.
6. **Export:** Download a report or action items for later reference.

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

Replace the placeholders with your actual GitHub repository URL and folder name.

### 2. Install dependencies

```bash
python -m pip install streamlit pandas
```

### 3. Launch the application

```bash
python -m streamlit run app.py
```

The application will open in your browser at the local address shown in the terminal.

---

## 📋 Expected Input Format

MIA expects conversation messages in a sender-and-message format:

```text
Aisha: We need to finalize the project.
Rahul: I will complete the login page by tomorrow.
Priya: I will test the dashboard by Friday.
Aisha: We decided to use Streamlit for the prototype.
```

For best results, keep each message on a separate line and use the format `Sender: message`.

---

## 🎯 Use Cases

- **College Projects:** Keep track of team discussions, tasks, and deadlines.
- **Hackathons:** Organize project responsibilities and important decisions.
- **Group Work:** Quickly catch up on conversations after being away.
- **Team Coordination:** Search for commitments and review action items.

---

## ⚠️ Current Limitations

MIA is an early-stage, rule-based prototype.

- Task, deadline, priority, and decision detection may be inaccurate.
- Task ownership may be misidentified when a message mentions another person.
- Summaries depend on predefined rules rather than a large language model.
- Conversation history is session-based and is not intended as permanent storage.
- Direct integration with messaging platforms such as WhatsApp or Discord is not currently available.

Important results should be checked against the original conversation.

---

## 🔮 Future Improvements

Potential areas for further development include:

- More accurate task ownership and deadline extraction.
- Better handling of completed, pending, and overdue tasks.
- Context-aware conversation summarization.
- Improved handling of ambiguous messages and follow-up replies.
- Optional integration with language models.
- Direct integrations with supported messaging platforms.
- Persistent storage and user accounts.

---

## 👨‍💻 Project Status

**Status:** Working prototype

MIA demonstrates how rule-based text processing can turn unstructured conversation messages into organized, searchable information through a simple web interface.

---

## 🌐 Try the App

**[Launch MIA — Message Intelligence Assistant](https://what-did-i-miss-3g7jrmn8kt4v8rj8zsjguq.streamlit.app/)**

---

*Built with Python and Streamlit.*
