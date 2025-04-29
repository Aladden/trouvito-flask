# src/routes/user.py
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models import db, User, Advertisement, RatingReview

user_bp = Blueprint("user", __name__)

# Get current user's profile data (for profile page)
@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user_ads = Advertisement.query.filter_by(user_id=current_user.id).order_by(Advertisement.created_at.desc()).all()
    user_reviews = RatingReview.query.filter_by(reviewed_user_id=current_user.id).order_by(RatingReview.timestamp.desc()).all()

    ads_data = [
        {
            "id": ad.id,
            "title": ad.title,
            "status": ad.status,
            "created_at": ad.created_at.isoformat(),
            "category": ad.category.name if ad.category else None,
            "location": f"{ad.location.city}, {ad.location.region}" if ad.location else None
        } for ad in user_ads
    ]

    reviews_data = [
        {
            "id": review.id,
            "rating": review.rating,
            "review_text": review.review_text,
            "timestamp": review.timestamp.isoformat(),
            "reviewer": {
                "id": review.reviewer.id,
                "username": review.reviewer.username
            }
        } for review in user_reviews
    ]

    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "profile_info": current_user.profile_info,
        "created_at": current_user.created_at.isoformat(),
        "ads": ads_data,
        "reviews": reviews_data
    })

# Update current user's profile
@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.json
    email = data.get("email")
    profile_info = data.get("profile_info")
    # Password change could be handled in a separate endpoint

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Check if email is already taken by another user
    existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        return jsonify({"error": "Email already in use by another account"}), 409

    current_user.email = email
    current_user.profile_info = profile_info
    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "profile_info": current_user.profile_info
        }
    })

# Get public profile data for a specific user
@user_bp.route("/<int:user_id>/profile", methods=["GET"])
def get_public_profile(user_id):
    user = User.query.get_or_404(user_id)
    user_ads = Advertisement.query.filter_by(user_id=user.id, status='active').order_by(Advertisement.created_at.desc()).all()
    user_reviews = RatingReview.query.filter_by(reviewed_user_id=user.id).order_by(RatingReview.timestamp.desc()).all()

    ads_data = [
        {
            "id": ad.id,
            "title": ad.title,
            "price": ad.price,
            "created_at": ad.created_at.isoformat(),
            "category": ad.category.name if ad.category else None,
            "location": f"{ad.location.city}, {ad.location.region}" if ad.location else None,
            "image": ad.images[0].image_path if ad.images else None # Get first image path
        } for ad in user_ads
    ]

    reviews_data = [
        {
            "id": review.id,
            "rating": review.rating,
            "review_text": review.review_text,
            "timestamp": review.timestamp.isoformat(),
            "reviewer": {
                "id": review.reviewer.id,
                "username": review.reviewer.username
            }
        } for review in user_reviews
    ]

    # Calculate average rating
    average_rating = db.session.query(db.func.avg(RatingReview.rating)).filter(RatingReview.reviewed_user_id == user.id).scalar()

    return jsonify({
        "id": user.id,
        "username": user.username,
        "profile_info": user.profile_info,
        "created_at": user.created_at.isoformat(),
        "ads": ads_data,
        "reviews": reviews_data,
        "average_rating": round(average_rating, 1) if average_rating else None,
        "review_count": len(user_reviews)
    })

