from flask import render_template

from services import get_crop_rows


def register_colture_routes(app):
    @app.route("/colture")
    def colture():
        return render_template(
            "readonly_inventory_table.html",
            title="Colture",
            subtitle="Visualizza tutte le colture disponibili nel database.",
            table_heading="Elenco colture",
            columns=["Varietà", "Specie", "Descrizione"],
            rows=get_crop_rows(),
        )
