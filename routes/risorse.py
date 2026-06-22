from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import RisorsaMateriale, SchedaManutenzione
from services import (
    get_maintenance_rows,
    get_next_maintenance_id,
    get_resource_by_id,
    get_resource_label,
    get_resources,
)
from utils import get_company_email


def save_resources(resource_type):
    company_email = get_company_email()
    if not company_email:
        return redirect(url_for("login"))

    resource_ids = request.form.getlist("resource_id[]")
    brands = request.form.getlist("brand[]")
    models = request.form.getlist("model[]")
    years = request.form.getlist("year[]")
    extra_values = request.form.getlist("extra_value[]")
    prices = request.form.getlist("price[]")

    submitted_rows = list(zip(resource_ids, brands, models, years, extra_values, prices))

    query = RisorsaMateriale.query.filter_by(email_azienda_agricola=company_email)
    if resource_type == "macchinari":
        query = query.filter_by(macchina_agricola=True)
    else:
        query = query.filter_by(attrezzatura=True)

    existing_resources = {resource.id_risorsa_materiale: resource for resource in query.all()}
    new_resources = {}

    for resource_id_raw, brand_raw, model_raw, year_raw, extra_raw, price_raw in submitted_rows:
        resource_id_raw = (resource_id_raw or "").strip()
        brand = (brand_raw or "").strip()
        model = (model_raw or "").strip()
        year_raw = (year_raw or "").strip()
        extra_value = (extra_raw or "").strip()
        price_raw = (price_raw or "").strip().replace("€", "").replace(",", ".")

        if not any([resource_id_raw, brand, model, year_raw, extra_value, price_raw]):
            continue

        if not all([brand, model, year_raw, price_raw]):
            flash("Completa marca, modello, anno e prezzo prima di salvare la risorsa.", "danger")
            return redirect(
                url_for("risorse_macchinari" if resource_type == "macchinari" else "risorse_attrezzature")
            )

        try:
            year = int(year_raw)
            price = Decimal(price_raw)
        except (InvalidOperation, ValueError):
            flash("Anno o prezzo non validi nelle risorse materiali.", "danger")
            return redirect(
                url_for("risorse_macchinari" if resource_type == "macchinari" else "risorse_attrezzature")
            )

        quantity = None
        plate = None
        if resource_type == "attrezzature":
            if extra_value:
                try:
                    quantity = int(extra_value)
                except ValueError:
                    flash("La quantità delle attrezzature deve essere un numero intero.", "danger")
                    return redirect(url_for("risorse_attrezzature"))
        else:
            plate = extra_value or None

        if resource_id_raw:
            try:
                resource_id = int(resource_id_raw)
            except ValueError:
                flash("ID risorsa non valido.", "danger")
                return redirect(
                    url_for("risorse_macchinari" if resource_type == "macchinari" else "risorse_attrezzature")
                )
        else:
            resource_id = None

        key = resource_id if resource_id is not None else f"new-{len(new_resources) + 1}"
        if key in new_resources:
            flash("Ci sono risorse duplicate nella tabella. Controlla i dati inseriti.", "danger")
            return redirect(
                url_for("risorse_macchinari" if resource_type == "macchinari" else "risorse_attrezzature")
            )

        new_resources[key] = {
            "brand": brand,
            "model": model,
            "year": year,
            "plate": plate,
            "price": price,
            "quantity": quantity,
            "resource_id": resource_id,
        }

    existing_ids = set(existing_resources.keys())
    kept_ids = {data["resource_id"] for data in new_resources.values() if data["resource_id"] is not None}
    resources_to_remove = existing_ids - kept_ids

    try:
        for resource_data in new_resources.values():
            resource_id = resource_data["resource_id"]
            if resource_id is not None and resource_id in existing_resources:
                resource = existing_resources[resource_id]
                resource.marca = resource_data["brand"]
                resource.modello = resource_data["model"]
                resource.anno_acquisto = resource_data["year"]
                resource.targa = resource_data["plate"]
                resource.prezzo = resource_data["price"]
                resource.quantita = resource_data["quantity"]
            else:
                db.session.add(
                    RisorsaMateriale(
                        email_azienda_agricola=company_email,
                        marca=resource_data["brand"],
                        modello=resource_data["model"],
                        anno_acquisto=resource_data["year"],
                        targa=resource_data["plate"],
                        prezzo=resource_data["price"],
                        quantita=resource_data["quantity"],
                        macchina_agricola=(resource_type == "macchinari"),
                        attrezzatura=(resource_type == "attrezzature"),
                    )
                )

        for resource_id in resources_to_remove:
            db.session.delete(existing_resources[resource_id])

        db.session.commit()
        flash(
            "Macchinari salvati correttamente."
            if resource_type == "macchinari"
            else "Attrezzature salvate correttamente.",
            "success",
        )
    except IntegrityError:
        db.session.rollback()
        flash(
            "Salvataggio non riuscito per un vincolo del database. Controlla se la risorsa è collegata ad altri dati.",
            "danger",
        )
    except Exception:
        db.session.rollback()
        flash("Salvataggio risorse non riuscito. Riprova.", "danger")

    return redirect(url_for("risorse_macchinari" if resource_type == "macchinari" else "risorse_attrezzature"))


