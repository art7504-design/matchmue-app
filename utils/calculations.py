def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    คำนวณค่า BMR (Basal Metabolic Rate) ด้วยสมการ Mifflin-St Jeor
    คือพลังงานพื้นฐานที่ร่างกายต้องการขณะพักผ่อน
    """
    # ตรวจสอบค่าติดลบหรือค่าศูนย์เพื่อป้องกัน Error
    if weight <= 0 or height <= 0 or age <= 0:
        return 0.0

    if gender == 'ชาย':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else: # หญิง
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    return round(bmr, 2)

def calculate_tdee(bmr: float, activity_multiplier: float) -> float:
    """
    คำนวณค่า TDEE (Total Daily Energy Expenditure)
    คือพลังงานทั้งหมดที่ใช้ในแต่ละวัน รวมการทำกิจกรรมและการออกกำลังกาย
    """
    tdee = bmr * activity_multiplier
    return round(tdee, 2)

def calculate_target_calories(tdee: float, goal_type: str) -> float:
    """
    คำนวณโควต้าแคลอรี่ที่เหมาะสมต่อวันตามเป้าหมาย (ลด/รักษา/เพิ่ม)
    """
    if goal_type == 'ลดน้ำหนัก':
        # ลด 500 kcal จาก TDEE เพื่อลดน้ำหนักอย่างปลอดภัย (ประมาณ 0.5 กก. ต่อสัปดาห์)
        target = tdee - 500
    elif goal_type == 'สร้างกล้ามเนื้อ':
        # เพิ่ม 300 kcal จาก TDEE เพื่อให้มีพลังงานเหลือไปสร้างกล้ามเนื้อ (Caloric Surplus)
        target = tdee + 300
    else: 
        # รักษาน้ำหนัก (คงค่า TDEE ไว้เท่าเดิม)
        target = tdee
        
    # ป้องกันไม่ให้แคลอรี่เป้าหมายต่ำเกินไปจนเป็นอันตรายต่อร่างกาย (ขั้นต่ำที่แนะนำทั่วไปคือ 1200)
    if target < 1200 and target > 0:
        target = 1200.0
        
    return round(target, 2)

def calculate_remaining_calories(target_calories: float, consumed_calories: float) -> float:
    """
    คำนวณโควต้าแคลอรี่ที่เหลือในวันนั้น
    """
    remaining = target_calories - consumed_calories
    return round(remaining, 2)

def calculate_meal_quota(target_calories: float, meals_per_day: int = 3) -> float:
    """
    (ฟังก์ชันเสริม) แบ่งโควต้าแคลอรี่เป้าหมายออกเป็นมื้อ เพื่อนำไปกรองเมนูอาหาร
    ค่าเริ่มต้นคือแบ่งเป็น 3 มื้อ
    """
    if target_calories <= 0 or meals_per_day <= 0:
        return 0.0
        
    meal_quota = target_calories / meals_per_day
    return round(meal_quota, 2)
def calculate_target_protein(weight: float, goal_type: str) -> float:
    """
    คำนวณเป้าหมายโปรตีน (กรัม) ต่อวัน อิงตามน้ำหนักตัวและเป้าหมาย
    """
    if goal_type == 'สร้างกล้ามเนื้อ':
        # สำหรับการฝึกเวทเทรนนิ่งอย่างหนัก ต้องการโปรตีน 2.0g ต่อน้ำหนักตัว 1kg
        target = weight * 2.0
    elif goal_type == 'ลดน้ำหนัก':
        # ลดน้ำหนักต้องรักษามวลกล้ามเนื้อ ใช้โปรตีน 1.5g ต่อน้ำหนักตัว 1kg
        target = weight * 1.5
    else:
        # รักษาน้ำหนัก ใช้โปรตีนพื้นฐาน 1.0g ต่อน้ำหนักตัว 1kg
        target = weight * 1.0
        
    return round(target, 1)