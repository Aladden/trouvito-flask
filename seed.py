# seed.py
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app, db # Import app and db from main
from src.models import Category, Location

# Define initial data
categories_data = [
    {"name": "Voitures"},
    {"name": "Propriétés"},
    {"name": "Téléphones"},
    {"name": "Électronique"},
    {"name": "Meubles"},
    {"name": "Emplois"},
    {"name": "Services"},
    {"name": "Communauté"}
]

locations_data = [
    # Add more comprehensive list for Côte d'Ivoire later if needed
    {"city": "Abidjan", "region": "Lagunes"},
    {"city": "Yamoussoukro", "region": "Lacs"},
    {"city": "Bouaké", "region": "Vallée du Bandama"},
    {"city": "Daloa", "region": "Haut-Sassandra"},
    {"city": "San-Pédro", "region": "Bas-Sassandra"},
    {"city": "Korhogo", "region": "Savanes"},
    {"city": "Man", "region": "Montagnes"},
    {"city": "Divo", "region": "Lôh-Djiboua"}
]

def seed_database():
    with app.app_context():
        print("Seeding database...")

        # Seed Categories
        existing_categories = {cat.name for cat in Category.query.all()}
        for cat_data in categories_data:
            if cat_data["name"] not in existing_categories:
                category = Category(name=cat_data["name"])
                db.session.add(category)
                # Use single quotes inside f-string for dictionary keys
                print(f"Added category: {cat_data['name']}")
            else:
                print(f"Category already exists: {cat_data['name']}")

        # Seed Locations
        existing_locations = {(loc.city, loc.region) for loc in Location.query.all()}
        for loc_data in locations_data:
            if (loc_data["city"], loc_data["region"]) not in existing_locations:
                location = Location(city=loc_data["city"], region=loc_data["region"])
                db.session.add(location)
                # Use single quotes inside f-string for dictionary keys
                print(f"Added location: {loc_data['city']}, {loc_data['region']}")
            else:
                print(f"Location already exists: {loc_data['city']}, {loc_data['region']}")

        try:
            db.session.commit()
            print("Database seeding completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during seeding: {e}")

if __name__ == "__main__":
    seed_database()

