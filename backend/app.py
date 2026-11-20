import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.database.db import init_db, DB_PATH
from backend.routes.auth_routes import auth_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.student_routes import student_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.ml_routes import ml_bp
from backend.routes.dataset_routes import dataset_bp
from backend.routes.report_routes import report_bp

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
    app.config.from_object(Config)

    # Enable CORS for frontend dev server & production
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Auto-initialize DB if not present
    if not os.path.exists(DB_PATH):
        print("Database not found. Initializing database schema...")
        init_db()

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(report_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "CampusTrack AI Backend",
            "version": "1.0.0"
        }), 200

    # Unified SPA Frontend Serving: serve index.html for all non-API routes if built
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return jsonify({"error": "Resource not found"}), 404
        if os.path.exists(FRONTEND_DIST):
            file_path = os.path.join(FRONTEND_DIST, path)
            if path and os.path.exists(file_path):
                return send_from_directory(FRONTEND_DIST, path)
            return send_from_directory(FRONTEND_DIST, "index.html")
        return jsonify({
            "service": "CampusTrack AI API Server",
            "status": "Running",
            "message": "Frontend is running separately on http://localhost:5173"
        })

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error occurred"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting CampusTrack AI API server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
