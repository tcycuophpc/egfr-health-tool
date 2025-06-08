import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 模擬資料筆數
N = 1500
np.random.seed(42)

data = []
for _ in range(N):
    age = np.random.randint(40, 90)
    bmi = np.random.uniform(18.5, 32)
    sbp = np.random.randint(100, 160)
    dbp = np.random.randint(60, 100)
    smoking = np.random.randint(0, 21)
    drinking = np.random.randint(0, 7)
    chewing = np.random.randint(0, 6)
    drug = np.random.randint(0, 6)
    supp = np.random.randint(0, 5)
    chronic_count = np.random.randint(0, 5)
    frail_score = np.random.randint(0, 6)
    has_diabetes = np.random.randint(0, 2)
    has_htn = np.random.randint(0, 2)
    has_stroke = np.random.randint(0, 2)

    # 模擬 eGFR 值（加入生理邏輯與隨機擾動）
    egfr = (
        120
        - 0.7 * age
        - 1.2 * bmi
        - 0.25 * sbp
        - 1.5 * frail_score
        - 3.5 * has_diabetes
        - 2.0 * has_htn
        - 1.5 * has_stroke
        - 0.8 * smoking
        + np.random.normal(0, 5)
    )
    egfr = max(5, min(egfr, 120))  # 限定範圍

    data.append([
        age, bmi, sbp, dbp, smoking, drinking, chewing, drug, supp,
        chronic_count, frail_score, has_diabetes, has_htn, has_stroke, egfr
    ])

columns = [
    "age", "bmi", "sbp", "dbp", "smoking_freq", "drinking_freq",
    "chewing_freq", "drug_freq", "supp_freq", "chronic_count",
    "frail_score", "has_diabetes", "has_hypertension", "has_stroke", "egfr"
]

df = pd.DataFrame(data, columns=columns)

# 分割資料
X = df.drop("egfr", axis=1)
y = df["egfr"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 建立模型
model = GradientBoostingRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    random_state=42
)
model.fit(X_train, y_train)

# 模型評估
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"✅ 模型完成！RMSE={rmse:.2f}, R²={r2:.3f}")

# 儲存模型
joblib.dump(model, "egfr_model.pkl")
print("✅ 模型已儲存為 egfr_model.pkl")
