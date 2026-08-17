import os
import sys
import django

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib


# -----------------------------------------
# Django setup
# -----------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodforecast.settings")

django.setup()


# Import Django model
from foodapp.models import MealRecord


# -----------------------------------------
# Get data from database
# -----------------------------------------

records = MealRecord.objects.all()

data = []

for record in records:

    data.append({
        "attendance": record.attendance,
        "temperature": record.temperature,
        "rainfall": record.rainfall,
        "holiday": int(record.holiday),
        "day_of_week": record.date.weekday(),
        "demand": record.meals_consumed
    })


# Convert to Pandas DataFrame
df = pd.DataFrame(data)

print("\nDataset:")
print(df)

print("\nNumber of records:", len(df))


# -----------------------------------------
# Features and target
# -----------------------------------------

X = df[
    [
        "attendance",
        "temperature",
        "rainfall",
        "holiday",
        "day_of_week"
    ]
]

y = df["demand"]


# -----------------------------------------
# Split dataset
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# -----------------------------------------
# Create ML model
# -----------------------------------------

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# Train model
model.fit(X_train, y_train)


# -----------------------------------------
# Test model
# -----------------------------------------

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)

print("\nModel Performance")
print("-----------------")
print("Mean Absolute Error:", round(mae, 2))


# -----------------------------------------
# Save model
# -----------------------------------------

model_path = os.path.join(
    BASE_DIR,
    "ml",
    "demand_model.pkl"
)

joblib.dump(model, model_path)

print("\nModel saved successfully!")
print("Location:", model_path)