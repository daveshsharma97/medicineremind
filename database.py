from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///medicines.db")

Base = declarative_base()

class Medicine(Base):
    __tablename__ = "medicines"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    time = Column(String)
    dose = Column(String)
    days = Column(String)

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

# This line always stays at the VERY BOTTOM!
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)