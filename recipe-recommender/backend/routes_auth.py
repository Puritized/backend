from flask import Blueprint, request, jsonify
from app import db
from models import User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from app import app

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 400
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "registered"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token, "is_premium": user.is_premium})
