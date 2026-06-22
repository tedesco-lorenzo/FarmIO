from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Appezzamento, Assegnazione, InterventoOperativo, RisorsaMateriale, Soggetto, Utilizzo
from services import (
    get_equipment_options,
    get_intervention_plot_options,
    get_intervention_rows,
    get_machinery_options,
    get_subject_options,
)
from utils import get_company_email, parse_datetime_input


def register_interventi_routes(app):
    @app.route("/interventi-operativi/salva", methods=["POST"])
    def interventi_operativi_salva():
        company_email = get_company_email()
        if not company_email:
            return redirect(url_for("login"))

        start_values = request.form.getlist("start_at[]")
        end_values = request.form.getlist("end_at[]")
        description_values = request.form.getlist("description[]")
        subject_values = request.form.getlist("subjects[]")
        machinery_values = request.form.getlist("machinery[]")
        equipment_values = request.form.getlist("equipment[]")
        plot_values = request.form.getlist("plot[]")

        submitted_rows = list(
            zip(
                start_values,
                end_values,
                description_values,
                subject_values,
                machinery_values,
                equipment_values,
                plot_values,
            )
        )

        valid_plot_ids = {
            plot.id_appezzamento
            for plot in Appezzamento.query.filter_by(email_azienda_agricola=company_email).all()
        }
        valid_subject_ids = {
            subject.id_soggetto
            for subject in Soggetto.query.filter_by(email_azienda_agricola=company_email).all()
        }
        valid_resources = {
            resource.id_risorsa_materiale: resource
            for resource in RisorsaMateriale.query.filter_by(email_azienda_agricola=company_email).all()
        }

        validated_rows = []
        seen_keys = set()

        for (
            start_raw,
            end_raw,
            description_raw,
            subjects_raw,
            machinery_raw,
            equipment_raw,
            plot_raw,
        ) in submitted_rows:
            start_raw = (start_raw or "").strip()
            end_raw = (end_raw or "").strip()
            description = (description_raw or "").strip()
            plot_raw = (plot_raw or "").strip()
            subjects_raw = (subjects_raw or "").strip()
            machinery_raw = (machinery_raw or "").strip()
            equipment_raw = (equipment_raw or "").strip()

            if not any([start_raw, end_raw, description, plot_raw, subjects_raw, machinery_raw, equipment_raw]):
                continue

            if not start_raw or not description or not plot_raw:
                flash("Ogni intervento deve avere almeno inizio, descrizione e appezzamento.", "danger")
                return redirect(url_for("interventi_operativi"))

            start_at = parse_datetime_input(start_raw)
            if start_at is None:
                flash("La data/ora di inizio non è valida. Usa per esempio 22/06/2026 14:30.", "danger")
                return redirect(url_for("interventi_operativi"))

            end_at = None
            if end_raw:
                end_at = parse_datetime_input(end_raw)
                if end_at is None:
                    flash("La data/ora di fine non è valida. Usa per esempio 22/06/2026 16:00.", "danger")
                    return redirect(url_for("interventi_operativi"))
                if end_at < start_at:
                    flash("La data/ora di fine non può essere prima dell'inizio.", "danger")
                    return redirect(url_for("interventi_operativi"))

            try:
                plot_id = int(plot_raw)
            except ValueError:
                flash("Appezzamento non valido.", "danger")
                return redirect(url_for("interventi_operativi"))

            if plot_id not in valid_plot_ids:
                flash("L'appezzamento selezionato non appartiene all'azienda loggata.", "danger")
                return redirect(url_for("interventi_operativi"))

            key = (start_at, plot_id)
            if key in seen_keys:
                flash("Ci sono due interventi con lo stesso inizio e lo stesso appezzamento.", "danger")
                return redirect(url_for("interventi_operativi"))
            seen_keys.add(key)

            subject_ids = []
            if subjects_raw:
                try:
                    subject_ids = sorted({int(value) for value in subjects_raw.split(",") if value.strip()})
                except ValueError:
                    flash("Uno dei soggetti selezionati non è valido.", "danger")
                    return redirect(url_for("interventi_operativi"))
                if not set(subject_ids).issubset(valid_subject_ids):
                    flash("Uno dei soggetti selezionati non appartiene all'azienda loggata.", "danger")
                    return redirect(url_for("interventi_operativi"))

            machinery_ids = []
            if machinery_raw:
                try:
                    machinery_ids = sorted({int(value) for value in machinery_raw.split(",") if value.strip()})
                except ValueError:
                    flash("Uno dei macchinari selezionati non è valido.", "danger")
                    return redirect(url_for("interventi_operativi"))

            equipment_ids = []
            if equipment_raw:
                try:
                    equipment_ids = sorted({int(value) for value in equipment_raw.split(",") if value.strip()})
                except ValueError:
                    flash("Una delle attrezzature selezionate non è valida.", "danger")
                    return redirect(url_for("interventi_operativi"))

            all_resource_ids = machinery_ids + equipment_ids
            for resource_id in all_resource_ids:
                resource = valid_resources.get(resource_id)
                if resource is None:
                    flash("Una delle risorse selezionate non appartiene all'azienda loggata.", "danger")
                    return redirect(url_for("interventi_operativi"))
                if resource_id in machinery_ids and not resource.macchina_agricola:
                    flash("Una risorsa selezionata nei macchinari non è un macchinario.", "danger")
                    return redirect(url_for("interventi_operativi"))
                if resource_id in equipment_ids and not resource.attrezzatura:
                    flash("Una risorsa selezionata nelle attrezzature non è una attrezzatura.", "danger")
                    return redirect(url_for("interventi_operativi"))

            validated_rows.append(
                {
                    "start_at": start_at,
                    "end_at": end_at,
                    "description": description,
                    "plot_id": plot_id,
                    "subject_ids": subject_ids,
                    "resource_ids": sorted(set(all_resource_ids)),
                }
            )

        try:
            company_plot_ids = list(valid_plot_ids)
            if company_plot_ids:
                company_interventions = InterventoOperativo.query.filter(
                    InterventoOperativo.id_appezzamento.in_(company_plot_ids)
                ).all()
                for intervention in company_interventions:
                    Assegnazione.query.filter_by(
                        id_appezzamento=intervention.id_appezzamento,
                        data_ora_inizio_intervento_operativo=intervention.data_ora_inizio,
                        email_azienda_agricola=company_email,
                    ).delete()
                    Utilizzo.query.filter_by(
                        id_appezzamento=intervention.id_appezzamento,
                        data_ora_inizio_intervento_operativo=intervention.data_ora_inizio,
                    ).delete()
                    db.session.delete(intervention)

            for row in validated_rows:
                db.session.add(
                    InterventoOperativo(
                        data_ora_inizio=row["start_at"],
                        data_ora_fine=row["end_at"],
                        descrizione=row["description"],
                        id_appezzamento=row["plot_id"],
                    )
                )

                for subject_id in row["subject_ids"]:
                    db.session.add(
                        Assegnazione(
                            id_appezzamento=row["plot_id"],
                            data_ora_inizio_intervento_operativo=row["start_at"],
                            email_azienda_agricola=company_email,
                            id_soggetto=subject_id,
                        )
                    )

                for resource_id in row["resource_ids"]:
                    db.session.add(
                        Utilizzo(
                            id_risorsa_materiale=resource_id,
                            id_appezzamento=row["plot_id"],
                            data_ora_inizio_intervento_operativo=row["start_at"],
                        )
                    )

            db.session.commit()
            flash("Interventi operativi salvati correttamente.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Salvataggio interventi non riuscito per un vincolo del database.", "danger")
        except Exception:
            db.session.rollback()
            flash("Salvataggio interventi non riuscito. Riprova.", "danger")

        return redirect(url_for("interventi_operativi"))

    @app.route("/interventi-operativi")
    def interventi_operativi():
        return render_template(
            "operational_interventions.html",
            title="Interventi Operativi",
            subtitle="Visualizza, aggiungi o modifica gli interventi operativi.",
            table_id="interventi-operativi-table",
            save_action=url_for("interventi_operativi_salva"),
            rows=get_intervention_rows(),
            machinery_options=get_machinery_options(),
            equipment_options=get_equipment_options(),
            plot_options=get_intervention_plot_options(),
            subject_options=get_subject_options(),
        )
