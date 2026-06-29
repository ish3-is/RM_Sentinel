import time
import requests
import psutil
import os
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SERVER_URL = "https://grievous-lucrative-cartridge.ngrok-free.dev/api/logs"
AGENT_ID = "Laptop-M"

# المجلد المراد مراقبته (تأكد من إنشائه على سطح المكتب أو أي مسار تفضله)
WATCH_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "RM_Sentinel_Watch")
if not os.path.exists(WATCH_DIR):
    os.makedirs(WATCH_DIR)

# متغير مشترك لحفظ حالة آخر ملف مريب تم اكتشافه
last_file_alert = {"status": False, "file_name": ""}

class SentinelFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            print(f"[!] New file detected: {file_name}")
            last_file_alert["status"] = True
            last_file_alert["file_name"] = file_name

def start_fim():
    event_handler = SentinelFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIR, recursive=False)
    observer.start()
    print(f"[*] File Integrity Monitoring started on: {WATCH_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def collect_and_send():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # نتحقق إذا كان الفاحص لقط ملف جديد
        suspicious_file = 0
        file_msg = ""
        if last_file_alert["status"]:
            suspicious_file = 1
            file_msg = last_file_alert["file_name"]
            last_file_alert["status"] = False # إعادة تصنيير التنبيه بعد إرساله
        
        payload = {
            "agent_id": AGENT_ID,
            "cpu_usage": cpu,
            "ram_usage": ram,
            "failed_logins": 0,  # رجعناه صفر عشان ما يتداخل مع اختبار الملفات
            "suspicious_file": suspicious_file,
            "file_name": file_msg,
            "timestamp": now
        }
        
        try:
            response = requests.post(SERVER_URL, json=payload)
            print(f"Sent logs -> File Event: {suspicious_file}, Server response: {response.json()}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            
        time.sleep(4)

if __name__ == "__main__":
    print(f"Agent v3 with FIM is running...")
    # تشغيل مراقب الملفات في خلفية مستقلة (Thread)
    fim_thread = threading.Thread(target=start_fim, daemon=True)
    fim_thread.start()
    
    # تشغيل مرسل التقارير الأساسي
    collect_and_send()