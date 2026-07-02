import os

from utils.calculations import calculate_target_calories, calculate_target_protein
import streamlit as st
from utils.calculations import calculate_target_calories

st.set_page_config(page_title="กำหนดเป้าหมาย", page_icon="🎯")

# 1. ระบบป้องกันการข้ามขั้นตอน (Error Handling)
# หากผู้ใช้กดมาหน้านี้โดยที่ยังไม่ได้คำนวณ TDEE ระบบจะแจ้งเตือนและหยุดการทำงานของหน้านี้
if 'user_profile' not in st.session_state or st.session_state.user_profile.get('tdee', 0) == 0:
    st.warning("⚠️ ไม่พบข้อมูลกายภาพของคุณ กรุณากลับไปคำนวณค่า BMR และ TDEE ในเมนู '1_Calculate_BMR' ก่อนครับ")
    st.stop()

header3_path = os.path.join("BannerAndApppic", "header 3.jpg")
if os.path.exists(header3_path):
    st.image(header3_path, use_container_width=True)
else:
    st.title("🎯 แผนการของคุณ")
st.write("เลือกเป้าหมายทางโภชนาการ เพื่อให้ระบบคำนวณโควต้าพลังงานที่เหมาะสมสำหรับคุณ")

# 2. สร้างตัวเลือกเป้าหมาย (เทียบเท่ากับกล่อง 3 กล่องใน Wireframe หน้า 2)
goal_options = ["ลดน้ำหนัก", "รักษาน้ำหนัก", "สร้างกล้ามเนื้อ"]
current_goal = st.session_state.user_profile.get('goal_type', 'รักษาน้ำหนัก')

# ถ้าค่าเดิมไม่มีใน list ให้ตั้งค่าพื้นฐาน
if current_goal not in goal_options:
    current_goal = "รักษาน้ำหนัก"

selected_goal = st.radio("โปรดระบุเป้าหมายปัจจุบันของคุณ:", goal_options, index=goal_options.index(current_goal), horizontal=True)

st.markdown("---")

# 3. แสดงช่องกรอกข้อมูลที่เปลี่ยนไปตามเป้าหมายที่เลือก (Dynamic UI)
if selected_goal == "ลดน้ำหนัก":
    st.subheader("📉 เป้าหมาย: ลดน้ำหนัก")
    col1, col2 = st.columns(2)
    with col1:
        weight_to_lose = st.number_input("- น้ำหนักที่ต้องการลด (กิโลกรัม)", min_value=0.0, step=0.5, format="%.1f")
    with col2:
        duration_weeks = st.number_input("- ระยะเวลา (สัปดาห์)", min_value=1, step=1)
        
elif selected_goal == "รักษาน้ำหนัก":
    st.subheader("⚖️ เป้าหมาย: ควบคุมน้ำหนัก")
    st.info("เพื่อให้ร่างกายได้รับพลังงานอย่างเหมาะสมและทำงานได้อย่างมีประสิทธิภาพ")
    
elif selected_goal == "สร้างกล้ามเนื้อ":
    st.subheader("💪 เป้าหมาย: สร้างกล้ามเนื้อ")
    # รองรับตารางการฝึกที่มีความถี่สูง
    weight_training_hours = st.number_input("จำนวนชั่วโมงเวทเทรนนิ่งต่อสัปดาห์", min_value=0, max_value=40, value=6, step=1)

st.markdown("<br>", unsafe_allow_html=True)

# 4. ปุ่มยืนยันและคำนวณโควต้าแคลอรี่
if st.button("ยืนยันแผนการและคำนวณโควต้า", type="primary", use_container_width=True):
    tdee = st.session_state.user_profile['tdee']
    weight = st.session_state.user_profile['weight'] # ดึงน้ำหนักมาใช้คิดโปรตีน
    
    target_cal = calculate_target_calories(tdee, selected_goal)
    target_protein = calculate_target_protein(weight, selected_goal) # คำนวณโปรตีน
    
    st.session_state.user_profile.update({
        'goal_type': selected_goal,
        'daily_calorie_target': target_cal,
        'calories_consumed': 0.0, 
        'calories_remaining': target_cal,
        'daily_protein_target': target_protein, # บันทึกโปรตีนเป้าหมาย
        'protein_consumed': 0.0                 # รีเซ็ตการกินโปรตีน
    })
    
    st.success("✅ บันทึกเป้าหมายเรียบร้อยแล้ว!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="โควต้าพลังงานต่อวัน", value=f"{target_cal:,.0f} kcal")
    with col2:
        st.metric(label="เป้าหมายโปรตีนต่อวัน", value=f"{target_protein:,.0f} g")