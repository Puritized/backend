import os
import hmac
import hashlib
import requests
from flask import Blueprint, request, jsonify, current_app
from app import db
from models import User

payments_bp = Blueprint("payments", __name__)

PAYSTACK_INIT_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_AMOUNT_NGN = int(os.getenv("PAYSTACK_AMOUNT_NGN", "1000"))
PAYSTACK_CALLBACK_URL = os.getenv("PAYSTACK_CALLBACK_URL")

@payments_bp.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400

    amount_kobo = PAYSTACK_AMOUNT_NGN * 100
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "amount": amount_kobo,
        "callback_url": PAYSTACK_CALLBACK_URL,
        "metadata": {"email": email}
    }
    r = requests.post(PAYSTACK_INIT_URL, json=payload, headers=headers, timeout=15)
    if r.status_code != 200:
        return jsonify({"error": "Paystack init failed", "detail": r.text}), 500
    data = r.json()
    if not data.get("status"):
        return jsonify({"error": "Paystack error", "detail": data}), 500
    return jsonify({"authorization_url": data["data"].get("authorization_url"), "reference": data["data"].get("reference")})

@payments_bp.route("/webhook", methods=["POST"])
def paystack_webhook():
    # Verify signature
    signature = request.headers.get("x-paystack-signature")
    payload = request.get_data()
    computed = hmac.new(PAYSTACK_SECRET.encode(), payload, hashlib.sha512).hexdigest()
    if signature != computed:
        return jsonify({"error": "invalid signature"}), 400

    event = request.json or {}
    if event.get("event") == "charge.success":
        data = event.get("data", {})
        customer_email = (data.get("customer") or {}).get("email") or (data.get("metadata") or {}).get("email")
        if customer_email:
            user = User.query.filter_by(email=customer_email).first()
            if user:
                user.is_premium = True
                db.session.commit()
    return jsonify({"status": "ok"}), 200