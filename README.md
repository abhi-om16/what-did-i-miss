# 💬 MIA — What Did I Miss?

**Catch up on conversations. Find decisions. Never miss an action item.**

MIA is a conversation catch-up assistant built with Python and Streamlit. It helps users quickly understand what happened in a conversation without having to read every message.

## 🚀 The Problem

Important decisions, deadlines, and tasks can get buried in long group chats. Catching up takes time, and it's easy to overlook something important.

## ✨ Features

- **Conversation Summary:** Get a concise overview of the conversation.
- **Action Item Detection:** Identify tasks mentioned in messages.
- **Deadline Detection:** Highlight detected deadlines.
- **Decision Tracking:** Extract important decisions from conversations.
- **Priority Inbox:** Review important items that need attention.
- **Supporting Evidence:** View the messages associated with detected tasks.
- **Demo Conversation:** Explore the app using sample messages.
- **Privacy-Focused Processing:** The current version uses Python-based rules to analyze pasted text without sending it to an external AI API.

## 🛠️ Tech Stack

- Python
- Streamlit
- Regular expressions and rule-based text processing
- Git and GitHub

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/abhi-om16/what-did-i-miss.git
cd what-did-i-miss
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to use MIA.

## 📁 Project Structure

```text
what-did-i-miss/
├── app.py
├── requirements.txt
├── .gitignore
├── .streamlit/
├── sample_data/
├── src/
└── tests/
```

- `app.py` — Streamlit user interface and application flow.
- `src/` — Conversation parsing, analysis, and prioritization logic.
- `sample_data/` — Sample conversation data.
- `tests/` — Project tests.
- `requirements.txt` — Python dependencies.
- `.streamlit/` — Streamlit configuration.

## 🔒 Privacy

The current version processes pasted conversation text using local Python rules and does not send it to an external AI API. Avoid pasting sensitive or confidential conversations into the application. Production deployment and data handling should be reviewed before using real private conversations.

## 🎯 Project Goal

MIA aims to make conversations easier to catch up on by turning scattered messages into clear summaries, decisions, and actionable tasks.

## 👨‍💻 Author

**Abhinav Om**

GitHub: [@abhi-om16](https://github.com/abhi-om16)

---

*Built as a learning project exploring Python, text processing, and Streamlit application development.*