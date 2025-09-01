import os
import json
import openai
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, app
from models import User, Favorite

recipes_bp = Blueprint("recipes", __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def _parse_json_from_text(text):
    # try to extract JSON if model wraps in fences
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
    try:
        return json.loads(text)
    except Exception:
        # last resort: return raw as list of lines
        return {"recipes": [{"id": i, "name": line, "ingredients": [], "instructions": ""} 
                             for i, line in enumerate(text.splitlines(), 1) if line.strip()]}

@recipes_bp.route("/recipes", methods=["POST"])
def free_recipes():
    """Free (short) recipes: no auth required"""
    data = request.get_json() or {}
    ingredients = data.get("ingredients", "")
    number = int(data.get("number", 5))
    prompt = f"Give {number} short recipe suggestions (title, ingredients list, 3 short steps) using: {ingredients}. Return JSON object with key 'recipes' which is an array. Each recipe: id (int), name (string), ingredients (array), instructions (string)."
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a concise cooking assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )
        text = resp["choices"][0]["message"]["content"]
        parsed = _parse_json_from_text(text)
    except Exception as e:
        return jsonify({"error": "OpenAI error", "detail": str(e)}), 500
    return jsonify(parsed)

@recipes_bp.route("/premium/recipes", methods=["POST"])
@jwt_required()
def premium_recipes():
    """Premium recipes: user must be premium"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_premium:
        return jsonify({"error": "premium account required"}), 403
    data = request.get_json() or {}
    ingredients = data.get("ingredients", "")
    number = int(data.get("number", 5))
    prompt = (
        f"Provide {number} detailed recipes using: {ingredients}. For each recipe provide: id, name, ingredients (with approximate quantities), "
        "step-by-step instructions (detailed), estimated prep and cook times, and short nutrition summary. Return valid JSON with key 'recipes'."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini" if os.getenv("OPENAI_MODEL") else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert chef and nutritionist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1200
        )
        text = resp["choices"][0]["message"]["content"]
        parsed = _parse_json_from_text(text)
    except Exception as e:
        return jsonify({"error": "OpenAI error", "detail": str(e)}), 500
    return jsonify(parsed)

# Favorites endpoints (free for logged-in users)
@recipes_bp.route("/favorites/add", methods=["POST"])
@jwt_required()
def add_favorite():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    recipe_name = data.get("recipe_name")
    ingredients = data.get("ingredients", [])
    instructions = data.get("instructions", "")
    if not recipe_name:
        return jsonify({"error": "recipe_name required"}), 400
    fav = Favorite(user_id=user_id, recipe_name=recipe_name,
                   ingredients="||".join(ingredients), instructions=instructions)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "saved"}), 201

@recipes_bp.route("/favorites/list", methods=["GET"])
@jwt_required()
def list_favorites():
    user_id = get_jwt_identity()
    favs = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).all()
    out = []
    for f in favs:
        out.append({
            "id": f.id,
            "recipe_name": f.recipe_name,
            "ingredients": f.ingredients.split("||") if f.ingredients else [],
            "instructions": f.instructions
        })
    return jsonify(out)