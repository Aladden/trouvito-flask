# src/models/location.py
from .user import db # Use the existing db instance

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    # Add more specific fields if needed, e.g., neighborhood

    # Relationship
    ads = db.relationship("Advertisement", back_populates="location", lazy=True)

    # Ensure unique combination of region and city
    __table_args__ = (db.UniqueConstraint("region", "city", name="_region_city_uc"),)

    def __repr__(self):
        return f"<Location {self.city}, {self.region}>"

