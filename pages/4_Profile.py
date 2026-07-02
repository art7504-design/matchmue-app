import os

import streamlit as st

st.set_page_config(page_title="โปรไฟล์โภชนาการ", page_icon="👤")

# 1. ระบบป้องกันการข้ามขั้นตอน (หากยังไม่มีข้อมูลการคำนวณ BMR จะไม่แสดงหน้านี้)
if 'user_profile' not in st.session_state or st.session_state.user_profile.get('bmr', 0) == 0:
    st.warning("⚠️ ไม่พบข้อมูลโปรไฟล์ของคุณ กรุณากลับไปกรอกข้อมูลกายภาพในเมนู '1_Calculate_BMR' ก่อนครับ")
    st.stop()

# ดึงข้อมูลจากกล่องความจำมาไว้ในตัวแปรสั้นๆ เพื่อให้เขียนโค้ดง่ายขึ้น
profile = st.session_state.user_profile

header5_path = os.path.join("BannerAndApppic", "header 5.jpg")
if os.path.exists(header5_path):
    st.image(header5_path, use_container_width=True)
else:
    st.title("👤 โปรไฟล์โภชนาการของคุณ")
st.markdown("---")

# 2. ส่วนสถานะโควต้าพลังงานประจำวัน (Daily Quota Tracker)
st.subheader("📊 สรุปโควต้าแคลอรี่วันนี้")

target = profile['daily_calorie_target']
consumed = profile['calories_consumed']
remaining = profile['calories_remaining']

# แสดงผลแบบ 3 การ์ดตัวเลข (Metrics)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="โควต้าเป้าหมายต่อวัน", value=f"{target:,.0f} kcal")
with col2:
    st.metric(label="ทานไปแล้ววันนี้", value=f"{consumed:,.0f} kcal")
with col3:
    # หากแคลอรี่คงเหลือน้อยกว่า 0 ตัวเลขจะแสดงเป็นสถานะแจ้งเตือนติดลบ
    if remaining >= 0:
        st.metric(label="โควต้าคงเหลือ", value=f"{remaining:,.0f} kcal")
    else:
        st.metric(label="ทานเกินโควต้าไปแล้ว", value=f"{abs(remaining):,.0f} kcal", delta=f"-{abs(remaining):,.0f} kcal", delta_color="inverse")
# แถบแสดงความคืบหน้าโปรตีน
target_pro = profile.get('daily_protein_target', 0.0)
consumed_pro = profile.get('protein_consumed', 0.0)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🥩 สรุปการได้รับโปรตีน")
if target_pro > 0:
    pro_percentage = min(consumed_pro / target_pro, 1.0)
    st.progress(pro_percentage)
    
    st.write(f"ได้รับโปรตีนแล้ว **{consumed_pro:,.1f}g** จากเป้าหมาย **{target_pro:,.1f}g**")
# 3. แถบแสดงความคืบหน้าการกิน (Progress Bar)
st.markdown("<br>", unsafe_allow_html=True)
if target > 0:
    # คำนวณเปอร์เซ็นต์ โดยใช้ min เพื่อไม่ให้แถบหลุดเกิน 100% ในกรณีที่กินเกิน
    progress_percentage = min(consumed / target, 1.0)
    st.progress(progress_percentage)
    
    actual_percentage = (consumed / target) * 100
    st.write(f"คุณใช้โควต้าพลังงานประจำวันไปแล้ว **{actual_percentage:.1f}%**")

st.markdown("---")

# 4. แสดงรายละเอียดกายภาพและเป้าหมายระบบหลังบ้าน
st.subheader("📋 รายละเอียดข้อมูลระบบ")

detail_col1, detail_col2 = st.columns(2)
with detail_col1:
    st.markdown(f"""
    * **เพศ:** {profile['gender']}
    * **อายุ:** {profile['age']} ปี
    * **น้ำหนัก:** {profile['weight']} กิโลกรัม
    * **ส่วนสูง:** {profile['height']} เซนติเมตร
    """)


with detail_col2:
    st.markdown(f"""
    * **ค่า BMR (Basal Metabolic Rate):** {profile['bmr']:,.2f} kcal
    * **ค่า TDEE (Daily Energy Expense):** {profile['tdee']:,.2f} kcal
    * **แผนการ/เป้าหมายปัจจุบัน:** <span style='color: #FF4B4B; font-weight: bold;'>{profile['goal_type']}</span>
    """, unsafe_allow_html=True)

st.markdown("---")

# 5. ปุ่มสำหรับเคลียร์ค่าเริ่มต้นใหม่ (Reset Button สำหรับขึ้นวันใหม่)
st.subheader("🔄 เริ่มต้นวันใหม่")
st.write("เมื่อขึ้นวันใหม่ คุณสามารถกดปุ่มด้านล่างเพื่อล้างสถิติการทานอาหาร ให้กลับไปเริ่มนับโควต้าจากเต็มจำนวนอีกครั้ง")

if st.button("รีเซ็ตตัวนับโควต้าอาหารประจำวัน", type="secondary", use_container_width=True):
    # ปรับค่าการกินกลับเป็นศูนย์ และให้ค่าคงเหลือเท่ากับเป้าหมายเริ่มต้น
    st.session_state.user_profile['calories_consumed'] = 0.0
    st.session_state.user_profile['calories_remaining'] = target
    
    st.success("🔄 รีเซ็ตระบบนับแคลอรี่เรียบร้อยแล้ว ขอให้มีความสุขกับมื้ออาหารในวันใหม่ครับ!")
    # สั่งให้ Streamlit รีเฟรชหน้าจอเพื่อแสดงผลค่าที่เปลี่ยนไปทันที
    st.rerun()