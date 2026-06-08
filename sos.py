from datetime import datetime

def trigger_sos(patient_name: str, 
                phone: str,
                latitude: float, 
                longitude: float):
    
    # Create Google Maps link
    maps_link = f"https://maps.google.com/?q={latitude},{longitude}"
    
    # Create alert message
    alert = {
        "emergency": "SOS ALERT!",
        "patient": patient_name,
        "phone": phone,
        "location": maps_link,
        "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "message": f"URGENT! {patient_name} needs help!",
    }
    
    print(f"🆘 SOS TRIGGERED by {patient_name}!")
    print(f"📍 Location: {maps_link}")
    print(f"🕐 Time: {alert['time']}")
    
    return alert