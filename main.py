from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, Medicine, User, FamilyMember, TakenRecord
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
                 days: str = "Daily",
                 duration: str = "Ongoing",
                 db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    # Calculate end date based on duration
    end_date = ""
    if duration == "7 days":
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    elif duration == "1 month":
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    elif duration == "3 months":
        end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
    # Ongoing = empty (never expires)

    new_medicine = Medicine(
        name=medicine_name,
        dose=dose,
        time=reminder_time,
        days=days,
        end_date=end_date
    )
    db.add(new_medicine)
    db.commit()
    try:
        set_reminder(medicine_name, dose, reminder_time)
    except Exception as e:
        print(f"Reminder error: {e}")   
    return {
        "message": "Reminder set and saved!",
        "medicine": medicine_name,
        "time": reminder_time,
        "dose": dose
    }

# GET all medicines for the app


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
    # Mark medicine as taken
@app.post("/taken")
def mark_taken(phone: str, medicine_name: str, db: Session = Depends(get_db)):
    from datetime import datetime
    new_record = TakenRecord(
        phone=phone,
        medicine_name=medicine_name,
        taken_date=datetime.now().strftime("%Y-%m-%d"),
        taken_time=datetime.now().strftime("%H:%M")
    )
    db.add(new_record)
    db.commit()
    return {"message": "Marked as taken!"}


# Get taken records for a phone
@app.get("/taken/{phone}")
def get_taken(phone: str, db: Session = Depends(get_db)):
    records = db.query(TakenRecord).filter(
        TakenRecord.phone == phone).all()
    return {
        "taken": [
            {"medicine": r.medicine_name,
             "date": r.taken_date,
             "time": r.taken_time}
            for r in records
        ]
    }


@app.delete("/medicines/{medicine_id}")
def delete_medicine(medicine_id: int):
    db = SessionLocal()
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if medicine:
        db.delete(medicine)
        db.commit()
        db.close()
        return {"message": "Medicine deleted"}
    db.close()
    return {"message": "Medicine not found"}