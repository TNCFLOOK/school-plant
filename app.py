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
st.markdown("if not plants_dict":)
    st.warning("ยังไม่มีข้อมูลพรรณไม้ในระบบ กรุณาเพิ่มข้อมูลในระบบหลังบ้าน")
else:
    plant_name = st.selectbox("เลือกพืชที่ต้องการศึกษา:", list(plants_dict.keys()))
    
    if plant_name:
        data = plants_dict[plant_name]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if data.get('image') and os.path.exists(data['image']):
                st.image(data['image'], caption=plant_name, use_column_width=True)
            else:
                st.info("ไม่มีรูปภาพพืชนี้")
                
        with col2:
            st.subheader(f"🌱 {plant_name}")
            st.write(f"**ชื่อวิทยาศาสตร์:** *{data['scientific_name']}*")
            st.success(f"**สรรพคุณ:** {data['benefit']}")
            
            # สร้าง QR Code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(f"โรงเรียนฐานปัญญา - พืช: {plant_name} | ชื่อวิทย์: {data['scientific_name']} | สรรพคุณ: {data['benefit']}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = io.BytesIO()
            img.save(buf)
            st.image(buf.getvalue(), width=180, caption=f"QR Code ของ {plant_name}")with st.form("login_form"):
    user_id = st.text_input("กรอกเลขประจำตัว (นักเรียน / ครู / แอดมิน):")
    submit_login = st.form_submit_button("เข้าสู่ระบบ")
    
    if submit_login:
        users = st.session_state['data']['users']
        if user_id in users:
            user_info = users[user_id]
            st.success(f"ยินดีต้อนรับ คุณ{user_info['name']} (สถานะ: {user_info['role']})")
            
            # บันทึกประวัติการเข้าสู่ระบบ (Logs)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                "id": user_id,
                "name": user_info['name'],
                "role": user_info['role'],
                "time": now_str
            }
            st.session_state['data']['logs'].append(log_entry)
            save_data(st.session_state['data'])
        else:
            st.error("ไม่พบเลขประจำตัวนี้ในระบบ กรุณาติดต่อผู้ดูแลระบบ")# รหัสผ่านแอดมิน