def render_resource_maintenance_page(resource_type, resource_id):
    resource = get_resource_by_id(resource_id, resource_type)
    if resource is None:
        abort(404)

    resource_label = get_resource_label(resource)
    resource_page_endpoint = "risorse_macchinari" if resource_type == "macchinari" else "risorse_attrezzature"
    save_endpoint = (
        "risorse_macchinari_manutenzioni_salva"
        if resource_type == "macchinari"
        else "risorse_attrezzature_manutenzioni_salva"
    )

    return render_template(
        "maintenance_table.html",
        title="Scheda manutenzione",
        subtitle=f"Storico manutenzioni di {resource_label}.",
        table_id=f"manutenzioni-{resource_type}-{resource_id}",
        maintenances=get_maintenance_rows(resource_id),
        next_maintenance_id=get_next_maintenance_id(resource_id),
        save_action=url_for(save_endpoint, resource_id=resource_id),
        resource_type=resource_type,
        resource_id=resource_id,
        resource_label=resource_label,
        resource_page_url=url_for(resource_page_endpoint),
    )


def save_resource_maintenances(resource_type, resource_id):
    resource = get_resource_by_id(resource_id, resource_type)
    if resource is None:
        abort(404)

    maintenance_ids = request.form.getlist("maintenance_id[]")
    dates = request.form.getlist("date[]")
    costs = request.form.getlist("cost[]")
    descriptions = request.form.getlist("description[]")

    submitted_rows = list(zip(maintenance_ids, dates, costs, descriptions))
    existing_maintenances = {
        maintenance.id_manutenzione: maintenance
        for maintenance in SchedaManutenzione.query.filter_by(id_risorsa_materiale=resource_id).all()
    }
    next_maintenance_id = max(existing_maintenances.keys(), default=0) + 1
    new_maintenances = {}

    for maintenance_id_raw, date_raw, cost_raw, description_raw in submitted_rows:
        maintenance_id_raw = (maintenance_id_raw or "").strip()
        date_raw = (date_raw or "").strip()
        cost_raw = (cost_raw or "").strip().replace("€", "").replace(",", ".")
        description = (description_raw or "").strip()

        if not any([maintenance_id_raw, date_raw, cost_raw, description]):
            continue

        if not all([date_raw, cost_raw, description]):
            flash("Ogni manutenzione deve avere data, costo e descrizione.", "danger")
            return redirect(
                url_for(
                    "risorse_macchinari_manutenzioni"
                    if resource_type == "macchinari"
                    else "risorse_attrezzature_manutenzioni",
                    resource_id=resource_id,
                )
            )

        parsed_date = None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                parsed_date = datetime.strptime(date_raw, fmt).date()
                break
            except ValueError:
                continue
        if parsed_date is None:
            flash("La data manutenzione deve essere nel formato GG/MM/AAAA.", "danger")
            return redirect(
                url_for(
                    "risorse_macchinari_manutenzioni"
                    if resource_type == "macchinari"
                    else "risorse_attrezzature_manutenzioni",
                    resource_id=resource_id,
                )
            )

        try:
            parsed_cost = Decimal(cost_raw)
        except InvalidOperation:
            flash("Il costo manutenzione non è valido.", "danger")
            return redirect(
                url_for(
                    "risorse_macchinari_manutenzioni"
                    if resource_type == "macchinari"
                    else "risorse_attrezzature_manutenzioni",
                    resource_id=resource_id,
                )
            )

        if maintenance_id_raw:
            try:
                maintenance_id = int(maintenance_id_raw)
            except ValueError:
                flash("ID manutenzione non valido.", "danger")
                return redirect(
                    url_for(
                        "risorse_macchinari_manutenzioni"
                        if resource_type == "macchinari"
                        else "risorse_attrezzature_manutenzioni",
                        resource_id=resource_id,
                    )
                )
        else:
            maintenance_id = next_maintenance_id
            next_maintenance_id += 1

        if maintenance_id in new_maintenances:
            flash("Ci sono manutenzioni duplicate nella tabella.", "danger")
            return redirect(
                url_for(
                    "risorse_macchinari_manutenzioni"
                    if resource_type == "macchinari"
                    else "risorse_attrezzature_manutenzioni",
                    resource_id=resource_id,
                )
            )

        new_maintenances[maintenance_id] = {
            "data": parsed_date,
            "costo_manutenzione": parsed_cost,
            "descrizione": description,
        }

    maintenance_ids_to_remove = set(existing_maintenances.keys()) - set(new_maintenances.keys())

    try:
        for maintenance_id, maintenance_data in new_maintenances.items():
            maintenance = existing_maintenances.get(maintenance_id)
            if maintenance:
                maintenance.data = maintenance_data["data"]
                maintenance.costo_manutenzione = maintenance_data["costo_manutenzione"]
                maintenance.descrizione = maintenance_data["descrizione"]
            else:
                db.session.add(
                    SchedaManutenzione(
                        id_risorsa_materiale=resource_id,
                        id_manutenzione=maintenance_id,
                        data=maintenance_data["data"],
                        costo_manutenzione=maintenance_data["costo_manutenzione"],
                        descrizione=maintenance_data["descrizione"],
                    )
                )

        for maintenance_id in maintenance_ids_to_remove:
            db.session.delete(existing_maintenances[maintenance_id])

        db.session.commit()
        flash("Scheda manutenzione salvata correttamente.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Salvataggio manutenzioni non riuscito per un vincolo del database.", "danger")
    except Exception:
        db.session.rollback()
        flash("Salvataggio manutenzioni non riuscito. Riprova.", "danger")

    return redirect(
        url_for(
            "risorse_macchinari_manutenzioni"
            if resource_type == "macchinari"
            else "risorse_attrezzature_manutenzioni",
            resource_id=resource_id,
        )
    )


