import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 假設這些是輸入參數（你可改成表單輸入）
egfr = st.number_input("請輸入 eGFR (mL/min/1.73m²)", min_value=0.0, max_value=150.0, value=85.0)
bmi = st.number_input("請輸入 BMI", min_value=10.0, max_value=50.0, value=22.0)
frail_score = st.slider("請輸入衰弱分數 (0-5)", 0, 5, 1)

drinking = st.selectbox("飲酒狀況", ["不喝", "偶爾", "經常"])
smoking = st.selectbox("抽菸狀況", ["不抽", "已戒菸", "目前仍抽"])
betel_nut = st.selectbox("嚼檳榔", ["否", "是"])
drug_use = st.selectbox("藥物濫用", ["否", "目前有"])
stress = st.slider("壓力指數 (0-10)", 0, 10, 3)
sleep_hours = st.slider("平均睡眠時間 (小時)", 0, 15, 7)

st.title("健康評估與衛教建議系統")

# 衰弱判斷
if frail_score <= 1:
    frail_status = "無衰弱"
elif frail_score <= 3:
    frail_status = "前衰弱"
else:
    frail_status = "衰弱"

# eGFR 標準與狀況
def egfr_status(egfr):
    if egfr >= 90:
        return "正常腎功能"
    elif egfr >= 60:
        return "輕度腎功能減退"
    elif egfr >= 30:
        return "中度腎功能減退"
    else:
        return "重度腎功能減退"

egfr_state = egfr_status(egfr)

# 折線圖數據示例，這邊用固定假資料，可替換成實際輸入歷史數據
data = pd.DataFrame({
    '時間': ['1月', '2月', '3月', '4月', '5月'],
    'eGFR': [90, 88, 85, 83, egfr],
    'BMI': [22, 22.5, 22.8, 23, bmi],
    '壓力指數': [4, 5, 3, 4, stress],
    '睡眠時數': [7, 6, 7, 8, sleep_hours]
})

# 畫折線圖
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data['時間'], data['eGFR'], marker='o', label='eGFR', color='green')
ax.plot(data['時間'], data['BMI'], marker='o', label='BMI', color='blue')
ax.plot(data['時間'], data['壓力指數'], marker='o', label='壓力指數', color='orange')
ax.plot(data['時間'], data['睡眠時數'], marker='o', label='睡眠時數', color='purple')

ax.set_xlabel("時間")
ax.set_ylabel("數值")
ax.set_title("健康指標歷史趨勢")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# 顯示評估結果
st.subheader("評估結果")
st.write(f"eGFR 狀況: **{egfr_state}**")
st.write(f"BMI: **{bmi:.1f}**")
st.write(f"衰弱狀況: **{frail_status}**")

# 衛教建議 (豐富版)
st.subheader("📚 衛教建議")

# eGFR 衛教
if egfr >= 90:
    st.info("""
    💡 **正常腎功能**
    - 您的腎功能正常，請持續保持良好的生活習慣，包括均衡飲食、適當運動與定期健康檢查。
    - 減少過度服用藥物或含有腎毒性的物質（如某些止痛藥）。
    - 保持良好的血壓和血糖控制，避免腎臟負擔過重。
    - 參考衛福部腎臟病防治網站，了解更多預防慢性腎臟病的資訊。
    """)
elif egfr >= 60:
    st.warning("""
    ⚠️ **輕度腎功能減退**
    - 您的腎功能已有輕微下降，建議：
      - 控制血壓與血糖，減少腎臟進一步損傷。
      - 避免長期使用可能損害腎臟的藥物（如NSAIDs）。
      - 注意飲食中鹽分與蛋白質攝取量，遵照醫師或營養師指示調整。
      - 定期回診追蹤腎功能，早期發現異常以利治療。
    - 衛福部相關慢性腎病管理資源可供參考。
    """)
elif egfr >= 30:
    st.error("""
    ❗ **中度腎功能減退**
    - 腎臟功能中度受損，您需要：
      - 積極與腎臟科醫師配合治療，監控疾病進展。
      - 嚴格控制飲食，避免過多蛋白質與鹽分攝取。
      - 避免使用腎毒性藥物及不必要的補充品。
      - 留意身體水腫、高血壓、尿量改變等警訊，並儘速就醫。
      - 衛福部有提供專業的慢性腎病患者衛教手冊，可作為參考。
    """)
else:
    st.error("""
    ❗ **重度腎功能減退**
    - 腎臟功能嚴重下降，可能需要透析或腎臟移植：
      - 請務必與腎臟專科醫師密切合作。
      - 注意日常生活中避免感染及腎臟負擔。
      - 配合醫療團隊安排定期治療與監控。
      - 衛福部腎臟病患者照護資源將幫助您瞭解如何自我照護與病情管理。
    """)

# BMI 衛教
if bmi < 18.5:
    st.info("""
    💡 **體重過輕**
    - 可能造成免疫力下降、營養不良及疲倦無力。
    - 建議增加高蛋白質與高熱量飲食，適度增加健康脂肪攝取。
    - 定期檢查身體狀況，排除潛在疾病導致體重下降。
    - 衛福部建議透過營養師指導擬定個人化飲食計畫。
    """)
elif 18.5 <= bmi < 24:
    st.info("""
    💡 **體重正常**
    - 請持續維持均衡飲食及規律運動，避免體重波動過大。
    - 均衡攝取五大類食物，少吃高油脂、高糖及高鹽食物。
    - 衛福部健康飲食指南提供實用建議，助您保持理想體重。
    """)
