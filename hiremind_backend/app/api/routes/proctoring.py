from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import ProctorEvent, AssessmentAttempt
from app.schemas.schemas import ProctorEventRequest

router = APIRouter(prefix="/api/proctor", tags=["Proctoring"])

VIOLATION_WEIGHTS = {
    "tab_switch": 5,
    "face_missing": 10,
    "fullscreen_exit": 8,
    "multi_face": 15,
    "copy_paste": 12,
    "other": 3,
}


@router.post("/event", status_code=201)
def log_proctor_event(
    payload: ProctorEventRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Log a proctoring violation event."""
    attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.id == payload.session_id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Session not found")

    event = ProctorEvent(
        attempt_id=attempt.id,
        event_type=payload.event_type,
        timestamp=payload.timestamp,
        metadata_=payload.metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "event_id": str(event.id),
        "session_id": str(attempt.id),
        "event_type": event.event_type,
        "severity_weight": VIOLATION_WEIGHTS.get(payload.event_type, 3),
    }


@router.get("/session/{attempt_id}/summary")
def get_session_summary(
    attempt_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter", "admin")),
):
    """Summarise all proctoring events for an attempt."""
    events = (
        db.query(ProctorEvent)
        .filter(ProctorEvent.attempt_id == attempt_id)
        .order_by(ProctorEvent.timestamp)
        .all()
    )

    counts: dict = {}
    total_penalty = 0
    for e in events:
        counts[e.event_type] = counts.get(e.event_type, 0) + 1
        total_penalty += VIOLATION_WEIGHTS.get(e.event_type, 3)

    risk_level = "low"
    if total_penalty >= 50:
        risk_level = "high"
    elif total_penalty >= 20:
        risk_level = "medium"

    return {
        "attempt_id": str(attempt_id),
        "total_events": len(events),
        "event_counts": counts,
        "total_penalty_score": total_penalty,
        "cheating_risk": risk_level,
        "events": [
            {
                "id": str(e.id),
                "type": e.event_type,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in events
        ],
    }
