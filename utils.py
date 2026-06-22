from datetime import datetime, timedelta
from decimal import Decimal

from flask import session
from sqlalchemy import text

from extensions import db


PUBLIC_ENDPOINTS = {"login", "register", "forgot_password", "logout", "static"}
COMPANY_EMAIL_SESSION_KEY = "azienda_email"


def test_database_connection():
    db.session.execute(text("SELECT 1"))


def normalize_email(value):
    return (value or "").strip().lower()


def get_company_email():
    return session.get(COMPANY_EMAIL_SESSION_KEY)


def format_decimal(value, places=2):
    if value is None:
        return ""
    return f"{Decimal(value):.{places}f}"


def format_date(value):
    if value is None:
        return ""
    return value.strftime("%d/%m/%Y")


def format_time(value):
    if value is None:
        return ""
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    return value.strftime("%H:%M")


def format_datetime(value):
    if value is None:
        return ""
    return value.strftime("%d/%m/%Y %H:%M")


def parse_datetime_input(value):
    normalized = (value or "").strip()
    if not normalized:
        return None

    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%d-%m-%Y %H:%M"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    return None


def parse_date_input(value):
    normalized = (value or "").strip()
    if not normalized:
        return None

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue
    return None


def parse_time_input(value):
    normalized = (value or "").strip()
    if not normalized:
        return None

    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(normalized, fmt).time()
        except ValueError:
            continue
    return None


def format_currency(value):
    if value is None:
        return "-"
    formatted = f"{Decimal(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {formatted}"


def bool_to_si_no(value):
    return "Sì" if value else "No"


def create_user_session(email, user_name, role="user", company_email=None):
    session["authenticated"] = True
    session["user_email"] = email
    session["user_role"] = role
    session["user_name"] = user_name
    session[COMPANY_EMAIL_SESSION_KEY] = company_email or email
