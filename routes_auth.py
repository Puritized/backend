from flask import Blueprint, request, jsonify
import jwt, datetime
from models import db, User

auth_bp = Blueprint("auth", __name__)
SECRET_KEY = "your_secret_key"  # put in env in production!

# ---------------------------
# Register
# ---------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    # Simple hash (not Werkzeug)
    import hashlib
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    user = User(email=email, password_hash=hashed_pw, is_premium=False)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ---------------------------
# Login
# ---------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    import hashlib
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    if hashed_pw != user.password_hash:
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "token": token,
        "is_premium": user.is_premium
    }), 200
