from flask import Flask, request, jsonify, render_template, redirect, url_for
import google.generativeai as genai
from mpesa_payment import mpesa_bp
from extensions import db
from models import Question
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.register_blueprint(mpesa_bp)


# Configure the database URI (here we use SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)  # Properly bind SQLAlchemy to the Flask app

# Ensure tables are created
with app.app_context():
    db.create_all()

# Set up the Google Generative AI
MY_API_KEY = ""  # Replace with your actual API key
genai.configure(api_key=MY_API_KEY)

# Configure the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=(
        "You are an expert in farming and irrigation. You provide farmers with the best modern farming and irrigation techniques, "
        "how to fight disease through pesticides and all available mechanisms. You offer skills on how to operate farm tools and machinery, "
        "how to add value to their farm outputs, and the best investments they can make in the agricultural sector. "
        "Crops to focus on include rice, tomatoes, peas, maize, sugarcane, oranges, bananas, and beans."
    ),
)

chat_session = model.start_chat(history=[])

# Endpoint to redirect to the dashboard
@app.route("/")
def index():
    return redirect(url_for('dashboard'))

# Dashboard Route
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Routes for each Farm Inputs & Service page

@app.route("/fertilizers")
def fertilizers():
    return render_template("fertilizers.html")

@app.route("/seedlings")
def seedlings():
    return render_template("seedlings.html")

@app.route("/pesticides")
def pesticides():
    return render_template("pesticides.html")

@app.route("/chemicals")
def chemicals():
    return render_template("chemicals.html")

@app.route("/rotavation")
def rotavation():
    return render_template("rotavation.html")

@app.route("/harvesting")
def harvesting():
    return render_template("harvesting.html")

@app.route("/soil_tests")
def soiltest():
    return render_template("soil_tests.html")

@app.route("/transports")
def transports():
    return render_template("transports.html")

@app.route("/crop_production")
def crop_production():
    return render_template("crop_production.html")

@app.route("/agronomist_dashboard")
def agronomist_dashboard():
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    return render_template("agronomist_dashboard.html", questions=questions)



@app.route('/submit_question', methods=['POST'])
def submit_question():
    data = request.get_json()
    question_text = data.get('question')
    user_name = data.get('user_name', "Anonymous")
    if not question_text:
        return jsonify({"error": "Question text is required"}), 400

    new_question = Question(user_name=user_name, question_text=question_text)
    db.session.add(new_question)
    db.session.commit()
    return jsonify({"message": "Question submitted", "question_id": new_question.id}), 200


@app.route('/get_questions', methods=['GET'])
def get_questions():
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "user_name": q.user_name,
            "question": q.question_text,
            "reply": q.reply_text,
            "timestamp": q.timestamp.isoformat(),
            "replied_at": q.replied_at.isoformat() if q.replied_at else None,
            "document_url": q.document_url,
            "image_url": q.image_url
        })
    return jsonify(result), 200

@app.after_request
def add_header(response):
    """Disable caching to always load updated HTML files."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



# Endpoint for chatbot interaction (API)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the user message from the web request
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({"reply": "Please provide a valid message."}), 400

        # Process the message with the chatbot
        response = chat_session.send_message(user_message)

        # Return the chatbot's response
        return jsonify({"reply": response.text}), 200

    except Exception as e:
        return jsonify({"reply": f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)


    
