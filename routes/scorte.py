from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, request, url_for

from extensions import db
from models import Scorta
from services import get_inventory_records
from utils import get_company_email


def register_scorte_routes(app):
    @app.route("/scorte")
    def scorte():
        return render_template(
            "inventory_table.html",
            title="Scorte",
            subtitle="Visualizza le disponibilita di magazzino e aggiorna il prezzo unitario.",
            table_heading="Elenco scorte",
            inventory_records=get_inventory_records(),
            save_action=url_for("scorte_salva"),
        )

    @app.route("/scorte/salva", methods=["POST"])
    def scorte_salva():
        company_email = get_company_email()
        if not company_email:
            return redirect(url_for("login"))

        years = request.form.getlist("year[]")
        crop_varieties = request.form.getlist("crop_variety[]")
        crop_species = request.form.getlist("crop_species[]")
        prices = request.form.getlist("price[]")

        submitted_rows = list(zip(years, crop_varieties, crop_species, prices))
        stock_rows = {
            (str(stock.anno), stock.varieta_coltura, stock.specie_coltura): stock
            for stock in Scorta.query.filter_by(email_azienda_agricola=company_email).all()
        }

        try:
            for year_raw, crop_variety_raw, crop_species_raw, price_raw in submitted_rows:
                stock_key = (
                    (year_raw or "").strip(),
                    (crop_variety_raw or "").strip(),
                    (crop_species_raw or "").strip(),
                )
                if not all(stock_key):
                    continue

                stock_row = stock_rows.get(stock_key)
                if stock_row is None:
                    flash("Una riga scorte non esiste più nel database. Ricarica la pagina e riprova.", "danger")
                    db.session.rollback()
                    return redirect(url_for("scorte"))

                normalized_price = (price_raw or "").strip().replace("€", "").replace(",", ".")
                stock_row.prezzo_unitario = Decimal(normalized_price or "0")

            db.session.commit()
            flash("Prezzi scorte salvati correttamente.", "success")
        except (InvalidOperation, ValueError):
            db.session.rollback()
            flash("Inserisci un prezzo valido nelle scorte.", "danger")
        except Exception:
            db.session.rollback()
            flash("Salvataggio scorte non riuscito. Riprova.", "danger")

        return redirect(url_for("scorte"))
