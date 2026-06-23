from decimal import Decimal, InvalidOperation

from flask import abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Appezzamento, Coltura, Irrigazione, Raccolta, Trattamento
from services import (
    apply_harvest_changes_to_inventory,
    get_crop_selection_data,
    get_next_plot_id,
    get_plot_history,
    get_plots,
)
from utils import get_company_email, parse_date_input, parse_time_input


def save_plot_history(plot_id, history_type):
    company_email = get_company_email()
    if not company_email:
        return redirect(url_for("login"))

    plot = Appezzamento.query.filter_by(
        id_appezzamento=plot_id,
        email_azienda_agricola=company_email,
    ).first()
    if plot is None:
        abort(404)

    dates = request.form.getlist("date[]")

    try:
        if history_type == "trattamenti":
            water_quantities = request.form.getlist("water_quantity[]")
            product_names = request.form.getlist("product_name[]")
            product_quantities = request.form.getlist("product_quantity[]")
            submitted_rows = list(zip(dates, water_quantities, product_names, product_quantities))
            validated_records = []
            seen_dates = set()

            for date_raw, water_raw, product_raw, quantity_raw in submitted_rows:
                date_raw = (date_raw or "").strip()
                water_raw = (water_raw or "").strip().replace(",", ".")
                product_name = (product_raw or "").strip()
                quantity_raw = (quantity_raw or "").strip().replace(",", ".")

                if not any([date_raw, water_raw, product_name, quantity_raw]):
                    continue

                if not all([date_raw, water_raw, product_name, quantity_raw]):
                    flash(
                        "Ogni trattamento deve avere data, quantità acqua, prodotto e quantità prodotto.",
                        "danger",
                    )
                    return redirect(url_for("appezzamento_trattamenti", plot_id=plot_id))

                parsed_date = parse_date_input(date_raw)
                if parsed_date is None:
                    flash("La data dei trattamenti deve essere nel formato GG/MM/AAAA.", "danger")
                    return redirect(url_for("appezzamento_trattamenti", plot_id=plot_id))

                try:
                    water_quantity = Decimal(water_raw)
                    product_quantity = Decimal(quantity_raw)
                except InvalidOperation:
                    flash("Le quantità dei trattamenti non sono valide.", "danger")
                    return redirect(url_for("appezzamento_trattamenti", plot_id=plot_id))

                if parsed_date in seen_dates:
                    flash(
                        "Non puoi inserire due trattamenti con la stessa data nello stesso appezzamento.",
                        "danger",
                    )
                    return redirect(url_for("appezzamento_trattamenti", plot_id=plot_id))
                seen_dates.add(parsed_date)

                validated_records.append(
                    Trattamento(
                        data=parsed_date,
                        id_appezzamento=plot_id,
                        quantita_acqua=water_quantity,
                        nome_prodotto=product_name,
                        quantita_prodotto=product_quantity,
                    )
                )

            Trattamento.query.filter_by(id_appezzamento=plot_id).delete(synchronize_session=False)
            for treatment_record in validated_records:
                db.session.add(treatment_record)
            success_message = "Storico trattamenti salvato correttamente."
            redirect_endpoint = "appezzamento_trattamenti"

        elif history_type == "irrigazione":
            start_times = request.form.getlist("start_time[]")
            product_names = request.form.getlist("product_name[]")
            product_quantities = request.form.getlist("product_quantity[]")
            submitted_rows = list(zip(dates, start_times, product_names, product_quantities))
            validated_records = []
            seen_dates = set()

            for date_raw, time_raw, product_raw, quantity_raw in submitted_rows:
                date_raw = (date_raw or "").strip()
                time_raw = (time_raw or "").strip()
                product_name = (product_raw or "").strip()
                quantity_raw = (quantity_raw or "").strip().replace(",", ".")

                if not any([date_raw, time_raw, product_name, quantity_raw]):
                    continue

                if not date_raw:
                    flash("Ogni irrigazione deve avere almeno la data.", "danger")
                    return redirect(url_for("appezzamento_irrigazione", plot_id=plot_id))

                parsed_date = parse_date_input(date_raw)
                if parsed_date is None:
                    flash("La data delle irrigazioni deve essere nel formato GG/MM/AAAA.", "danger")
                    return redirect(url_for("appezzamento_irrigazione", plot_id=plot_id))

                parsed_time = parse_time_input(time_raw) if time_raw else None
                if time_raw and parsed_time is None:
                    flash("L'orario irrigazione deve essere nel formato HH:MM.", "danger")
                    return redirect(url_for("appezzamento_irrigazione", plot_id=plot_id))

                if quantity_raw:
                    try:
                        product_quantity = Decimal(quantity_raw)
                    except InvalidOperation:
                        flash("La quantità prodotto dell'irrigazione non è valida.", "danger")
                        return redirect(url_for("appezzamento_irrigazione", plot_id=plot_id))
                else:
                    product_quantity = None

                if parsed_date in seen_dates:
                    flash(
                        "Non puoi inserire due irrigazioni con la stessa data nello stesso appezzamento.",
                        "danger",
                    )
                    return redirect(url_for("appezzamento_irrigazione", plot_id=plot_id))
                seen_dates.add(parsed_date)

                validated_records.append(
                    Irrigazione(
                        data=parsed_date,
                        id_appezzamento=plot_id,
                        ora_inizio=parsed_time,
                        nome_prodotto=product_name or None,
                        quantita_prodotto=product_quantity,
                    )
                )

            Irrigazione.query.filter_by(id_appezzamento=plot_id).delete(synchronize_session=False)
            for irrigation_record in validated_records:
                db.session.add(irrigation_record)
            success_message = "Storico irrigazione salvato correttamente."
            redirect_endpoint = "appezzamento_irrigazione"

        elif history_type == "raccolta":
            harvest_quantities = request.form.getlist("harvest_quantity[]")
            stock_years = request.form.getlist("stock_year[]")
            valid_crops = {(crop.varieta, crop.specie) for crop in Coltura.query.all()}
            crop_variety = plot.varieta_coltura
            crop_species = plot.specie_coltura
            submitted_rows = list(zip(dates, harvest_quantities, stock_years))
            validated_records = []
            seen_dates = set()

            if (crop_variety, crop_species) not in valid_crops:
                flash(
                    "La coltura collegata all'appezzamento non è valida. Controlla varietà e specie dell'appezzamento.",
                    "danger",
                )
                return redirect(url_for("appezzamento_raccolta", plot_id=plot_id))

            for date_raw, quantity_raw, year_raw in submitted_rows:
                date_raw = (date_raw or "").strip()
                quantity_raw = (quantity_raw or "").strip().replace(",", ".")
                year_raw = (year_raw or "").strip()

                if not any([date_raw, quantity_raw, year_raw]):
                    continue

                if not all([date_raw, quantity_raw, year_raw]):
                    flash(
                        "Ogni raccolta deve avere data, quantità e anno scorta.",
                        "danger",
                    )
                    return redirect(url_for("appezzamento_raccolta", plot_id=plot_id))

                parsed_date = parse_date_input(date_raw)
                if parsed_date is None:
                    flash("La data delle raccolte deve essere nel formato GG/MM/AAAA.", "danger")
                    return redirect(url_for("appezzamento_raccolta", plot_id=plot_id))

                try:
                    harvest_quantity = Decimal(quantity_raw)
                    stock_year = int(year_raw)
                except (InvalidOperation, ValueError):
                    flash("Quantità o anno scorta della raccolta non validi.", "danger")
                    return redirect(url_for("appezzamento_raccolta", plot_id=plot_id))

                if parsed_date in seen_dates:
                    flash(
                        "Non puoi inserire due raccolte con la stessa data nello stesso appezzamento.",
                        "danger",
                    )
                    return redirect(url_for("appezzamento_raccolta", plot_id=plot_id))
                seen_dates.add(parsed_date)

                validated_records.append(
                    Raccolta(
                        data=parsed_date,
                        id_appezzamento=plot_id,
                        quantita_raccolta=harvest_quantity,
                        anno_scorta=stock_year,
                        email_azienda_agricola=company_email,
                        varieta_coltura=crop_variety,
                        specie_coltura=crop_species,
                    )
                )

            apply_harvest_changes_to_inventory(
                company_email=company_email,
                plot_id=plot_id,
                new_harvest_records=validated_records,
            )
            db.session.flush()

            Raccolta.query.filter_by(
                id_appezzamento=plot_id,
                email_azienda_agricola=company_email,
            ).delete(synchronize_session=False)
            for harvest_record in validated_records:
                db.session.add(harvest_record)
            success_message = "Storico raccolta salvato correttamente."
            redirect_endpoint = "appezzamento_raccolta"

        else:
            abort(404)

        db.session.commit()
        flash(success_message, "success")
    except ValueError as error:
        db.session.rollback()
        flash(str(error), "danger")
    except IntegrityError:
        db.session.rollback()
        flash(
            "Salvataggio non riuscito per un vincolo del database. Controlla i dati collegati a colture o scorte.",
            "danger",
        )
    except Exception:
        db.session.rollback()
        flash("Salvataggio non riuscito. Riprova.", "danger")

    return redirect(url_for(redirect_endpoint, plot_id=plot_id))


