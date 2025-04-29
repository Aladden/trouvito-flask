# src/models/__init__.py
# This file makes the models directory a Python package
# Import models here to make them easily accessible

from .user import db, User
from .category import Category
from .location import Location
from .advertisement import Advertisement, AdImage
from .message import Message
from .rating_review import RatingReview

# You can optionally define __all__ to control imports with *
__all__ = ["db", "User", "Category", "Location", "Advertisement", "AdImage", "Message", "RatingReview"]

