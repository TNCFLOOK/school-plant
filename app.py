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
                            decoded = base64.b64decode(plant_info["image_base64"])
                            plant_info["image"] = decoded if len(decoded) > 10 else None
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
        if img_data is not None and isinstance(img_data, bytes) and len(img_data) > 10:
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
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🌿 เข้าสู่ระบบพฤกษศาสตร์โรงเรียน</h2>", unsafe_allow_html=True)
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
                    st.error(f"ไม่พบเลขประจำตัว '{input_id}' ในระบบ")
    st.stop()

# ==========================================
# 🖥️ Sidebar เมนู
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

def generate_qr_code(plant_name):
    base_url = "https://school-plant-gbfwt8zbdxa9mnjf7yay36.streamlit.app"
    qr_data = f"{base_url}/?plant={plant_name}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
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
            
            img_data = data.get('image')
            if img_data is not None and isinstance(img_data, bytes) and len(img_data) > 10:
                try:
                    st.image(img_data, caption=f"ภาพถ่าย {plant_name}", use_column_width=True)
                except Exception:
                    st.warning("⚠️ ไฟล์รูปภาพเสียหาย กรุณาอัปโหลดรูปภาพใหม่อีกครั้งในเมนูจัดการพืช")
            else:
                st.warning("⚠️ ยังไม่มีรูปภาพประกอบสำหรับพืชชนิดนี้ (สามารถไปอัปโหลดได้ที่เมนูจัดการพืช)")

        with col2:
            st.subheader("📱 QR Code ประจำต้นไม้ (สแกนง่าย)")
            try:
                qr_bytes = generate_qr_code(plant_name)
                st.image(qr_bytes, width=250)
                st.success("QR Code พร้อมใช้งาน สแกนเพื่อเปิดดูข้อมูลพืชได้ทันที!")
            except Exception as e:
                st.error("ไม่สามารถสร้าง QR Code ได้")

# ==========================================
# 2. จัดการข้อมูลพืช (Admin Only)
# ==========================================
elif menu == "🛠️ จัดการข้อมูลพืช (เพิ่ม/แก้ไข/ลบ)":
    st.title("🛠️ ระบบหลังบ้าน: จัดการข้อมูลพืชพฤกษศาสตร์")
    
    tab1, tab2, tab3 = st.tabs(["➕ เพิ่มพืชใหม่", "✏️ แก้ไขรายละเอียดพืช", "❌ ลบข้อมูลพืช"])
    
    with tab1:
        st.subheader("เพิ่มข้อมูลพืชและอัปโหลดรูปภาพใหม่")
        with st.form("add_plant_form"):
            new_name = st.text_input("ชื่อพืช (ภาษาไทย)")
            new_sci = st.text_input("ชื่อวิทยาศาสตร์")
            new_family = st.text_input("วงศ์ (Family)")
            new_benefit = st.text_area("ประโยชน์ / สรรพคุณ")
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพพืช (PNG, JPG)", type=["png", "jpg", "jpeg"])
            
            submit_plant = st.form_submit_button("บันทึกข้อมูลพืช")
            
            if submit_plant:
                if new_name and new_sci:
                    if new_name in st.session_state['plants']:
                        st.error("มีชื่อพืชนี้อยู่ในระบบแล้ว")
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
                    st.error("กรุณากรอกชื่อพืชและชื่อวิทยาศาสตร์")

    with tab2:
        st.subheader("แก้ไขรายละเอียดและจัดการรูปภาพพืช")
        if st.session_state['plants']:
            selected_plant = st.selectbox("เลือกพืชที่ต้องการแก้ไข", list(st.session_state['plants'].keys()), key="edit_plant_select")
            current_data = st.session_state['plants'][selected_plant]

            with st.form("edit_plant_form"):
                edit_name = st.text_input("ชื่อพืช", value=selected_plant)
                edit_sci = st.text_input("ชื่อวิทยาศาสตร์", value=current_data.get('scientific_name', ''))
                edit_family = st.text_input("วงศ์ (Family)", value=current_data.get('family', ''))
                edit_benefit = st.text_area("ประโยชน์ / สรรพคุณ", value=current_data.get('benefit', ''))
                
                st.write("---")
                curr_img = current_data.get('image')
                has_valid_img = (curr_img is not None and isinstance(curr_img, bytes) and len(curr_img) > 10)
                
                if has_valid_img:
                    try:
                        st.image(curr_img, width=150, caption="รูปภาพปัจจุบันในระบบ")
                    except Exception:
                        pass
                    delete_image_checkbox = st.checkbox("🗑️ ติ๊กเพื่อลบรูปภาพนี้ออก")
                else:
                    st.info("พืชนี้ยังไม่มีรูปภาพในระบบ")
                    delete_image_checkbox = False

                edit_file = st.file_uploader("อัปโหลดรูปภาพใหม่ (หากต้องการเปลี่ยน)", type=["png", "jpg", "jpeg"], key="edit_img")
                
                submit_edit = st.form_submit_button("บันทึกการแก้ไข")
                
                if submit_edit:
                    if edit_name and edit_sci:
                        if edit_name != selected_plant:
                            if edit_name in st.session_state['plants']:
                                st.error("ชื่อพืชใหม่ซ้ำกับที่มีอยู่แล้ว")
                                st.stop()
                            else:
                                st.session_state['plants'][edit_name] = st.session_state['plants'].pop(selected_plant)
                        
                        target_data = st.session_state['plants'][edit_name]
                        target_data['scientific_name'] = edit_sci
                        target_data['family'] = edit_family
                        target_data['benefit'] = edit_benefit
                        
                        # จัดการสถานะรูปภาพ (ลบรูป / เปลี่ยนรูปใหม่ / คงรูปเดิม)
                        if delete_image_checkbox:
                            target_data['image'] = None
                        elif edit_file is not None:
                            target_data['image'] = edit_file.read()
                        
                        save_plants()
                        st.success(f"แก้ไขข้อมูลพืชสำเร็จ!")
                        st.rerun()
                    else:
                        st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
        else:
            st.info("ยังไม่มีข้อมูลพืชในระบบ")

    with tab3:
        st.subheader("ลบข้อมูลพืช")
        if st.session_state['plants']:
            plant_to_delete = st.selectbox("เลือกพืชที่ต้องการลบ", list(st.session_state['plants'].keys()), key="del_plant_select")
            if st.button("ยืนยันการลบพืช"):
                del st.session_state['plants'][plant_to_delete]
                save_plants()
                st.success("ลบข้อมูลพืชเรียบร้อยแล้ว!")
                st.rerun()
        else:
            st.info("ไม่มีข้อมูลพืชให้ลบ")