if pwd == "admin1234":
    st.success("เข้าสู่ระบบหลังบ้านสำเร็จ!")
    
    tab1, tab2, tab3 = st.tabs(["จัดการพรรณไม้", "จัดการสมาชิก", "ดูประวัติการเข้าสู่ระบบ"])
    
    # --- TAB 1: จัดการพรรณไม้ (เพิ่ม, แก้ไข, ลบ) ---
    with tab1:
        st.subheader("🌿 จัดการข้อมูลพรรณไม้")
        action = st.radio("เลือกการทำงานพืช:", ["เพิ่มพืชใหม่", "แก้ไข/ลบ พืชที่มีอยู่"], horizontal=True)
        
        if action == "เพิ่มพืชใหม่":
            with st.form("add_plant_form"):
                p_name = st.text_input("ชื่อพืช (ช่องบอกว่านี่คือต้นอะไร)")
                p_sci = st.text_input("ชื่อวิทยาศาสตร์")
                p_ben = st.text_area("สรรพคุณ")
                p_img = st.file_uploader("อัปโหลดรูปภาพพืช", type=["jpg", "png", "jpeg"])
                
                submitted = st.form_submit_button("บันทึกพืชใหม่")
                if submitted and p_name:
                    img_path = None
                    if p_img is not None:
                        img_path = os.path.join(UPLOAD_DIR, f"{p_name}_{p_img.name}")
                        with open(img_path, "wb") as f:
                            f.write(p_img.getbuffer())
                            
                    st.session_state['data']['plants'][p_name] = {
                        "scientific_name": p_sci,
                        "benefit": p_ben,
                        "image": img_path
                    }
                    save_data(st.session_state['data'])
                    st.success(f"บันทึกพืช '{p_name}' เรียบร้อยแล้ว!")
                    st.rerun()
                    
        elif action == "แก้ไข/ลบ พืชที่มีอยู่":
            plants = st.session_state['data']['plants']
            if not plants:
                st.info("ยังไม่มีข้อมูลพืชในระบบ")
            else:
                selected_p = st.selectbox("เลือกพืชที่ต้องการจัดการ:", list(plants.keys()))
                p_data = plants[selected_p]
                
                with st.form("edit_plant_form"):
                    new_sci = st.text_input("ชื่อวิทยาศาสตร์", value=p_data['scientific_name'])
                    new_ben = st.text_area("สรรพคุณ", value=p_data['benefit'])
                    new_img = st.file_uploader("เปลี่ยนรูปภาพพืช (ถ้ามี)", type=["jpg", "png", "jpeg"])
                    
                    col_e1, col_e2 = st.columns(2)
                    update_btn = col_e1.form_submit_button("อัปเดตข้อมูลพืช")
                    delete_btn = col_e2.form_submit_button("ลบพืชนี้")
                    
                    if update_btn:
                        img_path = p_data['image']
                        if new_img is not None:
                            img_path = os.path.join(UPLOAD_DIR, f"{selected_p}_{new_img.name}")
                            with open(img_path, "wb") as f:
                                f.write(new_img.getbuffer())
                                
                        st.session_state['data']['plants'][selected_p] = {
                            "scientific_name": new_sci,
                            "benefit": new_ben,
                            "image": img_path
                        }
                        save_data(st.session_state['data'])
                        st.success(f"อัปเดตข้อมูล '{selected_p}' สำเร็จ!")
                        st.rerun()
                        
                    if delete_btn:
                        del st.session_state['data']['plants'][selected_p]
                        save_data(st.session_state['data'])
                        st.warning(f"ลบพืช '{selected_p}' เรียบร้อยแล้ว!")
                        st.rerun()

    # --- TAB 2: จัดการสมาชิก (เพิ่ม/ลบ นักเรียน, ครู, แอดมิน) ---
    with tab2:
        st.subheader("👥 จัดการรายชื่อสมาชิก (นักเรียน / ครู / ผู้ดูแลระบบ)")
        
        with st.form("add_user_form"):
            u_id = st.text_input("เลขประจำตัว / รหัสสมาชิก")
            u_name = st.text_input("ชื่อ - นามสกุล")
            u_role = st.selectbox("สถานะ", ["นักเรียน", "ครู", "ผู้ดูแลระบบ"])
            u_class = st.text_input("ชั้นเรียน / แผนก (ถ้ามี)", value="-")
            
            if st.form_submit_button("เพิ่มสมาชิก"):
                if u_id and u_name:
                    st.session_state['data']['users'][u_id] = {
                        "name": u_name,
                        "role": u_role,
                        "class": u_class
                    }
                    save_data(st.session_state['data'])
                    st.success(f"เพิ่มสมาชิก '{u_name}' สำเร็จ!")
                    st.rerun()
                else:
                    st.error("กรุณากรอกเลขประจำตัวและชื่อให้ครบถ้วน")
        
        st.write("---")
        st.subheader("รายชื่อสมาชิกทั้งหมดในระบบ")
        users = st.session_state['data']['users']
        for uid, info in list(users.items()):
            col_u1, col_u2 = st.columns([4, 1])
            col_u1.write(f"**รหัส:** {uid} | **ชื่อ:** {info['name']} | **สถานะ:** {info['role']} | **ชั้น/แผนก:** {info['class']}")
            if col_u2.button(f"ลบ {uid}", key=f"del_user_{uid}"):
                del st.session_state['data']['users'][uid]
                save_data(st.session_state['data'])
                st.success(f"ลบรหัส {uid} สำเร็จ!")
                st.rerun()

    # --- TAB 3: ดูประวัติการเข้าสู่ระบบรายวัน ---
    with tab3:
        st.subheader("📊 ประวัติการเข้าสู่ระบบรายวัน (Login History)")
        logs = st.session_state['data']['logs']
        
        if not logs:
            st.info("ยังไม่มีประวัติการเข้าสู่ระบบ")
        else:
            filter_date = st.text_input("กรองตามวันที่ (รูปแบบ YYYY-MM-DD เช่น 2026-09-23) หรือเว้นว่างเพื่อดูทั้งหมด:")
            
            filtered_logs = logs
            if filter_date:
                filtered_logs = [l for l in logs if filter_date in l['time']]
            
            st.write(f"จำนวนรายการทั้งหมด: {len(filtered_logs)} ครั้ง")
            for log in reversed(filtered_logs):
                st.markdown(f"- 🕒 **เวลา:** {log['time']} | **รหัส:** {log['id']} | **ชื่อ:** {log['name']} | **สถานะ:** {log['role']}")

elif pwd != "":
    st.error("รหัสผ่านไม่ถูกต้อง (รหัสคือ admin1234)")
