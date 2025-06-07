import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import joblib

# 產生模擬訓練資料
data = []
import random
for _ in range(300):
    smoking = random.randint(0, 20)
    drinking = random.randint(0, 7)
    chewing = random.randint(0, 10)
    drug = random.randint(0, 5)
    supp = random.randint(0, 5)
    chronic = random.randint(0, 3)
    # 模擬 egfr 值，假設生活習慣越差 eGFR 越低
    egfr = 120 - smoking * 0.8 - drinking * 1.0 - chewing * 1.2 - drug * 2.5 - supp * 0.5 - chronic * 5 + random.gauss(0, 5)
    data.append([smoking, drinking, chewing, drug, supp, chronic, max(egfr, 5)])

df = pd.DataFrame(data, columns=[
    "smoking_freq", "drinking_freq", "chewing_freq", "drug_freq", "supp_freq", "chronic_count", "egfr"
])

X = df.drop("egfr", axis=1)
y = df["egfr"]

model = GradientBoostingRegressor()
model.fit(X, y)

joblib.dump(model, "egfr_model.pkl")
print("模型訓練完成並已儲存為 egfr_model.pkl")
