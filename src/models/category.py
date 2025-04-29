# src/models/category.py
from .user import db # Use the existing db instance

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon_class = db.Column(db.String(50), nullable=True) # Optional: For FontAwesome or similar icons

    # Relationship
    ads = db.relationship("Advertisement", back_populates="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

