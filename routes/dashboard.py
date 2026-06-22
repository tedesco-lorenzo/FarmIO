from flask import redirect, render_template, url_for

from services import get_dashboard_data


def register_dashboard_routes(app):
    @app.route("/")
    def home():
        return render_template("index.html", dashboard=get_dashboard_data())
