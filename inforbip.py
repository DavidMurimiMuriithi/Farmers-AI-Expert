from flask import Flask, request, jsonify
import requests
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = ''
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# Infobip API credentials
INFOBIP_API_KEY = ''
INFOBIP_BASE_URL = ''  # Replace with your Infobip base URL
INFOBIP_WHATSAPP_NUMBER = ''  # Your Infobip WhatsApp number

# Infobip Webhook for WhatsApp
@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.json
    if data:
        message = data.get('messages', [{}])[0].get('text', '').lower()
        sender = data.get('messages', [{}])[0].get('from', '')

        # Generate response using Gemini API
        response = generate_response(message)

        # Send response back to WhatsApp via Infobip
        send_whatsapp_message(sender, response)

    return jsonify({"status": "success"}), 200

def generate_response(user_input):
    # Use Gemini API to generate a response
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return "Sorry, I encountered an error while processing your request. Please try again later."

def send_whatsapp_message(recipient, message):
    # Send a WhatsApp message using Infobip API
    url = f"{INFOBIP_BASE_URL}/whatsapp/1/message/text"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "from": INFOBIP_WHATSAPP_NUMBER,
        "to": +254798694625,
        "content": {
            "text": message
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
