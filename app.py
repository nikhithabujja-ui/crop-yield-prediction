from flask import Flask, render_template, request, jsonify
import pickle
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)


# =========================
# LOAD TRAINED MODEL
# =========================

with open("crop_yield_model.pkl", "rb") as file:
    model = pickle.load(file)


# =========================
# CROP MAPPING
# =========================

crop_names = {
    0: "Rice",
    1: "Wheat",
    2: "Maize",
    3: "Cotton",
    4: "Sugarcane",
    5: "Groundnut"
}

crop_mapping = {
    "Rice": 0,
    "Wheat": 1,
    "Maize": 2,
    "Cotton": 3,
    "Sugarcane": 4,
    "Groundnut": 5
}


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():

    conn = sqlite3.connect("crop_yield.db")

    conn.row_factory = sqlite3.Row

    return conn


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# CROP RECOMMENDATIONS
# =========================

@app.route("/recommendations")
def recommendations():

    return render_template("crop_recommendations.html")


# =========================
# PREDICTION
# =========================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        crop = request.form["crop"]

        rainfall = float(request.form["rainfall"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        soil_ph = float(request.form["soil_ph"])
        nitrogen = float(request.form["nitrogen"])
        phosphorus = float(request.form["phosphorus"])
        potassium = float(request.form["potassium"])


        crop_code = crop_mapping[crop]


        input_data = pd.DataFrame(
            [[
                crop_code,
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


        prediction = model.predict(input_data)[0]

        prediction = round(float(prediction), 2)


        # =========================
        # SAVE TO DATABASE
        # =========================

        conn = get_db_connection()

        conn.execute(
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
                crop,
                rainfall,
                temperature,
                humidity,
                soil_ph,
                nitrogen,
                phosphorus,
                potassium,
                prediction,
                datetime.now().strftime("%Y-%m-%d %I:%M %p")
            )
        )

        conn.commit()

        conn.close()


        # =========================
        # RESULT PAGE
        # =========================

        return render_template(
            "result.html",
            prediction=prediction,
            crop=crop,
            rainfall=rainfall,
            temperature=temperature,
            humidity=humidity,
            soil_ph=soil_ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium
        )


    except Exception as e:

        return render_template(
            "error.html",
            title="❌ Prediction Error",
            message=str(e)
        )


# =========================
# PREDICTION HISTORY
# =========================

@app.route("/history")
def history():

    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            crop,
            rainfall,
            temperature,
            humidity,
            soil_ph,
            predicted_yield,
            prediction_date
        FROM predictions
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()


    return render_template(
        "history.html",
        rows=rows
    )


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()


    total_predictions = conn.execute(
        "SELECT COUNT(*) FROM predictions"
    ).fetchone()[0]


    latest = conn.execute(
        """
        SELECT
            crop,
            predicted_yield
        FROM predictions
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()


    average_yield = conn.execute(
        "SELECT AVG(predicted_yield) FROM predictions"
    ).fetchone()[0]


    chart_rows = conn.execute(
        """
        SELECT
            id,
            crop,
            predicted_yield
        FROM predictions
        ORDER BY id ASC
        """
    ).fetchall()


    conn.close()


    latest_crop = latest["crop"] if latest else "No data"

    latest_yield = latest["predicted_yield"] if latest else 0

    average_yield = (
        round(average_yield, 2)
        if average_yield
        else 0
    )


    chart_data = [

        {
            "id": row["id"],
            "crop": row["crop"],
            "yield": row["predicted_yield"]
        }

        for row in chart_rows

    ]


    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        latest_crop=latest_crop,
        latest_yield=latest_yield,
        average_yield=average_yield,
        chart_data=chart_data
    )


# =========================
# PREDICTION DETAILS
# =========================

@app.route("/prediction/<int:prediction_id>")
def prediction_details(prediction_id):

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
        WHERE id = ?
        """,
        (prediction_id,)
    )


    prediction = cursor.fetchone()

    conn.close()


    if prediction is None:

        return render_template(
            "error.html",
            title="❌ Prediction Not Found",
            message="The requested prediction does not exist."
        )


    return render_template(
        "prediction_details.html",
        prediction=prediction
    )


# =========================
# API - PREDICTION
# =========================

@app.route("/api/predict", methods=["POST"])
def api_predict():

    try:

        data = request.get_json()


        crop = data["crop"]

        rainfall = float(data["rainfall"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        soil_ph = float(data["soil_ph"])
        nitrogen = float(data["nitrogen"])
        phosphorus = float(data["phosphorus"])
        potassium = float(data["potassium"])


        crop_code = crop_mapping[crop]


        input_data = pd.DataFrame(
            [[
                crop_code,
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


        prediction = model.predict(input_data)[0]

        prediction = round(float(prediction), 2)


        return jsonify({

            "success": True,

            "crop": crop,

            "predicted_yield": prediction

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        })


# =========================
# API - HISTORY
# =========================

@app.route("/api/history")
def api_history():

    conn = get_db_connection()


    rows = conn.execute(
        """
        SELECT *
        FROM predictions
        ORDER BY id DESC
        """
    ).fetchall()


    conn.close()


    history_data = [

        dict(row)

        for row in rows

    ]


    return jsonify(history_data)


# =========================
# API - DASHBOARD
# =========================

@app.route("/api/dashboard")
def api_dashboard():

    conn = get_db_connection()


    total_predictions = conn.execute(
        "SELECT COUNT(*) FROM predictions"
    ).fetchone()[0]


    average_yield = conn.execute(
        "SELECT AVG(predicted_yield) FROM predictions"
    ).fetchone()[0]


    latest = conn.execute(
        """
        SELECT
            crop,
            predicted_yield
        FROM predictions
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()


    conn.close()


    return jsonify({

        "total_predictions": total_predictions,

        "average_yield":
            round(average_yield, 2)
            if average_yield
            else 0,

        "latest_crop":
            latest["crop"]
            if latest
            else None,

        "latest_yield":
            latest["predicted_yield"]
            if latest
            else 0

    })


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(debug=True)