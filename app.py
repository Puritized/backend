import os
import hmac
import hashlib
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-secret")

db = SQLAlchemy(app)

# import models after db instantiated
from models import User, Favorite

# Blueprints
from routes_auth import auth_bp
from routes_recipes import recipes_bp
from routes_payments import payments_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(recipes_bp, url_prefix="/api")
app.register_blueprint(payments_bp, url_prefix="/api/payments")

# Serve frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    # create tables if not exist
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
