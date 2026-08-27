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
    # ค่าเริ่มต้น: แอดมินหลักเลขประจำตัว 'admin01'
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
    menu_options.append("จัดการข้อมูลพืช (เพิ่ม/แก้ไข/ลบ)")
    menu_options.append("จัดการผู้ดูแลระบบ (Admin)")

menu = st.sidebar.selectbox("เมนูการใช้งาน", menu_options)

# ==========================================
# ฟังก์ชันช่วยสร้าง QR Code
# ==========================================
def generate_qr_code(plant_name, data):
    qr_data = f"พืช: {plant_name} | ชื่อวิทย์: {data['scientific_name']} | วงศ์: {data['family']} | สรรพคุณ: {data['benefit']}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

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
            st.subheader("📱 QR Code อัตโนมัติประจำต้นไม้")
            qr_bytes = generate_qr_code(plant_name, data)
            st.image(qr_bytes, width=250)
            st.success("QR Code ถูกสร้างอัตโนมัติจากข้อมูลล่าสุด สามารถสแกนเพื่อดูข้อมูลพืชได้ทันที!")

# ==========================================
# 2. จัดการข้อมูลพืช (เพิ่ม / แก้ไข / ลบ) (Admin Only)
# ==========================================
elif menu == "จัดการข้อมูลพืช (เพิ่ม/แก้ไข/ลบ)":
    st.title("🛠️ ระบบจัดการหลังบ้าน: ข้อมูลพืชพฤกษศาสตร์")
    
    tab1, tab2, tab3 = st.tabs(["➕ เพิ่มพืชใหม่", "✏️ แก้ไขรายละเอียดพืช", "❌ ลบข้อมูลพืช"])
    
    # --- Tab 1: เพิ่มพืชใหม่ ---
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
                        st.success(f"เพิ่มข้อมูลพืช '{new_name}' และสร้าง QR Code เรียบร้อยแล้ว!")
                else:
                    st.error("กรุณากรอกชื่อพืชและชื่อวิทยาศาสตร์ให้ครบถ้วน")

    # --- Tab 2: แก้ไขรายละเอียดพืช ---
    with tab2:
        st.subheader("แก้ไขรายละเอียดและสรรพคุณพืช")
        if len(st.session_state['plants']) > 0:
            selected_plant = st.selectbox("เลือกพืชที่ต้องการแก้ไข", list(st.session_state['plants'].keys()), key="edit_select")
            current_data = st.session_state['plants'][selected_plant]

            with st.form("edit_plant_form"):
                edit_name = st.text_input("ชื่อพืช (เปลี่ยนชื่อได้)", value=selected_plant)
                edit_sci = st.text_input("ชื่อวิทยาศาสตร์", value=current_data['scientific_name'])
                edit_family = st.text_input("วงศ์ (Family)", value=current_data['family'])
                edit_benefit = st.text_area("ประโยชน์ / สรรพคุณ", value=current_data['benefit'])
                
                st.write("---")
                st.write("รูปภาพปัจจุบัน:")
                if current_data['image'] is not None:
                    st.image(current_data['image'], width=150)
                else:
                    st.info("ยังไม่มีรูปภาพ")

                edit_file = st.file_uploader("อัปโหลดเปลี่ยนรูปภาพใหม่ (ถ้าต้องการเปลี่ยน)", type=["png", "jpg", "jpeg"], key="edit_img")
                
                submit_edit = st.form_submit_button("บันทึกการแก้ไข & อัปเดต QR Code")
                
                if submit_edit:
                    if edit_name and edit_sci:
                        # จัดการกรณีเปลี่ยนชื่อพืชหลัก
                        if edit_name != selected_plant:
                            if edit_name in st.session_state['plants']:
                                st.error("ชื่อพืชใหม่นี้ซ้ำกับที่มีอยู่แล้วในระบบ")
                                st.stop()
                            else:
                                st.session_state['plants'][edit_name] = st.session_state['plants'].pop(selected_plant)
                        
                        # อัปเดตข้อมูล
                        target_data = st.session_state['plants'][edit_name]
                        target_data['scientific_name'] = edit_sci
                        target_data['family'] = edit_family
                        target_data['benefit'] = edit_benefit
                        
                        if edit_file is not None:
                            target_data['image'] = edit_file.read()
                            
                        st.success(f"แก้ไขข้อมูลพืช '{edit_name}' สำเร็จ! ระบบได้สร้าง QR Code ใหม่ให้อัตโนมัติแล้ว")
                        st.rerun()
                    else:
                        st.error("กรุณากรอกชื่อพืชและชื่อวิทยาศาสตร์")
        else:
            st.info("ยังไม่มีข้อมูลพืชในระบบสำหรับแก้ไข")

    # --- Tab 3: ลบข้อมูลพืช ---
    with tab3:
        st.subheader("ลบข้อมูลพืชที่มีในระบบ")
        if len(st.session_state['plants']) > 0:
            plant_to_delete = st.selectbox("เลือกพืชที่ต้องการลบ", list(st.session_state['plants'].keys()), key="del_select")
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
