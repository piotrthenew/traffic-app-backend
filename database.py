import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Połączenie z bazą danych
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model użytkownika (z username)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

# Model zgłoszenia
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(JSONB)  # Przechowuje współrzędne {lat: 52.23, lng: 21.01}
    report_type = Column(String(50))  # Korek, wypadek, remont, etc.
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))  # Kto dodał zgłoszenie

    # Relacja opcjonalna
    user = relationship("User", backref="reports")

# Model komentarza (krok 3)
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))
    report_id = Column(Integer, ForeignKey("reports.id"))

    # Relacje
    user = relationship("User", backref="comments")
    report = relationship("Report", backref="comments")

# Tworzenie tabel
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency do sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()