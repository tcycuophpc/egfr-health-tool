import streamlit as st
import pandas as pd
import seaborn as sns

# 計算 eGFR
def calculate_egfr(age, creatinine, sex):
    if sex == '女性':
        k = 0.7
        a = -0.329
        gender_factor = 1.018
    else:
        k = 0.9
        a = -0.411
        gender_factor = 1
    egfr = 141 * min(creatinine / k, 1) ** a * max(creatinine / k, 1) ** -1.209 * 0.993 ** age * gender_factor
    return egfr

# 預估衰弱分數
def frailty_score(inputs):
    score = 0
    if inputs['grip_strength'] == '無力':
        score += 1
    if inputs['slow_walk'] == '是':
        score += 1
    if inputs['weight_loss'] == '是':
        score += 1
    if inputs['fatigue'] == '是':
        score += 1
    if inputs['activity_level'] == '低':
        score += 1
    return score

# 衰弱程度對應
def frailty_level(score):
    if score == 0:
        return "無衰弱"
    elif score <= 2:
        return "前衰弱"
    else:
        return "衰弱"

# 主程式
def main():
    st.set_page_config(page_title="整合性健康評估工具", page_icon="🩺")
    st.title("🩺 健康評估、生活習慣分析與衰弱預測")

    with st.form("health_form"):
        st.header("📋 基本資料")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("年齡 (歲)", 1, 120, 65)
            sex = st.selectbox("生理性別", ["女性", "男性"])
            height = st.number_input("身高 (公分)", 100.0, 250.0, 165.0)
        with col2:
            weight = st.number_input("體重 (公斤)", 30.0, 200.0, 70.0)
            creatinine = st.number_input("肌酐值 (mg/dL)", 0.1, 15.0, 1.0)
            sbp = st.number_input("收縮壓 SBP", 80, 250, 130)
            dbp = st.number_input("舒張壓 DBP", 40, 150, 85)

        st.header("🧠 衰弱量表（Fried Criteria）")
        grip_strength = st.radio("握力是否無力", ["有力", "無力"])
        slow_walk = st.radio("步行是否遲緩", ["否", "是"])
        weight_loss = st.radio("最近是否無故體重減輕", ["否", "是"])
        fatigue = st.radio("是否經常感到疲倦", ["否", "是"])
        activity_level = st.radio("日常活動量", ["正常", "低"])

        st.header("💬 生活習慣")
        drinking = st.selectbox("飲酒習慣", ["不喝", "偶爾", "經常"])
        smoking = st.selectbox("抽菸習慣", ["不抽", "已戒菸", "目前仍抽"])
        betel_nut = st.selectbox("是否嚼檳榔", ["否", "偶爾", "經常"])
        drug_use = st.selectbox("藥物濫用史", ["無", "過去有", "目前有"])
        stress = st.slider("自評壓力程度 (0 = 無壓力, 10 = 非常大壓力)", 0, 10, 4)
        sleep_hours = st.slider("平均每日睡眠時間 (小時)", 0.0, 12.0, 7.0)

        submitted = st.form_submit_button("送出分析")

    if submitted:
        bmi = weight / (height / 100) ** 2
        egfr = calculate_egfr(age, creatinine, sex)
        score = frailty_score({
            'grip_strength': grip_strength,
            'slow_walk': slow_walk,
            'weight_loss': weight_loss,
            'fatigue': fatigue,
            'activity_level': activity_level,
        })
        frail_status = frailty_level(score)

        st.header("📊 分析結果")
        st.metric("eGFR (ml/min/1.73m²)", f"{egfr:.1f}")
        st.metric("BMI (kg/m²)", f"{bmi:.1f}")
        st.metric("衰弱評估", f"{frail_status}（分數：{score}）")

        st.subheader("📌 衛教建議")

        # 血壓
        if sbp < 90 or dbp < 60:
            st.warning("⚠️ 血壓偏低")
            st.write("注意頭暈、虛弱等症狀。請多補充水分、避免久站或突然起身，必要時諮詢醫師。")
        elif sbp >= 140 or dbp >= 90:
            st.warning("⚠️ 血壓偏高")
            st.write("建議減少鈉攝取、增加運動、避免菸酒與壓力，並定期追蹤血壓。")
        else:
            st.info("血壓正常，請維持良好生活習慣。")

        # 體重
        if bmi < 18.5:
            st.warning("⚠️ 體重過輕")
            st.write("可能營養不良或體力不足，請增加蛋白質與熱量攝取，必要時諮詢營養師。")
        elif bmi >= 27:
            st.warning("⚠️ 體重過重")
            st.write("建議控制飲食與增加運動，以減少代謝疾病風險。")
        else:
            st.info("體重正常，請持續保持。")

        # 腎功能
        if egfr < 60:
            st.error("❗ 腎功能下降")
            st.write("減少蛋白質攝取，避免使用止痛藥與高鈉食品，並定期追蹤腎功能。")
        else:
            st.info("腎功能正常，請保持充足水分與健康飲食。")

        # 衰弱衛教
        if frail_status == "前衰弱":
            st.warning("⚠️ 您處於前衰弱狀態")
            st.write("建議增加日常活動量、維持均衡飲食並監測身體變化。")
        elif frail_status == "衰弱":
            st.error("❗ 您已符合衰弱標準")
            st.write("建議多參與復能運動、營養補充、並考慮老年醫學門診評估。")

        # 生活習慣建議
        st.subheader("🍷 生活習慣建議")

        if drinking != "不喝":
            st.warning("建議限制酒精攝取，避免對肝臟與神經系統造成傷害。")

        if smoking == "目前仍抽":
            st.warning("強烈建議戒菸以降低心肺與癌症風險。")

        if betel_nut != "否":
            st.warning("嚼檳榔會提高口腔癌風險，建議停止。")

        if drug_use == "目前有":
            st.error("⚠️ 目前有藥物濫用，建議儘速尋求專業協助。")

        if stress >= 7:
            st.warning("壓力偏高，建議尋找紓壓方式，如運動、冥想、諮詢心理師。")

        if sleep_hours < 5 or sleep_hours > 10:
            st.warning("睡眠時數異常，建議建立規律作息與睡前放鬆習慣。")
        else:
            st.info("睡眠時數正常，請持續保持良好睡眠品質。")

        # 衰弱風險圖示
        st.subheader("📉 衰弱風險圖示")
        fig, ax = plt.subplots()
        categories = ['體重', '血壓', '腎功能', '衰弱量表', '生活習慣']
        values = [
            1 if 18.5 <= bmi <= 27 else 0,
            1 if 90 <= sbp < 140 and 60 <= dbp < 90 else 0,
            1 if egfr >= 60 else 0,
            2 - score / 5,
            1 - (int(drinking != "不喝") + int(smoking == "目前仍抽") + int(betel_nut != "否") + int(drug_use == "目前有") + int(stress >= 7) + int(sleep_hours < 5 or sleep_hours > 10)) / 6
        ]
        ax.bar(categories, values, color=sns.color_palette("coolwarm", len(values)))
        ax.set_ylim(0, 1.2)
        ax.set_ylabel("健康指數")
        ax.set_title("各構面衰弱風險指標（越高越健康）")
        st.pyplot(fig)

if __name__ == '__main__':
    main()
