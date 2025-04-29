# src/routes/review.py
import os
import sys
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models import db, RatingReview, User, Advertisement

review_bp = Blueprint("review", __name__)

# Create a new review for a user
@review_bp.route("/user/<int:reviewed_user_id>", methods=["POST"])
@login_required
def create_review(reviewed_user_id):
    data = request.json
    rating = data.get("rating")
    review_text = data.get("review_text")
    # advertisement_id = data.get("advertisement_id") # Optional: Link review to a specific transaction/ad

    if not rating:
        return jsonify({"error": "Rating is required"}), 400

    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    reviewed_user = User.query.get(reviewed_user_id)
    if not reviewed_user:
        return jsonify({"error": "User being reviewed not found"}), 404

    if reviewed_user_id == current_user.id:
        return jsonify({"error": "Cannot review yourself"}), 400

    # Optional: Check if user already reviewed this user (or this transaction)
    # existing_review = RatingReview.query.filter_by(reviewer_id=current_user.id, reviewed_user_id=reviewed_user_id).first()
    # if existing_review:
    #     return jsonify({"error": "You have already reviewed this user"}), 409

    new_review = RatingReview(
        rating=rating,
        review_text=review_text,
        reviewer_id=current_user.id,
        reviewed_user_id=reviewed_user_id
        # advertisement_id=advertisement_id # Optional
    )
    db.session.add(new_review)
    db.session.commit()

    return jsonify({
        "message": "Review submitted successfully",
        "review": {
            "id": new_review.id,
            "rating": new_review.rating,
            "review_text": new_review.review_text,
            "timestamp": new_review.timestamp.isoformat(),
            "reviewer_id": new_review.reviewer_id,
            "reviewed_user_id": new_review.reviewed_user_id
        }
    }), 201

# Get reviews for a specific user
@review_bp.route("/user/<int:reviewed_user_id>", methods=["GET"])
def get_reviews_for_user(reviewed_user_id):
    user = User.query.get_or_404(reviewed_user_id)
    reviews = RatingReview.query.filter_by(reviewed_user_id=user.id).order_by(RatingReview.timestamp.desc()).all()

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
        } for review in reviews
    ]

    # Calculate average rating
    average_rating = db.session.query(db.func.avg(RatingReview.rating)).filter(RatingReview.reviewed_user_id == user.id).scalar()

    return jsonify({
        "reviews": reviews_data,
        "average_rating": round(average_rating, 1) if average_rating else None,
        "review_count": len(reviews)
    })

