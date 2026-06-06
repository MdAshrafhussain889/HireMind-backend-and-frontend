# SmartSkale HireMind AI

AI-Powered Hiring and Assessment Platform built using FastAPI, Next.js, PostgreSQL, Redis, OpenAI, and Judge0.

## Overview

SmartSkale HireMind AI is an intelligent recruitment platform that helps organizations conduct AI-assisted hiring assessments through:

* Candidate Registration & Authentication
* Recruiter Dashboard
* MCQ Assessments
* Coding Assessments
* AI Question Generation
* AI-Based Candidate Evaluation
* Live Proctoring
* Performance Analytics & Reports
* Judge0 Code Execution Engine

---

## Project Structure

```text
HireMind-backend-and-frontend
│
├── hiremind_backend
│   ├── app
│   ├── alembic
│   ├── judge0
│   ├── requirements.txt
│   └── docker-compose.yml
│
├── hiremind_frontend
│   ├── src
│   ├── package.json
│   └── next.config.mjs
│
└── README.md
```

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL
* Redis
* JWT Authentication
* OpenAI API
* Judge0

### Frontend

* Next.js 14
* React
* TypeScript
* Tailwind CSS
* Zustand

### Database

* PostgreSQL 16

### Cache

* Redis 7

### AI Services

* OpenAI GPT Models
* Judge0 Code Execution API

---

## Prerequisites

Install the following software:

* Python 3.10
* Node.js 18+
* Docker Desktop
* Git

---

## Backend Setup

Navigate to backend folder:

```bash
cd hiremind_backend
```

Create virtual environment:

```bash
py -3.10 -m venv venv
```

Activate environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create `.env` file inside backend folder:

```env
DATABASE_URL=postgresql://hiremind:password@127.0.0.1:5432/hiremind
REDIS_URL=redis://localhost:6379/0

OPENAI_API_KEY=YOUR_OPENAI_KEY

JUDGE0_API_URL=http://127.0.0.1:2358
JUDGE0_API_KEY=

JWT_SECRET=YOUR_SECRET_KEY
JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://127.0.0.1:8000

ENVIRONMENT=development

PROCTORING_ENABLED=true
AI_EVALUATION_ENABLED=true
```

---

## Start PostgreSQL & Redis

```bash
docker compose up -d db redis
```

Verify:

```bash
docker ps
```

---

## Run Database Migrations

```bash
python -m alembic upgrade head
```

---

## Start Backend

```bash
uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Navigate to frontend folder:

```bash
cd hiremind_frontend
```

Install dependencies:

```bash
npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Run frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

---

## Judge0 Setup (Optional)

Start Judge0 locally:

```bash
docker compose -f docker-compose.judge0.yml up -d
```

Judge0 URL:

```text
http://127.0.0.1:2358
```

---

## Features

### Recruiter

* Create Assessments
* Generate AI Questions
* Monitor Candidates
* View Reports
* Candidate Evaluation

### Candidate

* Register/Login
* Attempt MCQ Tests
* Attempt Coding Challenges
* AI-Assisted Assessment
* View Results

### AI Services

* GPT Question Generation
* Candidate Evaluation
* Performance Feedback
* Automated Scoring

---

## API Endpoints

### Authentication

```text
/api/auth/register
/api/auth/login
/api/auth/me
```

### Assessments

```text
/api/assessments
/api/assessments/list
```

### Attempts

```text
/api/attempts
/api/attempts/recruiter/all
```

### AI

```text
/api/ai
```

### Reports

```text
/api/reports
```

### Proctoring

```text
/api/proctoring
```

---

## Author

**Mohammed Ashraf Hussain**


---

## License

This project is intended for educational, research, and recruitment platform development purposes.
