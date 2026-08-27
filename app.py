import streamlit as st
import qrcode
from PIL import Image
import io

st.set_page_config(page_title="ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา", page_icon="🌿", layout="wide")

st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌿 ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>พัฒนาโปรแกรมโดย Tnc</p>", unsafe_allow_html=True)
st.write("---")

if 'plants' not in st.session_state:
    st.session_state['plants'] = {
        "ต้นราชพฤกษ์": {
            "scientific_name": "Cassia fistula",
            "benefit": "ช่วยขับพยาธิและเป็นยาระบายอ่อนๆ",
            "image": None
        }
    }

if 'students' not in st.session_state:
    st.session_state['students'] = {
        "6501": {"name": "เด็กชายสมชาย ใจดี", "class": "ม.3/1"}
    }

menu = st.sidebar.selectbox("เลือกหน้า", ["หน้าหลัก (ค้นหา & QR Code)", "ระบบหลังบ้าน (Admin)"])

if menu == "หน้าหลัก (ค้นหา & QR Code)":
    st.title("🌱 ค้นหาข้อมูลพรรณไม้")
    plant_name = st.selectbox("เลือกพืช:", list(st.session_state['plants'].keys()))
    
    if plant_name:
        data = st.session_state['plants'][plant_name]
        st.write(f"**ชื่อวิทยาศาสตร์:** {data['scientific_name']}")
        st.success(f"**สรรพคุณ:** {data['benefit']}")
        
        # สร้าง QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f"โรงเรียนฐานปัญญา - พืช: {plant_name} | สรรพคุณ: {data['benefit']}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf)
        st.image(buf.getvalue(), width=200, caption=f"QR Code ของ {plant_name}")

elif menu == "ระบบหลังบ้าน (Admin)":
    st.title("🔒 ระบบหลังบ้าน")
    pwd = st.text_input("รหัสผ่านผู้ดูแลระบบ:", type="password")
    
    if pwd == "admin1234":
        st.success("เข้าสู่ระบบสำเร็จ!")
        tab1, tab2 = st.tabs(["เพิ่มพืช", "เพิ่มนักเรียน"])
        
        with tab1:
            with st.form("p_form"):
                name = st.text_input("ชื่อพืช")
                sci = st.text_input("ชื่อวิทยาศาสตร์")
                ben = st.text_area("สรรพคุณ")
                if st.form_submit_button("บันทึกพืช") and name:
                    st.session_state['plants'][name] = {"scientific_name": sci, "benefit": ben, "image": None}
                    st.success("บันทึกสำเร็จ!")
                    
        with tab2:
            with st.form("s_form"):
                sid = st.text_input("เลขประจำตัวนักเรียน")
                sname = st.text_input("ชื่อ-นามสกุล")
                sclass = st.text_input("ชั้นเรียน")
                if st.form_submit_button("บันทึกนักเรียน") and sid:
                    st.session_state['students'][sid] = {"name": sname, "class": sclass}
                    st.success("บันทึกนักเรียนสำเร็จ!")
    elif pwd != "":
        st.error("รหัสผ่านไม่ถูกต้อง (รหัสคือ admin1234)")

st.write("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2026 ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา | Developed by Tnc</p>", unsafe_allow_html=True)
