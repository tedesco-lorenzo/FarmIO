from flask import render_template

from services import get_inventory_rows


def register_scorte_routes(app):
    @app.route("/scorte")
    def scorte():
        return render_template(
            "readonly_inventory_table.html",
            title="Scorte",
            subtitle="Visualizza le disponibilita di magazzino senza possibilita di modifica.",
            table_heading="Elenco scorte",
            columns=["Anno", "Quantità", "Prezzo", "Varietà", "Specie"],
            rows=get_inventory_rows(),
        )
