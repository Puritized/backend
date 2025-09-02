import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Recipe Generator ===
def generate_recipe(ingredients):
    """Use OpenAI API to generate a recipe based on given ingredients"""
    prompt = f"Suggest a detailed recipe using these ingredients: {', '.join(ingredients)}. Include steps and measurements."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating recipe: {str(e)}"


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/")

    # App configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-secret")

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Import models AFTER db is initialized
    from models import User, Favorite  

    # Import blueprints
    from routes_auth import auth_bp
    from routes_recipes import recipes_bp
    from routes_payments import payments_bp
    from routes_favorites import favorites_bp   # new favorites routes

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(recipes_bp, url_prefix="/api/recipes")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(favorites_bp, url_prefix="/api/favorites")

    # Serve frontend
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    # Auto-create tables (not for production migrations)
    with app.app_context():
        db.create_all()

    return app


# Entry point for Gunicorn
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
