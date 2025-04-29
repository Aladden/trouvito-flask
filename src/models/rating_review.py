# src/models/rating_review.py
from .user import db # Use the existing db instance
from datetime import datetime

class RatingReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) # e.g., 1 to 5 stars
    review_text = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # Optional: Link review to a specific ad transaction
    # advertisement_id = db.Column(db.Integer, db.ForeignKey("advertisement.id"), nullable=True)

    # Relationships
    reviewer = db.relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_written")
    reviewed_user = db.relationship("User", foreign_keys=[reviewed_user_id], back_populates="reviews_received")
    # advertisement = db.relationship("Advertisement") # If linking to ads

    # Ensure a user can only review another user once (or once per transaction if linked to ad)
    # __table_args__ = (db.UniqueConstraint("reviewer_id", "reviewed_user_id", name="_reviewer_reviewed_uc"),)
    # Consider if multiple reviews should be allowed, perhaps linked to specific ads/transactions.
    # For now, allowing multiple reviews between users.

    def __repr__(self):
        return f"<RatingReview by {self.reviewer_id} for {self.reviewed_user_id} - {self.rating} stars>"

