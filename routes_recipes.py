from flask import Blueprint, request, jsonify
from app import client  # import the OpenAI client from app.py

recipes_bp = Blueprint("recipes", __name__)

# --- POST /api/recipes (generate recipe) ---
@recipes_bp.route("", methods=["POST"])
def generate_recipe():
    data = request.get_json()
    ingredients = data.get("ingredients")

    if not ingredients:
        return jsonify({"error": "Please provide ingredients"}), 400

    try:
        prompt = f"Create a simple recipe using the following ingredients: {', '.join(ingredients)}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        recipe = response.choices[0].message.content.strip()

        return jsonify({"recipes": [recipe]})
    except Exception as e:
        print("Error in /api/recipes:", e)  # logs to server
        return jsonify({"error": "Failed to generate recipe"}), 500


# --- GET /api/recipes (sample/fallback) ---
@recipes_bp.route("", methods=["GET"])
def get_recipes():
    try:
        # Example: static list or fetch from DB
        sample_recipes = [
            {"id": 1, "title": "Jollof Rice"},
            {"id": 2, "title": "Fried Plantain"}
        ]
        return jsonify(sample_recipes)
    except Exception as e:
        print("Error in GET /api/recipes:", e)
        return jsonify({"error": "Failed to load recipes"}), 500
