from flask import abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import PuntoVendita
from services import get_client_detail, get_order_detail, get_sales_orders, get_sales_points
from utils import get_company_email


def register_punto_vendita_routes(app):
    @app.route("/punto-vendita")
    def punto_vendita():
        return redirect(url_for("punto_vendita_gestione"))

    @app.route("/punto-vendita/gestione")
    def punto_vendita_gestione():
        selected_point_vat = (request.args.get("point_vat") or "").strip()
        return render_template(
            "sales_points_table.html",
            title="Gestione Punti Vendita",
            subtitle="Visualizza, aggiungi o modifica i punti vendita della tua azienda.",
            table_id="punti-vendita-table",
            sales_points=get_sales_points(point_vat=selected_point_vat or None),
            selected_point_vat=selected_point_vat,
            save_action=url_for("punto_vendita_gestione_salva"),
        )

    @app.route("/punto-vendita/gestione/salva", methods=["POST"])
    def punto_vendita_gestione_salva():
        company_email = get_company_email()
        if not company_email:
            return redirect(url_for("login"))

        original_vats = request.form.getlist("original_vat[]")
        vat_numbers = request.form.getlist("vat_number[]")
        names = request.form.getlist("name[]")
        addresses = request.form.getlist("address[]")
        opening_hours_values = request.form.getlist("opening_hours[]")
        channels = request.form.getlist("channel[]")

        submitted_rows = list(
            zip(original_vats, vat_numbers, names, addresses, opening_hours_values, channels)
        )
        existing_sales_points = {
            sales_point.partita_iva: sales_point
            for sales_point in PuntoVendita.query.filter_by(email_azienda_agricola=company_email).all()
        }
        processed_original_vats = set()

        try:
            for (
                original_vat_raw,
                vat_number_raw,
                name_raw,
                address_raw,
                opening_hours_raw,
                channel_raw,
            ) in submitted_rows:
                original_vat = (original_vat_raw or "").strip()
                vat_number = (vat_number_raw or "").strip()
                name = (name_raw or "").strip()
                address = (address_raw or "").strip()
                opening_hours = (opening_hours_raw or "").strip()
                channel = (channel_raw or "").strip()

                if not any([original_vat, vat_number, name, address, opening_hours, channel]):
                    continue

                if not all([vat_number, name, address, channel]):
                    flash("Ogni punto vendita deve avere P. IVA, nome, indirizzo e tipo.", "danger")
                    return redirect(url_for("punto_vendita_gestione"))

                if channel not in {"Online", "Fisico"}:
                    flash("Il tipo del punto vendita deve essere Online o Fisico.", "danger")
                    return redirect(url_for("punto_vendita_gestione"))

                if original_vat:
                    sales_point = existing_sales_points.get(original_vat)
                    if sales_point is None:
                        flash("Un punto vendita non esiste più nel database. Ricarica la pagina e riprova.", "danger")
                        return redirect(url_for("punto_vendita_gestione"))
                    processed_original_vats.add(original_vat)
                else:
                    if vat_number in existing_sales_points:
                        flash("Esiste già un punto vendita con questa P. IVA.", "danger")
                        return redirect(url_for("punto_vendita_gestione"))
                    sales_point = PuntoVendita(email_azienda_agricola=company_email)
                    db.session.add(sales_point)

                sales_point.partita_iva = vat_number
                sales_point.nome = name
                sales_point.indirizzo = address
                sales_point.orari_apertura = opening_hours or None
                sales_point.online = channel == "Online"
                sales_point.negozio_fisico = channel == "Fisico"

            for original_vat, sales_point in existing_sales_points.items():
                if original_vat not in processed_original_vats:
                    db.session.delete(sales_point)

            db.session.commit()
            flash("Punti vendita salvati correttamente.", "success")
        except IntegrityError:
            db.session.rollback()
            flash(
                "Salvataggio non riuscito per un vincolo del database. Controlla P. IVA duplicate o punti vendita collegati agli ordini.",
                "danger",
            )
        except Exception:
            db.session.rollback()
            flash("Salvataggio punti vendita non riuscito. Riprova.", "danger")

        return redirect(url_for("punto_vendita_gestione"))

    @app.route("/punto-vendita/online")
    def punto_vendita_online():
        selected_point_vat = (request.args.get("point_vat") or "").strip()
        return render_template(
            "readonly_orders_table.html",
            title="Punto Vendita Online",
            subtitle="Elenco ordini clienti del canale online.",
            orders=get_sales_orders("online", point_vat=selected_point_vat or None),
            sales_points=get_sales_points("online"),
            selected_point_vat=selected_point_vat,
            filter_endpoint="punto_vendita_online",
            detail_endpoint="punto_vendita_online_cliente",
            order_detail_endpoint="punto_vendita_online_ordine",
            show_online_fields=True,
        )

    @app.route("/punto-vendita/fisico")
    def punto_vendita_fisico():
        selected_point_vat = (request.args.get("point_vat") or "").strip()
        return render_template(
            "readonly_orders_table.html",
            title="Punto Vendita Fisico",
            subtitle="Elenco ordini clienti del punto vendita fisico.",
            orders=get_sales_orders("fisico", point_vat=selected_point_vat or None),
            sales_points=get_sales_points("fisico"),
            selected_point_vat=selected_point_vat,
            filter_endpoint="punto_vendita_fisico",
            detail_endpoint="punto_vendita_fisico_cliente",
            order_detail_endpoint="punto_vendita_fisico_ordine",
            show_online_fields=False,
        )

    @app.route("/punto-vendita/online/cliente/<int:client_id>")
    def punto_vendita_online_cliente(client_id):
        client = get_client_detail("online", client_id)
        if client is None:
            abort(404)
        return render_template(
            "client_orders_detail.html",
            title=f"Cliente {client['name']} {client['surname']}",
            subtitle="Scheda cliente in sola lettura.",
            client=client,
        )

    @app.route("/punto-vendita/fisico/cliente/<int:client_id>")
    def punto_vendita_fisico_cliente(client_id):
        client = get_client_detail("fisico", client_id)
        if client is None:
            abort(404)
        return render_template(
            "client_orders_detail.html",
            title=f"Cliente {client['name']} {client['surname']}",
            subtitle="Scheda cliente in sola lettura.",
            client=client,
        )

    @app.route("/punto-vendita/online/ordine/<order_id>")
    def punto_vendita_online_ordine(order_id):
        order = get_order_detail("online", order_id)
        if order is None:
            abort(404)
        return render_template(
            "order_detail.html",
            title=f"Ordine {order['order_id']}",
            subtitle="Scheda ordine in sola lettura.",
            order=order,
        )

    @app.route("/punto-vendita/fisico/ordine/<order_id>")
    def punto_vendita_fisico_ordine(order_id):
        order = get_order_detail("fisico", order_id)
        if order is None:
            abort(404)
        return render_template(
            "order_detail.html",
            title=f"Ordine {order['order_id']}",
            subtitle="Scheda ordine in sola lettura.",
            order=order,
        )
