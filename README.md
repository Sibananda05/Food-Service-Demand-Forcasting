# Smart Food Service Management System

## 📌 Project Overview

The Smart Food Service Management System is a Django-based web application designed to reduce food wastage through intelligent demand forecasting, food safety verification, surplus food management, and redistribution.

The system combines Machine Learning with rule-based food safety checks to help organizations prepare the right amount of food and safely redistribute surplus food.

## 🚀 Main Features

### 1. 📊 Demand Forecasting
Uses a trained Machine Learning model to predict food demand based on:

- Attendance
- Temperature
- Rainfall
- Holiday
- Day of the week

The system also calculates recommended food preparation with an additional 5% buffer.

### 2. 🛡️ Food Safety Check

The system checks surplus food using:

- Storage temperature
- Storage duration

Food is considered safe when:

- Temperature ≤ 5°C
- Storage time ≤ 24 hours

Otherwise, it is marked as unsafe.

### 3. 🍱 Surplus Food Management

Users can:

- Add surplus food
- Enter quantity
- Record storage conditions
- Automatically check food safety
- View surplus food records

### 4. ♻️ Food Redistribution

Safe surplus food can be redistributed to verified recipients.

The system:

- Checks whether food is safe
- Checks available quantity
- Allows selection of verified recipients
- Updates remaining quantity
- Marks food as redistributed when quantity reaches zero

### 5. 📈 Dashboard

The dashboard provides an overview of:

- Total demand predictions
- Predicted meals
- Recommended meals
- Total surplus food
- Safe food
- Unsafe food
- Redistributed food
- Redistribution quantity
- Total recipients
- Verified recipients
- Recent predictions
- Recent surplus food

### 6. 🔐 Django Admin

The Django admin panel can be used to manage:

- Meal records
- Demand forecasts
- Recipients
- Surplus food
- Redistributions

## 🛠️ Technologies Used

- Python
- Django
- HTML
- CSS
- Machine Learning
- scikit-learn
- Joblib
- SQLite

## 📁 Project Structure

```text
Smart-Food-Service/
│
├── manage.py
├── requirements.txt
├── .gitignore
│
├── ml/
│   └── demand_model.pkl
│
├── templates/
│   ├── home.html
│   ├── dashboard.html
│   ├── predict.html
│   ├── food_safety.html
│   ├── add_surplus.html
│   └── surplus_list.html
│
└── app/
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── urls.py
    └── admin.py