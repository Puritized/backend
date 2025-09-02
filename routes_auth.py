from flask import Blueprint, request, jsonify
from models import db, User
import hashlib

auth_bp = Blueprint("auth", __name__)

# ---------------------------
# Helper: Hash Password
# ---------------------------
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------
# Register Route
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

    # Use SHA-256 hash instead of Werkzeug
    hashed_pw = hash_password(password)

    user = User(email=email, password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ---------------------------
# Login Route
# ---------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    # Compare SHA-256 hashes
    if user and user.password_hash == hash_password(password):
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401
