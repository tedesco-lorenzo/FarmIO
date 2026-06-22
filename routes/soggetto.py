from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import RegistrazioneOre, Soggetto
from services import get_subjects
from utils import format_date, format_decimal, get_company_email


def register_soggetto_routes(app):
    @app.route("/soggetto")
    def soggetto():
        return render_template(
            "subjects_table.html",
            title="Soggetto",
            subtitle="Gestisci persone e aziende esterne in un'unica tabella.",
            table_id="soggetto-table",
            subjects=get_subjects(),
            save_action=url_for("soggetto_salva"),
        )

    @app.route("/soggetto/salva", methods=["POST"])
    def soggetto_salva():
        company_email = get_company_email()
        if not company_email:
            return redirect(url_for("login"))

        subject_ids = request.form.getlist("subject_id[]")
        hourly_pays = request.form.getlist("hourly_pay[]")
        subject_types = request.form.getlist("subject_type[]")
        company_names = request.form.getlist("company_name[]")
        vat_numbers = request.form.getlist("vat_number[]")
        names = request.form.getlist("name[]")
        surnames = request.form.getlist("surname[]")
        birth_dates = request.form.getlist("birth_date[]")
        ibans = request.form.getlist("iban[]")
        tax_codes = request.form.getlist("tax_code[]")
        managers = request.form.getlist("manager[]")

        submitted_rows = list(
            zip(
                subject_ids,
                hourly_pays,
                subject_types,
                company_names,
                vat_numbers,
                names,
                surnames,
                birth_dates,
                ibans,
                tax_codes,
                managers,
            )
        )

        existing_subjects = {
            subject_record.id_soggetto: subject_record
            for subject_record in Soggetto.query.filter_by(email_azienda_agricola=company_email).all()
        }
        next_subject_id = max(existing_subjects.keys(), default=0) + 1
        updated_subjects = {}

        for (
            subject_id_raw,
            hourly_pay_raw,
            subject_type_raw,
            company_name_raw,
            vat_number_raw,
            name_raw,
            surname_raw,
            birth_date_raw,
            iban_raw,
            tax_code_raw,
            manager_raw,
        ) in submitted_rows:
            subject_id_raw = (subject_id_raw or "").strip()
            hourly_pay_raw = (hourly_pay_raw or "").strip().replace("€", "").replace(",", ".")
            subject_type = (subject_type_raw or "").strip()
            company_name = (company_name_raw or "").strip()
            vat_number = (vat_number_raw or "").strip()
            name = (name_raw or "").strip()
            surname = (surname_raw or "").strip()
            birth_date_raw = (birth_date_raw or "").strip()
            iban = (iban_raw or "").strip()
            tax_code = (tax_code_raw or "").strip()
            manager_raw = (manager_raw or "").strip()

            if not any(
                [
                    subject_id_raw,
                    hourly_pay_raw,
                    subject_type,
                    company_name,
                    vat_number,
                    name,
                    surname,
                    birth_date_raw,
                    iban,
                    tax_code,
                    manager_raw,
                ]
            ):
                continue

            if not hourly_pay_raw or not subject_type:
                flash("Ogni soggetto deve avere almeno paga oraria e tipo compilati.", "danger")
                return redirect(url_for("soggetto"))

            if subject_type not in {"Dipendente", "Azienda esterna"}:
                flash("Tipo soggetto non valido.", "danger")
                return redirect(url_for("soggetto"))

            try:
                hourly_pay = Decimal(hourly_pay_raw)
            except InvalidOperation:
                flash("Inserisci una paga oraria valida per ogni soggetto.", "danger")
                return redirect(url_for("soggetto"))

            birth_date = None
            if birth_date_raw:
                parsed = None
                for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                    try:
                        parsed = datetime.strptime(birth_date_raw, fmt).date()
                        break
                    except ValueError:
                        continue
                if parsed is None:
                    flash("La data di nascita deve essere nel formato GG/MM/AAAA.", "danger")
                    return redirect(url_for("soggetto"))
                birth_date = parsed

            is_external = subject_type == "Azienda esterna"
            manager = False if is_external else manager_raw == "Sì"
            operaio = False if is_external else not manager

            if is_external and not company_name:
                flash("Per una azienda esterna devi indicare la ragione sociale.", "danger")
                return redirect(url_for("soggetto"))

            if not is_external and (not name or not surname):
                flash("Per un dipendente devi inserire sia nome che cognome.", "danger")
                return redirect(url_for("soggetto"))

            if subject_id_raw:
                try:
                    subject_id = int(subject_id_raw)
                except ValueError:
                    flash("ID soggetto non valido.", "danger")
                    return redirect(url_for("soggetto"))
            else:
                subject_id = next_subject_id
                next_subject_id += 1

            if subject_id in updated_subjects:
                flash("Ci sono soggetti duplicati nella tabella. Controlla i dati inseriti.", "danger")
                return redirect(url_for("soggetto"))

            updated_subjects[subject_id] = {
                "stipendio_orario": hourly_pay,
                "denominazione_sociale": company_name if is_external else None,
                "azienda_esterna": is_external,
                "partita_iva": vat_number or None,
                "nome": None if is_external else (name or None),
                "cognome": None if is_external else (surname or None),
                "data_nascita": None if is_external else birth_date,
                "iban": None if is_external else (iban or None),
                "codice_fiscale": None if is_external else (tax_code or None),
                "manager": manager,
                "operaio": operaio,
            }

        subjects_to_remove = set(existing_subjects.keys()) - set(updated_subjects.keys())

        try:
            for subject_id, subject_data in updated_subjects.items():
                existing_subject = existing_subjects.get(subject_id)
                if existing_subject:
                    existing_subject.stipendio_orario = subject_data["stipendio_orario"]
                    existing_subject.denominazione_sociale = subject_data["denominazione_sociale"]
                    existing_subject.azienda_esterna = subject_data["azienda_esterna"]
                    existing_subject.partita_iva = subject_data["partita_iva"]
                    existing_subject.nome = subject_data["nome"]
                    existing_subject.cognome = subject_data["cognome"]
                    existing_subject.data_nascita = subject_data["data_nascita"]
                    existing_subject.iban = subject_data["iban"]
                    existing_subject.codice_fiscale = subject_data["codice_fiscale"]
                    existing_subject.manager = subject_data["manager"]
                    existing_subject.operaio = subject_data["operaio"]
                else:
                    db.session.add(
                        Soggetto(
                            email_azienda_agricola=company_email,
                            id_soggetto=subject_id,
                            stipendio_orario=subject_data["stipendio_orario"],
                            denominazione_sociale=subject_data["denominazione_sociale"],
                            azienda_esterna=subject_data["azienda_esterna"],
                            partita_iva=subject_data["partita_iva"],
                            nome=subject_data["nome"],
                            cognome=subject_data["cognome"],
                            data_nascita=subject_data["data_nascita"],
                            iban=subject_data["iban"],
                            codice_fiscale=subject_data["codice_fiscale"],
                            manager=subject_data["manager"],
                            operaio=subject_data["operaio"],
                        )
                    )

            for subject_id in subjects_to_remove:
                db.session.delete(existing_subjects[subject_id])

            db.session.commit()
            flash("Soggetti salvati correttamente.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Salvataggio soggetti non riuscito per un vincolo del database.", "danger")
        except Exception:
            db.session.rollback()
            flash("Salvataggio soggetti non riuscito. Riprova.", "danger")

        return redirect(url_for("soggetto"))

    @app.route("/soggetto/dipendenti")
    def soggetto_dipendenti():
        return redirect(url_for("soggetto"))

    @app.route("/soggetto/dipendenti/ore/<int:employee_id>")
    def soggetto_dipendente_ore(employee_id):
        company_email = get_company_email()
        time_entries = []
        total_hours = Decimal("0.00")

        if company_email:
            time_entries = (
                RegistrazioneOre.query.filter_by(
                    email_azienda_agricola=company_email,
                    id_soggetto=employee_id,
                )
                .order_by(RegistrazioneOre.data.desc())
                .all()
            )
            total_hours = sum((Decimal(time_entry.ore) for time_entry in time_entries), Decimal("0.00"))

        return render_template(
            "employee_hours.html",
            title="Totale ore lavorate",
            employee_id=employee_id,
            total_hours=format_decimal(total_hours),
            columns=["Data", "Ore", "ID"],
            rows=[
                [format_date(time_entry.data), format_decimal(time_entry.ore), str(employee_id)]
                for time_entry in time_entries
            ],
        )

    @app.route("/soggetto/aziende-esterne")
    def soggetto_aziende_esterne():
        return redirect(url_for("soggetto"))
