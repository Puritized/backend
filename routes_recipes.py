from flask import Blueprint, request, jsonify
import openai
import os

recipes_bp = Blueprint("recipes", __name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@recipes_bp.route("/generate", methods=["POST"])
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
        return jsonify({"recipe": recipe})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
