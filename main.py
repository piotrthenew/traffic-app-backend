from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(title="TrafficApp API", version="1.0.0")

# TYMCZASOWA LISTA ZGŁOSZEŃ (DZIAŁA TYLKO GDY SERWER DZIAŁA)
temp_reports = []
temp_report_id = 1

# KONFIGURACJA JWT
SECRET_KEY = "twoj_super_tajny_klucz_do_pracy_inzynierskiej_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== FUNKCJE POMOCNICZE ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Sprawdza czy hasło jest poprawne"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashuje hasło"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Tworzy token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==================== MODELE DANYCH ====================

class UserInDB(BaseModel):
    """Model użytkownika (tymczasowo)"""
    id: int
    email: str
    username: Optional[str] = None
    password: str
    disabled: bool = False
    created_at: Optional[datetime] = None

class ReportCreate(BaseModel):
    """Model danych dla zgłoszenia"""
    title: str
    description: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    report_type: str = "other"

class Token(BaseModel):
    """Model tokena JWT"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Dane w tokenie"""
    email: Optional[str] = None

# ==================== ENDPOINTY AUTORYZACJI ====================

@app.post("/register", response_model=dict)
def register(email: str, password: str, username: Optional[str] = None):
    """Rejestracja nowego użytkownika"""
    hashed = get_password_hash(password)
    return {
        "message": "Użytkownik zarejestrowany",
        "user": {
            "email": email,
            "username": username,
            "hashed_password": hashed[:20] + "..."
        }
    }

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Logowanie - zwraca token JWT"""
    access_token = create_access_token(data={"sub": form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/users/me", response_model=dict)
def read_users_me(token: str = Depends(oauth2_scheme)):
    """Zwraca dane zalogowanego użytkownika"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token")
        return {"email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

# ==================== ENDPOINTY ZGŁOSZEŃ ====================

@app.get("/")
def read_root():
    return {
        "status": "OK", 
        "message": "🚀 TrafficApp API (tryb tymczasowy - baza wyłączona)",
        "timestamp": datetime.now().isoformat(),
        "author": "Piotr Śledziewski",
        "note": "Baza danych tymczasowo wyłączona"
    }

@app.get("/reports")
def get_reports():
    """Zwraca listę zgłoszeń (tymczasowo z pamięci)"""
    print(f"🟢 GET /reports - zwracam {len(temp_reports)} zgłoszeń")
    return {"reports": temp_reports}

@app.post("/reports")
def create_report(report_data: ReportCreate):
    """Dodaje nowe zgłoszenie (tymczasowo do pamięci)"""
    global temp_report_id, temp_reports

    print("=" * 50)
    print("📢 OTRZYMANO NOWE ZGŁOSZENIE")
    print(f"   Tytuł: {report_data.title}")
    print(f"   Opis: {report_data.description}")
    print(f"   Lat: {report_data.lat}, Lng: {report_data.lng}")
    print(f"   Typ: {report_data.report_type}")
    print("=" * 50)

    new_report = {
        "id": temp_report_id,
        "title": report_data.title,
        "description": report_data.description,
        "location": {"lat": report_data.lat, "lng": report_data.lng} if report_data.lat and report_data.lng else None,
        "report_type": report_data.report_type,
        "created_at": datetime.now().isoformat(),
        "user_id": 1
    }

    temp_reports.append(new_report)
    print(f"✅ Dodano zgłoszenie ID: {temp_report_id}")
    print(f"📋 Aktualna liczba zgłoszeń w pamięci: {len(temp_reports)}")
    print(f"📋 Zawartość temp_reports: {temp_reports}")

    temp_report_id += 1

    return {
        "message": "Zgłoszenie dodane!",
        "report": {
            "id": new_report["id"],
            "title": new_report["title"],
            "type": new_report["report_type"]
        }
    }

@app.get("/test-db")
def test_database():
    """Sprawdza połączenie z bazą (tymczasowo)"""
    return {
        "database_status": "TEMPORARILY_DISABLED", 
        "message": "Baza danych tymczasowo wyłączona"
    }