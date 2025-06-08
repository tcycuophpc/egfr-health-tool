import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import datetime
import numpy as np
import joblib

USER_DATA_FILE = "user_data.json"
MODEL_FILE = "egfr_model.pkl"
os.makedirs("charts", exist_ok=True)

# 顯示圖片
st.image("護理系圖檔.png", caption="中國醫藥大學護理學系 (School of Nursing, CMU)", use_container_width=True)

# 資料載入與儲存
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 登入介面
def user_login():
    st.title("健康評估登入系統")
    id_last4 = st.text_input("身分證後四碼")
    birth4 = st.text_input("生日四碼 (MMDD)")
    if st.button("登入"):
        if len(id_last4) == 4 and len(birth4) == 4:
            user_id = id_last4 + birth4
            user_data = load_user_data()
            if user_id == "12345678":
                st.session_state["user_id"] = user_id
                st.session_state["is_admin"] = True
                st.success("管理者登入成功")
            else:
                if user_id not in user_data:
                    user_data[user_id] = {"records": []}
                    save_user_data(user_data)
                st.session_state["user_id"] = user_id
                st.session_state["is_admin"] = False
                st.success("登入成功")
        else:
            st.warning("請正確輸入共 8 碼")

# 檢查登入狀態
if "user_id" not in st.session_state:
    user_login()
    st.stop()

user_id = st.session_state["user_id"]
user_data = load_user_data()

# 基本資訊輸入
st.title("🩺 健康評估")

name = st.text_input("姓名")
age = st.number_input("年齡", 1, 120)
height = st.number_input("身高 (cm)", 100.0, 250.0)
weight = st.number_input("體重 (kg)", 30.0, 200.0)
bmi = round(weight / ((height / 100) ** 2), 1)
st.metric("BMI 指數", bmi)

sbp = st.slider("收縮壓 SBP", 80, 200)
dbp = st.slider("舒張壓 DBP", 40, 130)
egfr = st.number_input("eGFR(ml/min/1.73m²)", 1.0, 120.0)

# 生活習慣
st.subheader("生活習慣（次數輸入）")
smoking_freq = st.slider("每日抽菸支數", 0, 40)
drinking_freq = st.slider("每週飲酒次數", 0, 14)
chewing_freq = st.slider("每日嚼檳榔次數", 0, 20)
drug_freq = st.slider("每月藥物濫用次數", 0, 30)
supp_freq = st.slider("每日保健品使用次數", 0, 10)

# 慢性病史
st.subheader("慢性病史")
chronic_illnesses = st.multiselect("請勾選曾罹患的慢性病", ["糖尿病", "高血壓", "中風", "其他"])
chronic_count = len(chronic_illnesses)

# FRAIL 指標
st.subheader("FRAIL 衰弱指標")
f = st.radio("Fatigue 疲憊感", ["是", "否"])
r = st.radio("Resistance 肌力減弱", ["是", "否"])
a = st.radio("Ambulation 行走困難", ["是", "否"])
i = st.radio("Illnesses 慢性病多於5種", ["是", "否"])
l = st.radio("Loss of weight 體重下降", ["是", "否"])
frail_score = [f, r, a, i, l].count("是")
frail_status = "健壯" if frail_score == 0 else "前衰弱" if frail_score in [1, 2] else "衰弱"
st.write(f"FRAIL 總分：{frail_score}，狀態：{frail_status}")

# 儲存紀錄
if st.button("儲存紀錄"):
    today = datetime.date.today().isoformat()
    record = {
        "date": today, "egfr": egfr, "sbp": sbp, "dbp": dbp, "bmi": bmi,
        "frail": frail_score, "frail_status": frail_status,
        "smoking_freq": smoking_freq, "drinking_freq": drinking_freq,
        "chewing_freq": chewing_freq, "drug_freq": drug_freq,
        "supp_freq": supp_freq, "chronic_count": chronic_count,
        "chronic_illnesses": chronic_illnesses
    }

    if user_id not in user_data:
        user_data[user_id] = {"records": []}
    if "records" not in user_data[user_id]:
        user_data[user_id]["records"] = []

    user_data[user_id]["records"].append(record)
    user_data[user_id]["records"] = user_data[user_id]["records"][-10:]
    save_user_data(user_data)
    st.success("✅ 紀錄已儲存")

# 模型預測
model = joblib.load(MODEL_FILE) if os.path.exists(MODEL_FILE) else None
predicted_egfr = None
if model:
    input_data = [[
        smoking_freq, drinking_freq, chewing_freq,
        drug_freq, supp_freq, chronic_count
    ]]
    predicted_egfr = model.predict(input_data)[0]
    st.metric("預測下一次 eGFR", f"{predicted_egfr:.2f} ml/min/1.73m²")

# 衛教建議
st.subheader("📌 健康衛教與掛號建議")
if egfr < 60 or (predicted_egfr and predicted_egfr < 60):
    st.warning("🔶 腎功能偏低：eGFR 小於 60，建議就醫")
    st.markdown("""
- **eGFR 是腎功能的重要指標**。若低於 60，代表腎臟過濾效率下降，需及早診治。
- 控制高血壓、血糖與避免藥物傷腎行為是重點。
- 建議掛號 [腎臟科](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30500A&flag=first)
""")

if "糖尿病" in chronic_illnesses:
    st.info("📌 糖尿病患者注意腎臟與眼睛健康")
    st.markdown("""
- 高血糖會加速腎絲球硬化，建議嚴控血糖。
- 每年追蹤腎功能（eGFR、尿蛋白）與眼底檢查。
- 建議掛號 [新陳代謝科](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30300A&flag=first)
""")

if "高血壓" in chronic_illnesses:
    st.info("📌 血壓控制需穩定")
    st.markdown("""
- 血壓過高會加重腎臟與心血管負擔，建議目標 < 130/80。
- 減鹽、運動與規律用藥是控制關鍵。
- 建議掛號 [心臟內科](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30100A&flag=first)
""")

if "中風" in chronic_illnesses:
    st.info("📌 中風後應積極預防再發")
    st.markdown("""
- 控制三高（血壓、血糖、血脂）
- 規律復健、服藥與生活調整
- 建議掛號 [神經內科](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30900A&flag=first)
""")

if smoking_freq > 5 or drinking_freq > 3 or chewing_freq > 2:
    st.info("🚭 高風險生活行為")
    st.markdown("""
- 吸菸與嚼檳榔皆為一級致癌物，會增加心腎與癌症風險。
- 飲酒超過建議量也會影響肝腎與代謝。
- 建議諮詢 [家庭醫學科](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=31300A&flag=first)
""")

if frail_score > 2:
    st.info("🧓 衰弱風險建議")
    st.markdown("""
- 增加蛋白質與營養補充，加強肌力訓練
- 避免跌倒、感染、住院等併發症
- 建議掛號 [復健科](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=31700A&flag=first)
""")

# 趨勢圖與歷史資料
records = user_data.get(user_id, {}).get("records", [])
if records:
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["predicted_egfr"] = df["egfr"].ewm(span=2).mean()

    st.subheader("📈 eGFR 與預測趨勢")
    st.line_chart(df[["egfr", "predicted_egfr"]].tail(10))

    st.subheader("📄 最近五筆紀錄")
    st.dataframe(df.tail(5))