def register_risorse_routes(app):
    @app.route("/risorse-materiali")
    def risorse_materiali():
        return redirect(url_for("risorse_attrezzature"))

    @app.route("/risorse-materiali/attrezzature")
    def risorse_attrezzature():
        return render_template(
            "resources_table.html",
            title="Attrezzature",
            subtitle="Visualizza o aggiungi le attrezzature aziendali.",
            table_id="attrezzature-table",
            resources=get_resources("attrezzature"),
            save_action=url_for("risorse_attrezzature_salva"),
            resource_type="attrezzature",
            extra_column_label="Quantità",
            extra_required=False,
        )

    @app.route("/risorse-materiali/attrezzature/salva", methods=["POST"])
    def risorse_attrezzature_salva():
        return save_resources("attrezzature")

    @app.route("/risorse-materiali/attrezzature/<int:resource_id>/manutenzioni")
    def risorse_attrezzature_manutenzioni(resource_id):
        return render_resource_maintenance_page("attrezzature", resource_id)

    @app.route("/risorse-materiali/attrezzature/<int:resource_id>/manutenzioni/salva", methods=["POST"])
    def risorse_attrezzature_manutenzioni_salva(resource_id):
        return save_resource_maintenances("attrezzature", resource_id)

    @app.route("/risorse-materiali/macchinari")
    def risorse_macchinari():
        return render_template(
            "resources_table.html",
            title="Macchinari",
            subtitle="Visualizza o aggiungi i macchinari aziendali.",
            table_id="macchinari-table",
            resources=get_resources("macchinari"),
            save_action=url_for("risorse_macchinari_salva"),
            resource_type="macchinari",
            extra_column_label="Targa",
            extra_required=False,
        )

    @app.route("/risorse-materiali/macchinari/salva", methods=["POST"])
    def risorse_macchinari_salva():
        return save_resources("macchinari")

    @app.route("/risorse-materiali/macchinari/<int:resource_id>/manutenzioni")
    def risorse_macchinari_manutenzioni(resource_id):
        return render_resource_maintenance_page("macchinari", resource_id)

    @app.route("/risorse-materiali/macchinari/<int:resource_id>/manutenzioni/salva", methods=["POST"])
    def risorse_macchinari_manutenzioni_salva(resource_id):
        return save_resource_maintenances("macchinari", resource_id)
