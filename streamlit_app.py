import streamlit as st
import pandas as pd
import json
import os
import datetime
import numpy as np
import joblib

USER_DATA_FILE = "user_data.json"
MODEL_FILE = "egfr_model.pkl"
ADMIN_ACCOUNTS = ["12345678"]
os.makedirs("charts", exist_ok=True)

st.image("護理系圖檔.png", caption="中國醫藥大學護理學系 (School of Nursing, CMU)", use_container_width=True)

# 資料處理
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def user_login():
    st.title("健康評估登入系統")
    id_last4 = st.text_input("身分證後四碼")
    birth4 = st.text_input("生日四碼 (MMDD)")
    if st.button("登入"):
        if len(id_last4) == 4 and len(birth4) == 4:
            user_id = id_last4 + birth4
            user_data = load_user_data()
            if user_id in ADMIN_ACCOUNTS:
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

if "user_id" not in st.session_state:
    user_login()
    st.stop()

user_id = st.session_state["user_id"]
is_admin = st.session_state.get("is_admin", False)
user_data = load_user_data()

# 管理者頁面
if is_admin:
    st.title("📊 管理者總覽")
    all_records = []
    for uid, udata in user_data.items():
        for rec in udata.get("records", []):
            rec["user_id"] = uid
            all_records.append(rec)
    if all_records:
        df_all = pd.DataFrame(all_records)
        df_all["date"] = pd.to_datetime(df_all["date"])
        st.dataframe(df_all.sort_values("date", ascending=False))
        st.subheader("各使用者平均 eGFR")
        st.bar_chart(df_all.groupby("user_id")["egfr"].mean())
        st.subheader("整體 eGFR 趨勢")
        st.line_chart(df_all.groupby("date")["egfr"].mean())
    else:
        st.info("尚無任何紀錄")
    st.stop()

# 使用者頁面
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

st.subheader("生活習慣（次數輸入）")
smoking_freq = st.slider("每日抽菸支數", 0, 40)
drinking_freq = st.slider("每週飲酒次數", 0, 14)
chewing_freq = st.slider("每日嚼檳榔次數", 0, 20)
drug_freq = st.slider("每月藥物濫用次數", 0, 30)
supp_freq = st.slider("每日保健品使用次數", 0, 10)

st.subheader("慢性病史")
chronic_illnesses = st.multiselect("請勾選曾罹患的慢性病", ["糖尿病", "高血壓", "中風", "其他"])
chronic_count = len(chronic_illnesses)

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
    user_data[user_id]["records"].append(record)
    user_data[user_id]["records"] = user_data[user_id]["records"][-10:]
    save_user_data(user_data)
    st.success("✅ 紀錄已儲存")

# 載入模型與預測
model = joblib.load(MODEL_FILE) if os.path.exists(MODEL_FILE) else None
predicted_egfr = None

if model:
    input_data = [[
        age, bmi, sbp, dbp,
        smoking_freq, drinking_freq, chewing_freq,
        drug_freq, supp_freq, chronic_count,
        frail_score,
        int("糖尿病" in chronic_illnesses),
        int("高血壓" in chronic_illnesses),
        int("中風" in chronic_illnesses)
    ]]
    predicted_egfr = model.predict(input_data)[0]
    st.metric("預測下一次 eGFR", f"{predicted_egfr:.2f} ml/min/1.73m²")
    st.caption("📅 預測基準時間：下一次 eGFR 為三個月後的推估值")
    future_date = (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    st.write(f"🔮 預估日期：**{future_date}**")
    st.write(f"🧪 預估腎功能 (eGFR)：**{predicted_egfr:.2f} ml/min/1.73m²**")

    if predicted_egfr < 60:
        st.warning("⚠️ 預測結果顯示您的腎功能可能持續低於標準值，建議持續監測並諮詢專業醫師。")
    else:
        st.info("✅ 預測結果良好，請持續維持健康生活習慣與定期追蹤。")

    # 模擬未來趨勢
    future_dates = [datetime.date.today() + datetime.timedelta(days=90 * i) for i in range(1, 7)]
    future_egfrs = [predicted_egfr * (0.97 ** i) for i in range(6)]  # 每三個月下降 3%
    future_df = pd.DataFrame({
        "date": future_dates,
        "預測eGFR": future_egfrs
    })
    st.subheader("📈 未來 18 個月 eGFR 預測趨勢")
    st.line_chart(future_df.set_index("date"))

# 趨勢與歷史紀錄
records = user_data.get(user_id, {}).get("records", [])
if records:
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["predicted_egfr"] = df["egfr"].ewm(span=2).mean()
    st.subheader("📉 過去 eGFR 與趨勢")
    st.line_chart(df[["egfr", "predicted_egfr"]].tail(10))
    st.subheader("📄 最近五筆紀錄")
    st.dataframe(df.tail(5))
