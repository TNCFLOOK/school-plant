import streamlit as st
import qrcode
from PIL import Image
import io
import json
import os
import base64

st.set_page_config(page_title="ระบบสารสนเทศพฤกษศาสตร์โรงเรียน", page_icon="🌿", layout="wide")

# ==========================================
# 📂 ฟังก์ชันจัดการบันทึกและโหลดข้อมูลด้วย Base64 (ป้องกันรูปหายบน Cloud)
# ==========================================
PLANTS_FILE = "plants_data.json"
STUDENTS_FILE = "students_data.json"

def load_plants():
    if os.path.exists(PLANTS_FILE):
        try:
            with open(PLANTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for plant_name, plant_info in data.items():
                    # แปลง string base64 กลับเป็น bytes ของรูปภาพ
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
        if p_data.get("image") is not None and isinstance(p_data["image"], bytes):
            img_b64 = base64.b64encode(p_data["image"]).decode('utf-8')
        
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

# --- โหลดข้อมูลเข้าสู่ Session State ---
if 'plants' not in st.session_state:
    st.session_state['plants'] = load_plants()

if 'students' not in st.session_state:
    st.session_state['students'] = load_students()

if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

# ==========================================
# 🔐 ระบบหน้า Login ก่อนเข้าใช้งานระบบหลัก
# ==========================================
if st.session_state['logged_in_user'] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🌿 เข้าสู่ระบบพฤกษศาสตร์โรงเรียน</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #555;'>กรุณากรอกเลขประจำตัวเพื่อเข้าใช้งาน</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            input_id = st.text_input("เลขประจำตัว (นักเรียน / แอดมิน)").strip()
            submit_login = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
            
            if submit_login:
                if not input_id:
                    st.error("กรุณากรอกเลขประจำตัว")
                elif input_id in st.session_state['students']:
                    st.session_state['logged_in_user'] = input_id
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error(f"ไม่พบเลขประจำตัว '{input_id}' ในระบบ กรุณาติดต่อแอดมินเพื่อลงทะเบียน")
    st.stop()

# ==========================================
# 🖥️ เมื่อเข้าสู่ระบบแล้ว (Sidebar และเมนูหลัก)
# ==========================================
current_user_id = st.session_state['logged_in_user']
user_info = st.session_state['students'].get(current_user_id, {"name": "ผู้ใช้งาน", "class": "-", "role": "User"})

st.sidebar.title("👤 ข้อมูลผู้ใช้งาน")
st.sidebar.info(f"**ชื่อ:** {user_info['name']}\n\n**เลขประจำตัว:** `{current_user_id}`\n\n**ชั้นเรียน:** {user_info['class']}\n\n**สถานะ:** {user_info['role']}")

if st.sidebar.button("🚪 ออกจากระบบ", use_container_width=True):
    st.session_state['logged_in_user'] = None
    st.rerun()

st.sidebar.markdown("---")

menu_options = ["🏠 หน้าหลัก (ค้นหา & QR Code)"]
if user_info.get('role') == "Admin":
    menu_options.append("🛠️ จัดการข้อมูลพืช (เพิ่ม/แก้ไข/ลบ)")
    menu_options.append("👥 จัดการข้อมูลนักเรียน/ผู้ใช้")

menu = st.sidebar.selectbox("📂 เมนูการใช้งาน", menu_options)

# ==========================================
# ฟังก์ชันช่วยสร้าง QR Code
# ==========================================
def generate_qr_code(plant_name, data):
    qr_data = f"พืช: {plant_name} | ชื่อวิทย์: {data.get('scientific_name', '')} | วงศ์: {data.get('family', '')} | สรรพคุณ: {data.get('benefit', '')}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# ==========================================
# 1. หน้าหลัก (ค้นหาพืช & QR Code)
# ==========================================
if menu == "🏠 หน้าหลัก (ค้นหา & QR Code)":
    st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🌿 ระบบสารสนเทศพฤกษศาสตร์โรงเรียน</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>โรงเรียนฐานปัญญา</p>", unsafe_allow_html=True)
    st.write("---")

    if not st.session_state['plants']:
        st.warning("ยังไม่มีข้อมูลพืชในระบบ กรุณาให้แอดมินเพิ่มข้อมูลพืช")
    else:
        plant_name = st.selectbox("🔍 เลือกหรือค้นหาชื่อพืช", list(st.session_state['plants'].keys()))
        data = st.session_state['plants'][plant_name]

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader(f"🌱 ชื่อพืช: {plant_name}")
            st.write(f"**ชื่อวิทยาศาสตร์:** *{data.get('scientific_name', '-') }*")
            st.write(f"**วงศ์:** {data.get('family', '-')}")
            st.write(f"**ประโยชน์/สรรพคุณ:** {data.get('benefit', '-')}")
            
            # ตรวจสอบรูปภาพอย่างปลอดภัยเพื่อป้องกัน TypeError
            img_data = data.get('image')
            if img_data is not None and isinstance(img_data, bytes) and len(img_data) > 0:
                try:
                    st.image(img_data, caption=f"ภาพถ่าย {plant_name}", use_column_width=True)
                except Exception:
                    st.info("ไม่สามารถแสดงรูปภาพได้ (รูปแบบไฟล์ไม่ถูกต้อง)")
            else:
                st.info("ยังไม่มีรูปภาพประกอบสำหรับพืชชนิดนี้")

        with col2:
            st.subheader("📱 QR Code อัตโนมัติประจำต้นไม้")
            try:
                qr_bytes = generate_qr_code(plant_name, data)
                st.image(qr_bytes, width=250)
                st.success("QR Code ถูกสร้างอัตโนมัติจากข้อมูลล่าสุด สามารถสแกนเพื่อดูข้อมูลพืชได้ทันที!")
            except Exception as e:
                st.error("ไม่สามารถสร้าง QR Code ได้ในขณะนี้")

# ==========================================
# 2. จัดการข้อมูลพืช (Admin Only)
# ==========================================
elif menu == "🛠️ จัดการข้อมูลพืช (เพิ่ม/แก้ไข/ลบ)":
    st.title("🛠️ ระบบหลังบ้าน: จัดการข้อมูลพืชพฤกษศาสตร์")
    
    tab1, tab2, tab3 = st.tabs(["➕ เพิ่มพืชใหม่", "✏️ แก้ไขรายละเอียดพืช", "❌ ลบข้อมูลพืช"])
    
    with tab1:
        st.subheader("เพิ่มข้อมูลพืชและอัปโหลดรูปภาพใหม่")
        with st.form("add_plant_form"):
            new_name = st.text_input("ชื่อพืช (ภาษาไทย/ชื่อสามัญ)")
            new_sci = st.text_input("ชื่อวิทยาศาสตร์")
            new_family = st.text_input("วงศ์ (Family)")
            new_benefit = st.text_area("ประโยชน์ / สรรพคุณ")
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพพืช (PNG, JPG)", type=["png", "jpg", "jpeg"])
            
            submit_plant = st.form_submit_button("บันทึกและสร้าง QR Code อัตโนมัติ")
            
            if submit_plant:
                if new_name and new_sci:
                    if new_name in st.session_state['plants']:
                        st.error("มีชื่อพืชนี้อยู่ในระบบแล้ว กรุณาใช้เมนูแก้ไขข้อมูล")
                    else:
                        img_bytes = uploaded_file.read() if uploaded_file is not None else None
                        st.session_state['plants'][new_name] = {
                            "scientific_name": new_sci,
                            "family": new_family,
                            "benefit": new_benefit,
                            "image": img_bytes
                        }
                        save_plants()
                        st.success(f"เพิ่มข้อมูลพืช '{new_name}' เรียบร้อยแล้ว!")
                        st.rerun()
                else:
                    st.error("กรุณากรอกชื่อพืชและชื่อวิทยาศาสตร์ให้ครบถ้วน")

    with tab2:
        st.subheader("แก้ไขรายละเอียดและสรรพคุณพืช")
        if st.session_state['plants']:
            selected_plant = st.selectbox("เลือกพืชที่ต้องการแก้ไข", list(st.session_state['plants'].keys()), key="edit_plant_select")
            current_data = st.session_state['plants'][selected_plant]

            with st.form("edit_plant_form"):
                edit_name = st.text_input("ชื่อพืช (เปลี่ยนชื่อได้)", value=selected_plant)
                edit_sci = st.text_input("ชื่อวิทยาศาสตร์", value=current_data.get('scientific_name', ''))
                edit_family = st.text_input("วงศ์ (Family)", value=current_data.get('family', ''))
                edit_benefit = st.text_area("ประโยชน์ / สรรพคุณ", value=current_data.get('benefit', ''))
                
                st.write("---")
                st.write("รูปภาพปัจจุบัน:")
                if current_data.get('image') is not None and isinstance(current_data['image'], bytes):
                    try:
                        st.image(current_data['image'], width=150)
                    except Exception:
                        st.info("ไม่สามารถแสดงรูปภาพปัจจุบันได้")
                else:
                    st.info("ยังไม่มีรูปภาพ")

                edit_file = st.file_uploader("อัปโหลดเปลี่ยนรูปภาพใหม่ (ถ้าต้องการเปลี่ยน)", type=["png", "jpg", "jpeg"], key="edit_img")
                
                submit_edit = st.form_submit_button("บันทึกการแก้ไข & อัปเดต QR Code")
                
                if submit_edit:
                    if edit_name and edit_sci:
                        if edit_name != selected_plant:
                            if edit_name in st.session_state['plants']:
                                st.error("ชื่อพืชใหม่นี้ซ้ำกับที่มีอยู่แล้วในระบบ")
                                st.stop()
                            else:
                                st.session_state['plants'][edit_name] = st.session_state['plants'].pop(selected_plant)
                        
                        target_data = st.session_state['plants'][edit_name]
                        target_data['scientific_name'] = edit_sci
                        target_data['family'] = edit_family
                        target_data['benefit'] = edit_benefit
                        
                        if edit_file is not None:
                            target_data['image'] = edit_file.read()
                            
                        save_plants()
                        st.success(f"แก้ไขข้อมูลพืช '{edit_name}' สำเร็จ!")
                        st.rerun()
                    else:
                        st.error("กรุณากรอกชื่อพืชและชื่อวิทยาศาสตร์")
        else:
            st.info("ยังไม่มีข้อมูลพืชในระบบสำหรับแก้ไข")

    with tab3:
        st.subheader("ลบข้อมูลพืชที่มีในระบบ")
        if st.session_state['plants']:
            plant_to_delete = st.selectbox("เลือกพืชที่ต้องการลบ", list(st.session_state['plants'].keys()), key="del_plant_select")
            if st.button("ยืนยันการลบพืช"):
                del st.session_state['plants'][plant_to_delete]
                save_plants()
                st.success(f"ลบข้อมูลพืช '{plant_to_delete}' เรียบร้อยแล้ว!")
                st.rerun()
        else:
            st.info("ไม่มีข้อมูลพืชให้ลบ")

# ==========================================
# 3. จัดการข้อมูลนักเรียน/ผู้ใช้ (Admin Only)
# ==========================================
elif menu == "👥 จัดการข้อมูลนักเรียน/ผู้ใช้":
    st.title("👥 ระบบหลังบ้าน: จัดการข้อมูลนักเรียนและผู้ใช้งาน")
    
    tab1, tab2, tab3 = st.tabs(["➕ เพิ่มนักเรียนใหม่", "✏️ แก้ไขข้อมูลนักเรียน", "❌ ลบนักเรียนออกจากระบบ"])
    
    with tab1:
        st.subheader("เพิ่มเลขประจำตัว ชื่อ และชั้นเรียนของนักเรียน")
        with st.form("add_student_form"):
            new_id = st.text_input("เลขประจำตัวนักเรียน (เช่น 65002)").strip()
            new_name = st.text_input("ชื่อ-นามสกุล นักเรียน").strip()
            new_class = st.text_input("ชั้นเรียน (เช่น ม.3/1 หรือ ม.1/2)").strip()
            new_role = st.selectbox("กำหนดบทบาท", ["User", "Admin"])
            
            submit_student = st.form_submit_button("บันทึกข้อมูลนักเรียน")
            
            if submit_student:
                if new_id and new_name and new_class:
                    if new_id in st.session_state['students']:
                        st.error(f"เลขประจำตัว '{new_id}' นี้มีอยู่ในระบบแล้ว!")
                    else:
                        st.session_state['students'][new_id] = {
                            "name": new_name,
                            "class": new_class,
                            "role": new_role
                        }
                        save_students()
                        st.success(f"เพิ่มนักเรียน '{new_name}' (เลขประจำตัว: {new_id}) สำเร็จเรียบร้อย!")
                        st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลให้ครบทุกช่อง")

    with tab2:
        st.subheader("แก้ไขชื่อ ชั้นเรียน หรือเปลี่ยนเลขประจำตัวนักเรียน")
        if st.session_state['students']:
            selected_student_id = st.selectbox("เลือกนักเรียนที่ต้องการแก้ไข (จากเลขประจำตัว)", list(st.session_state['students'].keys()), key="edit_stu_select")
            current_stu_data = st.session_state['students'][selected_student_id]

            with st.form("edit_student_form"):
                edit_id = st.text_input("เลขประจำตัว (แก้ไขได้)", value=selected_student_id).strip()
                edit_name = st.text_input("ชื่อ-นามสกุล", value=current_stu_data.get('name', '')).strip()
                edit_class = st.text_input("ชั้นเรียน", value=current_stu_data.get('class', '')).strip()
                edit_role = st.selectbox("บทบาทในระบบ", ["User", "Admin"], index=0 if current_stu_data.get('role')=="User" else 1)
                
                submit_edit_stu = st.form_submit_button("บันทึกการแก้ไขข้อมูลนักเรียน")
                
                if submit_edit_stu:
                    if edit_id and edit_name and edit_class:
                        if edit_id != selected_student_id:
                            if edit_id in st.session_state['students']:
                                st.error("เลขประจำตัวใหม่นี้ซ้ำกับผู้อื่นในระบบ")
                                st.stop()
                            else:
                                st.session_state['students'][edit_id] = st.session_state['students'].pop(selected_student_id)
                        
                        target_stu = st.session_state['students'][edit_id]
                        target_stu['name'] = edit_name
                        target_stu['class'] = edit_class
                        target_stu['role'] = edit_role
                        
                        save_students()
                        st.success("แก้ไขข้อมูลนักเรียนเรียบร้อยแล้ว!")
                        st.rerun()
                    else:
                        st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
        else:
            st.info("ยังไม่มีข้อมูลนักเรียนในระบบ")

    with tab3:
        st.subheader("ลบข้อมูลนักเรียนออกจากระบบ")
        if st.session_state['students']:
            stu_to_delete = st.selectbox("เลือกนักเรียนที่ต้องการลบ", list(st.session_state['students'].keys()), key="del_stu_select")
            st.warning(f"กำลังจะลบ: {st.session_state['students'][stu_to_delete].get('name')} ({stu_to_delete})")
            
            if st.button("ยืนยันการลบนักเรียน"):
                if stu_to_delete == current_user_id:
                    st.error("คุณไม่สามารถลบบัญชีที่กำลังใช้งานอยู่ได้!")
                else:
                    del st.session_state['students'][stu_to_delete]
                    save_students()
                    st.success("ลบข้อมูลนักเรียนเรียบร้อยแล้ว!")
                    st.rerun()
        else:
            st.info("ไม่มีข้อมูลนักเรียนให้ลบ")
