import os
import streamlit as st
from utils.calculations import calculate_target_calories, calculate_target_protein

st.set_page_config(page_title="กำหนดเป้าหมาย", page_icon="🎯")

# 1. ระบบป้องกันการข้ามขั้นตอน (Error Handling)
if 'user_profile' not in st.session_state or st.session_state.user_profile.get('tdee', 0) == 0:
    st.warning("⚠️ ไม่พบข้อมูลกายภาพของคุณ กรุณากลับไปคำนวณค่า BMR และ TDEE ในเมนู '1_Calculate_BMR' ก่อนครับ")
    st.stop()

header3_path = os.path.join("BannerAndApppic", "header 3.jpg")
if os.path.exists(header3_path):
    st.image(header3_path, use_container_width=True)
else:
    st.title("🎯 แผนการของคุณ")
st.write("เลือกเป้าหมายทางโภชนาการ เพื่อให้ระบบคำนวณโควต้าพลังงานที่เหมาะสมสำหรับคุณ")

# 2. สร้างตัวเลือกเป้าหมาย
goal_options = ["ลดน้ำหนัก", "รักษาน้ำหนัก", "สร้างกล้ามเนื้อ"]
current_goal = st.session_state.user_profile.get('goal_type', 'รักษาน้ำหนัก')

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
    weight_training_hours = st.number_input("จำนวนชั่วโมงเวทเทรนนิ่งต่อสัปดาห์", min_value=0, max_value=40, value=6, step=1)

st.markdown("<br>", unsafe_allow_html=True)

# 4. ปุ่มยืนยันและคำนวณโควต้าแคลอรี่
if st.button("คำนวณโควต้าโภชนาการประจำวัน", type="primary", use_container_width=True):
    tdee = st.session_state.user_profile['tdee']
    weight = st.session_state.user_profile['weight'] 
    
    target_cal = calculate_target_calories(tdee, selected_goal)
    target_protein = calculate_target_protein(weight, selected_goal) 
    
    # อัปเดตข้อมูลทั้งหมดลงในกล่องความจำ
    st.session_state.user_profile.update({
        'goal_type': selected_goal,
        'daily_calorie_target': target_cal,
        'calories_consumed': 0.0, 
        'calories_remaining': target_cal,
        'daily_protein_target': target_protein, 
        'protein_consumed': 0.0                 
    })
    
    st.success("✅ บันทึกเป้าหมายและคำนวณโควต้าเรียบร้อยแล้ว!")
    # สั่งรีเฟรชหน้าจอ 1 ครั้งเพื่อให้เงื่อนไขด้านล่างทำงานได้อย่างเสถียร
    st.rerun()

# =========================================================
# 5. ส่วนแสดงผลลัพธ์และปุ่มไปขั้นตอนต่อไป (แยกออกมานอกปุ่มกดคำนวณ)
# =========================================================
if st.session_state.user_profile.get('daily_calorie_target', 0) > 0:
    st.markdown("---")
    saved_cal = st.session_state.user_profile['daily_calorie_target']
    saved_protein = st.session_state.user_profile['daily_protein_target']
    
    # แสดงผลการ์ดตัวเลขสรุปเป้าหมาย
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="โควต้าพลังงานเป้าหมาย", value=f"{saved_cal:,.0f} kcal / วัน")
    with res_col2:
        st.metric(label="เป้าหมายโปรตีนที่ต้องได้รับ", value=f"{saved_protein:,.1f} g / วัน")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ปุ่มเปลี่ยนหน้าไปหน้า 3 (ทำงานได้ลื่นไหล 100% ไม่ติดขัดแล้วครับ)
    if st.button("🗺️ ไปขั้นตอนต่อไป: ค้นหาร้านอาหารและแผนที่", type="primary", use_container_width=True):
        st.switch_page("pages/3_Map_and_Menu.py")