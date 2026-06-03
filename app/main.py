from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_

from app.ai_agent import analyze_lead
from app.config import AI_MODE
from app.database import Base, SessionLocal, engine
from app.models import Lead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LeadMind AI")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

ALLOWED_STATUSES = ["Новая", "В работе", "Закрыта"]
ALLOWED_SCORES = ["Горячая", "Теплая", "Холодная"]


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "LeadMind AI",
            "message": "",
            "analysis": None,
            "ai_mode": AI_MODE,
        },
    )


@app.post("/analyze", response_class=HTMLResponse)
def analyze(request: Request, message: str = Form(...)):
    analysis = analyze_lead(message)

    db = SessionLocal()

    lead = Lead(
        original_message=message,
        summary=analysis["summary"],
        service_type=analysis["service_type"],
        area=analysis["area"],
        location=analysis["location"],
        timeline=analysis["timeline"],
        budget=analysis["budget"],
        lead_score=analysis["lead_score"],
        status="Новая",
        missing_data=", ".join(analysis["missing_data"]),
        next_step=analysis["next_step"],
        client_reply=analysis["client_reply"],
    )

    db.add(lead)
    db.commit()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "LeadMind AI",
            "message": message,
            "analysis": analysis,
            "ai_mode": AI_MODE,
        },
    )


@app.get("/leads", response_class=HTMLResponse)
def leads(
    request: Request,
    q: str = "",
    status: str = "",
    score: str = "",
):
    db = SessionLocal()

    query = db.query(Lead)
    search_text = q.strip()

    if search_text:
        query = query.filter(
            or_(
                Lead.original_message.ilike(f"%{search_text}%"),
                Lead.service_type.ilike(f"%{search_text}%"),
                Lead.location.ilike(f"%{search_text}%"),
                Lead.budget.ilike(f"%{search_text}%"),
                Lead.timeline.ilike(f"%{search_text}%"),
            )
        )

    if status in ALLOWED_STATUSES:
        query = query.filter(Lead.status == status)

    if score in ALLOWED_SCORES:
        query = query.filter(Lead.lead_score == score)

    all_leads = query.order_by(Lead.id.desc()).all()
    total_found = len(all_leads)

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="leads.html",
        context={
            "title": "Заявки - LeadMind AI",
            "leads": all_leads,
            "statuses": ALLOWED_STATUSES,
            "scores": ALLOWED_SCORES,
            "current_q": q,
            "current_status": status,
            "current_score": score,
            "total_found": total_found,
        },
    )


@app.post("/leads/{lead_id}/status")
def update_lead_status(lead_id: int, status: str = Form(...)):
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if lead and status in ALLOWED_STATUSES:
        lead.status = status
        db.commit()

    db.close()

    return RedirectResponse(url="/leads", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()

    total_leads = db.query(Lead).count()
    hot_leads = db.query(Lead).filter(Lead.lead_score == "Горячая").count()
    warm_leads = db.query(Lead).filter(Lead.lead_score == "Теплая").count()
    cold_leads = db.query(Lead).filter(Lead.lead_score == "Холодная").count()

    new_leads = db.query(Lead).filter(Lead.status == "Новая").count()
    in_progress_leads = db.query(Lead).filter(Lead.status == "В работе").count()
    closed_leads = db.query(Lead).filter(Lead.status == "Закрыта").count()

    recent_leads = db.query(Lead).order_by(Lead.id.desc()).limit(5).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "title": "Дашборд - LeadMind AI",
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "warm_leads": warm_leads,
            "cold_leads": cold_leads,
            "new_leads": new_leads,
            "in_progress_leads": in_progress_leads,
            "closed_leads": closed_leads,
            "recent_leads": recent_leads,
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "title": "О проекте - LeadMind AI",
            "ai_mode": AI_MODE,
        },
    )