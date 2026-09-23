import streamlit as st
import qrcode
from PIL import Image
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
# ตั้งค่าไฟล์ข้อมูล
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "botany_data.json"
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploaded_images"
)

# สร้างโฟลเดอร์เก็บรูปถ้ายังไม่มี
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
# โหลดข้อมูลจากไฟล์ถาวร
# =========================================================
def load_data():

    # ถ้ามีไฟล์เดิม ให้โหลดไฟล์เดิม
    if os.path.exists(DATA_FILE):

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            # ป้องกันข้อมูลเก่าไม่มีบางส่วน
            if "plants" not in data:
                data["plants"] = {}

            if "users" not in data:
                data["users"] = {}

            if "logs" not in data:
                data["logs"] = []

            return data

        except Exception as error:

            st.error(
                f"ไม่สามารถอ่านไฟล์ข้อมูลได้: {error}"
            )

            return create_default_data()

    # ถ้ายังไม่มีไฟล์ ให้สร้างครั้งแรก
    data = create_default_data()

    save_data(data)

    return data


# =========================================================
# บันทึกข้อมูลถาวร
# =========================================================
def save_data(data):

    try:

        # เขียนลงไฟล์ชั่วคราวก่อน
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

        # เปลี่ยนไฟล์ชั่วคราวเป็นไฟล์จริง
        os.replace(
            temp_file,
            DATA_FILE
        )

        return True

    except Exception as error:

        st.error(
            f"บันทึกข้อมูลไม่สำเร็จ: {error}"
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

    text = (
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

    qr.add_data(text)
    qr.make(fit=True)

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
def save_uploaded_image(
    uploaded_file,
    plant_name
):

    if uploaded_file is None:

        return None

    # ใช้ UUID ป้องกันชื่อไฟล์ซ้ำ
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
# ลบรูปภาพเก่า
# =========================================================
def delete_image(filepath):

    if filepath and os.path.exists(filepath):

        try:
            os.remove(filepath)
        except Exception:
            pass


# =========================================================
# HEADER
# =========================================================
st.title(
    "🌿 ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา"
)

st.caption(
    "ระบบจัดเก็บข้อมูลพรรณไม้ "
    "สำหรับนักเรียน ครู และผู้ดูแลระบบ"
)


# =========================================================
# กรณียังไม่ได้เข้าสู่ระบบ
# =========================================================
if not st.session_state.logged_in:

    st.info(
        "🔐 กรุณาเข้าสู่ระบบก่อนจึงจะสามารถดูข้อมูลพรรณไม้ได้"
    )

    st.divider()

    st.header("🔐 เข้าสู่ระบบ")

    with st.form("login_form"):

        user_id = st.text_input(
            "เลขประจำตัว / รหัสสมาชิก",
            placeholder="เช่น 6501 หรือ admin"
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

                user = users[user_id].copy()

                user["id"] = user_id

                st.session_state.logged_in = True

                st.session_state.current_user = user

                # -----------------------------------------
                # บันทึกประวัติ Login
                # -----------------------------------------
                login_time = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                log = {
                    "id": user_id,
                    "name": user.get("name", "-"),
                    "role": user.get("role", "-"),
                    "time": login_time
                }

                st.session_state.data[
                    "logs"
                ].append(log)

                # บันทึกข้อมูลทันที
                save_data(
                    st.session_state.data
                )

                st.success(
                    f"ยินดีต้อนรับ "
                    f"{user.get('name', '')}"
                )

                st.rerun()

            else:

                st.error(
                    "❌ ไม่พบรหัสสมาชิกนี้ "
                    "กรุณาติดต่อผู้ดูแลระบบ"
                )

    st.divider()

    st.caption(
        "ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา"
    )

    # -----------------------------------------------------
    # สำคัญมาก:
    # หยุดการทำงานตรงนี้
    # เพื่อไม่ให้ผู้ที่ยังไม่ Login
    # สามารถเข้าถึงข้อมูลพืชได้
    # -----------------------------------------------------
    st.stop()


# =========================================================
# หลังจาก Login แล้ว
# =========================================================
current_user = st.session_state.current_user

user_role = current_user.get(
    "role",
    "นักเรียน"
)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.header("🌿 เมนูระบบ")

    st.success(
        f"👤 {current_user.get('name', '-')}\n\n"
        f"สถานะ: {user_role}"
    )

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------
    if user_role == "ผู้ดูแลระบบ":

        menu = st.radio(
            "เลือกเมนู",
            [
                "🌱 ดูพรรณไม้",
                "🔧 จัดการพรรณไม้",
                "👥 จัดการสมาชิก",
                "📊 ประวัติการเข้าสู่ระบบ"
            ]
        )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------
    else:

        menu = st.radio(
            "เลือกเมนู",
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
# เมนู: ดูพรรณไม้
# =========================================================
if menu == "🌱 ดูพรรณไม้":

    st.header("🌱 ฐานข้อมูลพรรณไม้")

    plants = st.session_state.data.get(
        "plants",
        {}
    )

    if not plants:

        st.warning(
            "ยังไม่มีข้อมูลพรรณไม้ในระบบ"
        )

        if user_role == "ผู้ดูแลระบบ":

            st.info(
                "ไปที่เมนู "
                "🔧 จัดการพรรณไม้ "
                "เพื่อเพิ่มข้อมูล"
            )

    else:

        plant_names = list(
            plants.keys()
        )

        selected_plant = st.selectbox(
            "🌿 เลือกพืชที่ต้องการศึกษา",
            plant_names
        )

        plant = plants[
            selected_plant
        ]

        st.divider()

        col1, col2 = st.columns(
            [1, 2]
        )

        # -------------------------------------------------
        # รูปพืช
        # -------------------------------------------------
        with col1:

            image_path = plant.get(
                "image"
            )

            if (
                image_path
                and os.path.exists(image_path)
            ):

                try:

                    st.image(
                        image_path,
                        caption=selected_plant,
                        use_container_width=True
                    )

                except Exception:

                    st.warning(
                        "ไม่สามารถแสดงรูปภาพได้"
                    )

            else:

                st.info(
                    "🌱 พืชชนิดนี้ยังไม่มีรูปภาพ"
                )

        # -------------------------------------------------
        # รายละเอียดพืช
        # -------------------------------------------------
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
                    "ไม่มีข้อมูล"
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
# เมนู ADMIN: จัดการพรรณไม้
# =========================================================
elif menu == "🔧 จัดการพรรณไม้":

    if user_role != "ผู้ดูแลระบบ":

        st.error(
            "คุณไม่มีสิทธิ์เข้าถึงหน้านี้"
        )

        st.stop()

    st.header(
        "🔧 จัดการข้อมูลพรรณไม้"
    )

    tab_add, tab_edit = st.tabs(
        [
            "➕ เพิ่มพรรณไม้",
            "✏️ แก้ไข / ลบพรรณไม้"
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
            "add_plant_form",
            clear_on_submit=False
        ):

            plant_name = st.text_input(
                "ชื่อพืช *",
                placeholder="เช่น ต้นราชพฤกษ์"
            )

            scientific_name = st.text_input(
                "ชื่อวิทยาศาสตร์",
                placeholder="เช่น Cassia fistula"
            )

            benefit = st.text_area(
                "สรรพคุณ / ประโยชน์",
                placeholder="กรอกข้อมูลสรรพคุณของพืช"
            )

            # -------------------------------------------------
            # ช่องอัปโหลดรูปพืช
            # -------------------------------------------------
            plant_image = st.file_uploader(
                "🖼️ รูปภาพพืช",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                help="เลือกรูปภาพของพรรณไม้"
            )

            if plant_image:

                st.image(
                    plant_image,
                    caption="ตัวอย่างรูปพืช",
                    width=300
                )

            save_plant = st.form_submit_button(
                "💾 บันทึกข้อมูลพรรณไม้",
                use_container_width=True
            )

            if save_plant:

                plant_name = plant_name.strip()

                if not plant_name:

                    st.error(
                        "กรุณากรอกชื่อพืช"
                    )

                elif plant_name in st.session_state.data[
                    "plants"
                ]:

                    st.error(
                        "มีพืชชนิดนี้ในระบบแล้ว"
                    )

                else:

                    # บันทึกรูปลงโฟลเดอร์ถาวร
                    image_path = save_uploaded_image(
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

                    # บันทึก JSON
                    if save_data(
                        st.session_state.data
                    ):

                        st.success(
                            f"✅ เพิ่มพรรณไม้ "
                            f"'{plant_name}' "
                            f"เรียบร้อยแล้ว"
                        )

                        st.rerun()


    # =====================================================
    # แก้ไข / ลบพรรณไม้
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
                key="selected_edit_plant"
            )

            plant = plants[selected]

            # แสดงรูปเดิม
            old_image = plant.get(
                "image"
            )

            if (
                old_image
                and os.path.exists(old_image)
            ):

                st.image(
                    old_image,
                    caption="รูปปัจจุบัน",
                    width=300
                )

            else:

                st.info(
                    "ยังไม่มีรูปภาพพืช"
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

                # -------------------------------------------------
                # ช่องเปลี่ยนรูป
                # -------------------------------------------------
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
                    "💾 อัปเดตข้อมูล",
                    use_container_width=True
                )

                delete_button = col2.form_submit_button(
                    "🗑️ ลบพรรณไม้นี้",
                    use_container_width=True
                )

                # =================================================
                # UPDATE
                # =================================================
                if update_button:

                    image_path = old_image

                    # ถ้ามีรูปใหม่
                    if new_image:

                        # ลบรูปเก่า
                        delete_image(
                            old_image
                        )

                        # บันทึกรูปใหม่
                        image_path = save_uploaded_image(
                            new_image,
                            selected
                        )

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

                    if save_data(
                        st.session_state.data
                    ):

                        st.success(
                            "✅ อัปเดตข้อมูลพรรณไม้แล้ว"
                        )

                        st.rerun()

                # =================================================
                # DELETE
                # =================================================
                if delete_button:

                    # ลบรูปด้วย
                    delete_image(
                        old_image
                    )

                    del st.session_state.data[
                        "plants"
                    ][selected]

                    if save_data(
                        st.session_state.data
                    ):

                        st.success(
                            f"🗑️ ลบพรรณไม้ "
                            f"'{selected}' "
                            f"เรียบร้อยแล้ว"
                        )

                        st.rerun()


# =========================================================
# เมนู ADMIN: จัดการสมาชิก
# =========================================================
elif menu == "👥 จัดการสมาชิก":

    if user_role != "ผู้ดูแลระบบ":

        st.error(
            "คุณไม่มีสิทธิ์เข้าถึงหน้านี้"
        )

        st.stop()

    st.header(
        "👥 จัดการสมาชิก"
    )

    tab_add_user, tab_users = st.tabs(
        [
            "➕ เพิ่มสมาชิก",
            "📋 รายชื่อสมาชิก"
        ]
    )

    # -----------------------------------------------------
    # เพิ่มสมาชิก
    # -----------------------------------------------------
    with tab_add_user:

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
                        "รหัสสมาชิกนี้มีอยู่แล้ว"
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

                    if save_data(
                        st.session_state.data
                    ):

                        st.success(
                            "เพิ่มสมาชิกเรียบร้อยแล้ว"
                        )

                        st.rerun()


    # -----------------------------------------------------
    # รายชื่อสมาชิก
    # -----------------------------------------------------
    with tab_users:

        users = st.session_state.data[
            "users"
        ]

        if not users:

            st.info(
                "ยังไม่มีสมาชิก"
            )

        else:

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

                        st.markdown(
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
                                key=f"delete_user_{uid}",
                                use_container_width=True
                            ):

                                del st.session_state.data[
                                    "users"
                                ][uid]

                                save_data(
                                    st.session_state.data
                                )

                                st.rerun()


# =========================================================
# เมนู ADMIN: ประวัติ Login
# =========================================================
elif menu == "📊 ประวัติการเข้าสู่ระบบ":

    if user_role != "ผู้ดูแลระบบ":

        st.error(
            "คุณไม่มีสิทธิ์เข้าถึงหน้านี้"
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
            "ยังไม่มีประวัติการเข้าสู่ระบบ"
        )

    else:

        filter_date = st.text_input(
            "กรองวันที่ "
            "(YYYY-MM-DD) "
            "หรือเว้นว่างเพื่อดูทั้งหมด"
        )

        if filter_date:

            filtered_logs = [
                log
                for log in logs
                if filter_date
                in log.get("time", "")
            ]

        else:

            filtered_logs = logs

        st.metric(
            "จำนวนการเข้าสู่ระบบ",
            len(filtered_logs)
        )

        st.divider()

        for log in reversed(
            filtered_logs
        ):

            st.markdown(
                f"- 🕒 **{log.get('time', '-')}** "
                f"| รหัส: **{log.get('id', '-')}** "
                f"| ชื่อ: **{log.get('name', '-')}** "
                f"| สถานะ: **{log.get('role', '-')}**"
            )


# =========================================================
# ข้อมูลส่วนตัว
# =========================================================
elif menu == "👤 ข้อมูลของฉัน":

    st.header(
        "👤 ข้อมูลของฉัน"
    )

    st.write(
        f"**รหัสสมาชิก:** "
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
