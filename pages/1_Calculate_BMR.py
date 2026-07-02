import os

import streamlit as st
# นำเข้าฟังก์ชันคำนวณที่เขียนไว้ในโฟลเดอร์ utils
from utils.calculations import calculate_bmr, calculate_tdee

st.set_page_config(page_title="คำนวณ BMR", page_icon="🧮")

# 1. ตรวจสอบและสร้างตัวแปรความจำ (เผื่อกรณีผู้ใช้ข้ามหน้า Home แล้วกดมาหน้านี้เลย)
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'gender': 'ชาย', 'age': 0, 'weight': 0.0, 'height': 0.0,
        'bmr': 0.0, 'activity_multiplier': 1.2, 'tdee': 0.0,
        'goal_type': 'รักษาน้ำหนัก', 'daily_calorie_target': 0.0,
        'calories_consumed': 0.0, 'calories_remaining': 0.0
    }

header1_path = os.path.join("BannerAndApppic", "header 1.jpg")
if os.path.exists(header1_path):
    st.image(header1_path, use_container_width=True)
else:
    st.title("🧮 ข้อมูลกายภาพและ BMR")
st.write("กรุณากรอกข้อมูลของคุณเพื่อประมวลผลหาอัตราการเผาผลาญพลังงานพื้นฐาน (BMR) และพลังงานที่ใช้ต่อวัน (TDEE)")

# 2. สร้างฟอร์มกรอกข้อมูลแบบแบ่ง 2 คอลัมน์ให้ดูสวยงาม
col1, col2 = st.columns(2)

with col1:
    # ค่าเริ่มต้น (value) จะดึงมาจาก session_state เพื่อที่เวลาผู้ใช้เปลี่ยนหน้าไปมา ข้อมูลที่เคยกรอกจะไม่หาย
    gender = st.selectbox("เพศ", ["ชาย", "หญิง"], 
                          index=0 if st.session_state.user_profile['gender'] == 'ชาย' else 1)
    
    age = st.number_input("อายุ (ปี)", min_value=1, max_value=120, 
                          value=st.session_state.user_profile['age'] if st.session_state.user_profile['age'] > 0 else 20)

with col2:
    weight = st.number_input("น้ำหนัก (กิโลกรัม)", min_value=1.0, max_value=300.0, 
                             value=st.session_state.user_profile['weight'] if st.session_state.user_profile['weight'] > 0 else 60.0)
    
    height = st.number_input("ส่วนสูง (เซนติเมตร)", min_value=50.0, max_value=250.0, 
                             value=st.session_state.user_profile['height'] if st.session_state.user_profile['height'] > 0 else 165.0)

st.markdown("---")

# 3. ระดับกิจกรรม (Activity Level) สำหรับคำนวณ TDEE
header2_path = os.path.join("BannerAndApppic", "header 2.jpg")
if os.path.exists(header2_path):
    st.image(header2_path, use_container_width=True)
else:
    st.subheader("🏃‍♂️ ระดับการทำกิจกรรมในแต่ละวัน")
activity_options = {
    "ไม่ออกกำลังกายเลย หรือนั่งทำงานอยู่กับที่ (BMR x 1.2)": 1.2,
    "ออกกำลังกายเบาๆ 1-3 วัน/สัปดาห์ (BMR x 1.375)": 1.375,
    "ออกกำลังกายปานกลาง 3-5 วัน/สัปดาห์ (BMR x 1.55)": 1.55,
    "ออกกำลังกายอย่างหนัก (เวทเทรนนิ่ง/คาดิโอ) 6-7 วัน/สัปดาห์ (BMR x 1.725)": 1.725,
    "เป็นนักกีฬา หรือทำงานใช้แรงงานอย่างหนักทุกวัน (BMR x 1.9)": 1.9
}

# สร้าง Dropdown ให้เลือก และหาตัวคูณ (Multiplier) จากตัวเลือกที่กด
selected_activity = st.selectbox(
    "เลือกระดับกิจกรรมที่ตรงกับคุณที่สุด", 
    options=list(activity_options.keys())
)
activity_multiplier = activity_options[selected_activity]

# 4. ปุ่มกดประมวลผล
if st.button("ประมวลผล BMR และ TDEE", type="primary", use_container_width=True):
    # เรียกใช้สมการคณิตศาสตร์
    bmr_result = calculate_bmr(weight, height, age, gender)
    tdee_result = calculate_tdee(bmr_result, activity_multiplier)
    
    # อัปเดตข้อมูลทั้งหมดกลับเข้าไปในกล่องความจำ (Session State)
    st.session_state.user_profile.update({
        'gender': gender,
        'age': age,
        'weight': weight,
        'height': height,
        'bmr': bmr_result,
        'activity_multiplier': activity_multiplier,
        'tdee': tdee_result,
        'daily_protein_target': 0.0,
        'protein_consumed': 0.0
    })
    
    st.success("บันทึกข้อมูลกายภาพเรียบร้อยแล้ว!")
    
    # 5. แสดงผลลัพธ์เป็นกล่องตัวเลขขนาดใหญ่ (Metric)
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="BMR (พลังงานที่ร่างกายต้องใช้ขณะพัก)", value=f"{bmr_result:,.2f} kcal")
    with res_col2:
        st.metric(label="TDEE (พลังงานรวมที่ใช้ในแต่ละวัน)", value=f"{tdee_result:,.2f} kcal")
        
    st.info("👈 ข้อมูลถูกนำเข้าสู่ระบบแล้ว ไปที่เมนู '2_Set_Goal' เพื่อตั้งเป้าหมายโภชนาการได้เลย")