# 🌾 CropAI - AI-Based Crop Yield Prediction System

CropAI is an AI-based web application that predicts crop yield using weather and soil conditions.

## 🚀 Features

- 🌾 Select different crops
- 🌧️ Enter rainfall data
- 🌡️ Enter temperature
- 💧 Enter humidity
- 🧪 Enter soil pH
- 🌱 Enter nitrogen, phosphorus and potassium values
- 🤖 Machine Learning based crop yield prediction
- 📊 Prediction dashboard
- 📋 Prediction history
- 💾 SQLite database
- 🔌 REST API
- ⚠️ Input validation

## 🛠️ Technologies Used

### Frontend
- HTML
- CSS

### Backend
- Python
- Flask

### Machine Learning
- Scikit-learn
- Random Forest Regression
- Pandas
- NumPy

### Database
- SQLite

## 🌱 Supported Crops

- Rice
- Wheat
- Maize
- Cotton
- Sugarcane
- Groundnut

## 📂 Project Structure

```text
crop-yield-prediction/
│
├── data/
│   └── crop_yield.csv
│
├── static/
│   └── style.css
│
├── templates/
│   ├── dashboard.html
│   ├── error.html
│   ├── history.html
│   ├── index.html
│   └── result.html
│
├── app.py
├── database.py
├── train_model.py
├── add_date_column.py
├── crop_yield_model.pkl
├── crop_yield.db
├── .gitignore
└── README.md