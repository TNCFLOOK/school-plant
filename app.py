import streamlit as st
import qrcode
from PIL import Image
import io

st.set_page_config(page_title="ระบบสารสนเทศพฤกษศาสตร์โรงเรียน", page_icon="🌿", layout="wide")

# --- กำหนดค่าเริ่มต้นใน Session State ---
if 'plants' not in st.session_state:
    st.session_state['plants'] = {
        "ราชพฤกษ์ (คูน)": {
            "scientific_name": "Cassia fistula L.",
            "family": "Fabaceae",
            "benefit": "ไม้ดอกประดับ สมุนไพรพื้นบ้าน",
            "image": None
        }
    }

if 'users' not in st.session_state:
    # ค่าเริ่มต้น: แอดมินหลักเลขประจำตัว 'admin01' (รหัสผ่าน 1234 หรือกำหนดอิสระ)
    st.session_state['users'] = {
        "admin01": {"name": "ผู้ดูแลระบบหลัก", "role": "Admin"}
    }

if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

# --- ส่วนของการเข้าสู่ระบบ (Login Sidebar) ---
st.sidebar.title("🔐 เข้าสู่ระบบ")

if st.session_state['logged_in_user'] is None:
    login_id = st.sidebar.text_input("กรอกเลขประจำตัว (นักเรียน/ครู/แอดมิน)")
    if st.sidebar.button("เข้าสู่ระบบ"):
        if not login_id:
            st.sidebar.error("กรุณากรอกเลขประจำตัว")
        elif login_id in st.session_state['users']:
            st.session_state['logged_in_user'] = login_id
            st.session_state['user_role'] = st.session_state['users'][login_id]["role"]
            st.sidebar.success(f"ยินดีต้อนรับคุณ {st.session_state['users'][login_id]['name']}")
            st.rerun()
        else:
            # ถ้ารหัสไม่ตรงในระบบ ให้ถือว่าเป็นนักเรียน/คุณครูทั่วไปโดยอัตโนมัติ
            st.session_state['logged_in_user'] = login_id
            st.session_state['user_role'] = "User"
            st.sidebar.success(f"เข้าสู่ระบบสำเร็จ (ผู้ใช้งานทั่วไป: {login_id})")
            st.rerun()
else:
    st.sidebar.info((
        f"เข้าสู่ระบบโดย: {st.session_state['logged_in_user']}"
        f" ({st.session_state['user_role']})"
    ))
    if st.sidebar.button("ออกจากระบบ"):
        st.session_state['logged_in_user'] = None
        st.session_state['user_role'] = None
        st.rerun()

st.sidebar.markdown("---")

# --- เมนูหลัก ---
menu_options = ["หน้าหลัก (ค้นหา & QR Code)"]
if st.session_state['user_role'] == "Admin":
    menu_options.append("จัดการข้อมูลพืช & เพิ่มรูปภาพ")
    menu_options.append("จัดการผู้ดูแลระบบ (Admin)")

menu = st.sidebar.selectbox("เมนูการใช้งาน", menu_options)

# ==========================================
# 1. หน้าหลัก (ค้นหา & QR Code)
# ==========================================
if menu == "หน้าหลัก (ค้นหา & QR Code)":
    st.markdown(
        "<h1 style='text-align: center; color: #2E7D32;'>🌿 ระบบสารสนเทศพฤกษศาสตร์โรงเรียน</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; color: #555;'>โรงเรียนฐานปัญญา</p>",
        unsafe_allow_html=True
    )
    st.write("---")

    if len(st.session_state['plants']) == 0:
        st.warning("ยังไม่มีข้อมูลพืชในระบบ กรุณาให้แอดมินเพิ่มข้อมูลพืช")
    else:
        plant_name = st.selectbox("🔍 เลือกหรือค้นหาชื่อพืช", list(st.session_state['plants'].keys()))
        data = st.session_state['plants'][plant_name]

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader(f"🌱 ชื่อพืช: {plant_name}")
            st.write(f"**ชื่อวิทยาศาสตร์:** *{data['scientific_name']}*")
            st.write(f"**วงศ์:** {data['family']}")
            st.write(f"**ประโยชน์/สรรพคุณ:** {data['benefit']}")
            
            # แสดงรูปภาพถ้ามี
            if data['image'] is not None:
                st.image(data['image'], caption=f"ภาพถ่าย {plant_name}", use_column_width=True)
            else:
                st.info("ยังไม่มีรูปภาพประกอบสำหรับพืชชนิดนี้")

        with col2:
            st.subheader("📱 QR Code ประจำต้นไม้")
            qr_data = f"พืช: {plant_name} | ชื่อวิทย์: {data['scientific_name']} | ประโยชน์: {data['benefit']}"
            
            # สร้าง QR Code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # แปลงภาพเพื่อแสดงผลใน Streamlit
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            st.image(buffered.getvalue(), width=250)
            st.success("สแกน QR Code นี้เพื่อดูข้อมูลพืชผ่านมือถือได้ทันที!")

