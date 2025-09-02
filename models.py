from datetime import datetime
from app import db

# ---------------------------
# User Model
# ---------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)  # Premium flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one user -> many favorites
    favorites = db.relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}, Premium={self.is_premium}>"

# ---------------------------
# Favorite Recipes Model
# ---------------------------
class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_name = db.Column(db.String(255), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = db.relationship("User", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite {self.recipe_name} by User {self.user_id}>"

# ---------------------------
# Payment / Subscription Tracking (Optional, good for debugging)
# ---------------------------
class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reference = db.Column(db.String(255), unique=True, nullable=False)  # Paystack reference
    amount = db.Column(db.Integer, nullable=False)  # Stored in kobo
    status = db.Column(db.String(50), default="pending")  # pending, success, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="payments")

    def __repr__(self):
        return f"<Payment {self.reference}, Status={self.status}>"
