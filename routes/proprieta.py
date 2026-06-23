from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Appezzamento, Stabilimento, TerrenoAgricolo
from services import get_terrains
from utils import get_company_email


def register_proprieta_routes(app):
    @app.route("/immobili")
    def immobili():
        return redirect(url_for("proprieta_stabilimenti"))

    @app.route("/proprieta")
    def proprieta():
        return redirect(url_for("proprieta_stabilimenti"))

    @app.route("/proprieta/stabilimenti")
    def proprieta_stabilimenti():
        company_email = get_company_email()
        facilities = Stabilimento.query.filter_by(email_azienda_agricola=company_email).all()
        rows = [
            [
                facility.descrizione,
                facility.estensione,
                facility.anno_acquisto,
                facility.latitudine,
                facility.longitudine,
            ]
            for facility in facilities
        ]
        return render_template(
            "editable_table.html",
            title="Stabilimenti",
            subtitle="Visualizza o aggiungi gli stabilimenti aziendali.",
            table_id="stabilimenti-table",
            columns=["Descrizione", "Estensione", "Anno", "Latitudine", "Longitudine"],
            rows=rows,
            save_action=url_for("proprieta_stabilimenti_salva"),
            field_names=["descrizione", "estensione", "anno_acquisto", "latitudine", "longitudine"],
            required_column_indexes=[0, 1, 2, 3, 4],
        )

    @app.route("/proprieta/stabilimenti/salva", methods=["POST"])
    def proprieta_stabilimenti_salva():
        company_email = get_company_email()
        if not company_email:
            return redirect(url_for("login"))

        latitudini = request.form.getlist("latitudine[]")
        longitudini = request.form.getlist("longitudine[]")
        anni = request.form.getlist("anno_acquisto[]")
        descrizioni = request.form.getlist("descrizione[]")
        estensioni = request.form.getlist("estensione[]")

        new_rows = []

        for latitudine_raw, longitudine_raw, anno_raw, descrizione_raw, estensione_raw in zip(
            latitudini, longitudini, anni, descrizioni, estensioni
        ):
            latitudine_raw = (latitudine_raw or "").strip()
            longitudine_raw = (longitudine_raw or "").strip()
            anno_raw = (anno_raw or "").strip()
            descrizione = (descrizione_raw or "").strip()
            estensione_raw = (estensione_raw or "").strip()

            if not any([latitudine_raw, longitudine_raw, anno_raw, descrizione, estensione_raw]):
                continue

            if not all([latitudine_raw, longitudine_raw, anno_raw, descrizione, estensione_raw]):
                flash("Ogni riga di stabilimento deve essere completa.", "danger")
                return redirect(url_for("proprieta_stabilimenti"))

            try:
                new_rows.append(
                    Stabilimento(
                        email_azienda_agricola=company_email,
                        latitudine=Decimal(latitudine_raw),
                        longitudine=Decimal(longitudine_raw),
                        anno_acquisto=int(anno_raw),
                        descrizione=descrizione,
                        estensione=Decimal(estensione_raw),
                    )
                )
            except (InvalidOperation, ValueError):
                flash("Inserisci valori validi per coordinate, anno ed estensione.", "danger")
                return redirect(url_for("proprieta_stabilimenti"))

        try:
            Stabilimento.query.filter_by(email_azienda_agricola=company_email).delete()
            for facility in new_rows:
                db.session.add(facility)
            db.session.commit()
            flash("Stabilimenti salvati correttamente.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Controlla le coordinate: ci sono duplicati o dati non validi.", "danger")
        except Exception:
            db.session.rollback()
            flash("Salvataggio non riuscito. Riprova.", "danger")

        return redirect(url_for("proprieta_stabilimenti"))

    @app.route("/proprieta/terreni")
    def proprieta_terreni():
        return render_template(
            "terrains_table.html",
            title="Terreni",
            subtitle="Visualizza, modifica o aggiungi i terreni e apri i relativi appezzamenti.",
            table_id="terreni-table",
            terrains=get_terrains(),
            save_action=url_for("proprieta_terreni_salva"),
        )

    @app.route("/proprieta/terreni/salva", methods=["POST"])
    def proprieta_terreni_salva():
        company_email = get_company_email()
        if not company_email:
            return redirect(url_for("login"))

        latitudini = request.form.getlist("latitude[]")
        longitudini = request.form.getlist("longitude[]")
        anni = request.form.getlist("year[]")
        descrizioni = request.form.getlist("description[]")
        tipi_terreno = request.form.getlist("terrain_type[]")
        estensioni = request.form.getlist("surface[]")

        submitted_rows = list(zip(latitudini, longitudini, anni, descrizioni, tipi_terreno, estensioni))
        updated_terrains = {}

        for latitudine_raw, longitudine_raw, anno_raw, descrizione_raw, tipo_raw, estensione_raw in submitted_rows:
            latitudine_raw = (latitudine_raw or "").strip()
            longitudine_raw = (longitudine_raw or "").strip()
            anno_raw = (anno_raw or "").strip()
            descrizione = (descrizione_raw or "").strip()
            tipo_terreno = (tipo_raw or "").strip()
            estensione_raw = (estensione_raw or "").strip()

            if not any(
                [latitudine_raw, longitudine_raw, anno_raw, descrizione, tipo_terreno, estensione_raw]
            ):
                continue

            if not all(
                [latitudine_raw, longitudine_raw, anno_raw, descrizione, tipo_terreno, estensione_raw]
            ):
                flash("Completa tutti i campi della riga terreno prima di salvare.", "danger")
                return redirect(url_for("proprieta_terreni"))

            try:
                latitudine = Decimal(latitudine_raw)
                longitudine = Decimal(longitudine_raw)
                anno = int(anno_raw)
                estensione = Decimal(estensione_raw)
            except (InvalidOperation, ValueError):
                flash(
                    "Inserisci valori validi per coordinate, anno ed estensione dei terreni.",
                    "danger",
                )
                return redirect(url_for("proprieta_terreni"))

            key = (latitudine, longitudine)
            if key in updated_terrains:
                flash("Ci sono due terreni con le stesse coordinate. Controlla i dati inseriti.", "danger")
                return redirect(url_for("proprieta_terreni"))

            updated_terrains[key] = {
                "anno_acquisto": anno,
                "descrizione": descrizione,
                "tipologia_terreno": tipo_terreno,
                "estensione": estensione,
            }

        existing_terrains = {
            (terrain.latitudine, terrain.longitudine): terrain
            for terrain in TerrenoAgricolo.query.filter_by(email_azienda_agricola=company_email).all()
        }
        terrain_keys_to_remove = set(existing_terrains.keys()) - set(updated_terrains.keys())

        for latitudine, longitudine in terrain_keys_to_remove:
            has_plots = Appezzamento.query.filter_by(
                email_azienda_agricola=company_email,
                latitudine_terreno_agricolo=latitudine,
                longitudine_terreno_agricolo=longitudine,
            ).first()
            if has_plots:
                flash(
                    "Non puoi rimuovere o cambiare le coordinate di un terreno che ha già appezzamenti collegati.",
                    "danger",
                )
                return redirect(url_for("proprieta_terreni"))

        try:
            for key, terrain_data in updated_terrains.items():
                existing_terrain = existing_terrains.get(key)
                if existing_terrain:
                    existing_terrain.anno_acquisto = terrain_data["anno_acquisto"]
                    existing_terrain.descrizione = terrain_data["descrizione"]
                    existing_terrain.tipologia_terreno = terrain_data["tipologia_terreno"]
                    existing_terrain.estensione = terrain_data["estensione"]
                else:
                    db.session.add(
                        TerrenoAgricolo(
                            email_azienda_agricola=company_email,
                            latitudine=key[0],
                            longitudine=key[1],
                            anno_acquisto=terrain_data["anno_acquisto"],
                            descrizione=terrain_data["descrizione"],
                            tipologia_terreno=terrain_data["tipologia_terreno"],
                            estensione=terrain_data["estensione"],
                        )
                    )

            for key in terrain_keys_to_remove:
                db.session.delete(existing_terrains[key])

            db.session.commit()
            flash("Terreni salvati correttamente.", "success")
        except IntegrityError:
            db.session.rollback()
            flash(
                "Salvataggio terreni non riuscito per un vincolo del database. Controlla coordinate e collegamenti.",
                "danger",
            )
        except Exception:
            db.session.rollback()
            flash("Salvataggio terreni non riuscito. Riprova.", "danger")

        return redirect(url_for("proprieta_terreni"))
