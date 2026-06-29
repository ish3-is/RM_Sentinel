from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
import requests

# 1. إعدادات قاعدة البيانات والتوصيل
DATABASE_URL = "postgresql://postgres:rm_password_2026@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. موديل قاعدة البيانات (تمت إضافة أعمدة الجغرافيا لربط الخريطة)
class LogModel(Base):
    __tablename__ = "agent_logs_v6"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String)
    cpu_usage = Column(Float)
    ram_usage = Column(Float)
    failed_logins = Column(Integer)
    suspicious_file = Column(Integer, default=0)
    file_name = Column(String, default="")
    timestamp = Column(String)
    alert_triggered = Column(String, default="None")
    risk_score = Column(Integer, default=10)
    # الأعمدة الجديدة الخاصة بالخريطة والـ IP
    attacker_ip = Column(String, default="127.0.0.1")
    city = Column(String, default="Unknown")
    country = Column(String, default="Unknown")
    lat = Column(Float, default=24.7136)
    lon = Column(Float, default=46.6753)

Base.metadata.create_all(bind=engine)

# 3. تعريف الـ Schema (تم نقلها للأعلى لتجنب الـ NameError)
class LogData(BaseModel):
    agent_id: str
    cpu_usage: float
    ram_usage: float
    failed_logins: int
    suspicious_file: int = 0
    file_name: str = ""
    timestamp: str

# 4. تشغيل وتجهيز FastAPI
app = FastAPI(title="R&M Sentinel Server v5 (Map & Telegram Active)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. الإعدادات والدوال المساعدة (تيليجرام وجغرافيا)
TELEGRAM_TOKEN = "8625349188:AAGqWP_OlYby8_u0OeezGX95egDhissRM-I"
TELEGRAM_CHAT_ID = "985334430"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        print(f"📡 Telegram Server Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")

def get_ip_location(ip_address):
    if ip_address in ["127.0.0.1", "localhost", "::1"]:
        return {"country": "Saudi Arabia", "city": "Riyadh", "lat": 24.7136, "lon": 46.6753}
    try:
        res = requests.get(f"http://ip-api.com/json/{ip_address}").json()
        if res.get("status") == "success":
            return {
                "country": res.get("country", "Unknown"),
                "city": res.get("city", "Unknown"),
                "lat": res.get("lat", 24.7136),
                "lon": res.get("lon", 46.6753)
            }
    except:
        pass
    return {"country": "Unknown", "city": "Unknown", "lat": 24.7136, "lon": 46.6753}

def analyze_log(log: LogData):
    alerts = []
    if log.failed_logins > 15:
        alerts.append("🚨 Brute Force Attack Detected!")
    if log.cpu_usage > 80.0:
        alerts.append("⚠️ High CPU Usage - Possible Threat!")
    if log.suspicious_file == 1:
        alerts.append(f"🚨 Suspicious File Created: {log.file_name}")
        
    if alerts:
        return " | ".join(alerts)
    return "None"

# 6. الـ API الرئيسي لاستقبال اللوجات وحفظها
@app.post("/api/logs")
def receive_logs(log: LogData, request: Request, db: Session = Depends(get_db)):
    try:
        # لقط الأيبي والموقع الحقيقي
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        loc = get_ip_location(client_ip)
        
        alert_status = analyze_log(log)
        
        # حساب الـ Risk Score
        risk_score = 10
        if log.cpu_usage > 80.0: risk_score += 30
        if log.failed_logins > 15: risk_score += 55
        if log.suspicious_file == 1: risk_score += 65
        risk_score = min(risk_score, 100)
            
        # إرسال بلاغ التيليجرام مدعوماً بالبيانات الجغرافية
        if alert_status != "None":
            telegram_msg = (
                f"🛡️ R&M Sentinel Alert!\n"
                f"-------------------------\n"
                f"💻 Agent: {log.agent_id}\n"
                f"⚠️ Threat: {alert_status}\n"
                f"📊 Risk Score: {risk_score}/100\n"
                f"🌐 IP: {client_ip}\n"
                f"📍 Location: {loc['city']}, {loc['country']}\n"
                f"⏰ Time: {log.timestamp}"
            )
            send_telegram_alert(telegram_msg)
            
        # حفظ كل الإحصائيات مع الجغرافيا بالجدول
        db_log = LogModel(
            agent_id=log.agent_id,
            cpu_usage=log.cpu_usage,
            ram_usage=log.ram_usage,
            failed_logins=log.failed_logins,
            suspicious_file=log.suspicious_file,
            file_name=log.file_name,
            timestamp=log.timestamp,
            alert_triggered=alert_status,
            risk_score=risk_score,
            attacker_ip=client_ip,
            city=loc['city'],
            country=loc['country'],
            lat=loc['lat'],
            lon=loc['lon']
        )
        db.add(db_log)
        db.commit()
        
        return {
            "status": "success", 
            "alert": alert_status, 
            "risk_score": risk_score, 
            "lat": loc["lat"], 
            "lon": loc["lon"], 
            "ip": client_ip
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail="Server Error")

# 7. الـ API المسؤول عن تغذية الـ Dashboard بالبيانات
@app.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    try:
        return db.query(LogModel).filter(LogModel.alert_triggered != "None").order_by(LogModel.id.desc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching alerts")