from flask import (
    Flask, render_template, request, redirect,
    url_for, session, send_file, jsonify
)
import pickle
import numpy as np
from io import BytesIO
from datetime import datetime
import pdfkit
from history import save_history
from model import load_user_history

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# PDFKit Configuration
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

# Load the ML model
with open("health_model.pkl", "rb") as f:
    model = pickle.load(f)

# Label encoders, risk labels, advice and plans
label_encoders = {
    "Gender": {"Male": 1, "Female": 0},
    "Symptoms": {
        "Chest pain, fatigue": 0,
        "Headache, nausea": 1,
        "Cough, fever": 2,
        "Shortness of breath": 3,
        "Back pain, dizziness": 4,
        "None": 5
    },
    "Medical_History": {
        "Hypertension": 0,
        "Diabetes": 1,
        "Asthma": 2,
        "Heart Disease": 3,
        "Cancer": 4,
        "None": 5
    },
    "Medications": {
        "Aspirin": 0,
        "Metformin": 1,
        "Lisinopril": 2,
        "Atorvastatin": 3,
        "None": 4
    },
    "Lab_Reports": {
        "High cholesterol": 0,
        "Normal sugar": 1,
        "Low RBC": 2,
        "Elevated liver enzymes": 3,
        "Normal": 4,
        "High WBC": 5
    },
    "Lifestyle": {
        "Smoker": 0,
        "Active": 1,
        "Sedentary": 2,
        "Alcoholic": 3,
        "Healthy Diet": 4,
        "None": 5
    },
}

risk_labels = {0: "High Risk", 1: "Low Risk", 2: "Moderate Risk"}

advice_points = {
    "Low Risk": [
        "Maintain a healthy lifestyle.",
        "Continue regular checkups.",
        "Stay active and eat a balanced diet."
    ],
    "Moderate Risk": [
        "Consult a doctor for early prevention.",
        "Reduce risk factors like smoking or poor diet.",
        "Get recommended health screenings."
    ],
    "High Risk": [
        "Seek immediate medical attention.",
        "Monitor your condition closely with a specialist.",
        "Follow a strict medical and lifestyle plan."
    ]
}

personalized_plans = {
    "Low Risk": {
        "Diet": "Maintain your balanced diet. Include greens and hydrate well.",
        "Exercise": "Continue 30 min daily activity like brisk walking or yoga.",
        "Steps": "Keep your daily step goal between 7 000 – 10 000.",
        "Sleep": "Maintain 7 – 8 hours of restful sleep consistently.",
        "Wellness": "Keep stress low, stay hydrated, and continue regular checkups."
    },
    "Moderate Risk": {
        "Diet": "Reduce processed foods and sugar. Add more fiber and fruits.",
        "Exercise": "Start moderate workouts 5 ×/week (walking, stretching).",
        "Steps": "Gradually increase to 8 000 – 10 000 steps/day.",
        "Sleep": "Sleep 7 – 8 h, improve sleep hygiene (no screens, fixed times).",
        "Wellness": "Begin stress‑relief practices and limit smoking/alcohol."
    },
    "High Risk": {
        "Diet": "Follow a strict diet plan. Avoid salt, sugar, fried foods. Consult a dietician.",
        "Exercise": "Consult a doctor before starting exercise. Light walking or physiotherapy may help.",
        "Steps": "Start slowly—3 000 – 5 000 steps/day if advised by doctor.",
        "Sleep": "Ensure 8 h of high‑quality sleep. Use relaxation techniques.",
        "Wellness": "Quit smoking/alcohol, monitor vitals regularly, seek psychological support if needed."
    }
}

# Public routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        try:
            age             = int(request.form["Age"])
            gender          = label_encoders["Gender"][request.form["Gender"]]
            symptoms        = label_encoders["Symptoms"][request.form["Symptoms"]]
            medical_history = label_encoders["Medical_History"][request.form["Medical_History"]]
            medications     = label_encoders["Medications"][request.form["Medications"]]
            lab_reports     = label_encoders["Lab_Reports"][request.form["Lab_Reports"]]
            lifestyle       = label_encoders["Lifestyle"][request.form["Lifestyle"]]

            features        = [age, gender, symptoms, medical_history, medications, lab_reports, lifestyle]
            prediction      = model.predict([features])[0]
            result          = risk_labels.get(prediction, "Unknown")
            recommendations = advice_points.get(result, ["Consult a healthcare provider."])

            session["last_result"] = result
            session["last_input"]  = features

            save_history("guest", features, result)

            return render_template("result.html", result=result, recommendations=recommendations, plan=personalized_plans[result])
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template("form.html")

@app.route("/download")
def download():
    result     = session.get("last_result", "N/A")
    input_data = session.get("last_input", [])
    advice     = advice_points.get(result, [])
    plan       = personalized_plans.get(result, {})
    report_dt  = datetime.now().strftime("%d-%m-%Y")

    html = render_template("pdf_template.html", result=result, inputs=input_data,
                           recommendations=advice, plan=plan, date=report_dt)
    pdf = pdfkit.from_string(html, False, configuration=config)
    return send_file(BytesIO(pdf), as_attachment=True,
                     download_name="Health_Risk_Report.pdf")

@app.route("/download_plan")
def download_plan():
    result    = session.get("last_result", "N/A")
    plan      = personalized_plans.get(result, {})
    report_dt = datetime.now().strftime("%d-%m-%Y")

    html = render_template("plan_only_template.html", plan=plan, date=report_dt)
    pdf  = pdfkit.from_string(html, False, configuration=config)
    return send_file(BytesIO(pdf), as_attachment=True,
                     download_name="Personalized_Health_Plan.pdf")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name")
        email   = request.form.get("email")
        message = request.form.get("message")
        print(f"[Contact] {name=} {email=} {message=}")
        return redirect(url_for("welcome"))
    return render_template("contact.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/history")
def history():
    history_df   = load_user_history("guest")
    history_data = history_df.to_dict(orient="records")
    return render_template("history.html", history=history_data)

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"].lower()
    if "hi" in user_message or "hello" in user_message:
        reply = "Hello! How can I assist you with your health today?"
    elif "stress" in user_message:
        reply = "Try deep breathing, daily meditation, and sleeping 7–8 hours."
    elif "headache" in user_message:
        reply = "Drink water, rest well, and reduce screen time. If persistent, see a doctor."
    elif "diet" in user_message:
        reply = "Include vegetables, whole grains, and reduce sugar & oil intake."
    elif "sleep" in user_message:
        reply = "Adults need 7–9 hours of quality sleep for good health."
    else:
        reply = "Sorry, I’m still learning. You can ask me about sleep, stress, headache, or diet."
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
