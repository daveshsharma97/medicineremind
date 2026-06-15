import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use PostgreSQL if available, else SQLite for local testing
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///medicines.db")

# Fix for SQLAlchemy: postgres:// must be postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class Medicine(Base):
    __tablename__ = "medicines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    time = Column(String)
    dose = Column(String)
    days = Column(String)
    end_date = Column(String, default="")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    password = Column(String)

class FamilyMember(Base):
    __tablename__ = "family_members"
    id = Column(Integer, primary_key=True)
    patient_phone = Column(String)
    family_name = Column(String)
    family_phone = Column(String)
    relation = Column(String)
class TakenRecord(Base):
    __tablename__ = "taken_records"
    id = Column(Integer, primary_key=True)
    phone = Column(String)
    medicine_name = Column(String)
    taken_date = Column(String)
    taken_time = Column(String)

# This line always stays at the VERY BOTTOM!
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)