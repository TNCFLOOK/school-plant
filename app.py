import streamlit as st
import qrcode
from PIL import Image
import io
import json
import os
import base64

st.set_page_config(page_title="ระบบสารสนเทศพฤกษศาสตร์โรงเรียน", page_icon="🌿", layout="wide")

PLANTS_FILE = "plants_data.json"
STUDENTS_FILE = "students_data.json"

def load_plants():
    if os.path.exists(PLANTS_FILE):
        try:
            with open(PLANTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for plant_name, plant_info in data.items():
                    if plant_info.get("image_base64"):
                        try:
                            plant_info["image"] = base64.b64decode(plant_info["image_base64"])
                        except Exception:
                            plant_info["image"] = None
                    else:
                        plant_info["image"] = None
                return data
        except Exception:
            pass
    return {
        "ตำแยแมว": {
            "scientific_name": "Acalypha indica L.",
            "family": "Euphorbiaceae",
            "benefit": "รากหรือใบต้มน้ำดื่มขับเสมหะ ช่วยให้แมวผ่อนคลาย",
            "image": None
        }
    }

def save_plants():
    serializable_data = {}
    for p_name, p_data in st.session_state['plants'].items():
        img_b64 = None
        img_data = p_data.get("image")
        if img_data is not None:
            if isinstance(img_data, bytes):
                try:
                    img_b64 = base64.b64encode(img_data).decode('utf-8')
                except Exception:
                    pass
        
        serializable_data[p_name] = {
            "scientific_name": p_data.get("scientific_name", ""),
            "family": p_data.get("family", ""),
            "benefit": p_data.get("benefit", ""),
            "image_base64": img_b64
        }
    try:
        with open(PLANTS_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def load_students():
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "admin01": {"name": "ผู้ดูแลระบบหลัก", "class": "คณะครู", "role": "Admin"},
        "65001": {"name": "เด็กชายสมชาย เรียนดี", "class": "ม.3/1", "role": "User"}
    }

def save_students():
    try:
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state['students'], f, ensure_ascii=False, indent=4)
    except Exception:
        pass

if 'plants' not in st.session_state:
    st.session_state['plants'] = load_plants()

if 'students' not in st.session_state:
    st.session_state['students'] = load_students()

if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

# ==========================================
# 🔐 หน้า Login
# ==========================================
if st.session_state['logged_in_user'] is None:
    st.markdown("
