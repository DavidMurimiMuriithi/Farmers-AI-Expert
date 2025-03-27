# mpesa_payment.py
from flask import Blueprint, request, jsonify
import base64
import datetime
import requests

mpesa_bp = Blueprint('mpesa', __name__)

# Configuration - replace with your actual credentials
CONSUMER_KEY = "YxOXsJGNYqGasHB8JfrHWSxRbab6pGPkbl3jUzoecRmeAcWd"
CONSUMER_SECRET = "hwzSZndr4NnsunIoZRy08LJGyb3GqPUzMdaIPeN4IjryVMyndxO8Vc752cd3aEKK"
BUSINESS_SHORTCODE = "174379"  # e.g., "174379" for sandbox
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
CALLBACK_URL = "https://yourdomain.com/callback"  # Replace with your callback URL

def get_access_token():
    """
    Retrieves the access token from Safaricom Daraja API.
    """
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Could not obtain access token: " + response.text)

@mpesa_bp.route('/mpesa_payment', methods=['POST'])
def mpesa_payment():
    """
    Processes an MPesa payment via Safaricom Daraja.
    Expects a JSON payload with 'phone', 'amount', and 'product'.
    """
    data = request.get_json()
    phone = data.get('phone')
    amount = data.get('amount')
    product = data.get('product')

    if not phone or not amount or not product:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        access_token = get_access_token()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Generate timestamp and password for the STK push request
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = BUSINESS_SHORTCODE + PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode('utf-8')).decode('utf-8')

    stk_payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,          # The phone number sending the money
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone,       # The phone number to be charged
        "CallBackURL": CALLBACK_URL,
        "AccountReference": product,
        "TransactionDesc": f"Payment for {product}"
    }

    stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(stk_push_url, json=stk_payload, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
