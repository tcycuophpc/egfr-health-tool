# 總結版本說明：
# 這段 Streamlit 程式碼建立一個完整的健康評估應用，包含使用者登入、個人資料輸入、腎功能與衰弱評估、
# 給予個別化的衛教建議，並支援記錄儲存與趨勢圖展示。資料以 JSON 儲存，圖表以 PNG 格式儲存。

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import datetime

# 檔案與資料夾設定
USER_DATA_FILE = "user_data.json"
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

# 顯示護理系圖檔
st.image("img.png", caption="中國醫藥大學護理學系 (School of Nursing, CMU)", use_container_width=True)

# 載入與儲存使用者資料的函數
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 使用者登入介面（以身分證後四碼 + 生日四碼辨識）
def user_login():
    st.title("健康評估登入系統")
    id_last4 = st.text_input("身分證後四碼")
    birth4 = st.text_input("生日四碼 (MMDD)")
    if st.button("登入"):
        if len(id_last4) == 4 and len(birth4) == 4:
            user_id = id_last4 + birth4
            user_data = load_user_data()
            if user_id not in user_data:
                user_data[user_id] = {"records": []}
                save_user_data(user_data)
            st.session_state["user_id"] = user_id
            st.success("登入成功")
        else:
            st.warning("請正確輸入共 8 碼")

# 防呆：如果不是透過 streamlit run 執行，阻止繼續
if not st.runtime.exists():
    st.error("請使用 'streamlit run 檔案名.py' 啟動程式，不要用 python 直接執行。")
    st.stop()

# 若尚未登入，強制登入
if "user_id" not in st.session_state:
    user_login()
    st.stop()

# 主流程
user_id = st.session_state["user_id"]
user_data = load_user_data()
records = user_data[user_id].get("records", [])

# 健康資料輸入與分析
st.title("腎功能與健康參數評估")
name = st.text_input("姓名")
age = st.number_input("年齡", 1, 120)
height = st.number_input("身高(cm)", 100.0, 250.0)
weight = st.number_input("體重(kg)", 30.0, 200.0)
bmi = round(weight / ((height / 100) ** 2), 1)
st.write(f"BMI: {bmi}")

body_fat = st.slider("體脂率(%)", 5.0, 50.0)
sbp = st.number_input("收縮壓", 80, 200)
dbp = st.number_input("舒張壓", 40, 130)
sleep = st.select_slider("平均每日睡眠時間(小時)", options=[i * 0.5 for i in range(0, 25)])
eat = st.radio("一週蔬果攝取情況", ["均衡", "偏少", "非常少"])
egfr = st.number_input("eGFR(ml/min/1.73m²)", 1.0, 120.0)

# 生活習慣
st.subheader("生活習慣")
smoking = st.radio("是否有抽菸習慣", ["是", "否"])
drinking = st.radio("是否有喝酒習慣", ["是", "否"])
chewing = st.radio("是否有嚼檳榔習慣", ["是", "否"])
drugs = st.radio("是否有藥物濫用經驗", ["是", "否"])
meds = st.radio("是否有規律服用藥物、中藥或保健食品", ["是", "否"])

# FRAIL 量表
st.subheader("FRAIL 衰弱量表")
f = st.radio("疲憊(Fatigue)", ["是", "否"])
r = st.radio("抗阻力(Resistance)", ["是", "否"])
a = st.radio("行走能力(Ambulation)", ["是", "否"])
i = st.radio("慢性病(Illnesses)", ["是", "否"])
l = st.radio("體重減輕(Loss of weight)", ["是", "否"])
frail_score = [f, r, a, i, l].count("是")
frail_status = "健壯" if frail_score == 0 else "前衰弱" if frail_score in [1, 2] else "衰弱"

# 給予分析建議與衛教提醒
st.header("衛教建議與狀況分析")
feedback = []

if egfr >= 90:
    feedback.append("eGFR 正常，建議每年定期追蹤腎功能並維持良好生活習慣。")
elif 60 <= egfr < 90:
    feedback.append("eGFR 有輕度下降，建議增加水分攝取，減少高蛋白、高鹽食物攝取。")
elif 30 <= egfr < 60:
    feedback.append("eGFR 明顯下降，建議轉診腎臟科門診評估並持續控制血壓、血糖。")
else:
    feedback.append("eGFR 嚴重下降，請立即就醫，建議掛號：\n[中國醫藥大學附設醫院腎臟科掛號](https://www.cmuh.cmu.edu.tw/OnlineAppointment/AppointmentByDivision)")

if frail_status != "健壯":
    feedback.append(f"FRAIL 量表顯示 \"{frail_status}\"，建議增加日常活動與均衡飲食。")
else:
    feedback.append("衰弱量表顯示健壯，請持續保持良好體能。")

if body_fat > 30:
    feedback.append("體脂過高可能增加慢性病風險，建議改善飲食與運動。")
if sleep < 6:
    feedback.append("睡眠時間過短，建議每晚睡滿 6-8 小時。")
if eat != "均衡":
    feedback.append("蔬果攝取不均，建議每日至少五蔬果。")

if smoking == "是":
    feedback.append("建議戒菸以降低心肺與腎臟風險。")
if drinking == "是":
    feedback.append("建議節制飲酒避免肝腎損傷。")
if chewing == "是":
    feedback.append("嚼檳榔有致癌風險，建議儘早戒除。")
if drugs == "是":
    feedback.append("藥物濫用對健康有重大傷害，建議尋求專業協助。")
if meds == "是":
    feedback.append("請定期與醫療人員確認所服藥物與保健品是否合適。")

for item in feedback:
    st.info(item)

# 儲存紀錄按鈕與折線圖展示
if st.button("儲存本次紀錄"):
    today = datetime.date.today().isoformat()
    record = {
        "date": today, "egfr": egfr, "sleep": sleep, "body_fat": body_fat,
        "frail": frail_status, "bp": f"{sbp}/{dbp}", "weight": weight, "bmi": bmi
    }
    records.append(record)
    user_data[user_id]["records"] = records[-10:]
    save_user_data(user_data)
    st.success("紀錄已儲存")

# 健康趨勢圖
if records:
    df = pd.DataFrame(records)
    chart_path = os.path.join(CHART_DIR, f"{user_id}_chart.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    df_plot = df.set_index("date")
    df_plot[["egfr", "sleep", "body_fat", "weight"]].plot(ax=ax)
    plt.title("健康趨勢圖")
    plt.ylabel("數值")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(chart_path)
    st.image(chart_path, caption="健康趨勢圖")

# 近期三筆資料
st.subheader("近期三筆紀錄")
if records:
    st.table(pd.DataFrame(records[-3:]))
