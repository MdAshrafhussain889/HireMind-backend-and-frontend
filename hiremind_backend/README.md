# SmartSkale HireMind AI — Backend

FastAPI backend for the SmartSkale HireMind AI hiring & assessment platform.

## Stack
- **FastAPI** + Uvicorn
- **PostgreSQL** via SQLAlchemy + Alembic
- **Redis** (Celery-ready)
- **OpenAI GPT-4o** — question generation & evaluation
- **Judge0** — sandboxed code execution
- **JWT** auth + Google OAuth
- **ReportLab** — PDF report generation
- **WebSockets** — live proctoring stream

---

## Quick Start

### 1. Clone & configure
```bash
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY at minimum
```

### 2. Option A — Docker Compose (recommended)
```bash
docker-compose up --build
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 3. Option B — Local (venv)
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL + Redis (or use Docker just for them)
docker-compose up db redis -d

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Register candidate/recruiter |
| POST | /api/auth/login | JWT login |
| POST | /api/auth/google | Google OAuth |
| GET  | /api/auth/me | Current user |
| POST | /api/assessments/create | Create assessment (recruiter) |
| GET  | /api/assessments/list | List assessments (recruiter) |
| GET  | /api/assessments/{id} | Get assessment |
| GET  | /api/assessments/{id}/questions | Get questions |
| POST | /api/attempts/start/{assessment_id} | Start attempt (candidate) |
| POST | /api/attempts/{id}/answers | Save MCQ/aptitude answers |
| POST | /api/attempts/{id}/submit | Submit attempt |
| GET  | /api/attempts/my | My attempts (candidate) |
| GET  | /api/attempts/recruiter/all | All attempts (recruiter) |
| POST | /api/ai/generate-questions | GPT-4o question generation |
| POST | /api/ai/evaluate | GPT-4o candidate evaluation |
| POST | /api/ai/adaptive-difficulty | Next difficulty level |
| POST | /api/code/submit | Execute code via Judge0 |
| GET  | /api/code/languages | Supported languages |
| POST | /api/proctor/event | Log proctoring event |
| GET  | /api/proctor/session/{id}/summary | Proctoring summary |
| GET  | /api/reports/{candidate_id} | JSON or PDF report |
| WS   | /ws/proctor/{session_id} | Live proctoring WebSocket |

Full interactive docs: **http://localhost:8000/docs**

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | No | Redis URL (default localhost) |
| `OPENAI_API_KEY` | **Yes** | Your OpenAI API key |
| `JUDGE0_API_URL` | Yes | Judge0 API base URL |
| `JUDGE0_API_KEY` | Optional | RapidAPI Judge0 key for code execution |
| `JWT_SECRET` | Yes | 256-bit secret for JWT signing |
| `GOOGLE_CLIENT_ID` | Optional | For Google OAuth |

---

## Project Structure

```
hiremind_backend/
├── app/
│   ├── api/routes/
│   │   ├── auth.py          # Registration, login, OAuth
│   │   ├── assessments.py   # CRUD for assessments
│   │   ├── attempts.py      # Start/submit attempts
│   │   ├── ai.py            # GPT-4o question gen & evaluation
│   │   ├── code.py          # Judge0 code execution
│   │   ├── proctoring.py    # Violation event logging
│   │   ├── reports.py       # JSON + PDF reports
│   │   └── websocket.py     # Live proctoring WebSocket
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy engine & session
│   │   └── security.py      # JWT, bcrypt, RBAC
│   ├── models/user.py       # SQLAlchemy ORM models
│   ├── schemas/schemas.py   # Pydantic request/response schemas
│   ├── services/
│   │   ├── ai_service.py    # OpenAI GPT-4o wrapper
│   │   └── judge0_service.py # Judge0 API wrapper
│   └── main.py              # FastAPI app + router registration
├── alembic/                 # Database migrations
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Generating Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Notes
- The AI evaluation endpoint (`POST /api/ai/evaluate`) requires the attempt to have code submissions and MCQ answers stored.
- Without a Judge0 key, code execution routes will return 502. You can get a free tier at https://rapidapi.com/judge0-official/api/judge0-ce
- PDF reports require no extra setup (ReportLab is pure Python).
