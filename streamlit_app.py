import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# 根據 eGFR 判斷腎功能狀態與衰弱風險
def egfr_status(egfr):
    if egfr >= 90:
        return "正常腎功能", 0
    elif 60 <= egfr < 90:
        return "輕度腎功能減退", 1
    elif 30 <= egfr < 60:
        return "中度腎功能減退", 2
    elif 15 <= egfr < 30:
        return "重度腎功能減退", 3
    else:
        return "末期腎病", 4

# 檢查是否為整數或半整數
def is_int_or_half(num):
    return (num * 2) == int(num * 2)

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

        sleep_hours = st.number_input(
            "平均每日睡眠時間 (小時) - 僅限整數或半整數",
            min_value=0.0,
            max_value=12.0,
            step=0.5,
            format="%.1f",
            help="請輸入整數或半整數 (例如 6, 6.5, 7, 7.5)"
        )

        submitted = st.form_submit_button("送出分析")

    if submitted:
        if not is_int_or_half(sleep_hours):
            st.error("睡眠時間輸入錯誤，請輸入整數或半整數（例如 6, 6.5, 7, 7.5）")
            return

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
        egfr_state, egfr_frailty_score = egfr_status(egfr)

        lifestyle_risk_score = (
            int(drinking != "不喝") +
            int(smoking == "目前仍抽") +
            int(betel_nut != "否") +
            int(drug_use == "目前有") +
            int(stress >= 7) +
            int(sleep_hours < 5 or sleep_hours > 10)
        )

        total_frailty_score = score + egfr_frailty_score

        st.header("📊 分析結果")
        st.metric("eGFR (ml/min/1.73m²)", f"{egfr:.1f} ({egfr_state})")
        st.metric("BMI (kg/m²)", f"{bmi:.1f}")
        st.metric("衰弱評估", f"{frail_status}（Fried Criteria分數：{score}）")
        st.metric("eGFR 腎功能衰弱風險分數", f"{egfr_frailty_score} / 4")
        st.metric("生活習慣風險分數", f"{lifestyle_risk_score} / 6")
        st.metric("綜合衰弱風險分數", f"{total_frailty_score} / 10")

        st.subheader("📉 健康狀態折線圖（與理想值比較）")
        ideal_values = {
            '年齡': 65,
            'BMI': 22,
            '收縮壓 (SBP)': 120,
            '舒張壓 (DBP)': 80,
            'eGFR': 90,
            '壓力': 3,
            '睡眠 (小時)': 7.5,
        }
        actual_values = {
            '年齡': age,
            'BMI': bmi,
            '收縮壓 (SBP)': sbp,
            '舒張壓 (DBP)': dbp,
            'eGFR': egfr,
            '壓力': stress,
            '睡眠 (小時)': sleep_hours,
        }

        df_plot = pd.DataFrame({
            '指標': list(ideal_values.keys()) * 2,
            '類型': ['理想值'] * len(ideal_values) + ['實際值'] * len(actual_values),
            '數值': list(ideal_values.values()) + list(actual_values.values())
        })

        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_plot, x='指標', y='數值', hue='類型', marker='o', palette=['green', 'red'])
        plt.title("健康指標折線圖")
        plt.xlabel("健康指標")
        plt.ylabel("數值")
        plt.grid(True)
        for i, row in df_plot.iterrows():
            plt.text(i % len(ideal_values), row['數值'], f"{row['數值']:.1f}", ha='center', va='bottom' if row['類型']=='實際值' else 'top')
        st.pyplot(plt)

        st.subheader("📌 建議就醫科別與掛號連結（中國醫藥大學附設醫院台中總院）")
        if egfr < 60:
            st.markdown("- 腎臟內科 [掛號連結](https://www.cmuh.cmu.edu.tw/service/onlineappointment)")
        if sbp >= 140 or dbp >= 90:
            st.markdown("- 心臟內科 [掛號連結](https://www.cmuh.cmu.edu.tw/service/onlineappointment)")
        if bmi >= 27 or bmi < 18.5:
            st.markdown("- 新陳代謝科或營養師諮詢 [掛號連結](https://www.cmuh.cmu.edu.tw/service/onlineappointment)")
        if frail_status == "衰弱":
            st.markdown("- 老年醫學科或復健科 [掛號連結](https://www.cmuh.cmu.edu.tw/service/onlineappointment)")
        if drug_use == "目前有":
            st.markdown("- 精神科或藥癮治療中心 [掛號連結](https://www.cmuh.cmu.edu.tw/service/onlineappointment)")
        if smoking == "目前仍抽" or betel_nut != "否":
            st.markdown("- 戒菸門診、口腔外科或耳鼻喉科 [掛號連結](https://www.cmuh.cmu.edu.tw/service/onlineappointment)")

        st.subheader("📚 衛教建議")
        # eGFR 衛教
        if egfr >= 90:
            st.info("💡 您的腎功能正常，建議維持均衡飲食及適當運動，避免過量攝取高蛋白及鹽分。參考衛福部建議：健康腎臟，從生活做起。")
        elif 60 <= egfr < 90:
            st.warning("⚠️ 輕度腎功能減退，建議定期監測腎功能，避免使用對腎臟有害的藥物。衛福部提醒：早期發現，防止惡化。")
        elif 30 <= egfr < 60:
            st.error("❗ 中度腎功能減退，需嚴格控管血壓及血糖，並遵醫囑使用藥物。衛福部建議：慢性腎臟病患者應積極治療以延緩進展。")
        elif 15 <= egfr < 30:
            st.error("❗ 重度腎功能減退，建議積極就醫並遵從醫師指示進行治療。衛福部指出：重度腎臟病患者應考慮透析或其他療法。")
        else:
            st.error("❗ 末期腎病，請立即就醫。衛福部提醒：末期腎臟病需專業治療以維持生命。")

        # BMI 衛教
        if bmi < 18.5:
            st.info("💡 體重過輕可能導致免疫力下降與骨質疏鬆，建議補充營養並諮詢營養師。衛福部建議：均衡飲食、適度運動。")
        elif 18.5 <= bmi < 24:
            st.info("💡 體重正常，請持續保持健康生活習慣。衛福部建議：維持適當飲食與規律運動。")
        elif 24 <= bmi < 27:
            st.warning("⚠️ 體重過重，建議調整飲食與增加活動量。衛福部提醒：控制體重，預防代謝疾病。")
        else:
            st.error("❗ 肥胖，增加糖尿病與心血管疾病風險，請積極控制體重。衛福部建議：多運動、低熱量飲食。")

        # 血壓衛教
        if sbp < 120 and dbp < 80:
            st.info("💡 血壓正常，請持續良好生活習慣。衛福部建議：避免吸菸、均衡飲食。")
        elif 120 <= sbp < 140 or 80 <= dbp < 90:
            st.warning("⚠️ 血壓偏高，建議減少鹽分攝取與增加運動。衛福部提醒：控制血壓，預防心血管疾病。")
        else:
            st.error("❗ 高血壓，需遵照醫囑服藥並調整生活型態。衛福部建議：規律用藥、定期監測血壓。")

        # 壓力衛教
        if stress <= 3:
            st.info("💡 壓力適中，建議維持良好壓力管理。衛福部建議：充足休息與適度放鬆。")
        elif 4 <= stress <= 6:
            st.warning("⚠️ 壓力較大，建議嘗試運動與正念練習。衛福部提醒：壓力管理有助健康。")
        else:
            st.error("❗ 壓力過大，建議尋求心理諮詢或專業協助。衛福部建議：及早介入，避免憂鬱焦慮。")

        # 睡眠衛教
        if 6 <= sleep_hours <= 8:
            st.info("💡 睡眠充足，有助身體恢復。衛福部建議：保持規律作息。")
        elif sleep_hours < 6:
            st.warning("⚠️ 睡眠不足，可能影響身心健康。衛福部提醒：避免熬夜，創造良好睡眠環境。")
        else:
            st.warning("⚠️ 睡眠過多，可能反映健康問題。衛福部建議：如持續睡眠過多請就醫評估。")

        # 衰弱狀況衛教
        if frail_status == "無衰弱":
            st.info("💡 您目前無明顯衰弱跡象，請持續維持健康生活習慣。衛福部建議：多運動、多攝取蛋白質。")
        elif frail_status == "前衰弱":
            st.warning("⚠️ 您有部分衰弱徵兆，建議增加肌力訓練與營養攝取。衛福部提醒：早期介入可預防進一步惡化。")
        else:
            st.error("❗ 您有明顯衰弱，建議尋求醫療及復健團隊協助。衛福部建議：積極治療與持續追蹤。")

        st.info("更多資訊請參考衛福部網站：https://www.mohw.gov.tw/")

if __name__ == "__main__":
    main()
