import streamlit as st
import qrcode
from PIL import Image
import io
import json
import os
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
# ค่าคงที่
# =========================================================
DATA_FILE = "botany_data.json"
UPLOAD_DIR = "uploaded_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================================
# ข้อมูลเริ่มต้น
# =========================================================
def default_data():
    return {
        "plants": {
            "ต้นราชพฤกษ์": {
                "scientific_name": "Cassia fistula",
                "benefit": "ช่วยขับพยาธิและเป็นยาระบายอ่อนๆ",
                "image": None
            }
        },
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
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            # ป้องกันข้อมูลเก่าขาด key
            if "plants" not in data:
                data["plants"] = {}

            if "users" not in data:
                data["users"] = {}

            if "logs" not in data:
                data["logs"] = []

            return data

        except (json.JSONDecodeError, OSError):
            return default_data()

    return default_data()


# =========================================================
# บันทึกข้อมูล
# =========================================================
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )
        return True

    except OSError as error:
        st.error(f"ไม่สามารถบันทึกข้อมูลได้: {error}")
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
# ฟังก์ชันสร้าง QR Code
# =========================================================
def create_qr_code(plant_name, plant_data):
    qr_text = (
        f"โรงเรียนฐานปัญญา\n"
        f"พรรณไม้: {plant_name}\n"
        f"ชื่อวิทยาศาสตร์: {plant_data.get('scientific_name', '-')}\n"
        f"สรรพคุณ: {plant_data.get('benefit', '-')}"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4
    )

    qr.add_data(qr_text)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


# =========================================================
# Header
# =========================================================
st.title("🌿 ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา")
st.caption("ระบบจัดเก็บข้อมูลพรรณไม้ สมาชิก และประวัติการใช้งาน")


# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.header("🌱 เมนูระบบ")

    if st.session_state.logged_in:
        current = st.session_state.current_user

        st.success(
            f"เข้าสู่ระบบแล้ว\n\n"
            f"👤 {current['name']}\n\n"
            f"สถานะ: {current['role']}"
        )

        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()


