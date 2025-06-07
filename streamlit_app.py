import streamlit as st
import pandas as pd

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

def main():
    st.set_page_config(page_title="腎功能評估與衛教建議", page_icon="🩺")
    st.title("🩺 一般健康參數評估與衰弱風險")

    st.markdown("""
    此工具可協助您根據年齡、性別、肌酐數值、自填血壓與身高體重，預估腎功能 (eGFR)，
    並提供血壓、體重、腎功能及衰弱風險的個別衛教建議。
    """)

    with st.form("health_form"):
        st.header("🔢 請輸入您的基本資料")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("年齡 (歲)", min_value=1, max_value=120, value=65)
            sex = st.selectbox("生理性別", ["女性", "男性"])
            height = st.number_input("身高 (公分)", min_value=100.0, max_value=250.0, value=165.0)
        with col2:
            creatinine = st.number_input("肌酐值 (mg/dL)", min_value=0.1, max_value=15.0, value=1.0)
            sbp = st.number_input("收縮壓 SBP (mmHg)", min_value=80, max_value=250, value=130)
            dbp = st.number_input("舒張壓 DBP (mmHg)", min_value=40, max_value=150, value=85)
            weight = st.number_input("體重 (公斤)", min_value=30.0, max_value=200.0, value=70.0)

        st.header("💬 衰弱量表（請如實填寫）")
        frailty_items = {
            "是否在過去一年內體重無意減少超過 5 公斤？": st.checkbox("1️⃣ 體重是否在一年內無故減輕超過 5 公斤"),
            "是否覺得自己容易疲憊？": st.checkbox("2️⃣ 是否常覺得疲憊或無力"),
            "一週內是否從事低於 3 次運動？": st.checkbox("3️⃣ 是否每週運動次數少於 3 次"),
            "是否走路變慢，無法快速行走？": st.checkbox("4️⃣ 是否走路速度變慢"),
            "是否覺得握力變弱或提重物困難？": st.checkbox("5️⃣ 是否握力下降或提重物困難"),
        }

        submitted = st.form_submit_button("送出評估")

    if submitted:
        bmi = weight / (height / 100) ** 2
        egfr = calculate_egfr(age, creatinine, sex)
        frailty_score = sum(frailty_items.values())

        st.header("📊 評估結果")
        st.metric("eGFR (ml/min/1.73m²)", f"{egfr:.1f}")
        st.metric("BMI (kg/m²)", f"{bmi:.1f}")

        st.subheader("💡 衛教建議")

        # 血壓分析
        if sbp < 90 or dbp < 60:
            st.warning("血壓偏低")
            st.write("可能導致頭暈、跌倒風險，建議增加水分與鹽分攝取，避免突然起身，必要時就醫評估是否需藥物調整。")
        elif sbp >= 140 or dbp >= 90:
            st.warning("血壓偏高")
            st.write("建議減少鈉攝取（如少吃加工食品）、增加規律有氧運動、控制壓力，並依需要定期量測血壓。")
        else:
            st.info("血壓正常")
            st.write("請持續保持健康生活習慣，例如：均衡飲食、避免過鹹食物、規律運動與適當作息，以維持正常血壓。")

        # 體重（BMI）分析
        if bmi < 18.5:
            st.warning(f"體重過輕（BMI：{bmi:.1f}）")
            st.write("建議增加熱量與蛋白質攝取，如牛奶、豆製品、堅果等，並可搭配阻力訓練提升肌肉量。")
        elif bmi >= 27:
            st.warning(f"體重過重（BMI：{bmi:.1f}）")
            st.write("建議採取低油、低糖、高纖飲食，增加身體活動，設定健康減重目標，每週減少0.5～1公斤為宜。")
        else:
            st.info(f"體重正常（BMI：{bmi:.1f}）")
            st.write("請維持目前的飲食與運動習慣，並避免久坐與高熱量食物攝取。")

        # eGFR分析
        if egfr < 60:
            st.error(f"腎功能下降（eGFR：{egfr:.1f} ml/min/1.73m²）")
            st.write("建議減少蛋白質攝取、控制高血壓、限制鈉與磷攝取，並定期追蹤腎功能。必要時轉介腎臟專科。")
        else:
            st.info(f"腎功能正常（eGFR：{egfr:.1f} ml/min/1.73m²）")
            st.write("請持續保持飲水習慣、控制血壓與血糖、避免過度攝取蛋白質與止痛藥，以預防腎功能惡化。")

        # 衰弱量表結果
        st.subheader("🧓 衰弱風險分析")
        if frailty_score == 0:
            st.success("您目前無衰弱徵象")
            st.write("請持續規律運動、均衡飲食、與維持社會參與，以預防衰弱。")
        elif frailty_score <= 2:
            st.warning(f"您可能處於「前衰弱」狀態（分數：{frailty_score}）")
            st.write("建議增加身體活動、注意營養攝取、並定期評估身體功能。")
        else:
            st.error(f"有明顯衰弱徵象（分數：{frailty_score}）")
            st.write("建議就醫評估、規劃營養與運動介入方案，並注意跌倒與失能風險。")

        # 個別衰弱項目衛教
        st.subheader("📌 各項衰弱徵象與建議")

        if frailty_items["是否在過去一年內體重無意減少超過 5 公斤？"]:
            st.warning("❗ 體重有明顯減輕")
            st.write("建議增加蛋白質與熱量攝取，並諮詢營養師，排除潛在疾病如癌症或腸胃問題。")

        if frailty_items["是否覺得自己容易疲憊？"]:
            st.warning("❗ 經常感到疲憊")
            st.write("可能與睡眠品質、營養或心理壓力相關。建議改善作息、均衡飲食，必要時心理諮詢。")

        if frailty_items["一週內是否從事低於 3 次運動？"]:
            st.warning("❗ 活動量不足")
            st.write("建議每週進行至少 150 分鐘中等強度運動，如快走、有氧操、太極等。")

        if frailty_items["是否走路變慢，無法快速行走？"]:
            st.warning("❗ 行走變慢")
            st.write("可透過肌力與平衡訓練提升步態穩定性，預防跌倒，例如進行腿部阻力訓練。")

        if frailty_items["是否覺得握力變弱或提重物困難？"]:
            st.warning("❗ 握力下降")
            st.write("建議使用彈力球、重量訓練或日常提物等方式訓練前臂與手部肌肉。")

if __name__ == '__main__':
    main()
