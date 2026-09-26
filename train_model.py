import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

data = pd.read_csv("data/crop_yield.csv")

crop_mapping = {
    "Rice": 0,
    "Wheat": 1,
    "Maize": 2,
    "Cotton": 3,
    "Sugarcane": 4,
    "Groundnut": 5
}

data["crop"] = data["crop"].map(crop_mapping)

X = data[
    [
        "crop",
        "rainfall",
        "temperature",
        "humidity",
        "soil_ph",
        "nitrogen",
        "phosphorus",
        "potassium"
    ]
]

y = data["yield"]

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

with open("crop_yield_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model trained successfully!")
print("Model saved as crop_yield_model.pkl")