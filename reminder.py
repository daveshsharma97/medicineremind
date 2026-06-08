import schedule
import time
from datetime import datetime

def send_reminder(medicine_name: str, dose: str):
    print(f"⏰ REMINDER: Time to take {medicine_name}!")
    print(f"💊 Dose: {dose}")
    print(f"🕐 Time: {datetime.now().strftime('%H:%M')}")

def set_reminder(medicine_name: str, 
                 dose: str, 
                 reminder_time: str):
    # reminder_time format = "08:00"
    schedule.every().day.at(reminder_time).do(
        send_reminder, 
        medicine_name=medicine_name,
        dose=dose
    )
    print(f"✅ Reminder set for {medicine_name} at {reminder_time}")

def run_reminders():
    print("🔔 Reminder system is running...")
    while True:
        schedule.run_pending()
        time.sleep(30)