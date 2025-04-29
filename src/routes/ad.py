# src/routes/ad.py
import os
import sys
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from src.models import db, Advertisement, AdImage, Category, Location, User

ad_bp = Blueprint("ad", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Get list of ads (with basic filtering)
@ad_bp.route("", methods=["GET"])
def get_ads():
    # Add query parameters for filtering, searching, pagination later
    query = Advertisement.query.filter_by(status="active").order_by(Advertisement.created_at.desc())

    # Example filtering (can be expanded)
    category_id = request.args.get("category_id")
    location_id = request.args.get("location_id")
    search_term = request.args.get("search")

    if category_id:
        query = query.filter(Advertisement.category_id == category_id)
    if location_id:
        query = query.filter(Advertisement.location_id == location_id)
    if search_term:
        query = query.filter(Advertisement.title.ilike(f"%{search_term}%"))

    ads = query.all()

    ads_data = [
        {
            "id": ad.id,
            "title": ad.title,
            "price": ad.price,
            "created_at": ad.created_at.isoformat(),
            "category": ad.category.name if ad.category else None,
            "location": f"{ad.location.city}, {ad.location.region}" if ad.location else None,
            "image": ad.images[0].image_path if ad.images else None, # First image
            "user": {
                "id": ad.user.id,
                "username": ad.user.username
            }
        } for ad in ads
    ]
    return jsonify(ads_data)

# Get details for a specific ad
@ad_bp.route("/<int:ad_id>", methods=["GET"])
def get_ad_details(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)

    # Optionally hide non-active ads unless viewed by owner/admin
    # if ad.status != "active" and (not current_user.is_authenticated or ad.user_id != current_user.id):
    #     return jsonify({"error": "Ad not found or not active"}), 404

    images_data = [img.image_path for img in ad.images]
    seller_reviews = RatingReview.query.filter_by(reviewed_user_id=ad.user_id).order_by(RatingReview.timestamp.desc()).all()
    average_rating = db.session.query(db.func.avg(RatingReview.rating)).filter(RatingReview.reviewed_user_id == ad.user_id).scalar()

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
        } for review in seller_reviews
    ]

    return jsonify({
        "id": ad.id,
        "title": ad.title,
        "description": ad.description,
        "price": ad.price,
        "status": ad.status,
        "created_at": ad.created_at.isoformat(),
        "updated_at": ad.updated_at.isoformat(),
        "category": {"id": ad.category.id, "name": ad.category.name} if ad.category else None,
        "location": {"id": ad.location.id, "city": ad.location.city, "region": ad.location.region} if ad.location else None,
        "images": images_data,
        "user": {
            "id": ad.user.id,
            "username": ad.user.username,
            "created_at": ad.user.created_at.isoformat(),
            "average_rating": round(average_rating, 1) if average_rating else None,
            "review_count": len(seller_reviews)
        },
        "seller_reviews": reviews_data
    })

# Create a new ad
@ad_bp.route("", methods=["POST"])
@login_required
def create_ad():
    data = request.form
    files = request.files.getlist("images")

    title = data.get("title")
    description = data.get("description")
    category_id = data.get("category_id")
    location_id = data.get("location_id")
    price = data.get("price")

    if not title or not description or not category_id or not location_id:
        return jsonify({"error": "Missing required fields"}), 400

    # Validate category and location exist
    category = Category.query.get(category_id)
    location = Location.query.get(location_id)
    if not category or not location:
        return jsonify({"error": "Invalid category or location ID"}), 400

    new_ad = Advertisement(
        title=title,
        description=description,
        price=float(price) if price else None,
        user_id=current_user.id,
        category_id=category_id,
        location_id=location_id,
        status="active" # Default status
    )
    db.session.add(new_ad)
    db.session.flush() # Get the ID for the new ad before committing fully

    # Handle image uploads
    image_paths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create a unique filename to avoid collisions
            unique_filename = str(uuid.uuid4()) + "_" + filename
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            try:
                file.save(file_path)
                # Store relative path for web access
                web_path = os.path.join("/static/uploads", unique_filename).replace("\\", "/")
                ad_image = AdImage(advertisement_id=new_ad.id, image_path=web_path)
                db.session.add(ad_image)
                image_paths.append(web_path)
            except Exception as e:
                db.session.rollback() # Rollback if image saving fails
                return jsonify({"error": f"Failed to save image: {e}"}), 500

    db.session.commit()

    return jsonify({
        "message": "Ad created successfully",
        "ad": {
            "id": new_ad.id,
            "title": new_ad.title,
            "images": image_paths
        }
    }), 201

# Update an existing ad
@ad_bp.route("/<int:ad_id>", methods=["PUT"])
@login_required
def update_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)

    if ad.user_id != current_user.id:
        return jsonify({"error": "Forbidden: You can only update your own ads"}), 403

    data = request.json
    ad.title = data.get("title", ad.title)
    ad.description = data.get("description", ad.description)
    ad.price = data.get("price", ad.price)
    ad.category_id = data.get("category_id", ad.category_id)
    ad.location_id = data.get("location_id", ad.location_id)
    # Status changes handled separately

    # Image updates would be more complex (delete old, add new) - potentially handle via separate endpoint or logic

    db.session.commit()
    return jsonify({"message": "Ad updated successfully", "id": ad.id})

# Delete an ad
@ad_bp.route("/<int:ad_id>", methods=["DELETE"])
@login_required
def delete_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)

    if ad.user_id != current_user.id:
        return jsonify({"error": "Forbidden: You can only delete your own ads"}), 403

    # Delete associated images from filesystem (optional but recommended)
    for image in ad.images:
        try:
            # Construct absolute path from web path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            file_path = os.path.join(base_dir, image.image_path.lstrip("/"))
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting image file {image.image_path}: {e}") # Log error

    db.session.delete(ad)
    db.session.commit()
    return jsonify({"message": "Ad deleted successfully"})

# Update ad status (e.g., hide, mark sold, reactivate)
@ad_bp.route("/<int:ad_id>/status", methods=["PATCH"])
@login_required
def update_ad_status(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)

    if ad.user_id != current_user.id:
        return jsonify({"error": "Forbidden: You can only update status for your own ads"}), 403

    data = request.json
    new_status = data.get("status")

    allowed_statuses = ["active", "inactive", "hidden", "sold"]
    if new_status not in allowed_statuses:
        return jsonify({"error": f"Invalid status. Allowed statuses: {', '.join(allowed_statuses)}"}), 400

    ad.status = new_status
    db.session.commit()
    return jsonify({"message": f"Ad status updated to {new_status}", "id": ad.id, "status": ad.status})

# Get categories list
@ad_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.order_by(Category.name).all()
    return jsonify([{"id": cat.id, "name": cat.name} for cat in categories])

# Get locations list
@ad_bp.route("/locations", methods=["GET"])
def get_locations():
    # Consider adding filtering by region if needed
    locations = Location.query.order_by(Location.region, Location.city).all()
    return jsonify([{"id": loc.id, "city": loc.city, "region": loc.region} for loc in locations])