# ==========================================
# 2. จัดการข้อมูลพืช & เพิ่มรูปภาพ (Admin Only)
# ==========================================
elif menu == "จัดการข้อมูลพืช & เพิ่มรูปภาพ":
    st.title("🛠️ ระบบจัดการข้อมูลพืชและรูปภาพ")
    
    tab1, tab2 = st.tabs(["➕ เพิ่มพืชใหม่", "❌ ลบข้อมูลพืช"])
    
    with tab1:
        st.subheader("เพิ่มข้อมูลพืชและอัปโหลดรูปภาพ")
        with st.form("add_plant_form"):
            new_name = st.text_input("ชื่อพืช (ภาษาไทย/ชื่อสามัญ)")
            new_sci = st.text_input("ชื่อวิทยาศาสตร์")
            new_family = st.text_input("วงศ์ (Family)")
            new_benefit = st.text_area("ประโยชน์ / สรรพคุณ")
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพพืช (PNG, JPG)", type=["png", "jpg", "jpeg"])
            
            submit_plant = st.form_submit_button("บันทึกข้อมูลพืช")
            
            if submit_plant:
                if new_name and new_sci:
                    img_bytes = uploaded_file.read() if uploaded_file is not None else None
                    st.session_state['plants'][new_name] = {
                        "scientific_name": new_sci,
                        "family": new_family,
                        "benefit": new_benefit,
                        "image": img_bytes
                    }
                    st.success(f"เพิ่มข้อมูลพืช '{new_name}' สำเร็จเรียบร้อยแล้ว!")
                else:
                    st.error("กรุณากรอกชื่อพืชและชื่อวิทยาศาสตร์ให้ครบถ้วน")

    with tab2:
        st.subheader("ลบข้อมูลพืชที่มีในระบบ")
        if len(st.session_state['plants']) > 0:
            plant_to_delete = st.selectbox("เลือกพืชที่ต้องการลบ", list(st.session_state['plants'].keys()))
            if st.button("ยืนยันการลบพืช"):
                del st.session_state['plants'][plant_to_delete]
                st.success(f"ลบข้อมูลพืช '{plant_to_delete}' เรียบร้อยแล้ว!")
                st.rerun()
        else:
            st.info("ไม่มีข้อมูลพืชให้ลบ")

# ==========================================
# 3. จัดการผู้ดูแลระบบ (Admin Only)
# ==========================================
elif menu == "จัดการผู้ดูแลระบบ (Admin)":
    st.title("🛡️ จัดการสิทธิ์ผู้ดูแลระบบ (Admin)")
    
    with st.form("add_admin_form"):
        st.subheader("เพิ่มเลขประจำตัวแอดมินใหม่")
        new_admin_id = st.text_input("เลขประจำตัวครู/แอดมินใหม่")
        new_admin_name = st.text_input("ชื่อ-นามสกุล ผู้ดูแลระบบ")
        
        submit_admin = st.form_submit_button("บันทึกสิทธิ์แอดมิน")
        
        if submit_admin:
            if new_admin_id and new_admin_name:
                st.session_state['users'][new_admin_id] = {
                    "name": new_admin_name,
                    "role": "Admin"
                }
                st.success(f"เพิ่มสิทธิ์แอดมินให้เลขประจำตัว '{new_admin_id}' สำเร็จ!")
            else:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
                
    st.write("---")
    st.subheader("📋 รายชื่อผู้ดูแลระบบทั้งหมดในปัจจุบัน")
    for uid, info in st.session_state['users'].items():
        st.write(f"- **เลขประจำตัว:** `{uid}` | **ชื่อ:** {info['name']} | **สถานะ:** {info['role']}")
