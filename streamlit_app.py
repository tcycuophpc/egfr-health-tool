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

        st.subheader("依衰弱指數風險")
        if "frail" in df_all.columns:
            frail_avg = df_all.groupby("frail")["egfr"].mean()
            st.bar_chart(frail_avg)

        st.subheader("eGFR 預測分析")
        if len(df_all) >= 2:
            df_sorted = df_all.sort_values("date")
            df_sorted["predicted_egfr"] = df_sorted["egfr"].ewm(span=2).mean()
            st.line_chart(df_sorted[["egfr", "predicted_egfr"]].tail(10))

            # 新增折線圖分析：近五筆資料的衰弱趨勢
            st.subheader("衰弱趨勢圖 (FRAIL 分數)")
            frail_trend = df_sorted[df_sorted["user_id"] == user_id].tail(5)
            if not frail_trend.empty:
                fig, ax = plt.subplots()
                ax.plot(frail_trend["date"], frail_trend["frail"], marker='o', linestyle='-')
                ax.set_title("近五筆 FRAIL 衰弱趨勢")
                ax.set_ylabel("衰弱分數")
                ax.set_xlabel("日期")
                ax.grid(True)
                st.pyplot(fig)

    else:
        st.info("目前無使用者紀錄")
    st.stop()

# 使用者頁面
st.title("使用者健康評估")
name = st.text_input("姓名")
age = st.number_input("年齡", 1, 120)
height = st.number_input("身高 (cm)", 100.0, 250.0)
weight = st.number_input("體重 (kg)", 30.0, 200.0)

bmi = round(weight / ((height / 100) ** 2), 1)
st.metric("BMI 指數", bmi)

sbp = st.slider("收縮壓 SBP", 80, 200)
dbp = st.slider("舒張壓 DBP", 40, 130)

egfr = st.number_input("eGFR(ml/min/1.73m²)", 1.0, 120.0)

st.subheader("生活習慣")
smoking = st.selectbox("是否抽菸", ["否", "偶爾", "每天"])
drinking = st.selectbox("是否喝酒", ["否", "偶爾", "經常"])
chewing = st.selectbox("是否嚼檳榔", ["否", "偶爾", "經常"])
drugs = st.selectbox("是否有藥物濫用", ["否", "曾經", "正在使用"])
meds = st.selectbox("是否規律服藥或使用保健品", ["否", "是"])

st.subheader("FRAIL 衰弱指標")
f = st.radio("Fatigue 疲憊感", ["是", "否"])
r = st.radio("Resistance 肌力減弱", ["是", "否"])
a = st.radio("Ambulation 行走困難", ["是", "否"])
i = st.radio("Illnesses 慢性病多於5種", ["是", "否"])
l = st.radio("Loss of weight 體重下降", ["是", "否"])

frail_score = [f, r, a, i, l].count("是")
frail_status = "健壯" if frail_score == 0 else "前衰弱" if frail_score in [1,2] else "衰弱"

st.write(f"FRAIL 總分：{frail_score}，目前狀態：{frail_status}")

feedback = []
if egfr >= 90:
    feedback.append("eGFR 正常，請持續良好生活習慣。")
elif egfr >= 60:
    feedback.append("eGFR 輕度下降，建議減少高鹽高蛋白食物並多喝水。")
elif egfr >= 30:
    feedback.append("eGFR 明顯下降，請掛號腎臟科門診： [腎臟科預約](https://www.cmuh.cmu.edu.tw/OnlineAppointment/DymSchedule?table=30500A&flag=first)")
else:
    feedback.append("eGFR 嚴重異常，應立即就醫，建議立即轉診腎臟科。")

if frail_status != "健壯":
    feedback.append(f"目前屬於 {frail_status}，請加強飲食與運動，提升身體功能。")

if bmi >= 27:
    feedback.append("BMI 偏高，可能增加慢性病風險，建議調整飲食與運動。")
elif bmi < 18.5:
    feedback.append("BMI 偏低，請確認營養攝取是否足夠。")

if sbp >= 140 or dbp >= 90:
    feedback.append("血壓偏高，建議定期量測與控制，必要時諮詢醫師。")
elif sbp <= 90 or dbp <= 60:
    feedback.append("血壓偏低，注意是否有頭暈、疲勞等症狀。")

if smoking != "否":
    feedback.append("抽菸會加重腎臟與心肺負擔，建議戒菸。")
if drinking != "否":
    feedback.append("飲酒過量會影響肝腎功能，建議節制飲酒。")
if chewing != "否":
    feedback.append("檳榔為一級致癌物，應儘快戒除。")
if drugs != "否":
    feedback.append("藥物濫用對健康危害極大，應立即尋求協助。")
if meds == "是":
    feedback.append("使用保健品或藥物時應與醫師確認，以避免交互作用。")

st.subheader("健康建議")
for item in feedback:
    st.info(item)

if st.button("儲存紀錄"):
    today = datetime.date.today().isoformat()
    record = {
        "date": today, "egfr": egfr, "sbp": sbp, "dbp": dbp, "bmi": bmi,
        "frail": frail_score, "frail_status": frail_status, "smoking": smoking,
        "drinking": drinking, "chewing": chewing, "drugs": drugs, "meds": meds
    }
    records = user_data[user_id].get("records", [])
    records.append(record)
    user_data[user_id]["records"] = records[-10:]
    save_user_data(user_data)
    st.success("紀錄已儲存")

if user_data[user_id].get("records"):
    df = pd.DataFrame(user_data[user_id]["records"])
    st.subheader("📈 近五次健康趨勢圖")
    if len(df) >= 2:
        fig, ax = plt.subplots(figsize=(8,5))
        df_plot = df.set_index("date")
        df_plot[["egfr", "bmi"]].plot(ax=ax)
        ax.set_title("eGFR 與 BMI 變化")
        ax.set_ylabel("數值")
        ax.grid(True)
        st.pyplot(fig)

    st.subheader("📄 最近五筆紀錄")
    st.dataframe(df.tail(5))
