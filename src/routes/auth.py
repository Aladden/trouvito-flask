# src/routes/auth.py
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    # Use request.json if submitting via fetch with JSON, or request.form for direct form submission
    # Assuming fetch with JSON based on plan to improve UX
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input: No JSON data received"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user) # Log in the user immediately after registration
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username
        }
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    # Assuming fetch with JSON
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input: No JSON data received"}), 400

    login_identifier = data.get("login_identifier") # Expecting email or username
    password = data.get("password")

    if not login_identifier or not password:
        return jsonify({"error": "Missing login identifier or password"}), 400

    user = User.query.filter((User.email == login_identifier) | (User.username == login_identifier)).first()

    if user and user.check_password(password):
        login_user(user, remember=True) # Remember session
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username
            }
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    # No redirect needed if handled by frontend JS
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route("/status")
def status():
    if current_user.is_authenticated:
        return jsonify({
            "logged_in": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            }
        })
    else:
        return jsonify({"logged_in": False})