def register_appezzamenti_routes(app):
    @app.route("/appezzamenti")
    def appezzamenti():
        crop_selection_data = get_crop_selection_data()
        return render_template(
            "plots_table.html",
            title="Appezzamenti",
            subtitle="Visualizza, modifica o aggiungi gli appezzamenti e apri lo storico dedicato.",
            plots=get_plots(),
            save_action=url_for("appezzamenti_salva"),
            next_plot_id=get_next_plot_id(),
            crop_varieties=crop_selection_data["crop_varieties"],
            crop_species_by_variety=crop_selection_data["crop_species_by_variety"],
        )

    @app.route("/appezzamenti/salva", methods=["POST"])
    def appezzamenti_salva():
        company_email = get_company_email()
        if not company_email:
            return redirect(url_for("login"))

        plot_numbers = request.form.getlist("plot_number[]")
        soil_compositions = request.form.getlist("soil_composition[]")
        surfaces = request.form.getlist("surface[]")
        covers = request.form.getlist("cover[]")
        antigrandine_values = request.form.getlist("antigrandine[]")
        antibrina_values = request.form.getlist("antibrina[]")
        insurance_covers = request.form.getlist("insurance_cover[]")
        terrain_longitudes = request.form.getlist("terrain_longitude[]")
        terrain_latitudes = request.form.getlist("terrain_latitude[]")
        crop_varieties = request.form.getlist("crop_variety[]")
        crop_species_values = request.form.getlist("crop_species[]")

        submitted_rows = list(
            zip(
                plot_numbers,
                soil_compositions,
                surfaces,
                covers,
                antigrandine_values,
                antibrina_values,
                insurance_covers,
                terrain_longitudes,
                terrain_latitudes,
                crop_varieties,
                crop_species_values,
            )
        )

        existing_plots = {
            plot_record.id_appezzamento: plot_record
            for plot_record in Appezzamento.query.filter_by(email_azienda_agricola=company_email).all()
        }
        valid_crops = {(crop.varieta, crop.specie) for crop in Coltura.query.all()}
        updated_plots = {}

        for (
            plot_number_raw,
            soil_composition_raw,
            surface_raw,
            cover_raw,
            antigrandine_raw,
            antibrina_raw,
            insurance_cover_raw,
            terrain_longitude_raw,
            terrain_latitude_raw,
            crop_variety_raw,
            crop_species_raw,
        ) in submitted_rows:
            plot_number_raw = (plot_number_raw or "").strip()
            soil_composition = (soil_composition_raw or "").strip()
            surface_raw = (surface_raw or "").strip().replace(",", ".")
            cover_value = (cover_raw or "No").strip()
            antigrandine_value = (antigrandine_raw or "No").strip()
            antibrina_value = (antibrina_raw or "No").strip()
            insurance_cover_value = (insurance_cover_raw or "No").strip()
            terrain_longitude_raw = (terrain_longitude_raw or "").strip().replace(",", ".")
            terrain_latitude_raw = (terrain_latitude_raw or "").strip().replace(",", ".")
            crop_variety = (crop_variety_raw or "").strip()
            crop_species = (crop_species_raw or "").strip()

            if not any(
                [
                    soil_composition,
                    surface_raw,
                    terrain_longitude_raw,
                    terrain_latitude_raw,
                    crop_variety,
                    crop_species,
                ]
            ):
                continue

            if not all(
                [
                    plot_number_raw,
                    soil_composition,
                    surface_raw,
                    terrain_longitude_raw,
                    terrain_latitude_raw,
                    crop_variety,
                    crop_species,
                ]
            ):
                flash("Completa tutti i campi obbligatori dell'appezzamento prima di salvare.", "danger")
                return redirect(url_for("appezzamenti"))

            try:
                plot_number = int(plot_number_raw)
                surface = Decimal(surface_raw)
                terrain_longitude = Decimal(terrain_longitude_raw)
                terrain_latitude = Decimal(terrain_latitude_raw)
            except (InvalidOperation, ValueError):
                flash(
                    "Controlla numero, estensione e coordinate degli appezzamenti: alcuni valori non sono validi.",
                    "danger",
                )
                return redirect(url_for("appezzamenti"))

            if plot_number in updated_plots:
                flash("Ci sono due appezzamenti con lo stesso numero. Controlla la tabella.", "danger")
                return redirect(url_for("appezzamenti"))

            if (crop_variety, crop_species) not in valid_crops:
                flash(
                    "La coltura selezionata non è valida. Scegli una varietà e una specie presenti in Colture.",
                    "danger",
                )
                return redirect(url_for("appezzamenti"))

            updated_plots[plot_number] = {
                "composizione_terreno": soil_composition,
                "estensione": surface,
                "tipologia_copertura": "Copertura presente" if cover_value == "Sì" else None,
                "antigrandine": antigrandine_value == "Sì",
                "antibrina": antibrina_value == "Sì",
                "copertura_assicurativa": (
                    "Copertura assicurativa attiva" if insurance_cover_value == "Sì" else None
                ),
                "longitudine_terreno_agricolo": terrain_longitude,
                "latitudine_terreno_agricolo": terrain_latitude,
                "varieta_coltura": crop_variety,
                "specie_coltura": crop_species,
            }

        plots_to_remove = set(existing_plots.keys()) - set(updated_plots.keys())

        try:
            for plot_number, plot_data in updated_plots.items():
                existing_plot = existing_plots.get(plot_number)
                if existing_plot:
                    existing_plot.composizione_terreno = plot_data["composizione_terreno"]
                    existing_plot.estensione = plot_data["estensione"]
                    existing_plot.tipologia_copertura = plot_data["tipologia_copertura"]
                    existing_plot.antigrandine = plot_data["antigrandine"]
                    existing_plot.antibrina = plot_data["antibrina"]
                    existing_plot.copertura_assicurativa = plot_data["copertura_assicurativa"]
                    existing_plot.longitudine_terreno_agricolo = plot_data[
                        "longitudine_terreno_agricolo"
                    ]
                    existing_plot.latitudine_terreno_agricolo = plot_data[
                        "latitudine_terreno_agricolo"
                    ]
                    existing_plot.varieta_coltura = plot_data["varieta_coltura"]
                    existing_plot.specie_coltura = plot_data["specie_coltura"]
                else:
                    db.session.add(
                        Appezzamento(
                            id_appezzamento=plot_number,
                            email_azienda_agricola=company_email,
                            composizione_terreno=plot_data["composizione_terreno"],
                            estensione=plot_data["estensione"],
                            tipologia_copertura=plot_data["tipologia_copertura"],
                            antigrandine=plot_data["antigrandine"],
                            antibrina=plot_data["antibrina"],
                            copertura_assicurativa=plot_data["copertura_assicurativa"],
                            longitudine_terreno_agricolo=plot_data["longitudine_terreno_agricolo"],
                            latitudine_terreno_agricolo=plot_data["latitudine_terreno_agricolo"],
                            varieta_coltura=plot_data["varieta_coltura"],
                            specie_coltura=plot_data["specie_coltura"],
                        )
                    )

            for plot_number in plots_to_remove:
                db.session.delete(existing_plots[plot_number])

            db.session.commit()
            flash("Appezzamenti salvati correttamente.", "success")
        except IntegrityError:
            db.session.rollback()
            flash(
                "Salvataggio appezzamenti non riuscito. Controlla che terreno e coltura esistano già e che l'appezzamento non abbia collegamenti non rimovibili.",
                "danger",
            )
        except Exception:
            db.session.rollback()
            flash("Salvataggio appezzamenti non riuscito. Riprova.", "danger")

        return redirect(url_for("appezzamenti"))

    @app.route("/appezzamenti/<int:plot_id>/trattamenti")
    def appezzamento_trattamenti(plot_id):
        history = get_plot_history(plot_id, "trattamenti")
        if history is None:
            abort(404)
        return render_template(
            "plot_history.html",
            title=f"Storico Trattamenti - Appezzamento {history['plot']['id']}",
            subtitle="Visualizza, aggiungi o modifica lo storico trattamenti del singolo appezzamento.",
            history=history,
        )

    @app.route("/appezzamenti/<int:plot_id>/trattamenti/salva", methods=["POST"])
    def appezzamento_trattamenti_salva(plot_id):
        return save_plot_history(plot_id, "trattamenti")

    @app.route("/appezzamenti/<int:plot_id>/irrigazione")
    def appezzamento_irrigazione(plot_id):
        history = get_plot_history(plot_id, "irrigazione")
        if history is None:
            abort(404)
        return render_template(
            "plot_history.html",
            title=f"Storico Irrigazione - Appezzamento {history['plot']['id']}",
            subtitle="Visualizza, aggiungi o modifica lo storico irrigazione del singolo appezzamento.",
            history=history,
        )

    @app.route("/appezzamenti/<int:plot_id>/irrigazione/salva", methods=["POST"])
    def appezzamento_irrigazione_salva(plot_id):
        return save_plot_history(plot_id, "irrigazione")

    @app.route("/appezzamenti/<int:plot_id>/raccolta")
    def appezzamento_raccolta(plot_id):
        history = get_plot_history(plot_id, "raccolta")
        if history is None:
            abort(404)
        return render_template(
            "plot_history.html",
            title=f"Storico Raccolta - Appezzamento {history['plot']['id']}",
            subtitle="Visualizza, aggiungi o modifica lo storico raccolta del singolo appezzamento.",
            history=history,
        )

    @app.route("/appezzamenti/<int:plot_id>/raccolta/salva", methods=["POST"])
    def appezzamento_raccolta_salva(plot_id):
        return save_plot_history(plot_id, "raccolta")
