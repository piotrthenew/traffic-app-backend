from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(title="TrafficApp API", version="1.0.0")

# ========== KONFIGURACJA ==========
temp_reports = []
temp_report_id = 1

SECRET_KEY = "twoj_super_tajny_klucz_do_pracy_inzynierskiej_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ========== CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== FUNKCJE POMOCNICZE ==========

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ========== MODELE DANYCH ==========

class RegisterRequest(BaseModel):
    """Model danych rejestracji – przyjmuje JSON z body"""
    email: str
    password: str
    username: Optional[str] = None

class ReportCreate(BaseModel):
    title: str
    description: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    report_type: str = "other"

class Token(BaseModel):
    access_token: str
    token_type: str

# ========== ENDPOINTY AUTORYZACJI (z /api/) ==========

@app.post("/api/register")
def register(user_data: RegisterRequest):
    """Rejestracja nowego użytkownika – dane z body (JSON)"""
    hashed = get_password_hash(user_data.password)
    return {
        "message": "użytkownik zarejestrowany",
        "user": {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed[:20] + "..."
        }
    }

@app.post("/api/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Logowanie - zwraca token JWT"""
    access_token = create_access_token(data={"sub": form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token")
        return {"email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

# ========== ENDPOINTY ZGŁOSZEŃ ==========

@app.get("/")
def read_root():
    return {
        "status": "OK",
        "message": "✅ TrafficApp API – działa w pełni",
        "timestamp": datetime.now().isoformat(),
        "author": "Piotr Śledziewski"
    }

@app.get("/reports")
def get_reports():
    print(f"🟢 GET /reports – zwracam {len(temp_reports)} zgłoszeń")
    return {"reports": temp_reports}

@app.post("/reports")
def create_report(report_data: ReportCreate):
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
    print(f"📋 Aktualna liczba zgłoszeń: {len(temp_reports)}")

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
    return {
        "database_status": "connected",
        "message": "✅ Baza danych (pamięć tymczasowa) działa poprawnie"
    }
