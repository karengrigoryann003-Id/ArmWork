"""ArmWork Python backend։

Այս ֆայլը start է անում Flask API-ն և նույն server-ից տալիս է Frontend ֆայլերը։
Այդպես ուրիշ սարքից բացելիս պետք է միայն մեկ հասցե՝ http://ՔՈ-IP:5050/։
"""

from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.user_routes import user_bp

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "Frontend"


def create_app():
    app = Flask(__name__)

    # Թույլ ենք տալիս frontend-ին կանչել API-ն նաև local թեստերի ժամանակ։
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(chat_bp, url_prefix="/api/chats")

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok", "project": "ArmWork", "database": Config.DB_TYPE})

    @app.get("/")
    def frontend_index():
        """Բացում է կայքի գլխավոր էջը նույն Flask server-ից։"""
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/<path:file_path>")
    def frontend_files(file_path):
        """Տալիս է Frontend-ի html/css/js ֆայլերը։"""
        if file_path.startswith("api/"):
            abort(404)

        requested_file = FRONTEND_DIR / file_path
        if requested_file.is_file():
            return send_from_directory(FRONTEND_DIR, file_path)

        abort(404)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)
