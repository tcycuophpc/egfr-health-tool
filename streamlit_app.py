import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="健康評估與衛教建議系統", layout="wide")
st.title("🩺 健康評估與衛教建議系統")

# --- 使用者輸入 ---
st.header("📋 基本資訊與健康參數")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("年齡", min_value=1, max_value=120, value=65)
    height = st.number_input("身高（cm）", min_value=100, max_value=250, value=170)
    weight = st.number_input("體重（kg）", min_value=30.0, max_value=200.0, value=65.0)
    systolic = st.number_input("收縮壓（mmHg）", min_value=80, max_value=250, value=130)
    diastolic = st.number_input("舒張壓（mmHg）", min_value=40, max_value=150, value=85)

with col2:
    egfr = st.number_input("eGFR（mL/min/1.73m²）", min_value=0.0, max_value=150.0, value=85.0)
    sleep_hours = st.slider("平均每日睡眠時數（小時）", 0, 15, 7)
    stress = st.slider("壓力指數（0-10）", 0, 10, 3)
    drinking = st.selectbox("飲酒狀況", ["不喝", "偶爾", "經常"])
    smoking = st.selectbox("抽菸狀況", ["不抽", "已戒菸", "目前仍抽"])
    betel_nut = st.selectbox("嚼檳榔", ["否", "是"])
    drug_use = st.selectbox("藥物濫用", ["否", "目前有"])

# --- 計算 BMI ---
bmi = round(weight / ((height / 100) ** 2), 1)

# --- 衰弱簡易測試（FRAIL Scale） ---
st.header("📊 衰弱簡易測試（FRAIL Scale）")
st.write("請根據下列敘述選擇「是」或「否」")

f = st.radio("1️⃣ 疲倦：過去四週是否大部分時間感到疲倦？", ["否", "是"])
r = st.radio("2️⃣ 抵抗力：是否無法獨自走上10階樓梯？", ["否", "是"])
a = st.radio("3️⃣ 活動力：是否無法獨自走300公尺？", ["否", "是"])
i = st.radio("4️⃣ 疾病：是否患有5種以上慢性病？", ["否", "是"])
l = st.radio("5️⃣ 體重下降：過去半年是否非預期減重超過5公斤？", ["否", "是"])

frail_score = sum([f, r, a, i, l].count("是"))
frail_status = "無衰弱" if frail_score <= 1 else "前衰弱" if frail_score <= 3 else "衰弱"

# --- 腎功能狀態 ---
def egfr_status(e):
    if e >= 90:
        return "正常腎功能"
    elif e >= 60:
        return "輕度腎功能減退"
    elif e >= 30:
        return "中度腎功能減退"
    else:
        return "重度腎功能減退"

egfr_state = egfr_status(egfr)

# --- 折線圖資料（假資料） ---
data = pd.DataFrame({
    '月份': ['1月', '2月', '3月', '4月', '5月'],
    'eGFR': [90, 88, 85, 83, egfr],
    'BMI': [22.0, 22.3, 22.5, 22.7, bmi],
    '壓力指數': [4, 4, 3, 4, stress],
    '睡眠時數': [7, 6.5, 7, 8, sleep_hours]
})

# --- 顯示圖表 ---
st.header("📈 健康指標歷史趨勢")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(data['月份'], data['eGFR'], marker='o', label='eGFR', color='green')
ax.plot(data['月份'], data['BMI'], marker='o', label='BMI', color='blue')
ax.plot(data['月份'], data['壓力指數'], marker='o', label='壓力', color='orange')
ax.plot(data['月份'], data['睡眠時數'], marker='o', label='睡眠時數', color='purple')
ax.set_xlabel("時間")
ax.set_ylabel("數值")
ax.set_title("健康趨勢折線圖")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# --- 評估總結 ---
st.header("🧾 評估結果摘要")
st.markdown(f"- **年齡：** {age} 歲")
st.markdown(f"- **血壓：** {systolic}/{diastolic} mmHg")
st.markdown(f"- **BMI：** {bmi}")
st.markdown(f"- **eGFR 狀況：** **{egfr_state}**")
st.markdown(f"- **衰弱狀況：** **{frail_status}**")

# --- 衛教建議（延續原始設計） ---
st.header("📚 衛教建議")
#（原本的 eGFR、BMI、衰弱、生活習慣衛教建議請複製你原來的邏輯貼上這裡即可）

# --- 門診建議 ---
st.subheader("🏥 門診建議與掛號")
if egfr < 60 or frail_status == "衰弱":
    st.error("建議盡快至腎臟科及老年醫學科門診追蹤與治療。")
    st.markdown("[👉 點此前往中國醫藥大學附設醫院掛號](https://www.cmuh.cmu.edu.tw/OnlineAppointment/AppointmentByDivision)")
elif egfr < 90:
    st.warning("建議定期至腎臟科門診追蹤，並配合醫師指示。")
    st.markdown("[👉 點此前往中國醫藥大學附設醫院掛號](https://www.cmuh.cmu.edu.tw/OnlineAppointment/AppointmentByDivision)")
else:
    st.info("腎功能良好，請持續定期檢查與健康生活。")
