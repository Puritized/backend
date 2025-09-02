from flask import Blueprint, request, jsonify
import requests
import os

payments_bp = Blueprint("payments", __name__)

# Load Paystack secret key
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"


@payments_bp.route("/initialize", methods=["POST"])
def initialize_payment():
    """Initialize a Paystack transaction"""
    data = request.get_json()
    email = data.get("email")
    amount = data.get("amount")  # amount in kobo (e.g., 50000 = ₦500)

    if not email or not amount:
        return jsonify({"error": "Email and amount are required"}), 400

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": email,
        "amount": amount,
        "callback_url": "https://your-frontend-domain.com/payment/callback"
    }

    try:
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            json=payload,
            headers=headers
        )
        result = response.json()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payments_bp.route("/verify/<reference>", methods=["GET"])
def verify_payment(reference):
    """Verify a Paystack transaction"""
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    }

    try:
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=headers
        )
        result = response.json()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
