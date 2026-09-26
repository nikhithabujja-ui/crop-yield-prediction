from flask import Flask, render_template, request, jsonify
import pickle
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)


# ==============================
# LOAD MACHINE LEARNING MODEL
# ==============================

with open("crop_yield_model.pkl", "rb") as file:
    model = pickle.load(file)


# ==============================
# CROP MAPPING
# ==============================

crop_names = {
    0: "Rice",
    1: "Wheat",
    2: "Maize",
    3: "Cotton",
    4: "Sugarcane",
    5: "Groundnut"
}


# ==============================
# DATABASE CONNECTION
# ==============================

def get_db_connection():

    conn = sqlite3.connect("crop_yield.db")

    return conn


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():

    return render_template("index.html")


# ==============================
# PREDICTION
# ==============================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        crop = int(request.form["crop"])

        rainfall = float(request.form["rainfall"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        soil_ph = float(request.form["soil_ph"])
        nitrogen = float(request.form["nitrogen"])
        phosphorus = float(request.form["phosphorus"])
        potassium = float(request.form["potassium"])

    except (ValueError, KeyError):

        return render_template(
            "error.html",
            title="❌ Invalid Input",
            message="Please enter valid values in all fields."
        )


    # ==============================
    # VALIDATION
    # ==============================

    if crop not in crop_names:

        return render_template(
            "error.html",
            title="❌ Invalid Crop",
            message="Please select a valid crop."
        )


    if rainfall < 0:

        return render_template(
            "error.html",
            title="❌ Invalid Rainfall",
            message="Rainfall cannot be negative."
        )


    if temperature < -50 or temperature > 60:

        return render_template(
            "error.html",
            title="❌ Invalid Temperature",
            message="Please enter a realistic temperature."
        )


    if humidity < 0 or humidity > 100:

        return render_template(
            "error.html",
            title="❌ Invalid Humidity",
            message="Humidity must be between 0 and 100%."
        )


    if soil_ph < 0 or soil_ph > 14:

        return render_template(
            "error.html",
            title="❌ Invalid Soil pH",
            message="Soil pH must be between 0 and 14."
        )


    if nitrogen < 0:

        return render_template(
            "error.html",
            title="❌ Invalid Nitrogen",
            message="Nitrogen cannot be negative."
        )


    if phosphorus < 0:

        return render_template(
            "error.html",
            title="❌ Invalid Phosphorus",
            message="Phosphorus cannot be negative."
        )


    if potassium < 0:

        return render_template(
            "error.html",
            title="❌ Invalid Potassium",
            message="Potassium cannot be negative."
        )


    # ==============================
    # CROP NAME
    # ==============================

    crop_name = crop_names[crop]


    # ==============================
    # MODEL INPUT
    # ==============================

    features = pd.DataFrame(
        [[
            crop,
            rainfall,
            temperature,
            humidity,
            soil_ph,
            nitrogen,
            phosphorus,
            potassium
        ]],
        columns=[
            "crop",
            "rainfall",
            "temperature",
            "humidity",
            "soil_ph",
            "nitrogen",
            "phosphorus",
            "potassium"
        ]
    )


    # ==============================
    # AI PREDICTION
    # ==============================

    prediction = model.predict(features)[0]

    prediction = round(float(prediction), 2)


    # ==============================
    # DATE & TIME
    # ==============================

    prediction_date = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )


    # ==============================
    # SAVE TO DATABASE
    # ==============================

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions
        (
            crop,
            rainfall,
            temperature,
            humidity,
            soil_ph,
            nitrogen,
            phosphorus,
            potassium,
            predicted_yield,
            prediction_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            crop_name,
            rainfall,
            temperature,
            humidity,
            soil_ph,
            nitrogen,
            phosphorus,
            potassium,
            prediction,
            prediction_date
        )
    )

    conn.commit()

    conn.close()


    # ==============================
    # SHOW RESULT
    # ==============================

    return render_template(
        "result.html",
        prediction=prediction
    )


# ==============================
# HISTORY
# ==============================

