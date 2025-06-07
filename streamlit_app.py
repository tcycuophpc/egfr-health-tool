import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import datetime
import numpy as np
from autogluon.tabular import TabularPredictor

USER_DATA_FILE = "user_data.json"
os.makedirs("charts", exist_ok=True)

try:
    predictor = TabularPredictor.load("egfr_predictor/")
except:
    predictor = None

def load_user_data():
    return json.load(open(USER_DATA_FILE)) if os.path.exists(USER_DATA_FILE) else {}

def save_user_data(data):
    json.dump(data, open(USER_DATA_FILE, "w"), indent=2, ensure_ascii=False)

def user_login():
    st.title("健康評估登入系統")
    id_last4 = st.text_input("身分證後四碼")
    birth4 = st.text_input("生日四碼 (MMDD)")
    if st.button("登入"):
        if len(id_last4) == 4 and len(birth4) == 4:
            user_id = id_last4 + birth4
            if user_id == "12345678":
                st.session_state["user_id"] = user_id
                st.session_state["is_admin"] = True
                st.success("管理者登入成功")
            else:
                user_data = load_user_data()
                if user_id not in user_data:
                    user_data[user_id] = {"records": []}
                    save_user_data(user_data)
                st.session_state["user_id"] = user_id
                st.session_state["is_admin"] = False
                st.success("登入成功")
        else:
            st.warning("請正確輸入共 8 碼")

if "user_id" not in st.session_state:
    user_login()
    st.stop()
    user_id = st.session_state["user_id"]
is_admin = st.session_state.get("is_admin", False)
user_data = load_user_data()

if is_admin:
    st.title("📊 管理者總覽頁面")
    all_records = []
    for uid, data in user_data.items():
        for rec in data.get("records", []):
            rec["user_id"] = uid
            all_records.append(rec)
    if all_records:
        df_all = pd.DataFrame(all_records)
        st.dataframe(df_all)
        st.subheader("各使用者平均 eGFR")
        st.bar_chart(df_all.groupby("user_id")["egfr"].mean())
        st.subheader("整體 eGFR 變化趨勢")
        df_all["date"] = pd.to_datetime(df_all["date"])
        egrp = df_all.pivot_table(index="date", values="egfr", aggfunc="mean")
        st.line_chart(egrp)
    else:
        st.info("目前無使用者紀錄")
    st.stop()

# 使用者頁面開始
st.title("🩺 使用者健康評估系統")

name = st.text_input("姓名")
age = st.number_input("年齡", 1, 120)
height = st.number_input("身高 (cm)", 100.0, 250.0)
weight = st.number_input("體重 (kg)", 30.0, 200.0)
bmi = round(weight / ((height / 100) ** 2), 1)
st.metric("BMI 指數", bmi)

sbp = st.slider("收縮壓 SBP", 80, 200)
dbp = st.slider("舒張壓 DBP", 40, 130)
egfr = st.number_input("eGFR(ml/min/1.73m²)", 1.0, 120.0)

st.subheader("生活習慣（次數輸入）")
smoking_freq = st.slider("每日抽菸支數", 0, 40)
drinking_freq = st.slider("每週飲酒次數", 0, 14)
chewing_freq = st.slider("每日嚼檳榔次數", 0, 20)
drug_freq = st.slider("每月藥物濫用次數", 0, 30)
supp_freq = st.slider("每日保健品使用次數", 0, 10)

st.subheader("慢性病史")
chronic_illnesses = st.multiselect("請勾選您曾罹患的慢性病", ["糖尿病", "高血壓", "中風", "其他"])
chronic_count = len(chronic_illnesses)

st.subheader("FRAIL 衰弱指標")
f = st.radio("Fatigue 疲憊感", ["是", "否"])
r = st.radio("Resistance 肌力減弱", ["是", "否"])
a = st.radio("Ambulation 行走困難", ["是", "否"])
i = st.radio("Illnesses 慢性病多於5種", ["是", "否"])
l = st.radio("Loss of weight 體重下降", ["是", "否"])
frail_score = [f, r, a, i, l].count("是")
frail_status = "健壯" if frail_score == 0 else "前衰弱" if frail_score in [1, 2] else "衰弱"
st.write(f"FRAIL 總分：{frail_score}，目前狀態：{frail_status}")

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
    records = user_data[user_id].get("records", [])
    records.append(record)
    user_data[user_id]["records"] = records[-10:]
    save_user_data(user_data)
    st.success("✅ 紀錄已儲存")
    records = user_data[user_id].get("records", [])
if records:
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["predicted_egfr"] = df["egfr"].ewm(span=2).mean()

    st.subheader("📈 eGFR 趨勢圖")
    st.line_chart(df[["egfr", "predicted_egfr"]].tail(10))

    if predictor:
        sample = {
            "smoking_freq": smoking_freq,
            "drinking_freq": drinking_freq,
            "chewing_freq": chewing_freq,
            "drug_freq": drug_freq,
            "supp_freq": supp_freq,
            "chronic_count": chronic_count
        }
        sample_df = pd.DataFrame([sample])
        auto_pred = predictor.predict(sample_df)[0]
        st.metric("AutoML 預測 eGFR", f"{auto_pred:.2f} ml/min/1.73m²")

        st.subheader("📌 健康衛教與掛號建議")

        if egfr < 60 or auto_pred < 60:
            st.warning("🔶 腎功能低下：eGFR 小於 60")
            st.markdown("""
- 腎臟負責清除體內毒素，eGFR 小於 60 表示腎功能下降。
- 請減少高鹽、高蛋白飲食，避免腎毒性藥物。
- 建議至腎臟科進行尿液檢查與飲食評估。
[➡ 前往腎臟科預約](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30500A&flag=first)
""")

        if "糖尿病" in chronic_illnesses:
            st.info("📌 糖尿病與腎病變關聯")
            st.markdown("""
- 長期高血糖會破壞腎絲球，導致糖尿病腎病變。
- 每年至少檢查腎功能與眼底一次。
- 建議控制 A1C < 7%、少糖飲食。
[➡ 新陳代謝科掛號](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30300A&flag=first)
""")

        if "高血壓" in chronic_illnesses:
            st.info("📌 高血壓衛教")
            st.markdown("""
- 高血壓是腎臟與心血管疾病的主要危險因子。
- 飲食減鹽、維持血壓 <130/80 mmHg。
[➡ 心臟內科掛號](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30100A&flag=first)
""")

        if "中風" in chronic_illnesses:
            st.info("📌 中風患者注意")
            st.markdown("""
- 須預防再次中風與相關併發症。
- 建議服藥規律、控制三高。
[➡ 神經內科掛號](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30900A&flag=first)
""")

        if frail_score > 2:
            st.info("🏃‍♂️ 衰弱改善建議")
            st.markdown("""
- 補充蛋白質、維生素 D，避免體重下降。
- 參與運動班或復健活動。
[➡ 復健科掛號](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=31700A&flag=first)
""")

        if smoking_freq > 5 or drinking_freq > 3 or chewing_freq > 3 or drug_freq > 0:
            st.info("🚭 高風險生活習慣")
            st.markdown("""
- 抽菸：易造成心肺與腎臟負擔。
- 飲酒：長期傷肝腎，增加中風機率。
- 嚼檳榔：高風險致癌，應儘快戒除。
- 藥物濫用：傷害神經、肝腎，需專業戒治。
[➡ 家庭醫學科衛教與戒除輔導](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=31300A&flag=first)
""")

    st.subheader("📄 最近五筆紀錄")
    st.dataframe(df.tail(5))
