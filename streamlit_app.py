import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calculate_egfr(age, sex, scr):
    # eGFR 計算，採用 CKD-EPI 簡化版本（mg/dL）
    if sex == "男性":
        k = 0.9
        alpha = -0.411
        gender_factor = 1
    else:
        k = 0.7
        alpha = -0.329
        gender_factor = 1.018

    scr_k = scr / k
    eGFR = 141 * min(scr_k, 1) ** alpha * max(scr_k, 1) ** (-1.209) * (0.993 ** age) * gender_factor
    return eGFR

def egfr_frailty_risk(egfr):
    # eGFR 衰弱狀態判斷
    if egfr >= 90:
        status = "正常"
        risk = "低風險"
    elif 60 <= egfr < 90:
        status = "輕度下降"
        risk = "中低風險"
    elif 45 <= egfr < 60:
        status = "中度下降"
        risk = "中風險"
    elif 30 <= egfr < 45:
        status = "中重度下降"
        risk = "高風險"
    else:
        status = "重度下降"
        risk = "極高風險"
    return status, risk

def health_education(drinking, smoking, betel_nut, drug_use, stress, sleep_hours, bmi):
    st.subheader("📚 衛教建議")
    if drinking != "不喝":
        st.info(
            "💡 建議減少飲酒，過量飲酒可能導致肝臟疾病（肝硬化、肝癌）、高血壓、心律不整及多種癌症。"
            "適量飲酒可降低風險，建議女性每日酒精不超過1份（約10克酒精），男性不超過2份。"
            "飲酒也會影響睡眠品質與認知功能。"
        )
    else:
        st.info("💡 保持不飲酒有助肝臟健康及減少慢性病風險。")

    if smoking == "目前仍抽":
        st.info(
            "💡 建議戒菸，吸菸會大幅增加肺癌、口腔癌、心血管疾病、中風及慢性阻塞性肺病風險。"
            "戒菸後心肺功能可逐步改善，並減少二手菸危害家人。"
            "可尋求戒菸門診或使用戒菸輔助工具。"
        )
    elif smoking == "已戒菸":
        st.info("💡 已戒菸非常好！請持續維持，避免復吸。")

    if betel_nut != "否":
        st.info(
            "💡 嚼檳榔與口腔癌、牙周病及消化系統疾病高度相關，嚼檳榔會導致口腔黏膜病變。"
            "建議盡早戒除，並定期口腔檢查。"
        )
    else:
        st.info("💡 不嚼檳榔可降低口腔癌與相關疾病風險。")

    if drug_use == "目前有":
        st.info(
            "💡 藥物濫用會引發神經、肝腎、心理及社會功能受損，嚴重影響健康與生活。"
            "建議尋求專業治療資源，例如毒品危害防制中心、戒癮門診。"
        )
    elif drug_use == "過去有":
        st.info("💡 曾有藥物濫用史，請持續保持良好生活習慣與定期追蹤心理健康。")

    if stress >= 7:
        st.info(
            "💡 長期壓力會影響免疫系統、腸胃及心血管健康，可能導致焦慮、憂鬱。"
            "建議透過冥想、運動、心理諮詢等方式紓解壓力，保持充足睡眠。"
        )
    else:
        st.info("💡 壓力管理良好，有助身心健康。")

    if sleep_hours < 5:
        st.info(
            "💡 睡眠不足會影響記憶力、免疫力與代謝功能，增加慢性疾病風險，建議每天睡眠6至9小時。"
        )
    elif sleep_hours > 10:
        st.info(
            "💡 睡眠過多可能與抑鬱症、代謝症候群有關，建議維持規律、適度的睡眠時間。"
        )
    else:
        st.info("💡 睡眠時間適中，有助恢復體力與促進健康。")

    if bmi < 18.5:
        st.info(
            "💡 體重過輕可能導致營養不良、免疫力下降與骨質疏鬆，建議補充營養、適度增加蛋白質攝取與諮詢營養師。"
        )
    elif bmi >= 24 and bmi < 27:
        st.info(
            "💡 體重過重，建議透過均衡飲食與規律運動控制體重，預防代謝疾病。"
        )
    elif bmi >= 27:
        st.info(
            "💡 體重過高會增加代謝症候群、心血管疾病與糖尿病風險，建議積極控制體重與尋求專業營養諮詢。"
        )
    else:
        st.info("💡 體重正常，請持續保持良好飲食與運動習慣。")

def plot_health_line_chart(ideal_values, actual_values):
    df = pd.DataFrame({
        "項目": list(ideal_values.keys()),
        "理想值": list(ideal_values.values()),
        "實際值": list(actual_values.values())
    })

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(df))

    ax.plot(x, df["理想值"], label="理想值", color="green", linestyle='--', marker='o')
    ax.plot(x, df["實際值"], label="實際值", color="blue", linestyle='-', marker='o')

    for i in x:
        ax.text(i, df["實際值"][i] + 0.3, f'{df["實際值"][i]:.1f}', ha='center', fontsize=9, color='blue')
        ax.text(i, df["理想值"][i] - 0.8, df["項目"][i], ha='center', fontsize=9, color='green', rotation=45)

    ax.set_xticks(x)
    ax.set_xticklabels(df["項目"], rotation=45, ha='right')
    ax.set_ylabel("指數/數值")
    ax.set_xlabel("健康項目")
    ax.set_title("健康指標折線圖（理想值 vs 實際值）")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

def main():
    st.title("健康評估與 eGFR 批次預測分析工具")

    with st.form("health_form"):
        age = st.number_input("年齡", min_value=0, max_value=120, value=30)
        sex = st.selectbox("性別", ["男性", "女性"])
        scr = st.number_input("血清肌酸酐（mg/dL）", min_value=0.1, max_value=20.0, value=1.0, format="%.2f")

        drinking = st.selectbox("飲酒習慣", ["不喝", "偶爾喝", "常喝"])
        smoking = st.selectbox("抽菸狀況", ["不抽菸", "已戒菸", "目前仍抽"])
        betel_nut = st.selectbox("嚼檳榔", ["否", "偶爾", "常嚼"])
        drug_use = st.selectbox("藥物濫用", ["否", "過去有", "目前有"])
        stress = st.slider("壓力程度（1-10）", 1, 10, 5)
        sleep_hours = st.slider("每日睡眠時數", 0, 15, 7)

        weight = st.number_input("體重(公斤)", min_value=20.0, max_value=200.0, value=70.0, format="%.1f")
        height = st.number_input("身高(公分)", min_value=100.0, max_value=250.0, value=170.0, format="%.1f")

        submitted = st.form_submit_button("計算分析")

    if submitted:
        bmi = weight / ((height / 100) ** 2)
        eGFR = calculate_egfr(age, sex, scr)
        status, risk = egfr_frailty_risk(eGFR)

        st.header("📊 分析結果")
        st.write(f"您的 eGFR：**{eGFR:.2f} ml/min/1.73㎡**")
        st.write(f"腎功能狀態：**{status}**，對應衰弱風險為：**{risk}**")
        st.write(f"BMI：**{bmi:.1f}**")

        ideal_values = {
            "eGFR": 90,
            "BMI": 22,
            "睡眠(小時)": 7,
            "壓力(1-10)": 3
        }

        actual_values = {
            "eGFR": eGFR,
            "BMI": bmi,
            "睡眠(小時)": sleep_hours,
            "壓力(1-10)": stress
        }

        plot_health_line_chart(ideal_values, actual_values)

        health_education(drinking, smoking, betel_nut, drug_use, stress, sleep_hours, bmi)

if __name__ == "__main__":
    main()
