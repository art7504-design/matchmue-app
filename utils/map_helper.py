import folium
import pandas as pd
import base64
import os

def get_image_base64(image_path: str):
    """
    ฟังก์ชันสำหรับแปลงไฟล์ภาพจากโฟลเดอร์ให้กลายเป็นรหัส Base64
    เพื่อนำไปฝังในหน้าต่าง Popup ของ Folium ได้โดยตรง
    """
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                ext = image_path.split('.')[-1].lower()
                mime_type = "image/png" if ext == "png" else "image/jpeg"
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        print(f"Error loading image: {e}")
    return None

def generate_restaurant_map(filtered_df: pd.DataFrame, center_lat: float = 18.7975, center_lng: float = 99.0061) -> folium.Map:
    """
    ฟังก์ชันสำหรับสร้างแผนที่และปักหมุดร้านอาหารที่ตรงตามเงื่อนไข
    """
    m = folium.Map(location=[center_lat, center_lng], zoom_start=16)
    
    folium.Marker(
        location=[center_lat, center_lng],
        popup=folium.Popup("<div style='min-width: 150px;'><b>📍 จุดอ้างอิงของคุณ</b><br>โรงเรียนปรินส์รอยแยลส์วิทยาลัย</div>", max_width=250),
        tooltip="ตำแหน่งของคุณ (PRC)",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

    if filtered_df.empty:
        return m

    grouped = filtered_df.groupby(['restaurant_name', 'lat', 'lng'])

    for (res_name, lat, lng), group in grouped:
        menus = group.to_dict('records')
        main_menu = menus[0]
        other_menus = menus[1:]
        
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={center_lat},{center_lng}&destination={lat},{lng}"
        
        # --- เตรียมรูปภาพ ---
        img_html = ""
        pic_name = main_menu.get('Pic_name', '')
        if pd.notna(pic_name) and str(pic_name).strip() != "":
            img_path = os.path.join("Pic", str(pic_name).strip())
            img_base64 = get_image_base64(img_path)
            if img_base64:
                img_html = f"""
                <div style="text-align: center; margin-bottom: 10px;">
                    <img src="{img_base64}" style="width: 100%; max-height: 140px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                </div>
                """
        
        # --- ฟังก์ชันตัวช่วยจัดการค่าว่าง (NaN) ของรีวิวและคะแนน ---
        def get_score_review(menu_item):
            score = menu_item.get('Score')
            review = menu_item.get('Review')
            if pd.isna(score) or str(score).strip() == "": score = "-"
            if pd.isna(review) or str(review).strip() == "": review = "ยังไม่มีรีวิว"
            return score, review

        main_score, main_review = get_score_review(main_menu)
        
        # --- ส่วนประกอบ HTML สำหรับ Popup (เมนูหลัก) ---
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 260px;">
            <h4 style="margin-top: 0; margin-bottom: 10px; color: #2E86C1;">{res_name}</h4>
            {img_html}
            <ul style="padding-left: 20px; margin-bottom: 10px; line-height: 1.4;">
                <li><b>เมนู:</b> {main_menu['menu_name']}</li>
                <li><b>ราคา:</b> {main_menu['price_thb']} บาท</li>
                <li><b>พลังงาน:</b> <span style="color: #28B463; font-weight: bold;">{main_menu['calories_kcal']} kcal</span></li>
                <li><b>โปรตีน:</b> {main_menu.get('protein_g', 0)} g</li>
                <li style="margin-top: 4px; color: #555;">⭐ <b>{main_score}</b> | 💬 <i>"{main_review}"</i></li>
            </ul>
        """
        
        # --- ส่วนประกอบ HTML สำหรับเมนูอื่นๆ (ซ่อนใน Dropdown) ---
        if other_menus:
            popup_html += """
            <details style="margin-bottom: 12px; cursor: pointer;">
                <summary style="font-weight: bold; color: #E67E22; outline: none;">> ดูเมนูอื่นที่ผ่านเกณฑ์</summary>
                <ul style="padding-left: 20px; margin-top: 8px; font-size: 0.9em; color: #444;">
            """
            for om in other_menus:
                om_score, om_review = get_score_review(om)
                popup_html += f"""
                    <li style="margin-bottom: 8px; border-bottom: 1px dashed #ccc; padding-bottom: 6px;">
                        <b>{om['menu_name']}</b><br>
                        {om['price_thb']} บาท | <span style="color: #28B463;">{om['calories_kcal']} kcal</span> | โปรตีน {om.get('protein_g', 0)}g<br>
                        <span style="font-size: 0.9em; color: #666;">⭐ <b>{om_score}</b> | 💬 <i>"{om_review}"</i></span>
                    </li>
                """
            popup_html += """
                </ul>
            </details>
            """
            
        popup_html += f"""
            <a href="{google_maps_url}" target="_blank" style="background-color: #4285F4; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; display: inline-block; text-align: center; width: 85%;">
                🧭 นำทางไปร้านนี้
            </a>
        </div>
        """
        
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"🍽️ {res_name}", 
            icon=folium.Icon(color="green", icon="cutlery", prefix='fa')
        ).add_to(m)
        
    return m