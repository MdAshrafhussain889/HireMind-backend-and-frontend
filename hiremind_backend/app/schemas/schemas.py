from __future__ import annotations
from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Auth ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # candidate | recruiter | admin

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        if v not in ("candidate", "recruiter", "admin"):
            raise ValueError("Role must be candidate, recruiter, or admin")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Assessment ───────────────────────────────────────────────────────────────

class AssessmentCreateRequest(BaseModel):
    title: str
    role: str
    types: List[str]
    duration_minutes: int = 60
    proctoring: bool = True
    adaptive: bool = False


class AssessmentOut(BaseModel):
    id: UUID
    title: str
    role: str
    types: List[str]
    duration_minutes: int
    proctoring_enabled: bool
    adaptive: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Questions ────────────────────────────────────────────────────────────────

class QuestionOut(BaseModel):
    id: UUID
    type: str
    difficulty: str
    prompt: str
    options: Optional[List[str]] = None
    test_cases: Optional[List[dict]] = None
    points: int
    order: int

    class Config:
        from_attributes = True


# ── AI Services ──────────────────────────────────────────────────────────────

class GenerateQuestionsRequest(BaseModel):
    role: str
    skills: List[str]
    difficulty: str = "medium"
    types: List[str]
    count: int = 5


class EvaluateRequest(BaseModel):
    attempt_id: UUID
    code_submissions: List[dict] = Field(default_factory=list)   # optional override
    mcq_answers: List[dict] = Field(default_factory=list)         # optional override
    proctoring_data: Optional[dict] = None


# ── Code Submission ───────────────────────────────────────────────────────────

class CodeSubmitRequest(BaseModel):
    code: str
    language: str   # python|java|cpp|js|sql
    question_id: UUID
    attempt_id: UUID


class CodeSubmitResponse(BaseModel):
    passed_cases: int
    total_cases: int
    verdict: str
    runtime_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    failed_cases: List[dict] = Field(default_factory=list)


class MCQAnswerItem(BaseModel):
    question_id: UUID
    answer_index: Optional[int] = None
    answer_text: Optional[str] = None


class MCQAnswersSubmitRequest(BaseModel):
    answers: List[MCQAnswerItem]


class MCQAnswerOut(BaseModel):
    question_id: UUID
    answer_index: Optional[int] = None
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


# ── Proctoring ───────────────────────────────────────────────────────────────

class ProctorEventRequest(BaseModel):
    session_id: UUID   # attempt_id
    event_type: str
    timestamp: datetime
    frame_snapshot: Optional[str] = None  # base64
    metadata: Optional[dict] = None


# ── Reports ──────────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    candidate_id: UUID
    attempt_id: UUID
    total_score: Optional[float]
    technical_score: Optional[float]
    behavioral_score: Optional[float]
    evaluation_report: Optional[dict]
    proctoring_summary: Optional[dict]
    submitted_at: Optional[datetime]

    class Config:
        from_attributes = True
