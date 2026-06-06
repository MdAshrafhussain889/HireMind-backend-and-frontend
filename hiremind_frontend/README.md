# SmartSkale HireMind AI — Frontend

Next.js 14 frontend for the HireMind assessment platform. Connects to the FastAPI backend at `http://127.0.0.1:8000`.

## Quick Start

### 1. Install dependencies

```bash
cd hiremind_frontend
npm install
```

### 2. Configure environment

```bash
cp .env.local.example .env.local
```

Set `NEXT_PUBLIC_API_URL` to your backend URL (default `http://127.0.0.1:8000`).

### 3. Start backend (separate terminal)

```bash
cd ../hiremind_backend
docker-compose up
# or: uvicorn app.main:app --reload --port 8000
```

### 4. Run frontend

```bash
npm run dev
```

Open **http://localhost:3000**

## Demo Flow

1. **Register** as recruiter → create assessment with AI questions → **Publish (Active)**
2. Copy the **candidate join link** from the assessment detail page
3. **Register** as candidate (incognito / another browser) → open join link
4. Complete MCQ + coding questions → **Submit**
5. Back as recruiter → click **AI Evaluate** on the submitted attempt
6. View scores in the attempts table

## Pages

| Route | Role | Description |
|-------|------|-------------|
| `/` | Public | Landing page |
| `/login` | Public | Sign in |
| `/register` | Public | Create account |
| `/recruiter` | Recruiter | Dashboard + attempts |
| `/recruiter/assessments/new` | Recruiter | Create assessment |
| `/recruiter/assessments/[id]` | Recruiter | Assessment detail + join link |
| `/candidate` | Candidate | Dashboard + join by ID |
| `/candidate/join/[id]` | Candidate | Start attempt |
| `/candidate/attempt/[id]` | Candidate | Test UI (MCQ, Monaco, timer, proctoring) |

## Stack

- Next.js 14 (App Router)
- TypeScript + Tailwind CSS
- Zustand (auth state)
- Monaco Editor (coding questions)