@app.route("/history")
def history():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            crop,
            rainfall,
            temperature,
            humidity,
            soil_ph,
            nitrogen,
            phosphorus,
            potassium,
            predicted_yield,
            prediction_date
        FROM predictions
        ORDER BY id DESC
        """
    )

    predictions = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        predictions=predictions
    )


# ==============================
# DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    cursor = conn.cursor()


    # Total predictions

    cursor.execute(
        "SELECT COUNT(*) FROM predictions"
    )

    total_predictions = cursor.fetchone()[0]


    # Latest prediction

    cursor.execute(
        """
        SELECT crop, predicted_yield
        FROM predictions
        ORDER BY id DESC
        LIMIT 1
        """
    )

    latest = cursor.fetchone()


    if latest:

        latest_crop = latest[0]
        latest_yield = latest[1]

    else:

        latest_crop = "No data"
        latest_yield = 0


    # Average yield

    cursor.execute(
        """
        SELECT AVG(predicted_yield)
        FROM predictions
        """
    )

    average_yield = cursor.fetchone()[0]


    if average_yield is None:

        average_yield = 0

    average_yield = round(
        float(average_yield),
        2
    )


    # Chart data

    cursor.execute(
        """
        SELECT crop, predicted_yield
        FROM predictions
        ORDER BY id ASC
        """
    )

    chart_data = cursor.fetchall()

    conn.close()


    crop_names_for_chart = []

    crop_yields = []


    for row in chart_data:

        crop_names_for_chart.append(row[0])

        crop_yields.append(row[1])


    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        latest_crop=latest_crop,
        latest_yield=latest_yield,
        average_yield=average_yield,
        crop_names=crop_names_for_chart,
        crop_yields=crop_yields
    )


# ==============================
# API - PREDICTION
# ==============================

@app.route("/api/predict", methods=["POST"])
def api_predict():

    try:

        data = request.get_json()

        crop = int(data["crop"])
        rainfall = float(data["rainfall"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        soil_ph = float(data["soil_ph"])
        nitrogen = float(data["nitrogen"])
        phosphorus = float(data["phosphorus"])
        potassium = float(data["potassium"])

    except (TypeError, ValueError, KeyError):

        return jsonify({
            "success": False,
            "message": "Invalid input data."
        }), 400


    if crop not in crop_names:

        return jsonify({
            "success": False,
            "message": "Invalid crop."
        }), 400


    features = pd.DataFrame(
        [[
            crop,
            rainfall,
            temperature,
            humidity,
            soil_ph,
            nitrogen,
            phosphorus,
            potassium
        ]],
        columns=[
            "crop",
            "rainfall",
            "temperature",
            "humidity",
            "soil_ph",
            "nitrogen",
            "phosphorus",
            "potassium"
        ]
    )


    prediction = model.predict(features)[0]

    prediction = round(float(prediction), 2)


    return jsonify({

        "success": True,

        "crop": crop_names[crop],

        "predicted_yield": prediction,

        "unit": "tons/hectare"

    })


# ==============================
# API - HISTORY
# ==============================

@app.route("/api/history")
def api_history():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            crop,
            rainfall,
            temperature,
            humidity,
            soil_ph,
            nitrogen,
            phosphorus,
            potassium,
            predicted_yield,
            prediction_date
        FROM predictions
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()


    history_data = []


    for row in rows:

        history_data.append({

            "id": row[0],

            "crop": row[1],

            "rainfall": row[2],

            "temperature": row[3],

            "humidity": row[4],

            "soil_ph": row[5],

            "nitrogen": row[6],

            "phosphorus": row[7],

            "potassium": row[8],

            "predicted_yield": row[9],

            "prediction_date": row[10]

        })


    return jsonify({

        "success": True,

        "count": len(history_data),

        "predictions": history_data

    })


# ==============================
# API - DASHBOARD
# ==============================

@app.route("/api/dashboard")
def api_dashboard():

    conn = get_db_connection()

    cursor = conn.cursor()


    cursor.execute(
        "SELECT COUNT(*) FROM predictions"
    )

    total_predictions = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT AVG(predicted_yield)
        FROM predictions
        """
    )

    average_yield = cursor.fetchone()[0]


    if average_yield is None:

        average_yield = 0

    average_yield = round(
        float(average_yield),
        2
    )


    cursor.execute(
        """
        SELECT crop, predicted_yield
        FROM predictions
        ORDER BY id DESC
        LIMIT 1
        """
    )

    latest = cursor.fetchone()


    if latest:

        latest_crop = latest[0]
        latest_yield = latest[1]

    else:

        latest_crop = "No data"
        latest_yield = 0


    conn.close()


    return jsonify({

        "success": True,

        "total_predictions": total_predictions,

        "latest_crop": latest_crop,

        "latest_yield": latest_yield,

        "average_yield": average_yield

    })


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":

    app.run(debug=True)