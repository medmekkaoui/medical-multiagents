from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from langgraph.types import Command
from pydantic import BaseModel

from .database.database import Base, SessionLocal, engine
from .database.models import Consultation
from .graph import graph
from .pdf_generator import generate_pdf


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Multi-Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartConsultationRequest(BaseModel):
    patient_case: str


class ResumeConsultationRequest(BaseModel):
    thread_id: str
    answer: str


def _state_for(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        return graph.get_state(config).values
    except Exception:
        return {}


def _save_consultation(thread_id: str, values: dict):
    with SessionLocal() as db:
        consultation = (
            db.query(Consultation)
            .filter(Consultation.thread_id == thread_id)
            .one_or_none()
        )
        if consultation is None:
            consultation = Consultation(thread_id=thread_id)
            db.add(consultation)

        consultation.diagnostic_summary = values.get("diagnostic_summary")
        consultation.interim_care = values.get("interim_care")
        consultation.physician_treatment = values.get("physician_treatment")
        consultation.final_report = values.get("final_report")
        db.commit()


def _consultation_record(thread_id: str):
    with SessionLocal() as db:
        consultation = (
            db.query(Consultation)
            .filter(Consultation.thread_id == thread_id)
            .one_or_none()
        )
        if consultation is None:
            return None

        return {
            "thread_id": consultation.thread_id,
            "diagnostic_summary": consultation.diagnostic_summary,
            "interim_care": consultation.interim_care,
            "physician_treatment": consultation.physician_treatment,
            "final_report": consultation.final_report,
        }


def _build_response(thread_id: str, result: dict):
    if "__interrupt__" in result:
        interrupt_value = result["__interrupt__"][0].value
        response = {
            "thread_id": thread_id,
            "question_count": result.get("question_count", 0),
            "status": "interrupted",
        }

        if isinstance(interrupt_value, str):
            response["type"] = "patient_question"
            response["question"] = interrupt_value
            return response

        response["type"] = "physician_review"
        response["physician_review"] = interrupt_value
        return response

    _save_consultation(thread_id, result)
    return {
        "thread_id": thread_id,
        "status": "completed",
        "question_count": result.get("question_count"),
        "diagnostic_summary": result.get("diagnostic_summary"),
        "interim_care": result.get("interim_care"),
        "physician_treatment": result.get("physician_treatment"),
        "final_report": result.get("final_report"),
    }


@app.get("/")
def health_check():
    return {"status": "ok", "service": "medical-multiagents"}


@app.post("/sessions/start")
def start_session():
    thread_id = str(uuid4())
    _save_consultation(thread_id, {})
    return {
        "thread_id": thread_id,
        "message": "Session creee avec succes",
    }


@app.post("/consultation/start")
def start_consultation(request: StartConsultationRequest):
    if not request.patient_case.strip():
        raise HTTPException(status_code=400, detail="Le cas patient est obligatoire.")

    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [{"role": "user", "content": request.patient_case}],
        "question_count": 0,
        "patient_answers": [],
    }

    result = graph.invoke(initial_state, config=config)
    _save_consultation(thread_id, result)
    return _build_response(thread_id, result)


@app.post("/consultation/resume")
def resume_consultation(request: ResumeConsultationRequest):
    if not request.answer.strip():
        raise HTTPException(status_code=400, detail="La reponse est obligatoire.")

    config = {"configurable": {"thread_id": request.thread_id}}
    result = graph.invoke(Command(resume=request.answer), config=config)
    _save_consultation(request.thread_id, result)
    return _build_response(request.thread_id, result)


@app.get("/consultation/{thread_id}")
def get_consultation(thread_id: str):
    state_values = _state_for(thread_id)
    record = _consultation_record(thread_id)
    if not state_values and record is None:
        raise HTTPException(status_code=404, detail="Consultation introuvable.")

    return {
        "thread_id": thread_id,
        "state": state_values,
        "saved": record,
    }


@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str):
    state_values = _state_for(thread_id)
    record = _consultation_record(thread_id) or {}
    final_report = state_values.get("final_report") or record.get("final_report")

    if not final_report:
        raise HTTPException(status_code=404, detail="Rapport final non disponible.")

    return {
        "thread_id": thread_id,
        "final_report": final_report,
    }


@app.get("/consultation/{thread_id}/report/pdf")
def get_report_pdf(thread_id: str):
    report = get_report(thread_id)["final_report"]
    reports_dir = Path(__file__).resolve().parents[1] / "reports"
    pdf_path = reports_dir / f"rapport_{thread_id}.pdf"
    generate_pdf(report, pdf_path)
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )


@app.get("/consultations")
def list_consultations():
    with SessionLocal() as db:
        rows = db.query(Consultation).order_by(Consultation.id.desc()).all()
        return [
            {
                "thread_id": row.thread_id,
                "has_report": bool(row.final_report),
                "diagnostic_summary": row.diagnostic_summary,
            }
            for row in rows
        ]
