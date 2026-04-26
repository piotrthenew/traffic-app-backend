from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(title="TrafficApp API", version="1.0.0")

# ========== KONFIGURACJA ==========

# Tymczasowe przechowywanie (pamięć RAM)
temp_reports = []
temp_report_id = 1
temp_users = []  # Lista przechowująca zarejestrowanych użytkowników
temp_user_id = 1

# JWT
SECRET_KEY = "twoj_super_tajny_klucz_do_pracy_inzynierskiej_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hashowanie haseł
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# CORS - zezwala na wszystko (działa lokalnie i zdalnie)
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

def get_user_by_email(email: str):
    for user in temp_users:
        if user["email"] == email:
            return user
    return None

# ========== MODELE DANYCH ==========

class RegisterRequest(BaseModel):
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

# ========== ENDPOINTY Z PREFIKSEM /api/ (DLA FRONTENDU) ==========

@app.post("/api/register")
def api_register(user_data: RegisterRequest):
    """Rejestracja - przyjmuje JSON z body"""
    # Sprawdź czy użytkownik już istnieje
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Użytkownik z tym emailem już istnieje"
        )
    
    global temp_user_id
    hashed_password = get_password_hash(user_data.password)
    
    new_user = {
        "id": temp_user_id,
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password,
        "created_at": datetime.now().isoformat()
    }
    temp_users.append(new_user)
    temp_user_id += 1
    
    return {
        "message": "Użytkownik zarejestrowany pomyślnie",
        "user": {
            "email": user_data.email,
            "username": user_data.username
        }
    }

@app.post("/api/login", response_model=Token)
def api_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Logowanie - zwraca token JWT"""
    user = get_user_by_email(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło"
        )
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło"
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me")
def api_read_users_me(token: str = Depends(oauth2_scheme)):
    """Zwraca dane zalogowanego użytkownika"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token")
        user = get_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=401, detail="Użytkownik nie istnieje")
        return {"email": user["email"], "username": user["username"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

# ========== ENDPOINTY ZGŁOSZEŃ ==========

@app.get("/reports")
def get_reports():
    """Zwraca listę zgłoszeń"""
    return {"reports": temp_reports}

@app.post("/reports")
def create_report(report_data: ReportCreate):
    """Dodaje nowe zgłoszenie"""
    global temp_report_id, temp_reports
    
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
    temp_report_id += 1
    
    return {
        "message": "Zgłoszenie dodane!",
        "report": {
            "id": new_report["id"],
            "title": new_report["title"],
            "type": new_report["report_type"]
        }
    }

@app.get("/")
def read_root():
    return {
        "status": "OK",
        "message": "TrafficApp API działa!",
        "timestamp": datetime.now().isoformat(),
        "author": "Piotr Śledziewski"
    }

@app.get("/test-db")
def test_database():
    return {
        "database_status": "connected",
        "message": "Baza danych (pamięć tymczasowa) działa poprawnie"
    }


# ========== DODATKOWE ENDPOINTY KOMPATYBILNOŚCI (bez /api) ==========

@app.post("/register")
def register(email: str, password: str, username: Optional[str] = None):
    """Rejestracja - wersja bez /api (parametry w URL)"""
    return api_register(RegisterRequest(email=email, password=password, username=username))

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Logowanie - wersja bez /api"""
    return api_login(form_data)

@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    """Dane użytkownika - wersja bez /api"""
    return api_read_users_me(token)
