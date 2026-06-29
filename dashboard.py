import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# 1. إعدادات الصفحة العامة (ثيم سيبراني فخم)
st.set_page_config(page_title="RM Sentinel - Cyber Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #ff4d4d !important; text-align: right; }
    div.stMarkdown { text-align: right; direction: rtl; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ مركز إدارة العمليات الأمنية | RM_Sentinel SOC")
st.subheader("مراقبة سلامة الملفات والتحليل الجغرافي للتهديدات لايف")
st.markdown("---")

# 2. جلب البيانات من الـ API حق السيرفر
API_URL = "http://127.0.0.1:8000/api/alerts"

try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
    else:
        data = []
except Exception as e:
    st.error(f"❌ تعذر الاتصال بسيرفر الأمان الرئيسي. تأكد أن server.py شغال. الخطأ: {e}")
    data = []

# 3. معالجة البيانات وتحويلها لجدول تفرزه الواجهة
if data:
    df = pd.DataFrame(data)
    
    # حساب الإحصائيات للعدادات الفخمة
    total_alerts = len(df)
    high_risk_count = len(df[df['risk_score'] >= 75])
    
    # الصف الأول: العدادات الرقمية الفخمة
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🚨 إجمالي التنبيهات المكتشفة", value=total_alerts)
    with col2:
        st.metric(label="🔥 تهديدات عالية الخطورة (Risk >= 75)", value=high_risk_count)
    with col3:
        st.metric(label="🌐 آخر IP حاول المهاجمة", value=df['attacker_ip'].iloc[0] if 'attacker_ip' in df.columns else "127.0.0.1")
        
    st.markdown("---")
    
    # الصف الثاني: الخريطة التفاعلية مع رسمة النسب المئوية بجانب بعض
    chart_col, map_col = st.columns([1, 2])
    
    # أ) رسم النسبة المئوية للمخاطر (Pie Chart)
    with chart_col:
        st.markdown("### 📊 النسبة المئوية للمخاطر")
        # تقسيم التنبيهات حسب مستوى الخطورة
        df_risk = df['risk_score'].value_counts().reset_index()
        df_risk.columns = ['مستوى الخطورة', 'العدد']
        df_risk['مستوى الخطورة'] = df_risk['مستوى الخطورة'].apply(lambda x: f"خطر مرتفع ({x}%)" if x >= 75 else f"آمن/منخفض ({x}%)")
        
        fig = px.pie(df_risk, values='العدد', names='مستوى الخطورة', 
                     color_discrete_sequence=['#ff4d4d', '#2ecc71'],
                     hole=0.4)
        fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    # ب) رسم الخريطة الجغرافية مع الدوائر الحمراء (Folium Cyber Map)
    with map_col:
        st.markdown("### 🌍 خريطة التهديدات الجغرافية الحية")
        
        # أخذ آخر إحداثيات متوفرة لتمركز الخريطة عليها
        start_lat = df['lat'].iloc[0] if 'lat' in df.columns else 24.7136
        start_lon = df['lon'].iloc[0] if 'lon' in df.columns else 46.6753
        
        # إنشاء الخريطة بنمط داكن يناسب غرف الهكرز والـ SOC
        m = folium.Map(location=[start_lat, start_lon], zoom_start=5, tiles="CartoDB dark_matter")
        
        # رسم دائرة حمراء لكل هجمة مسجلة في النظام
        for _, row in df.iterrows():
            lat = row.get('lat', 24.7136)
            lon = row.get('lon', 46.6753)
            ip = row.get('attacker_ip', 'Unknown')
            city = row.get('city', 'Unknown')
            file = row.get('file_name', 'Unknown')
            
            # رسم الدائرة الحمراء (Circle)
            folium.Circle(
                location=[lat, lon],
                radius=90000, # نصف القطر بالمتر حول المدينة
                color='#ff1a1a',
                fill=True,
                fill_color='#ff4d4d',
                fill_opacity=0.4,
                popup=f"🚨 Threat IP: {ip}<br>📍 Location: {city}<br>📁 File: {file}"
            ).add_to(m)
            
        # عرض الخريطة داخل الـ Streamlit
        st_folium(m, width="100%", height=350)
        
    st.markdown("---")
    
    # الصف الثالث: جدول اللوجات التفصيلي بالأسفل
    st.markdown("### 📋 سجلات التنبيهات المفصلة (Logs Live Feed)")
    st.dataframe(df[['id', 'timestamp', 'attacker_ip', 'city', 'file_name', 'alert_triggered', 'risk_score']].rename(
        columns={
            'id': 'معرف اللوج', 'timestamp': 'الوقت والتاريخ', 'attacker_ip': 'عنوان IP المهاجم',
            'city': 'المدينة', 'file_name': 'اسم الملف المكتشف', 'alert_triggered': 'نوع التنبيه الأمني', 'risk_score': 'معدل الخطر'
        }
    ), use_container_width=True)

else:
    st.info("🟢 النظام مستقر حالياً. لا توجد أي تنبيهات أمنية نشطة في قاعدة البيانات.")