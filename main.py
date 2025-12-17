from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from pydantic import BaseModel
import database
from database import SessionLocal, engine, User, Report, create_tables

# Tworzymy tabele w bazie danych
create_tables()

app = FastAPI(title="TrafficApp API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model danych dla zgłoszenia
class ReportCreate(BaseModel):
    title: str
    description: str = None
    lat: float = None
    lng: float = None
    report_type: str = "other"

# Dependency dla bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "OK", 
        "message": "🚀 TrafficApp API z bazą danych działa!",
        "timestamp": datetime.now().isoformat(),
        "author": "Piotr Śledziewski"
    }

@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).all()
    return {"reports": reports}

@app.post("/reports")
def create_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    # Tworzymy nowe zgłoszenie
    new_report = Report(
        title=report_data.title,
        description=report_data.description,
        location={"lat": report_data.lat, "lng": report_data.lng} if report_data.lat and report_data.lng else None,
        report_type=report_data.report_type
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return {
        "message": "Zgłoszenie dodane!",
        "report": {
            "id": new_report.id,
            "title": new_report.title,
            "type": new_report.report_type
        }
    }

# Endpoint do sprawdzenia połączenia z bazą
@app.get("/test-db")
def test_database(db: Session = Depends(get_db)):
    try:
        # PROSTSZY TEST: próbujemy pobrać listę zgłoszeń
        reports_count = db.query(Report).count()
        return {
            "database_status": "OK", 
            "message": "Połączenie z bazą działa!",
            "reports_count": reports_count
        }
    except Exception as e:
        return {"database_status": "ERROR", "message": str(e)}