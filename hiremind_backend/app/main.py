from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import Base, engine
from app.api.routes import auth, assessments, ai, code, proctoring, reports, attempts, websocket

# Import models so SQLAlchemy registers them
import app.models.user  # noqa: F401

settings = get_settings()

app = FastAPI(
    title="SmartSkale HireMind AI",
    description="Enterprise AI Hiring & Assessment Platform — Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create tables on startup (use Alembic in production) ─────────────────────
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(assessments.router)
app.include_router(ai.router)
app.include_router(code.router)
app.include_router(proctoring.router)
app.include_router(reports.router)
app.include_router(attempts.router)
app.include_router(websocket.router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "HireMind AI", "version": "1.0.0"}


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "SmartSkale HireMind AI API",
        "docs": "/docs",
        "health": "/health",
    }