elif 24 <= bmi < 27:
    st.warning("""
    ⚠️ **體重過重**
    - 增加心血管疾病、糖尿病等慢性病風險。
    - 建議減少高熱量、高油脂食物，增加蔬果與全穀攝取。
    - 培養每日運動習慣，提升基礎代謝。
    - 衛福部推廣肥胖防治計畫與運動健康方案，請參考相關資源。
    """)
else:
    st.error("""
    ❗ **肥胖**
    - 顯著提高高血壓、糖尿病、中風等風險。
    - 建議與醫療團隊合作，制定減重與飲食計畫。
    - 培養規律運動習慣，控制熱量攝取。
    - 衛福部有肥胖病患專屬支持與衛教資訊，協助您健康管理。
    """)

# 衰弱指數衛教
if frail_status == "無衰弱":
    st.info("""
    💡 **無衰弱**
    - 恭喜您保持良好體力與生活品質。
    - 建議持續維持均衡飲食、規律運動、足夠休息。
    - 定期健康檢查，及早發現任何身體變化。
    - 衛福部推動老年健康促進計畫，鼓勵健康老化。
    """)
elif frail_status == "前衰弱":
    st.warning("""
    ⚠️ **前衰弱**
    - 您可能開始出現體力下降、疲倦等症狀。
    - 建議增加肌力與耐力訓練，如簡易肌力運動。
    - 注意蛋白質攝取與營養均衡。
    - 衛福部提供多項預防與延緩衰弱策略，鼓勵積極改變生活方式。
    """)
else:
    st.error("""
    ❗ **衰弱**
    - 可能出現活動能力下降、跌倒風險提高等。
    - 建議立即諮詢醫師及復健專家，進行功能復健與照護。
    - 注意安全環境與營養支持，避免併發症。
    - 衛福部老年醫學科有相關復健與長照衛教資源。
    """)

# 生活習慣衛教
if drinking != "不喝":
    st.warning("""
    ⚠️ **飲酒過量**
    - 長期過度飲酒會損害肝臟、心臟及神經系統。
    - 建議遵循衛福部酒精攝取指引，男性每日不超過兩杯，女性一杯。
    - 若有戒酒困難，可尋求戒酒門診或社會支持。
    """)
else:
    st.info("💡 **不飲酒**：持續保持，降低多種慢性疾病風險。")

if smoking == "目前仍抽":
    st.error("""
    ❗ **吸菸危害**
    - 吸菸是多種癌症與心血管疾病的主要危險因子。
    - 衛福部強烈建議戒菸，政府提供戒菸輔助資源。
    - 請尋求醫療團隊協助，使用戒菸門診與輔助工具。
    """)
elif smoking == "已戒菸":
    st.info("💡 **已戒菸**：恭喜您成功戒菸，繼續維持健康生活！")
else:
    st.info("💡 **不抽菸**：良好習慣，有助長壽與健康。")

if betel_nut != "否":
    st.error("""
    ❗ **嚼檳榔危害**
    - 嚼檳榔大幅提高口腔癌與食道癌風險。
    - 衛福部推廣全面禁嚼檳榔政策，並提供戒檳輔導。
    - 請儘早戒除，保護口腔健康與生命安全。
    """)
else:
    st.info("💡 **不嚼檳榔**：持續維持口腔健康，避免癌症風險。")

if drug_use == "目前有":
    st.error("""
    ❗ **藥物濫用**
    - 藥物濫用會對身心造成嚴重傷害，影響生活品質與社會功能。
    - 衛福部設有成癮防治中心，提供戒治與心理輔導。
    - 建議儘速尋求專業協助與治療。
    """)
else:
    st.info("💡 **無藥物濫用史**，請持續維持健康生活習慣。")

if stress >= 7:
    st.warning("""
    ⚠️ **壓力過大**
    - 長期高壓力會影響心理與生理健康，可能引發焦慮、失眠與慢性疾病。
    - 建議培養紓壓方法，如運動、冥想、與家人朋友交流。
    - 衛福部心理健康資源豐富，歡迎利用相關服務。
    """)
else:
    st.info("💡 **壓力正常**，請持續保持良好生活節奏與心態。")

if sleep_hours < 5 or sleep_hours > 10:
    st.warning("""
    ⚠️ **睡眠異常**
    - 過短或過長睡眠均可能影響身體代謝、記憶與免疫功能。
    - 建議成人每晚保持7至9小時優質睡眠。
    - 衛福部睡眠健康指導提供改善睡眠的實用建議。
    """)
else:
    st.info("💡 **睡眠充足**，有助於維持身心健康。")

# 門診建議與掛號連結
st.subheader("🏥 門診建議與掛號")
if egfr < 60 or frail_status == "衰弱":
    st.error("建議盡快至腎臟科及老年醫學科門診追蹤與治療。")
    st.markdown("[點此前往中國醫藥大學附設醫院台中總院掛號系統](https://www.cmuh.cmu.edu.tw/OnlineAppointment/AppointmentByDivision)")
elif egfr < 90:
    st.warning("建議定期至腎臟科門診追蹤，並配合醫師指示進行治療。")
    st.markdown("[點此前往中國醫藥大學附設醫院台中總院掛號系統](https://www.cmuh.cmu.edu.tw/OnlineAppointment/AppointmentByDivision)")
else:
    st.info("腎功能良好，建議持續定期健康檢查與良好生活習慣。")
