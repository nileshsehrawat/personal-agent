# 🤖 Personal Agent

A powerful, AI-integrated personal assistant that lives in your Telegram. Designed to manage your tasks, track your habits, remember important details, and schedule your life—all through a clean, service-oriented architecture.

## 🚀 Current Features
- **Task Management**: Create, list, complete, and delete tasks.
- **Habit Tracking**: Track daily/weekly habits with automatic streak calculation.
- **Event Scheduling**: Manage upcoming events and schedules.
- **Personal Memory**: A digital "second brain" to store and retrieve important facts.
- **Dual Interface**:
  - **Telegram Bot**: Direct command-based interaction (`/today`, `/tasks`, etc.).
  - **REST API**: Fully documented Swagger UI for programmatic access.
- **AI-Powered**: Integrated with **Groq (Llama 3)** for natural conversation.

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **LLM**: Groq API (Llama 3.3 70B)
- **Deployment**: Render.com
- **Interface**: Telegram Bot API

---

## ⚙️ Setup Instructions

If you want to host your own version of this agent, follow these steps:

### 1. Prerequisites
- Python 3.10+
- A Telegram account
- A Groq API account

### 2. Local Setup
1. **Clone the repo:**
   ```bash
   git clone <your-repo-url>
   cd personal-agent
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key
   ```

### 3. Telegram Bot Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram.
2. Create a new bot and copy the **API Token**.
3. Set your bot's domain (once deployed) using the Webhook URL:
   `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<YOUR_APP_URL>/webhook`

### 4. Deployment
This project is pre-configured for **Render**.
1. Push your code to GitHub.
2. Create a "Web Service" on Render.
3. Add your `TELEGRAM_TOKEN` and `GROQ_API_KEY` to the Environment tab.

---

## 📅 Roadmap & Future Plans

- [ ] **Phase 4: AI Tool Calling**: Move beyond commands. The AI will understand natural language like *"Remind me to call the doctor tomorrow"* and automatically call the `create_task` function.
- [ ] **Phase 5: Daily Briefings**: Automated morning messages summarizing your day's tasks, events, and habit streaks.
- [ ] **Phase 6: Advanced Integrations (n8n)**: Connecting the agent to external tools like Google Calendar, Gmail, and Notion.
- [ ] **Phase 7: Vector Memory**: Using RAG (Retrieval-Augmented Generation) to handle thousands of personal memories efficiently.

---

## 🤝 Contributing
Feel free to fork this project, open issues, or submit pull requests. Let's build the ultimate personal assistant!
