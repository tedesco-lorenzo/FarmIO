from flask import flash, redirect, render_template, request, session, url_for

from extensions import db
from models import AziendaAgricola
from utils import create_user_session, normalize_email


def register_auth_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("authenticated"):
            return redirect(url_for("home"))

        error_message = None
        if request.method == "POST":
            email = normalize_email(request.form.get("email"))
            password = request.form.get("password", "")
            try:
                company_account = AziendaAgricola.query.filter_by(email=email).first()
            except Exception:
                company_account = None
                error_message = "Connessione al database non disponibile. Riprova tra poco."

            if error_message is None and (
                company_account is None or company_account.password != password
            ):
                error_message = "Credenziali non valide. Controlla email e password."
            elif error_message is None:
                create_user_session(
                    email=company_account.email,
                    user_name=company_account.denominazione_sociale,
                    role="company",
                    company_email=company_account.email,
                )
                return redirect(url_for("home"))

        return render_template("login.html", error_message=error_message)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if session.get("authenticated"):
            return redirect(url_for("home"))

        error_message = None
        if request.method == "POST":
            company_name = request.form.get("denominazione_sociale", "").strip()
            foundation_year = request.form.get("anno_fondazione", "").strip()
            email = normalize_email(request.form.get("email"))
            password = request.form.get("password", "")
            repeat_password = request.form.get("repeat_password", "")

            if not company_name or not foundation_year or not email or not password:
                error_message = "Compila tutti i campi richiesti."
            elif not foundation_year.isdigit():
                error_message = "Inserisci un anno di fondazione valido."
            elif password != repeat_password:
                error_message = "Le password non coincidono."
            else:
                try:
                    existing_company = AziendaAgricola.query.filter_by(email=email).first()
                except Exception:
                    existing_company = None
                    error_message = "Connessione al database non disponibile. Riprova tra poco."

                if error_message is None and existing_company is not None:
                    error_message = "Esiste gia un utente con questa email."
                elif error_message is None:
                    new_company_account = AziendaAgricola(
                        email=email,
                        denominazione_sociale=company_name,
                        password=password,
                        anno_fondazione=int(foundation_year),
                    )
                    try:
                        db.session.add(new_company_account)
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                        error_message = "Registrazione non riuscita. Controlla i dati e riprova."

                    if error_message is None:
                        create_user_session(
                            email=new_company_account.email,
                            user_name=new_company_account.denominazione_sociale,
                            role="company",
                            company_email=new_company_account.email,
                        )
                        return redirect(url_for("home"))

        return render_template("register.html", error_message=error_message)

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if session.get("authenticated"):
            return redirect(url_for("home"))

        error_message = None
        if request.method == "POST":
            email = normalize_email(request.form.get("email"))
            password = request.form.get("password", "")
            repeat_password = request.form.get("repeat_password", "")

            if not email or not password or not repeat_password:
                error_message = "Compila tutti i campi richiesti."
            elif password != repeat_password:
                error_message = "Le password non coincidono."
            else:
                try:
                    company_account = AziendaAgricola.query.filter_by(email=email).first()
                except Exception:
                    company_account = None
                    error_message = "Connessione al database non disponibile. Riprova tra poco."

                if error_message is None and company_account is None:
                    error_message = "Nessun account trovato con questa email."
                elif error_message is None:
                    try:
                        company_account.password = password
                        db.session.commit()
                        flash("Password aggiornata correttamente. Ora puoi accedere.", "success")
                        return redirect(url_for("login"))
                    except Exception:
                        db.session.rollback()
                        error_message = "Aggiornamento password non riuscito. Riprova."

        return render_template("forgot-password.html", error_message=error_message)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
