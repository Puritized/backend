from flask import Blueprint, request, jsonify
import openai
import os

# Attach url_prefix to match frontend expectation
recipes_bp = Blueprint("recipes", __name__, url_prefix="/api/recipes")

openai.api_key = os.getenv("OPENAI_API_KEY")

@recipes_bp.route("", methods=["POST"])  # <-- POST /api/recipes
def generate_recipe():
    data = request.get_json()
    ingredients = data.get("ingredients")

    if not ingredients:
        return jsonify({"error": "Please provide ingredients"}), 400

    try:
        prompt = f"Create a simple recipe using the following ingredients: {ingredients}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        recipe = response.choices[0].text.strip()
        return jsonify({"recipes": [recipe]})  # frontend expects "recipes"
    except Exception as e:
        return jsonify({"error": str(e)}), 500
