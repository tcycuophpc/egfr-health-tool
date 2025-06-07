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
    st.title("🩺 一般健康參數評估與衛教")
    st.markdown("""
    此工具可協助您根據年齡、性別、肌酐數值、自填血壓與身高體重，預估腎功能 (eGFR)，
    並提供血壓、體重與腎功能的個別衛教建議。
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

        submitted = st.form_submit_button("送出評估")

    if submitted:
        bmi = weight / (height / 100) ** 2
        egfr = calculate_egfr(age, creatinine, sex)

        st.header("📊 評估結果")
        st.metric("eGFR (ml/min/1.73m²)", f"{egfr:.1f}")
        st.metric("BMI (kg/m²)", f"{bmi:.1f}")

        st.subheader("💡 衛教建議")

        # 血壓分析
        if sbp >= 140 or dbp >= 90:
            st.warning("血壓偏高")
            st.write("建議減少鈉攝取（如少吃加工食品）、增加規律有氧運動、控制壓力，並依需要定期量測血壓。")
        else:
            st.info("血壓正常")
            st.write("請持續保持健康生活習慣，例如：均衡飲食、避免過鹹食物、規律運動與適當作息，以維持正常血壓。")

        # 體重（BMI）分析
        if bmi >= 27:
            st.warning(f"體重過重（BMI：{bmi:.1f}）")
            st.write("建議採取低油、低糖、高纖飲食，增加身體活動，設定健康減重目標，每週減少0.5～1公斤為宜。")
        else:
            st.info(f"體重正常（BMI：{bmi:.1f}）")
            st.write("請維持目前的飲食與運動習慣，並避免久坐與高熱量食物攝取。可定期監測體重與BMI以掌握健康狀況。")

        # eGFR分析
        if egfr < 60:
            st.error(f"腎功能下降（eGFR：{egfr:.1f} ml/min/1.73m²）")
            st.write("建議減少蛋白質攝取、控制高血壓、限制鈉與磷攝取，並定期追蹤腎功能。必要時轉介腎臟專科。")
        else:
            st.info(f"腎功能正常（eGFR：{egfr:.1f} ml/min/1.73m²）")
            st.write("請持續保持飲水習慣、控制血壓與血糖、避免過度攝取蛋白質與止痛藥，以預防腎功能惡化。")

if __name__ == '__main__':
    main()
