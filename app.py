import streamlit as st
import qrcode
import io
import json
import os
import uuid
from datetime import datetime


# =========================================================
# ตั้งค่าหน้าเว็บ
# =========================================================

st.set_page_config(
    page_title="ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา",
    page_icon="🌿",
    layout="wide"
)


# =========================================================
# ตำแหน่งไฟล์แบบถาวร
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "botany_data.json"
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploaded_images"
)

# สร้างโฟลเดอร์รูปภาพ
os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        color: #198754;
        font-size: 35px;
        font-weight: bold;
    }

    .plant-card {
        padding: 20px;
        border-radius: 15px;
        background-color: #f4fff7;
        border: 1px solid #ccebd5;
        margin-bottom: 15px;
    }

    .login-box {
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #ddd;
        background-color: #fafafa;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ข้อมูลเริ่มต้น
# =========================================================

def create_default_data():

    return {
        "plants": {},

        "users": {
            "admin": {
                "name": "ผู้ดูแลระบบหลัก",
                "role": "ผู้ดูแลระบบ",
                "class": "-"
            },

            "6501": {
                "name": "เด็กชายสมชาย ใจดี",
                "role": "นักเรียน",
                "class": "ม.3/1"
            }
        },

        "logs": []
    }


# =========================================================
# โหลดข้อมูล
# =========================================================

def load_data():

    if not os.path.exists(DATA_FILE):

        data = create_default_data()

        save_data(data)

        return data

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if "plants" not in data:
            data["plants"] = {}

        if "users" not in data:
            data["users"] = {}

        if "logs" not in data:
            data["logs"] = []

        return data

    except Exception as error:

        st.error(
            f"ไม่สามารถโหลดข้อมูลได้: {error}"
        )

        return create_default_data()


# =========================================================
# บันทึกข้อมูลถาวร
# =========================================================

def save_data(data):

    try:

        temp_file = DATA_FILE + ".tmp"

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

        os.replace(
            temp_file,
            DATA_FILE
        )

        return True

    except Exception as error:

        st.error(
            f"ไม่สามารถบันทึกข้อมูลได้: {error}"
        )

        return False


# =========================================================
# Session State
# =========================================================

if "data" not in st.session_state:

    st.session_state.data = load_data()


if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "current_user" not in st.session_state:

    st.session_state.current_user = None


# =========================================================
# สร้าง QR Code
# =========================================================

def create_qr_code(
    plant_name,
    plant_data
):

    qr_text = (
        "ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา\n"
        f"พรรณไม้: {plant_name}\n"
        f"ชื่อวิทยาศาสตร์: "
        f"{plant_data.get('scientific_name', '-')}\n"
        f"สรรพคุณ: "
        f"{plant_data.get('benefit', '-')}"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4
    )

    qr.add_data(qr_text)

    qr.make(
        fit=True
    )

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return buffer


# =========================================================
# บันทึกรูปภาพ
# =========================================================

def save_image(
    uploaded_file,
    plant_name
):

    if uploaded_file is None:

        return None

    extension = os.path.splitext(
        uploaded_file.name
    )[1].lower()

    filename = (
        f"{plant_name}_"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    filepath = os.path.join(
        UPLOAD_DIR,
        filename
    )

    with open(
        filepath,
        "wb"
    ) as file:

        file.write(
            uploaded_file.getbuffer()
        )

    return filepath


# =========================================================
# ลบรูปภาพ
# =========================================================

def delete_image(
    image_path
):

    if (
        image_path
        and os.path.exists(image_path)
    ):

        try:

            os.remove(
                image_path
            )

        except Exception:
            pass


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '🌿 ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "ระบบฐานข้อมูลพรรณไม้สำหรับโรงเรียน"
)


# =========================================================
# LOGIN
# =========================================================

if not st.session_state.logged_in:

    st.info(
        "🔐 กรุณาเข้าสู่ระบบก่อนดูข้อมูลพรรณไม้"
    )

    st.divider()

    st.subheader(
        "🔐 เข้าสู่ระบบ"
    )

    with st.form(
        "login_form"
    ):

        user_id = st.text_input(
            "เลขประจำตัว / รหัสสมาชิก",
            placeholder="เช่น admin หรือ 6501"
        )

        login_button = st.form_submit_button(
            "เข้าสู่ระบบ",
            use_container_width=True
        )

        if login_button:

            user_id = user_id.strip()

            users = st.session_state.data.get(
                "users",
                {}
            )

            if user_id in users:

                user = users[
                    user_id
                ].copy()

                user["id"] = user_id

                st.session_state.logged_in = True

                st.session_state.current_user = user

                # บันทึก Login
                login_time = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                st.session_state.data[
                    "logs"
                ].append(
                    {
                        "id": user_id,
                        "name": user.get(
                            "name",
                            "-"
                        ),
                        "role": user.get(
                            "role",
                            "-"
                        ),
                        "time": login_time
                    }
                )

                save_data(
                    st.session_state.data
                )

                # Login เท่านั้นที่ rerun
                st.rerun()

            else:

                st.error(
                    "❌ ไม่พบรหัสสมาชิก"
                )

    st.divider()

    st.caption(
        "กรุณาติดต่อผู้ดูแลระบบหากไม่สามารถเข้าสู่ระบบได้"
    )

    # สำคัญ:
    # ไม่ให้คนที่ยังไม่ได้ Login เห็นข้อมูลพืช
    st.stop()


# =========================================================
# ข้อมูลผู้ใช้ปัจจุบัน
# =========================================================

current_user = (
    st.session_state.current_user
)

user_role = current_user.get(
    "role",
    "นักเรียน"
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header(
        "🌿 เมนูระบบ"
    )

    st.success(
        f"👤 {current_user.get('name', '-')}\n\n"
        f"สถานะ: {user_role}"
    )

    if user_role == "ผู้ดูแลระบบ":

        menu = st.radio(
            "เมนู",
            [
                "🌱 ดูพรรณไม้",
                "🔧 จัดการพรรณไม้",
                "👥 จัดการสมาชิก",
                "📊 ประวัติการเข้าสู่ระบบ"
            ]
        )

    else:

        menu = st.radio(
            "เมนู",
            [
                "🌱 ดูพรรณไม้",
                "👤 ข้อมูลของฉัน"
            ]
        )

    st.divider()

    if st.button(
        "🚪 ออกจากระบบ",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.current_user = None

        st.rerun()


# =========================================================
# ดูพรรณไม้
# =========================================================

if menu == "🌱 ดูพรรณไม้":

    st.header(
        "🌱 ฐานข้อมูลพรรณไม้"
    )

    plants = st.session_state.data.get(
        "plants",
        {}
    )

    if not plants:

        st.warning(
            "ยังไม่มีข้อมูลพรรณไม้ในระบบ"
        )

    else:

        plant_names = list(
            plants.keys()
        )

        selected_plant = st.selectbox(
            "เลือกพรรณไม้",
            plant_names,
            key="view_plant"
        )

        # ดึงข้อมูลล่าสุดจาก session_state
        plant = st.session_state.data[
            "plants"
        ].get(
            selected_plant
        )

        if plant:

            st.divider()

            col1, col2 = st.columns(
                [1, 2]
            )

            # รูป
            with col1:

                image_path = plant.get(
                    "image"
                )

                if (
                    image_path
                    and os.path.exists(
                        image_path
                    )
                ):

                    st.image(
                        image_path,
                        caption=selected_plant,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "🌱 ไม่มีรูปภาพ"
                    )

            # ข้อมูล
            with col2:

                st.subheader(
                    f"🌿 {selected_plant}"
                )

                st.markdown(
                    "**ชื่อวิทยาศาสตร์**"
                )

                st.write(
                    plant.get(
                        "scientific_name",
                        "-"
                    )
                )

                st.markdown(
                    "**สรรพคุณ / ประโยชน์**"
                )

                st.success(
                    plant.get(
                        "benefit",
                        "-"
                    )
                )

                st.markdown(
                    "### 📱 QR Code"
                )

                qr_buffer = create_qr_code(
                    selected_plant,
                    plant
                )

                st.image(
                    qr_buffer,
                    width=180
                )

                st.download_button(
                    "⬇️ ดาวน์โหลด QR Code",
                    data=qr_buffer.getvalue(),
                    file_name=(
                        f"{selected_plant}_QR.png"
                    ),
                    mime="image/png"
                )


# =========================================================
# จัดการพรรณไม้
# =========================================================

elif menu == "🔧 จัดการพรรณไม้":

    if user_role != "ผู้ดูแลระบบ":

        st.error(
            "ไม่มีสิทธิ์เข้าถึงหน้านี้"
        )

        st.stop()

    st.header(
        "🔧 จัดการข้อมูลพรรณไม้"
    )

    tab_add, tab_edit = st.tabs(
        [
            "➕ เพิ่มพรรณไม้",
            "✏️ แก้ไข / ลบ"
        ]
    )


    # =====================================================
    # เพิ่มพรรณไม้
    # =====================================================

    with tab_add:

        st.subheader(
            "➕ เพิ่มพรรณไม้ใหม่"
        )

        with st.form(
            "add_plant_form"
        ):

            plant_name = st.text_input(
                "ชื่อพืช *"
            )

            scientific_name = st.text_input(
                "ชื่อวิทยาศาสตร์"
            )

            benefit = st.text_area(
                "สรรพคุณ / ประโยชน์"
            )

            plant_image = st.file_uploader(
                "🖼️ รูปภาพพืช",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ]
            )

            if plant_image:

                st.image(
                    plant_image,
                    caption="ตัวอย่างรูปพืช",
                    width=300
                )

            save_button = st.form_submit_button(
                "💾 บันทึกพรรณไม้",
                use_container_width=True
            )

            if save_button:

                plant_name = (
                    plant_name.strip()
                )

                if not plant_name:

                    st.error(
                        "กรุณากรอกชื่อพืช"
                    )

                elif plant_name in st.session_state.data[
                    "plants"
                ]:

                    st.error(
                        "มีพืชชนิดนี้แล้ว"
                    )

                else:

                    image_path = save_image(
                        plant_image,
                        plant_name
                    )

                    st.session_state.data[
                        "plants"
                    ][plant_name] = {

                        "scientific_name":
                            scientific_name.strip(),

                        "benefit":
                            benefit.strip(),

                        "image":
                            image_path
                    }

                    save_data(
                        st.session_state.data
                    )

                    st.success(
                        f"✅ เพิ่ม '{plant_name}' "
                        "เรียบร้อยแล้ว"
                    )

                    # ไม่ใช้ st.rerun()
                    # ข้อมูลถูกเก็บใน session_state
                    # แล้ว


    # =====================================================
    # แก้ไข / ลบ
    # =====================================================

    with tab_edit:

        st.subheader(
            "✏️ แก้ไข / ลบพรรณไม้"
        )

        plants = st.session_state.data[
            "plants"
        ]

        if not plants:

            st.info(
                "ยังไม่มีข้อมูลพรรณไม้"
            )

        else:

            selected = st.selectbox(
                "เลือกพรรณไม้",
                list(plants.keys()),
                key="edit_plant"
            )

            plant = st.session_state.data[
                "plants"
            ][selected]

            old_image = plant.get(
                "image"
            )

            # รูปเดิม
            if (
                old_image
                and os.path.exists(
                    old_image
                )
            ):

                st.image(
                    old_image,
                    caption="รูปปัจจุบัน",
                    width=300
                )

            else:

                st.info(
                    "ยังไม่มีรูปภาพ"
                )

            with st.form(
                "edit_plant_form"
            ):

                new_scientific_name = st.text_input(
                    "ชื่อวิทยาศาสตร์",
                    value=plant.get(
                        "scientific_name",
                        ""
                    )
                )

                new_benefit = st.text_area(
                    "สรรพคุณ / ประโยชน์",
                    value=plant.get(
                        "benefit",
                        ""
                    )
                )

                new_image = st.file_uploader(
                    "🖼️ เปลี่ยนรูปภาพพืช",
                    type=[
                        "jpg",
                        "jpeg",
                        "png",
                        "webp"
                    ]
                )

                if new_image:

                    st.image(
                        new_image,
                        caption="รูปใหม่",
                        width=300
                    )

                col1, col2 = st.columns(2)

                update_button = col1.form_submit_button(
                    "💾 อัปเดต",
                    use_container_width=True
                )

                delete_button = col2.form_submit_button(
                    "🗑️ ลบ",
                    use_container_width=True
                )


                # =========================================
                # UPDATE
                # =========================================

                if update_button:

                    image_path = old_image

                    if new_image:

                        delete_image(
                            old_image
                        )

                        image_path = save_image(
                            new_image,
                            selected
                        )

                    # อัปเดตข้อมูลในหน่วยความจำทันที
                    st.session_state.data[
                        "plants"
                    ][selected] = {

                        "scientific_name":
                            new_scientific_name.strip(),

                        "benefit":
                            new_benefit.strip(),

                        "image":
                            image_path
                    }

                    # บันทึกลงไฟล์ถาวร
                    save_data(
                        st.session_state.data
                    )

                    st.success(
                        "✅ แก้ไขข้อมูลเรียบร้อยแล้ว"
                    )

                    # สำคัญ:
                    # ไม่มี st.rerun()


                # =========================================
                # DELETE
                # =========================================

                if delete_button:

                    delete_image(
                        old_image
                    )

                    del st.session_state.data[
                        "plants"
                    ][selected]

                    save_data(
                        st.session_state.data
                    )

                    st.success(
                        "🗑️ ลบพรรณไม้เรียบร้อยแล้ว"
                    )

                    # ไม่มี st.rerun()


# =========================================================
# จัดการสมาชิก
# =========================================================

elif menu == "👥 จัดการสมาชิก":

    if user_role != "ผู้ดูแลระบบ":

        st.error(
            "ไม่มีสิทธิ์เข้าถึงหน้านี้"
        )

        st.stop()

    st.header(
        "👥 จัดการสมาชิก"
    )

    tab_add, tab_list = st.tabs(
        [
            "➕ เพิ่มสมาชิก",
            "📋 สมาชิกทั้งหมด"
        ]
    )


    # =====================================================
    # เพิ่มสมาชิก
    # =====================================================

    with tab_add:

        with st.form(
            "add_user_form"
        ):

            user_id = st.text_input(
                "เลขประจำตัว / รหัสสมาชิก *"
            )

            user_name = st.text_input(
                "ชื่อ - นามสกุล *"
            )

            user_role = st.selectbox(
                "สถานะ",
                [
                    "นักเรียน",
                    "ครู",
                    "ผู้ดูแลระบบ"
                ]
            )

            user_class = st.text_input(
                "ชั้นเรียน / แผนก",
                value="-"
            )

            add_user = st.form_submit_button(
                "💾 เพิ่มสมาชิก",
                use_container_width=True
            )

            if add_user:

                user_id = user_id.strip()

                user_name = user_name.strip()

                if not user_id or not user_name:

                    st.error(
                        "กรุณากรอกข้อมูลให้ครบ"
                    )

                elif user_id in st.session_state.data[
                    "users"
                ]:

                    st.error(
                        "รหัสนี้มีอยู่แล้ว"
                    )

                else:

                    st.session_state.data[
                        "users"
                    ][user_id] = {

                        "name":
                            user_name,

                        "role":
                            user_role,

                        "class":
                            user_class.strip()
                    }

                    save_data(
                        st.session_state.data
                    )

                    st.success(
                        "✅ เพิ่มสมาชิกเรียบร้อยแล้ว"
                    )


    # =====================================================
    # รายชื่อสมาชิก
    # =====================================================

    with tab_list:

        users = st.session_state.data[
            "users"
        ]

        for uid, info in list(
            users.items()
        ):

            with st.container(
                border=True
            ):

                col1, col2 = st.columns(
                    [5, 1]
                )

                with col1:

                    st.write(
                        f"**รหัส:** {uid}"
                    )

                    st.write(
                        f"ชื่อ: "
                        f"{info.get('name', '-')}"
                    )

                    st.write(
                        f"สถานะ: "
                        f"{info.get('role', '-')}"
                    )

                    st.write(
                        f"ชั้น / แผนก: "
                        f"{info.get('class', '-')}"
                    )

                with col2:

                    if uid == "admin":

                        st.caption(
                            "บัญชีหลัก"
                        )

                    else:

                        if st.button(
                            "🗑️ ลบ",
                            key=f"delete_{uid}"
                        ):

                            del st.session_state.data[
                                "users"
                            ][uid]

                            save_data(
                                st.session_state.data
                            )

                            st.success(
                                "ลบสมาชิกแล้ว"
                            )


# =========================================================
# ประวัติ Login
# =========================================================

elif menu == "📊 ประวัติการเข้าสู่ระบบ":

    if user_role != "ผู้ดูแลระบบ":

        st.error(
            "ไม่มีสิทธิ์เข้าถึงหน้านี้"
        )

        st.stop()

    st.header(
        "📊 ประวัติการเข้าสู่ระบบ"
    )

    logs = st.session_state.data.get(
        "logs",
        []
    )

    if not logs:

        st.info(
            "ยังไม่มีประวัติ"
        )

    else:

        filter_date = st.text_input(
            "กรองวันที่ YYYY-MM-DD"
        )

        if filter_date:

            filtered = [
                log
                for log in logs
                if filter_date in log.get(
                    "time",
                    ""
                )
            ]

        else:

            filtered = logs

        st.metric(
            "จำนวนรายการ",
            len(filtered)
        )

        for log in reversed(
            filtered
        ):

            st.markdown(
                f"- 🕒 **{log.get('time', '-')}** "
                f"| {log.get('id', '-')} "
                f"| {log.get('name', '-')} "
                f"| {log.get('role', '-')}"
            )


# =========================================================
# ข้อมูลของฉัน
# =========================================================

elif menu == "👤 ข้อมูลของฉัน":

    st.header(
        "👤 ข้อมูลของฉัน"
    )

    st.write(
        f"**รหัส:** "
        f"{current_user.get('id', '-')}"
    )

    st.write(
        f"**ชื่อ:** "
        f"{current_user.get('name', '-')}"
    )

    st.write(
        f"**สถานะ:** "
        f"{current_user.get('role', '-')}"
    )

    st.write(
        f"**ชั้น / แผนก:** "
        f"{current_user.get('class', '-')}"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🌿 ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา"
)
