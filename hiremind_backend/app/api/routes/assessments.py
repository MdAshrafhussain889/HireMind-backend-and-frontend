from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import Assessment, Question
from app.schemas.schemas import AssessmentCreateRequest, AssessmentOut, QuestionOut

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])


@router.post("/create", response_model=AssessmentOut, status_code=201)
def create_assessment(
    payload: AssessmentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter", "admin")),
):
    assessment = Assessment(
        recruiter_id=current_user.id,
        title=payload.title,
        role=payload.role,
        types=payload.types,
        duration_minutes=payload.duration_minutes,
        proctoring_enabled=payload.proctoring,
        adaptive=payload.adaptive,
        status="draft",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/list", response_model=List[AssessmentOut])
def list_assessments(
    status: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter", "admin")),
):
    query = db.query(Assessment).filter(Assessment.recruiter_id == current_user.id)
    if status:
        query = query.filter(Assessment.status == status)
    return query.order_by(Assessment.created_at.desc()).all()


@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return a


@router.get("/{assessment_id}/questions", response_model=List[QuestionOut])
def get_questions(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    questions = (
        db.query(Question)
        .filter(Question.assessment_id == assessment_id)
        .order_by(Question.order)
        .all()
    )
    # Hide correct_answer from candidates
    if current_user.role == "candidate":
        for q in questions:
            q.correct_answer = None
    return questions


@router.patch("/{assessment_id}/status")
def update_status(
    assessment_id: UUID,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter", "admin")),
):
    a = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.recruiter_id == current_user.id,
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if status not in ("draft", "active", "archived"):
        raise HTTPException(status_code=400, detail="Invalid status")
    a.status = status
    db.commit()
    return {"id": str(assessment_id), "status": status}


@router.delete("/{assessment_id}", status_code=204)
def delete_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter", "admin")),
):
    a = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.recruiter_id == current_user.id,
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    db.delete(a)
    db.commit()
