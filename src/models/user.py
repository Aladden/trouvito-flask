# src/models/user.py
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for stronger hashes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_info = db.Column(db.Text, nullable=True)

    # Relationships
    ads = db.relationship("Advertisement", back_populates="user", lazy=True, cascade="all, delete-orphan")
    sent_messages = db.relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", lazy=True, cascade="all, delete-orphan")
    received_messages = db.relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", lazy=True, cascade="all, delete-orphan")
    reviews_written = db.relationship("RatingReview", foreign_keys="RatingReview.reviewer_id", back_populates="reviewer", lazy=True, cascade="all, delete-orphan")
    reviews_received = db.relationship("RatingReview", foreign_keys="RatingReview.reviewed_user_id", back_populates="reviewed_user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

    # Flask-Login required properties/methods are inherited from UserMixin
    # get_id is automatically handled if primary key is named 'id'

