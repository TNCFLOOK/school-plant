import streamlit as st
import qrcode
from PIL import Image
import io
import json
import os
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา", page_icon="🌿", layout="wide")

# ไฟล์สำหรับเก็บข้อมูลถาวร
DATA_FILE = "botany_data.json"
UPLOAD_DIR = "uploaded_images"

# สร้างโฟลเดอร์เก็บรูปภาพถ้ายังไม่มี
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ฟังก์ชันจัดการข้อมูล (Load/Save JSON)
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # ข้อมูลเริ่มต้น (Default Data)
    return {
        "plants": {
            "ต้นราชพฤกษ์": {
                "scientific_name": "Cassia fistula",
                "benefit": "ช่วยขับพยาธิและเป็นยาระบายอ่อนๆ",
                "image": None
            }
        },
        "users": {
            "admin": {"name": "ผู้ดูแลระบบหลัก", "role": "ผู้ดูแลระบบ", "class": "-"},
            "6501": {"name": "เด็กชายสมชาย ใจดี", "role": "นักเรียน", "class": "ม.3/1"}
        },
        "logs": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# โหลดข้อมูลเข้าสู่ session_state
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# ส่วนหัวของเว็บไซต์
st.markdown("