# =========================================================
# เมนูหลัก
# =========================================================
if st.session_state.logged_in:

    current_user = st.session_state.current_user

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------
    if current_user["role"] == "ผู้ดูแลระบบ":

        menu = st.sidebar.radio(
            "เลือกเมนู",
            [
                "🌿 พรรณไม้",
                "🔧 จัดการพรรณไม้",
                "👥 จัดการสมาชิก",
                "📊 ประวัติการเข้าสู่ระบบ"
            ]
        )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------
    else:

        menu = st.sidebar.radio(
            "เลือกเมนู",
            [
                "🌿 พรรณไม้",
                "👤 ข้อมูลของฉัน"
            ]
        )


    # =====================================================
    # หน้าพรรณไม้
    # =====================================================
    if menu == "🌿 พรรณไม้":

        st.header("🌿 ฐานข้อมูลพรรณไม้")

        plants = st.session_state.data.get("plants", {})

        if not plants:

            st.warning(
                "ยังไม่มีข้อมูลพรรณไม้ในระบบ "
                "กรุณาเพิ่มข้อมูลจากเมนูจัดการพรรณไม้"
            )

        else:

            plant_name = st.selectbox(
                "เลือกพืชที่ต้องการศึกษา",
                list(plants.keys())
            )

            if plant_name:

                plant = plants[plant_name]

                col1, col2 = st.columns([1, 2])

                # -----------------------------------------
                # รูปภาพ
                # -----------------------------------------
                with col1:

                    image_path = plant.get("image")

                    if (
                        image_path
                        and os.path.exists(image_path)
                    ):
                        try:
                            st.image(
                                image_path,
                                caption=plant_name,
                                use_container_width=True
                            )
                        except Exception:
                            st.info("ไม่สามารถแสดงรูปภาพได้")

                    else:
                        st.info("🌱 ยังไม่มีรูปภาพพืชชนิดนี้")

                # -----------------------------------------
                # รายละเอียด
                # -----------------------------------------
                with col2:

                    st.subheader(f"🌱 {plant_name}")

                    st.markdown(
                        f"**ชื่อวิทยาศาสตร์:** "
                        f"*{plant.get('scientific_name', '-')}*"
                    )

                    st.markdown("### 💊 สรรพคุณ")

                    st.success(
                        plant.get(
                            "benefit",
                            "ไม่มีข้อมูล"
                        )
                    )

                    # -------------------------------------
                    # QR Code
                    # -------------------------------------
                    st.markdown("### 📱 QR Code")

                    qr_buffer = create_qr_code(
                        plant_name,
                        plant
                    )

                    st.image(
                        qr_buffer,
                        width=180,
                        caption=f"QR Code - {plant_name}"
                    )

                    st.download_button(
                        label="⬇️ ดาวน์โหลด QR Code",
                        data=qr_buffer.getvalue(),
                        file_name=f"{plant_name}_QR.png",
                        mime="image/png"
                    )


    # =====================================================
    # จัดการพรรณไม้
    # =====================================================
    elif menu == "🔧 จัดการพรรณไม้":

        st.header("🔧 จัดการข้อมูลพรรณไม้")

        tab_add, tab_edit = st.tabs(
            [
                "➕ เพิ่มพรรณไม้",
                "✏️ แก้ไข / ลบ"
            ]
        )

        # -------------------------------------------------
        # เพิ่มพืช
        # -------------------------------------------------
        with tab_add:

            with st.form("add_plant_form"):

                plant_name = st.text_input(
                    "ชื่อพืช *"
                )

                scientific_name = st.text_input(
                    "ชื่อวิทยาศาสตร์"
                )

                benefit = st.text_area(
                    "สรรพคุณ / ประโยชน์"
                )

                uploaded_image = st.file_uploader(
                    "รูปภาพพืช",
                    type=[
                        "jpg",
                        "jpeg",
                        "png"
                    ]
                )

                submit = st.form_submit_button(
                    "💾 บันทึกพรรณไม้",
                    use_container_width=True
                )

                if submit:

                    plant_name = plant_name.strip()

                    if not plant_name:

                        st.error(
                            "กรุณากรอกชื่อพืช"
                        )

                    elif plant_name in st.session_state.data["plants"]:

                        st.error(
                            "มีพืชชนิดนี้อยู่ในระบบแล้ว"
                        )

                    else:

                        image_path = None

                        if uploaded_image:

                            safe_filename = (
                                f"{plant_name}_"
                                f"{uploaded_image.name}"
                            )

                            image_path = os.path.join(
                                UPLOAD_DIR,
                                safe_filename
                            )

                            with open(
                                image_path,
                                "wb"
                            ) as file:
                                file.write(
                                    uploaded_image.getbuffer()
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
                            f"เพิ่มพรรณไม้ "
                            f"'{plant_name}' "
                            f"เรียบร้อยแล้ว"
                        )

                        st.rerun()


        # -------------------------------------------------
        # แก้ไข / ลบ
        # -------------------------------------------------
        with tab_edit:

            plants = st.session_state.data["plants"]

            if not plants:

                st.info(
                    "ยังไม่มีข้อมูลพรรณไม้"
                )

            else:

                selected = st.selectbox(
                    "เลือกพรรณไม้",
                    list(plants.keys()),
                    key="edit_plant_select"
                )

                plant = plants[selected]

                with st.form("edit_plant_form"):

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
                        "เปลี่ยนรูปภาพ",
                        type=[
                            "jpg",
                            "jpeg",
                            "png"
                        ]
                    )

                    col1, col2 = st.columns(2)

                    update = col1.form_submit_button(
                        "💾 อัปเดตข้อมูล",
                        use_container_width=True
                    )

                    delete = col2.form_submit_button(
                        "🗑️ ลบพรรณไม้",
                        use_container_width=True
                    )

                    # -------------------------------------
                    # UPDATE
                    # -------------------------------------
                    if update:

                        image_path = plant.get(
                            "image"
                        )

                        if new_image:

                            new_filename = (
                                f"{selected}_"
                                f"{new_image.name}"
                            )

                            image_path = os.path.join(
                                UPLOAD_DIR,
                                new_filename
                            )

                            with open(
                                image_path,
                                "wb"
                            ) as file:

                                file.write(
                                    new_image.getbuffer()
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

                        save_data(
                            st.session_state.data
                        )

                        st.success(
                            "อัปเดตข้อมูลเรียบร้อยแล้ว"
                        )

                        st.rerun()

                    # -------------------------------------
                    # DELETE
                    # -------------------------------------
                    if delete:

                        old_image = plant.get(
                            "image"
                        )

                        if (
                            old_image
                            and os.path.exists(old_image)
                        ):
                            try:
                                os.remove(old_image)
                            except OSError:
                                pass

                        del st.session_state.data[
                            "plants"
                        ][selected]

                        save_data(
                            st.session_state.data
                        )

                        st.warning(
                            f"ลบ '{selected}' "
                            f"เรียบร้อยแล้ว"
                        )

                        st.rerun()


    # =====================================================
    # จัดการสมาชิก
    # =====================================================
    elif menu == "👥 จัดการสมาชิก":

        st.header("👥 จัดการสมาชิก")

        tab_add_user, tab_user_list = st.tabs(
            [
                "➕ เพิ่มสมาชิก",
                "📋 รายชื่อสมาชิก"
            ]
        )

        # -------------------------------------------------
        # เพิ่มสมาชิก
        # -------------------------------------------------
        with tab_add_user:

            with st.form("add_user_form"):

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

                submit_user = st.form_submit_button(
                    "💾 เพิ่มสมาชิก",
                    use_container_width=True
                )

                if submit_user:

                    user_id = user_id.strip()
                    user_name = user_name.strip()

                    if not user_id or not user_name:

                        st.error(
                            "กรุณากรอกข้อมูลที่จำเป็นให้ครบ"
                        )

                    elif user_id in st.session_state.data["users"]:

                        st.error(
                            "รหัสสมาชิกนี้มีอยู่แล้ว"
                        )

                    else:

                        st.session_state.data[
                            "users"
                        ][user_id] = {

                            "name": user_name,
                            "role": user_role,
                            "class": user_class.strip()
                        }

                        save_data(
                            st.session_state.data
                        )

                        st.success(
                            f"เพิ่มสมาชิก "
                            f"'{user_name}' "
                            f"เรียบร้อยแล้ว"
                        )

                        st.rerun()


        # -------------------------------------------------
        # รายชื่อสมาชิก
        # -------------------------------------------------
        with tab_user_list:

            users = st.session_state.data["users"]

            if not users:

                st.info(
                    "ยังไม่มีสมาชิก"
                )

            else:

                for uid, info in list(users.items()):

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
                                f"👤 ชื่อ: "
                                f"{info.get('name', '-')}"
                            )

                            st.write(
                                f"สถานะ: "
                                f"{info.get('role', '-')}"
                            )

                            st.write(
                                f"ชั้น/แผนก: "
                                f"{info.get('class', '-')}"
                            )

                        with col2:

                            # ป้องกันไม่ให้ admin ลบตัวเอง
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

                                    st.success(
                                        "ลบสมาชิกแล้ว"
                                    )

                                    st.rerun()


    # =====================================================
    # ประวัติ Login
    # =====================================================
    elif menu == "📊 ประวัติการเข้าสู่ระบบ":

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
                "จำนวนรายการ",
                len(filtered_logs)
            )

            st.divider()

            for log in reversed(filtered_logs):

                st.markdown(
                    f"- 🕒 **{log.get('time', '-')}"
                    f"** | "
                    f"รหัส: **{log.get('id', '-')}** | "
                    f"ชื่อ: **{log.get('name', '-')}** | "
                    f"สถานะ: **{log.get('role', '-')}**"
                )


    # =====================================================
    # ข้อมูลส่วนตัว
    # =====================================================
    elif menu == "👤 ข้อมูลของฉัน":

        st.header("👤 ข้อมูลของฉัน")

        st.info(
            "ข้อมูลสมาชิกที่เข้าสู่ระบบ"
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
# ยังไม่ได้ Login
# =========================================================
else:

    st.header("🌱 ฐานข้อมูลพรรณไม้")

    plants = st.session_state.data.get(
        "plants",
        {}
    )

    # -----------------------------------------------------
    # แสดงพรรณไม้แบบสาธารณะ
    # -----------------------------------------------------
    if plants:

        plant_name = st.selectbox(
            "เลือกพืชที่ต้องการศึกษา",
            list(plants.keys())
        )

        plant = plants[plant_name]

        col1, col2 = st.columns(
            [1, 2]
        )

        with col1:

            image_path = plant.get(
                "image"
            )

            if (
                image_path
                and os.path.exists(image_path)
            ):

                st.image(
                    image_path,
                    caption=plant_name,
                    use_container_width=True
                )

            else:

                st.info(
                    "🌱 ไม่มีรูปภาพ"
                )

        with col2:

            st.subheader(
                f"🌱 {plant_name}"
            )

            st.markdown(
                f"**ชื่อวิทยาศาสตร์:** "
                f"*{plant.get('scientific_name', '-')}*"
            )

            st.markdown(
                f"**สรรพคุณ:** "
                f"{plant.get('benefit', '-')}"
            )

            qr_buffer = create_qr_code(
                plant_name,
                plant
            )

            st.image(
                qr_buffer,
                width=160,
                caption="QR Code"
            )

    else:

        st.info(
            "ยังไม่มีข้อมูลพรรณไม้"
        )

    # =====================================================
    # Login
    # =====================================================
    st.divider()

    st.header("🔐 เข้าสู่ระบบ")

    with st.form("login_form"):

        user_id = st.text_input(
            "เลขประจำตัว / รหัสสมาชิก"
        )

        login_button = st.form_submit_button(
            "เข้าสู่ระบบ",
            use_container_width=True
        )

        if login_button:

            user_id = user_id.strip()

            users = st.session_state.data[
                "users"
            ]

            if user_id in users:

                user_info = users[user_id].copy()

                # เพิ่ม id เข้าไปเพื่อใช้ใน session
                user_info["id"] = user_id

                st.session_state.logged_in = True
                st.session_state.current_user = user_info

                # บันทึก Log
                now = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                log_entry = {
                    "id": user_id,
                    "name": user_info["name"],
                    "role": user_info["role"],
                    "time": now
                }

                st.session_state.data[
                    "logs"
                ].append(log_entry)

                save_data(
                    st.session_state.data
                )

                st.success(
                    f"ยินดีต้อนรับ "
                    f"{user_info['name']}"
                )

                st.rerun()

            else:

                st.error(
                    "ไม่พบรหัสสมาชิกนี้ "
                    "กรุณาติดต่อผู้ดูแลระบบ"
                )


# =========================================================
# Footer
# =========================================================
st.divider()

st.caption(
    "🌿 ระบบพฤกษศาสตร์โรงเรียนฐานปัญญา "
    "สำหรับจัดเก็บและเผยแพร่ข้อมูลพรรณไม้"
)
