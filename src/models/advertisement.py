# src/models/advertisement.py
from .user import db # Use the existing db instance
from datetime import datetime

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True) # Optional price
    status = db.Column(db.String(20), default='active', nullable=False) # e.g., 'active', 'inactive', 'hidden', 'sold'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="ads")
    category = db.relationship("Category", back_populates="ads")
    location = db.relationship("Location", back_populates="ads")
    images = db.relationship("AdImage", back_populates="advertisement", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Advertisement {self.title}>"

class AdImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False) # Path to the uploaded image file
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'), nullable=False)

    # Relationship
    advertisement = db.relationship("Advertisement", back_populates="images")

    def __repr__(self):
        return f"<AdImage {self.image_path} for Ad {self.advertisement_id}>"