# ==========================================
# 3. จัดการข้อมูลนักเรียน/ผู้ใช้ (Admin Only)
# ==========================================
elif menu == "👥 จัดการข้อมูลนักเรียน/ผู้ใช้":
    st.title("👥 ระบบหลังบ้าน: จัดการข้อมูลผู้ใช้งาน")
    
    tab1, tab2, tab3 = st.tabs(["➕ เพิ่มนักเรียน", "✏️ แก้ไขข้อมูล", "❌ ลบนักเรียน"])
    
    with tab1:
        with st.form("add_student_form"):
            new_id = st.text_input("เลขประจำตัว (เช่น 65002)").strip()
            new_name = st.text_input("ชื่อ-นามสกุล").strip()
            new_class = st.text_input("ชั้นเรียน (เช่น ม.6/1)").strip()
            new_role = st.selectbox("บทบาท", ["User", "Admin"])
            
            if st.form_submit_button("บันทึกนักเรียน"):
                if new_id and new_name and new_class:
                    if new_id in st.session_state['students']:
                        st.error("เลขประจำตัวนี้มีอยู่แล้ว")
                    else:
                        st.session_state['students'][new_id] = {"name": new_name, "class": new_class, "role": new_role}
                        save_students()
                        st.success("เพิ่มนักเรียนสำเร็จ!")
                        st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลให้ครบ")

    with tab2:
        if st.session_state['students']:
            selected_stu = st.selectbox("เลือกนักเรียน", list(st.session_state['students'].keys()), key="edit_s")
            curr_s = st.session_state['students'][selected_stu]
            with st.form("edit_stu_form"):
                e_id = st.text_input("เลขประจำตัว", value=selected_stu)
                e_name = st.text_input("ชื่อ", value=curr_s.get('name', ''))
                e_class = st.text_input("ชั้น", value=curr_s.get('class', ''))
                e_role = st.selectbox("บทบาท", ["User", "Admin"], index=0 if curr_s.get('role')=="User" else 1)
                
                if st.form_submit_button("บันทึกการแก้ไข"):
                    if e_id != selected_stu:
                        st.session_state['students'][e_id] = st.session_state['students'].pop(selected_stu)
                    st.session_state['students'][e_id].update({"name": e_name, "class": e_class, "role": e_role})
                    save_students()
                    st.success("แก้ไขสำเร็จ!")
                    st.rerun()

    with tab3:
        if st.session_state['students']:
            d_stu = st.selectbox("เลือกนักเรียนที่ต้องการลบ", list(st.session_state['students'].keys()), key="del_s")
            if st.button("ยืนยันลบ"):
                if d_stu == current_user_id:
                    st.error("ไม่สามารถลบบัญชีที่กำลังใช้งานอยู่ได้")
                else:
                    del st.session_state['students'][d_stu]
                    save_students()
                    st.success("ลบสำเร็จ!")
                    st.rerun()
