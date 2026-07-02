import os

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from utils.map_helper import generate_restaurant_map
from utils.calculations import calculate_meal_quota, calculate_remaining_calories

st.set_page_config(page_title="ค้นหาร้านอาหาร", page_icon="🗺️", layout="wide")

# 1. ระบบป้องกันการข้ามขั้นตอน
if 'user_profile' not in st.session_state or st.session_state.user_profile.get('daily_calorie_target', 0) == 0:
    st.warning("⚠️ ยังไม่มีข้อมูลโควต้าพลังงาน กรุณาตั้งเป้าหมายในเมนู '2_Set_Goal' ก่อนครับ")
    st.stop()

target_cal = st.session_state.user_profile['daily_calorie_target']

header4_path = os.path.join("BannerAndApppic", "header 4.jpg")
if os.path.exists(header4_path):
    st.image(header4_path, use_container_width=True)
else:
    st.title("🗺️ แผนที่ร้านอาหารอัจฉริยะ")
st.write(f"โควต้าพลังงานทั้งวันของคุณคือ: **{target_cal:,.0f} kcal**")

# 2. จำลองการแบ่งมื้ออาหารเพื่อหาโควต้าต่อมื้อ
col1, col2 = st.columns([1, 2])
with col1:
    meals_per_day = st.selectbox("แบ่งทานกี่มื้อต่อวัน?", [1, 2, 3, 4, 5], index=2)
with col2:
    meal_quota = calculate_meal_quota(target_cal, meals_per_day)
    st.info(f"💡 โควต้าที่แนะนำต่อมื้อ: **{meal_quota:,.0f} kcal**")

st.markdown("---")

# 3. โหลดและจัดการข้อมูล
try:
    # เพิ่ม dtype เพื่อบังคับให้อ่าน lat และ lng เป็นข้อความ (str) เข้ามาก่อน เพื่อป้องกันการสูญเสียทศนิยม
    df = pd.read_csv('data/mock_restaurants.csv', encoding='cp874', dtype={'lat': str, 'lng': str})
    
    # แปลงข้อความกลับเป็นตัวเลขทศนิยมความละเอียดสูง (float) สำหรับใช้งานในแผนที่
    df['lat'] = df['lat'].astype(float)
    df['lng'] = df['lng'].astype(float)
    
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดไฟล์ข้อมูลได้: {e}")
    st.stop()

# กรองเมนูที่ไม่เกินโควต้า
filtered_df = df[df['calories_kcal'] <= meal_quota].dropna(subset=['restaurant_name', 'menu_name', 'calories_kcal', 'protein_g'])

# 4. แสดงผลแผนที่
if not filtered_df.empty:
    m = generate_restaurant_map(filtered_df)
    st_folium(m, width=800, height=500, returned_objects=[])
else:
    st.warning("🥲 ขออภัย ไม่มีเมนูใดในบริเวณนี้ที่แคลอรี่ต่ำพอสำหรับโควต้ามื้อนี้ของคุณ")

st.markdown("---")

# 5. ฟังก์ชันอัปเดตโควต้าหลังทานอาหาร
st.subheader("🍽️ บันทึกมื้ออาหาร")
st.write("หากตัดสินใจเลือกทานเมนูใด ให้บันทึกเพื่อหักโควต้าพลังงานและโปรตีนประจำวันของคุณ")

if not filtered_df.empty:
    options_idx = filtered_df.index.tolist()
    
    # ฟังก์ชันแสดงผลเมนูใน Dropdown (วางไว้ตรงนี้ถูกต้องแล้วครับ)
    def display_menu_format(idx):
        row = filtered_df.loc[idx]
        return f"{row['restaurant_name']} - {row['menu_name']} ({row['calories_kcal']} kcal | โปรตีน {row['protein_g']}g)"
        
    selected_idx = st.selectbox(
        "เลือกเมนูที่คุณกำลังจะทาน:", 
        options=options_idx, 
        format_func=display_menu_format
    )
    
    if st.button("✅ ยืนยันการทานเมนูนี้", type="primary"):
        consumed_cal = float(filtered_df.loc[selected_idx, 'calories_kcal'])
        consumed_pro = float(filtered_df.loc[selected_idx, 'protein_g'])
        
        # อัปเดตข้อมูลลง Session State
        st.session_state.user_profile['calories_consumed'] += consumed_cal
        st.session_state.user_profile['protein_consumed'] += consumed_pro
        
        st.session_state.user_profile['calories_remaining'] = calculate_remaining_calories(
            st.session_state.user_profile['daily_calorie_target'],
            st.session_state.user_profile['calories_consumed']
        )
        
        st.success(f"บันทึกสำเร็จ! หักแคลอรี่ {consumed_cal:,.0f} kcal และได้รับโปรตีน {consumed_pro:,.0f}g")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 ดูสรุปโปรไฟล์โภชนาการของคุณ", type="secondary", use_container_width=True):
            st.switch_page("pages/4_Profile.py")