from flask import Flask, redirect, render_template, request, session, url_for

from extensions import db
from routes import register_routes
from utils import PUBLIC_ENDPOINTS, test_database_connection


def create_app():
    app = Flask(__name__)
    app.secret_key = "farmio-dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost:3306/farmio?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    db.init_app(app)
    register_routes(app)

    @app.before_request
    def require_authentication():
        endpoint = request.endpoint
        if endpoint in PUBLIC_ENDPOINTS:
            return None
        if endpoint is None:
            if session.get("authenticated"):
                return None
            return redirect(url_for("login"))
        if session.get("authenticated"):
            return None
        return redirect(url_for("login"))

    @app.route("/404")
    def page_404():
        return render_template("404.html"), 404

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    try:
        with app.app_context():
            test_database_connection()
        print("Connessione MySQL attiva.")
    except Exception as exc:
        print(f"Connessione MySQL non riuscita: {exc}")

    app.run(debug=True, use_reloader=False)
