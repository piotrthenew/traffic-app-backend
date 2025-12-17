from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session  # Tymczasowo wyłączone
from datetime import datetime
from typing import List
from pydantic import BaseModel
# import database  # Tymczasowo wyłączone
# from database import SessionLocal, engine, User, Report, create_tables  # Tymczasowo wyłączone

# Tworzymy tabele w bazie danych
# create_tables()  # Tymczasowo wyłączone

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

# Dependency dla bazy danych - TYMCZASOWO PROSTE
def get_db():
    # Tymczasowo zwracamy None zamiast sesji bazy danych
    yield None

@app.get("/")
def read_root():
    return {
        "status": "OK", 
        "message": "🚀 TrafficApp API (tryb tymczasowy - baza wyłączona)",
        "timestamp": datetime.now().isoformat(),
        "author": "Piotr Śledziewski",
        "note": "Baza danych tymczasowo wyłączona z powodu kompatybilności Python 3.13"
    }

@app.get("/reports")
def get_reports():  # Usunięto: db: Session = Depends(get_db)
    return {"reports": [], "message": "Tryb tymczasowy - baza wyłączona"}

@app.post("/reports")
def create_report(report_data: ReportCreate):  # Usunięto: db: Session = Depends(get_db)
    # Tymczasowo nie zapisujemy do bazy
    return {
        "message": "Zgłoszenie dodane (tryb testowy - baza tymczasowo wyłączona)",
        "report": {
            "id": 999,  # Tymczasowy ID
            "title": report_data.title,
            "type": report_data.report_type,
            "note": "Dane nie są zapisywane w bazie w trybie tymczasowym"
        }
    }

# Endpoint do sprawdzenia połączenia z bazą
@app.get("/test-db")
def test_database():  # Usunięto: db: Session = Depends(get_db)
    return {
        "database_status": "TEMPORARILY_DISABLED", 
        "message": "Baza danych tymczasowo wyłączona z powodu kompatybilności z Python 3.13",
        "action_required": "Należy zmienić wersję Pythona na 3.11 w ustawieniach Render"
    }