# 完整版 Streamlit 健康評估 App（含管理者頁與進階圖表）
# 功能：登入、記錄管理、健康參數分析、eGFR、衰弱、生活習慣、圖表儲存、管理者頁面

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import datetime

USER_DATA_FILE = "user_data.json"
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

st.image("護理系圖檔.png", caption="中國醫藥大學護理學系 (School of Nursing, CMU)", use_container_width=True)

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
        st.bar_chart(df_all.groupby("user_id")["egfr"].mean(), use_container_width=True)

        st.subheader("整體 eGFR 變化趨勢")
        egrp = df_all.pivot_table(index="date", values="egfr", aggfunc="mean")
        st.line_chart(egrp, use_container_width=True)

        st.subheader("依生活習慣分析")
        if "drinking" in df_all.columns:
            st.bar_chart(df_all.groupby("drinking")["egfr"].mean())
        if "smoking" in df_all.columns:
            st.bar_chart(df_all.groupby("smoking")["egfr"].mean())
    else:
        st.info("目前無使用者紀錄")
    st.stop()

st.title("🔍 健康評估問卷填寫")
now = datetime.datetime.now().strftime("%Y-%m-%d")

col1, col2 = st.columns(2)
age = col1.number_input("年齡", min_value=1, max_value=120, value=25)
height = col1.number_input("身高 (cm)", min_value=100, max_value=250, value=170)
weight = col1.number_input("體重 (kg)", min_value=30, max_value=200, value=70)
bp = col1.text_input("血壓 (如 120/80)")
bmi = round(weight / ((height/100)**2), 1)

sleep_hours = col2.slider("平均睡眠時數 (小時)", 0, 15, 7)
body_fat = col2.slider("體脂率 (%)", 5, 50, 25)
egfr = col2.number_input("eGFR (mL/min/1.73㎡)", min_value=0.0, max_value=150.0, value=85.0)

st.subheader("簡易衰弱測驗")
f = st.radio("是否經常感到疲憊？", ["是", "否"], horizontal=True)
r = st.radio("近半年體重是否無故下降？", ["是", "否"], horizontal=True)
a = st.radio("是否難以走完一段距離（如 400 公尺）？", ["是", "否"], horizontal=True)
i = st.radio("是否無法提起重物 (如米袋、購物袋)？", ["是", "否"], horizontal=True)
l = st.radio("是否有跌倒經驗？", ["是", "否"], horizontal=True)
frail_score = [f, r, a, i, l].count("是")

st.subheader("生活習慣")
drinking = st.selectbox("飲酒頻率", ["不喝", "偶爾", "經常"])
smoking = st.selectbox("是否抽菸", ["不抽", "已戒菸", "目前仍抽"])
betel = st.selectbox("是否嚼檳榔", ["否", "是"])
drug = st.selectbox("是否有藥物濫用經驗", ["否", "目前有"])
supplement = st.radio("是否規律使用保健食品/中藥？", ["是", "否"], horizontal=True)

if st.button("提交並儲存記錄"):
    rec = {
        "date": now,
        "age": age,
        "height": height,
        "weight": weight,
        "bmi": bmi,
        "bp": bp,
        "sleep": sleep_hours,
        "body_fat": body_fat,
        "egfr": egfr,
        "frail": frail_score,
        "drinking": drinking,
        "smoking": smoking,
        "betel": betel,
        "drug": drug,
        "supplement": supplement
    }
    user_data = load_user_data()
    user_data[user_id]["records"].append(rec)
    save_user_data(user_data)
    st.success("已儲存")

    df = pd.DataFrame(user_data[user_id]["records"])
    chart_path = os.path.join(CHART_DIR, f"{user_id}_chart.png")
    fig, ax = plt.subplots()
    df.tail(5).plot(x="date", y=["egfr", "bmi", "sleep", "body_fat"], ax=ax, marker="o")
    plt.title("健康指標趨勢圖")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path)
    st.image(chart_path)

    st.subheader("健康建議")
    if egfr >= 90:
        st.success("eGFR 正常，建議每年定期追蹤腎功能並維持良好生活習慣。")
    elif 60 <= egfr < 90:
        st.warning("eGFR 有輕度下降，建議增加水分攝取並避免高鹽高蛋白飲食。")
    elif 30 <= egfr < 60:
        st.error("eGFR 明顯下降，建議盡快轉診腎臟科門診評估。")
        st.markdown("👉 [預約腎臟科門診](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30500A&flag=first)")
    else:
        st.error("eGFR 嚴重下降，請立即就醫處理。")
        st.markdown("🚨 [緊急掛號 - 腎臟專科](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30500A&flag=first)")

    if bmi >= 27:
        st.warning("您的 BMI 顯示體重過重，建議控制體重以降低高血壓、糖尿病與腎病風險。")
        st.markdown("👉 [預約體重控制門診](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30500A&flag=first)")
    elif bmi < 18.5:
        st.info("您的 BMI 偏低，建議檢視營養攝取並尋求醫師建議。")
        st.markdown("👉 [預約營養門診](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30500A&flag=first)")
