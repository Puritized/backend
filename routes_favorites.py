from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Favorite

favorites_bp = Blueprint("favorites", __name__, url_prefix="/api/favorites")

# ---------------------------
# Test Route (for debugging)
# ---------------------------
@favorites_bp.route("/test", methods=["GET"])
def test_favorites():
    return jsonify({"message": "Favorites routes working"}), 200


# ---------------------------
# Save a favorite recipe
# ---------------------------
@favorites_bp.route("/", methods=["POST"])
@jwt_required()
def add_favorite():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    recipe_name = data.get("recipe_name")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")

    if not recipe_name or not ingredients or not instructions:
        return jsonify({"error": "Recipe name, ingredients, and instructions are required"}), 400

    favorite = Favorite(
        user_id=user_id,
        recipe_name=recipe_name,
        ingredients=ingredients,
        instructions=instructions,
    )
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": "Recipe saved to favorites"}), 201


# ---------------------------
# Get all favorites for the logged-in user
# ---------------------------
@favorites_bp.route("/", methods=["GET"])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()

    if not favorites:
        return jsonify({"message": "No favorites found"}), 200

    result = [
        {
            "id": fav.id,
            "recipe_name": fav.recipe_name,
            "ingredients": fav.ingredients,
            "instructions": fav.instructions,
            "created_at": fav.created_at.isoformat(),
        }
        for fav in favorites
    ]
    return jsonify(result), 200


# ---------------------------
# Delete a favorite by ID
# ---------------------------
@favorites_bp.route("/<int:favorite_id>", methods=["DELETE"])
@jwt_required()
def delete_favorite(favorite_id):
    user_id = get_jwt_identity()
    favorite = Favorite.query.filter_by(id=favorite_id, user_id=user_id).first()

    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite deleted"}), 200
