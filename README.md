# 🛡️ RM_Sentinel – Real-Time Host-Based IDS & SOC Dashboard

> **A real-time Host-Based Intrusion Detection System (HIDS) featuring File Integrity Monitoring (FIM), Dynamic Risk Scoring, Interactive SOC Dashboard, Threat Mapping, and Instant Incident Response.**

---

## 📌 Overview

**RM_Sentinel** is a cybersecurity project designed to simulate a lightweight Security Operations Center (SOC). It combines a Host-Based Intrusion Detection System (HIDS), File Integrity Monitoring (FIM), live threat visualization, and automated incident notifications into a single platform.

The system continuously monitors endpoints, detects suspicious activities, calculates a dynamic risk score, visualizes incidents on an interactive dashboard, and instantly alerts security analysts through Telegram.

---

## 🏗️ System Architecture
<img width="1536" height="1024" alt="ChatGPT Image 29 يونيو 2026، 09_38_54 ص" src="https://github.com/user-attachments/assets/8b915743-e1cf-484e-9e0b-387c6d1738fc" />

---

# ✨ Features

## 🔍 File Integrity Monitoring (FIM)

* Detects file creation
* Detects file modification
* Detects file deletion
* Real-time monitoring using **Watchdog**

---

## 🛡️ Host-Based Intrusion Detection (HIDS)

* Suspicious activity detection
* Resource usage monitoring
* Brute-force detection
* Endpoint monitoring

---

## 📊 Dynamic Risk Scoring

Custom scoring engine that evaluates incidents based on:

* Event type
* CPU usage
* Memory usage
* Threat severity

Produces a **0–100% Risk Score** for every detected event.

---

## 🌍 Interactive Threat Mapping

Displays attackers and monitored hosts on an interactive map using:

* Public IP lookup
* Geolocation API
* Latitude & Longitude
* City & Country detection
* Dark-themed cyber map

---

## 🚨 Instant Incident Response

Automatically sends Telegram alerts containing:

* Hostname
* Threat type
* Risk Score
* Public IP
* Location
* Timestamp

---

## 📈 SOC Dashboard

Built with **Streamlit** and includes:

* Live Event Feed
* Risk Gauge
* Pie Charts
* Threat Statistics
* Interactive Maps
* Real-Time Monitoring

---

# 🛠 Tech Stack

### Backend

* Python 3.12
* FastAPI
* SQLAlchemy

### Database

* PostgreSQL
* psycopg2

### Dashboard

* Streamlit
* Plotly
* Folium
* Streamlit-Folium

### Agent

* Watchdog
* Psutil
* Requests

### Networking

* Ngrok
* REST API
* JSON

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/RM_Sentinel.git

cd RM_Sentinel
```

## Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Server

```bash
python -m uvicorn server:app --reload
```

---

# ▶️ Run the Agent

```bash
python agent.py
```

---

# ▶️ Launch SOC Dashboard

```bash
streamlit run dashboard.py
```

---

# 📂 Project Structure

```
RM_Sentinel/
│
├── agent.py
├── server.py
├── dashboard.py
├── requirements.txt
├── database.py
├── models.py
├── utils/
├── screenshots/
└── README.md
```

---

# 🎯 Future Improvements

* SIEM Integration
* Multi-Agent Support
* Windows Service Deployment
* Email Notifications
* Threat Intelligence Integration
* MITRE ATT&CK Mapping
* YARA Rule Support
* Malware Detection
* Machine Learning Risk Analysis

---

# 📸 Screenshots

> Add screenshots of:

* SOC Dashboard
* Live Alerts
* Threat Map
* Telegram Notifications
* Risk Charts

---

# 📜 License

This project was developed for educational purposes and advanced cybersecurity demonstrations.

© 2026 RM_Sentinel. All Rights Reserved.
<img width="1536" height="1024" alt="ChatGPT Image 29 يونيو 2026، 09_38_54 ص" src="https://github.com/user-attachments/assets/d560ad6c-1302-49fa-a294-a37a8a6b5c27" />
