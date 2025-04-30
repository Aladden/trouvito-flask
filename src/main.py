import os
import sys

# Ensure we can import from the parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_login import LoginManager
from src.models import db, User
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.ad import ad_bp
from src.routes.message import message_bp
from src.routes.review import review_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# ✅ HARD-CODED MySQL DATABASE CONNECTION
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://trouvito_user:yourStrongPassword@localhost:3306/trouvito"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login.html'  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(ad_bp, url_prefix='/api/ads')
app.register_blueprint(message_bp, url_prefix='/api/messages')
app.register_blueprint(review_bp, url_prefix='/api/reviews')

# Create all tables if not already present
with app.app_context():
    db.create_all()

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# Serve static HTML (like index.html)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    full_path = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Local dev runner
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
