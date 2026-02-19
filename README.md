# 🏥 Doctor Appointment Scheduling Agent

An AI-powered doctor appointment scheduling system built with **Google Gemini**, **FastAPI**, **React**, and **PostgreSQL**. The agent uses function calling to intelligently check doctor availability, book appointments, send email confirmations, create Google Calendar events, generate analytics reports, and push notifications to Slack.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5--flash-4285F4?logo=google)

---

## ✨ Features

- **Natural Language Scheduling** — Chat naturally to check availability and book appointments
- **Gemini Function Calling** — AI agent autonomously invokes tools to fulfill requests
- **Doctor Availability Check** — Real-time availability lookup with time-of-day preferences (morning/afternoon/evening)
- **Appointment Booking** — End-to-end booking with conflict detection
- **Email Confirmations** — Automatic HTML confirmation emails via Gmail SMTP
- **Google Calendar Integration** — Calendar events created via service account
- **Slack Notifications** — Analytics reports pushed to a Slack channel
- **Analytics & Reporting** — Appointment counts, patient stats, and summary reports
- **Session Management** — Multi-turn conversation history per user session
- **React Chat UI** — Clean, responsive chat interface with typing indicators and suggested prompts

---

## 🏗️ Architecture

```
┌──────────────┐       POST /api/chat       ┌──────────────────┐
│  React UI    │ ─────────────────────────►  │  FastAPI Backend  │
│  (port 3000) │ ◄─────────────────────────  │  (port 8002)     │
└──────────────┘                             └────────┬─────────┘
                                                      │
                                             ┌────────▼─────────┐
                                             │  Gemini Agent     │
                                             │  (Function Call)  │
                                             └────────┬─────────┘
                                                      │
                     ┌────────────────────────────────┼────────────────────────────┐
                     │                  │              │              │             │
              ┌──────▼──────┐  ┌───────▼──────┐ ┌────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
              │ PostgreSQL  │  │   Google     │ │  Gmail   │ │  Slack    │ │ Analytics │
              │ Database    │  │   Calendar   │ │  SMTP    │ │  Bot     │ │  Reports  │
              └─────────────┘  └──────────────┘ └──────────┘ └───────────┘ └───────────┘
```

---

## 📁 Project Structure

```
├── backend/                        # FastAPI backend
│   └── app/
│       ├── main.py                 # App entry point, CORS, routes
│       ├── api/routes/chat.py      # POST /api/chat, DELETE /api/session
│       ├── models/schemas.py       # Pydantic request/response models
│       └── services/agent_service.py  # Gemini agent with tool orchestration
│
├── src/                            # Core agent & tools
│   ├── agent_gemini.py             # Standalone CLI agent (Gemini)
│   ├── agent.py                    # Base agent module
│   └── mcp_tools/                  # Tool implementations
│       ├── database.py             # PostgreSQL CRUD (availability, booking)
│       ├── calendar_tool.py        # Google Calendar event creation
│       ├── email_tool.py           # Gmail SMTP confirmations
│       ├── slack_tool.py           # Slack channel notifications
│       └── analytics_tool.py       # Appointment analytics & reports
│
├── doctor-appointment-agent/
│   ├── frontend/                   # React chat UI
│   │   └── src/components/
│   │       ├── ChatInterface.js    # Main chat component
│   │       ├── Message.js          # Message bubble component
│   │       └── TypingIndicator.js  # Typing animation
│   ├── test_calendar.py            # Calendar integration tests
│   ├── test_email.py               # Email tool tests
│   ├── test_slack.py               # Slack tool tests
│   └── test_analytics.py           # Analytics tool tests
│
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not committed)
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Google Cloud project with Calendar API enabled
- Gmail account with App Password
- Slack workspace with a bot token (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/naveendhukia/Doctor-Appointment-Agent.git
cd Doctor-Appointment-Agent
```

### 2. Set Up Python Environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
pip install -r doctor-appointment-agent/requirements.txt
```

### 3. Set Up PostgreSQL Database

Create the database and tables:

```sql
CREATE DATABASE appointments;

\c appointments

CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE doctor_availability (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id),
    day_of_week INTEGER NOT NULL,  -- 0=Monday, 6=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id),
    patient_name VARCHAR(100) NOT NULL,
    patient_email VARCHAR(100),
    appointment_time TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    status VARCHAR(20) DEFAULT 'confirmed'
);

-- Seed doctors
INSERT INTO doctors (name, specialty, email) VALUES
    ('Dr. Ahuja', 'Cardiology', 'ahuja@clinic.com'),
    ('Dr. Sharma', 'Pediatrics', 'sharma@clinic.com');

-- Seed availability (0=Mon, 1=Tue, ..., 4=Fri)
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time) VALUES
    (1, 0, '09:00', '17:00'), (1, 1, '09:00', '17:00'), (1, 2, '09:00', '17:00'),
    (1, 4, '09:00', '12:00'),  -- Dr. Ahuja: Mon-Wed 9-5, Fri 9-12
    (2, 0, '09:00', '17:00'), (2, 1, '09:00', '17:00'), (2, 2, '09:00', '17:00'),
    (2, 3, '09:00', '17:00'), (2, 4, '09:00', '17:00');  -- Dr. Sharma: Mon-Fri 9-5
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key

# PostgreSQL
DB_HOST=localhost
DB_NAME=appointments
DB_USER=postgres
DB_PASSWORD=your_db_password

# Google Calendar (Service Account)
GOOGLE_CREDENTIALS_FILE=service-account-key.json
GOOGLE_CALENDAR_ID=your_email@gmail.com

# Gmail SMTP
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Slack (optional)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=your_channel_id
```

### 5. Google Calendar Setup (Service Account)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Google Calendar API**
3. Create a **Service Account** and download the JSON key
4. Save the key as `service-account-key.json` in the project root
5. Share your Google Calendar with the service account email (grant **Make changes to events** permission)

### 6. Start the Backend

```bash
# From the project root directory
python -m uvicorn backend.app.main:app --reload --port 8002
```

The API will be available at `http://localhost:8002`. Verify with:
```bash
curl http://localhost:8002/health
```

### 7. Start the Frontend

```bash
cd doctor-appointment-agent/frontend
npm install
npm start
```

The React app will open at `http://localhost:3000`.

### 8. Run the CLI Agent (Optional)

You can also use the agent directly from the terminal:

```bash
cd src
python agent_gemini.py
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Health status |
| `POST` | `/api/chat` | Send a message to the agent |
| `DELETE` | `/api/session/{id}` | Clear conversation session |

### POST `/api/chat`

**Request:**
```json
{
  "message": "Check Dr. Ahuja's availability tomorrow morning",
  "session_id": "uuid-string"
}
```

**Response:**
```json
{
  "response": "Dr. Ahuja is available tomorrow morning at the following times: 9:00 AM, 9:30 AM, 10:00 AM...",
  "session_id": "uuid-string",
  "appointment_id": null
}
```

---

## 🛠️ Tools (Function Calling)

The Gemini agent has access to these tools, invoked automatically based on user intent:

| Tool | Description |
|------|-------------|
| `check_availability` | Query PostgreSQL for a doctor's open time slots on a given date |
| `book_appointment` | Book a slot, create calendar event, and send confirmation email |
| `get_report` | Generate analytics reports (today's appointments, patient counts, summaries) |

---

## 🧪 Running Tests

```bash
# Test database connection
python test_db.py

# Test Google Calendar integration
cd doctor-appointment-agent
python test_calendar.py

# Test email sending
python test_email.py

# Test Slack bot
python test_slack.py
```

---

## 📋 Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Model** | Google Gemini 2.5 Flash (function calling) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | React 19, Axios, UUID |
| **Database** | PostgreSQL + psycopg2 |
| **Calendar** | Google Calendar API (Service Account) |
| **Email** | Gmail SMTP (App Password) |
| **Notifications** | Slack SDK (Bot Token) |
| **Styling** | Custom CSS |

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 👤 Author

**Naveen Dhukia**  
GitHub: [@naveendhukia](https://github.com/naveendhukia)