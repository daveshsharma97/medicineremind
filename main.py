from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, Medicine, User, FamilyMember
from auth import hash_password, verify_password
from reminder import set_reminder, run_reminders
import threading
from sos import trigger_sos

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Welcome to MedicineRemind!"}
    # Start reminder system in background
@app.on_event("startup")
def start_reminders():
    thread = threading.Thread(target=run_reminders)
    thread.daemon = True
    thread.start()
    print("✅ Reminder system started!")

# Set a reminder AND save medicine to database
@app.post("/medicines/reminder")
def add_reminder(medicine_name: str,
                 dose: str,
                 reminder_time: str,
                 db: Session = Depends(get_db)):
    new_medicine = Medicine(
        name=medicine_name,
        dose=dose,
        time=reminder_time
    )
    db.add(new_medicine)
    db.commit()
    set_reminder(medicine_name, dose, reminder_time)
    return {
        "message": "Reminder set and saved!",
        "medicine": medicine_name,
        "time": reminder_time,
        "dose": dose
    }

# GET all medicines for the app
@app.get("/medicines")
def get_medicines(db: Session = Depends(get_db)):
    medicines = db.query(Medicine).all()
    return {
        "medicines": [
            {"name": m.name, "dose": m.dose, "time": m.time}
            for m in medicines
        ]
    }

# REGISTER - create new account
@app.post("/register")
def register(name: str, phone: str, 
             password: str, db: Session = Depends(get_db)):
    # Check if phone already exists
    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        raise HTTPException(status_code=400, 
                          detail="Phone already registered!")
    # Save new user
    user = User(name=name, phone=phone, 
                password=hash_password(password))
    db.add(user)
    db.commit()
    return {"message": "Account created!", "name": name}

# LOGIN - enter existing account
@app.post("/login")
def login(phone: str, password: str, 
          db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == phone).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, 
                          detail="Wrong phone or password!")
    return {"message": "Login successful!", "name": user.name}
    
    # SOS Emergency Button
@app.post("/sos")
def sos_emergency(
    patient_name: str,
    phone: str,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    alert = trigger_sos(
        patient_name=patient_name,
        phone=phone,
        latitude=latitude,
        longitude=longitude
    )
    return alert
# Add family member
@app.post("/family/add")
def add_family(
    patient_phone: str,
    family_name: str,
    family_phone: str,
    relation: str,
    db: Session = Depends(get_db)
):
    member = FamilyMember(
        patient_phone=patient_phone,
        family_name=family_name,
        family_phone=family_phone,
        relation=relation
    )
    db.add(member)
    db.commit()
    return {
        "message": "Family member added!",
        "family_name": family_name,
        "relation": relation
    }

# Family sees patient medicines
@app.get("/family/medicines/{patient_phone}")
def family_view(
    patient_phone: str,
    db: Session = Depends(get_db)
):
    medicines = db.query(Medicine).all()
    family = db.query(FamilyMember).filter(
        FamilyMember.patient_phone == patient_phone
    ).all()
    return {
        "medicines": medicines,
        "family_members": family
    }