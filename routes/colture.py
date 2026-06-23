from flask import render_template

from services import get_crop_rows


def register_colture_routes(app):
    @app.route("/colture")
    def colture():
        return render_template(
            "readonly_inventory_table.html",
            title="Colture",
            subtitle="Archivio di consultazione con specie, varietà e descrizioni delle colture disponibili.",
            table_heading="Archivio colture",
            columns=["Specie", "Varietà", "Descrizione"],
            rows=get_crop_rows(),
        )
