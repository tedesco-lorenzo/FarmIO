from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "farmio-dev-secret-key"

PUBLIC_ENDPOINTS = {"login", "register", "forgot_password", "logout", "static"}
TEMP_USERS = {
    "admin@farmio.local": {
        "first_name": "Admin",
        "last_name": "FarmIO",
        "password": "admin123",
        "role": "admin",
    }
}


def normalize_email(value):
    return (value or "").strip().lower()


def create_user_session(email):
    user = TEMP_USERS[email]
    session["authenticated"] = True
    session["user_email"] = email
    session["user_role"] = user["role"]
    session["user_name"] = f"{user['first_name']} {user['last_name']}".strip()


def get_sales_orders(channel):
    label = "Online" if channel == "online" else "Punto Vendita Fisico"
    return [
        {
            "order_id": f"{channel[:3].upper()}-001",
            "client_id": 1,
            "client_name": "Cliente 1",
            "client_surname": "Cognome 1",
            "client_address": "Indirizzo 1",
            "client_vat": "PIVA-CLI-001",
            "date": "00/00/0000",
            "total": "€ 0,00",
            "point_vat": "PIVA-001",
            "company_email": "azienda1@farmio.local",
            "channel_label": label,
        },
        {
            "order_id": f"{channel[:3].upper()}-002",
            "client_id": 2,
            "client_name": "Cliente 2",
            "client_surname": "Cognome 2",
            "client_address": "Indirizzo 2",
            "client_vat": "",
            "date": "00/00/0000",
            "total": "€ 0,00",
            "point_vat": "PIVA-002",
            "company_email": "azienda2@farmio.local",
            "channel_label": label,
        },
        {
            "order_id": f"{channel[:3].upper()}-003",
            "client_id": 3,
            "client_name": "Cliente 3",
            "client_surname": "Cognome 3",
            "client_address": "Indirizzo 3",
            "client_vat": "",
            "date": "00/00/0000",
            "total": "€ 0,00",
            "point_vat": "PIVA-003",
            "company_email": "azienda3@farmio.local",
            "channel_label": label,
        },
    ]


def get_client_detail(channel, client_id):
    orders = get_sales_orders(channel)
    order = next((item for item in orders if item["client_id"] == client_id), None)
    if order is None:
        return None

    return {
        "id": client_id,
        "name": order["client_name"],
        "surname": order["client_surname"],
        "channel_label": order["channel_label"],
        "email": f"cliente{client_id}@esempio.local",
        "address": order["client_address"],
        "vat_number": order["client_vat"],
        "payment_method": f"Metodo {client_id}",
        "orders": [
            {
                "order_id": order["order_id"],
                "date": order["date"],
                "total": order["total"],
                "point_vat": order["point_vat"],
                "company_email": order["company_email"],
                "client_address": order["client_address"],
                "client_vat": order["client_vat"],
            },
            {
                "order_id": f"{channel[:3].upper()}-00{client_id + 3}",
                "date": "00/00/0000",
                "total": "€ 0,00",
                "point_vat": f"PIVA-00{client_id + 3}",
                "company_email": f"azienda{client_id + 3}@farmio.local",
                "client_address": f"Indirizzo {client_id}",
                "client_vat": "",
            },
        ],
    }


def build_order_detail(channel, order):
    return {
        "order_id": order["order_id"],
        "client_id": order["client_id"],
        "client_name": order["client_name"],
        "client_surname": order["client_surname"],
        "client_address": order["client_address"],
        "client_vat": order["client_vat"],
        "date": order["date"],
        "total": order["total"],
        "point_vat": order["point_vat"],
        "company_email": order["company_email"],
        "channel_label": order["channel_label"],
        "payment_method": f"Metodo {order['client_id']}",
        "address": order["client_address"],
        "items": [
            ["Prodotto 1", "1", "€ 0,00"],
            ["Prodotto 2", "1", "€ 0,00"],
        ],
    }


def get_order_detail(channel, order_id):
    order = next((item for item in get_sales_orders(channel) if item["order_id"] == order_id), None)
    if order is not None:
        return build_order_detail(channel, order)

    prefix = f"{channel[:3].upper()}-"
    if not order_id.startswith(prefix):
        return None

    try:
        order_number = int(order_id.split("-")[-1])
    except ValueError:
        return None

    if order_number < 4:
        return None

    client_id = order_number - 3
    if client_id < 1 or client_id > 3:
        return None

    fallback_order = {
        "order_id": order_id,
        "client_id": client_id,
        "client_name": f"Cliente {client_id}",
        "client_surname": f"Cognome {client_id}",
        "client_address": f"Indirizzo {client_id}",
        "client_vat": "",
        "date": "00/00/0000",
        "total": "€ 0,00",
        "point_vat": f"PIVA-00{order_number}",
        "company_email": f"azienda{order_number}@farmio.local",
        "channel_label": "Online" if channel == "online" else "Punto Vendita Fisico",
    }
    return build_order_detail(channel, fallback_order)


def get_machinery_options():
    return [
        {"id": "mac-1", "label": "Macchinario 1"},
        {"id": "mac-2", "label": "Macchinario 2"},
        {"id": "mac-3", "label": "Macchinario 3"},
    ]


def get_equipment_options():
    return [
        {"id": "att-1", "label": "Attrezzatura 1"},
        {"id": "att-2", "label": "Attrezzatura 2"},
        {"id": "att-3", "label": "Attrezzatura 3"},
    ]


def get_intervention_plot_options():
    return [
        {"id": str(plot["id"]), "label": f'Appezzamento {plot["id"]}'} for plot in get_plots()
    ]


def get_terrains():
    return [
        {
            "id": 1,
            "latitude": "00.0000",
            "longitude": "00.0000",
            "year": "2020",
            "description": "Terreno 1",
            "terrain_type": "Tipo 1",
            "surface": "10,00 ha",
            "plot_ids": [1, 2],
        },
        {
            "id": 2,
            "latitude": "00.0001",
            "longitude": "00.0001",
            "year": "2021",
            "description": "Terreno 2",
            "terrain_type": "Tipo 2",
            "surface": "8,50 ha",
            "plot_ids": [3],
        },
        {
            "id": 3,
            "latitude": "00.0002",
            "longitude": "00.0002",
            "year": "2022",
            "description": "Terreno 3",
            "terrain_type": "Tipo 3",
            "surface": "12,00 ha",
            "plot_ids": [],
        },
    ]


def get_subjects():
    return [
        {
            "id": 1,
            "hourly_pay": "€ 15,00",
            "company_name": "",
            "external_company": "Dipendente",
            "vat_number": "",
            "name": "Mario",
            "surname": "Rossi",
            "birth_date": "01/01/1990",
            "iban": "IT00A0000000000000000000001",
            "tax_code": "RSSMRA90A01H501X",
            "manager": "Sì",
            "worker": "No",
            "email": "mario.rossi@farmio.local",
        },
        {
            "id": 2,
            "hourly_pay": "€ 12,00",
            "company_name": "",
            "external_company": "Dipendente",
            "vat_number": "",
            "name": "Luca",
            "surname": "Bianchi",
            "birth_date": "02/02/1994",
            "iban": "IT00A0000000000000000000002",
            "tax_code": "BNCLCU94B02H501Y",
            "manager": "No",
            "worker": "Sì",
            "email": "luca.bianchi@farmio.local",
        },
        {
            "id": 3,
            "hourly_pay": "€ 0,00",
            "company_name": "Azienda Esterna 1",
            "external_company": "Azienda esterna",
            "vat_number": "PIVA-EST-001",
            "name": "",
            "surname": "",
            "birth_date": "",
            "iban": "",
            "tax_code": "",
            "manager": "No",
            "worker": "No",
            "email": "aziendaesterna1@farmio.local",
        },
    ]


def get_subject_options():
    options = []
    for subject in get_subjects():
        if subject["external_company"] == "Azienda esterna":
            label = subject["company_name"] or f'Soggetto {subject["id"]}'
        else:
            label = f'{subject["name"]} {subject["surname"]}'.strip() or f'Soggetto {subject["id"]}'
        options.append({"id": str(subject["id"]), "label": label})
    return options


def get_plots():
    return [
        {
            "id": 1,
            "soil_composition": "Composizione 1",
            "surface": "00,00 ha",
            "cover_type": "Sì",
            "antigrandine": "Sì",
            "antibrina": "No",
            "insurance_cover": "Sì",
            "company_email": "azienda1@farmio.local",
            "terrain_longitude": "00.0000",
            "terrain_latitude": "00.0000",
            "crop_variety": "Varieta 1",
            "crop_species": "Specie 1",
        },
        {
            "id": 2,
            "soil_composition": "Composizione 2",
            "surface": "00,00 ha",
            "cover_type": "No",
            "antigrandine": "No",
            "antibrina": "Sì",
            "insurance_cover": "Sì",
            "company_email": "azienda2@farmio.local",
            "terrain_longitude": "00.0000",
            "terrain_latitude": "00.0000",
            "crop_variety": "Varieta 2",
            "crop_species": "Specie 2",
        },
        {
            "id": 3,
            "soil_composition": "Composizione 3",
            "surface": "00,00 ha",
            "cover_type": "Sì",
            "antigrandine": "Sì",
            "antibrina": "Sì",
            "insurance_cover": "No",
            "company_email": "azienda3@farmio.local",
            "terrain_longitude": "00.0000",
            "terrain_latitude": "00.0000",
            "crop_variety": "Varieta 3",
            "crop_species": "Specie 3",
        },
    ]


def get_plot_history(plot_id, history_type):
    plot = next((item for item in get_plots() if item["id"] == plot_id), None)
    if plot is None:
        return None

    labels = {
        "trattamenti": "Trattamenti",
        "irrigazione": "Irrigazione",
        "raccolta": "Raccolta",
    }
    columns_map = {
        "trattamenti": ["Data", "Qtà acqua", "Prodotto", "Qtà prodotto"],
        "irrigazione": ["Data", "Ora inizio", "Prodotto", "Qtà prodotto"],
        "raccolta": ["Data", "Qtà raccolta", "Anno scorta", "Email", "Varietà", "Specie"],
    }
    rows_map = {
        "trattamenti": [
            ["00/00/0000", "0", "Prodotto 1", "0"],
            ["00/00/0000", "0", "Prodotto 2", "0"],
            ["00/00/0000", "0", "Prodotto 3", "0"],
        ],
        "irrigazione": [
            ["00/00/0000", "00:00", "Prodotto 1", "0"],
            ["00/00/0000", "00:00", "Prodotto 2", "0"],
            ["00/00/0000", "00:00", "Prodotto 3", "0"],
        ],
        "raccolta": [
            ["00/00/0000", "0", "0000", "azienda1@farmio.local", "Varieta 1", "Specie 1"],
            ["00/00/0000", "0", "0000", "azienda2@farmio.local", "Varieta 2", "Specie 2"],
            ["00/00/0000", "0", "0000", "azienda3@farmio.local", "Varieta 3", "Specie 3"],
        ],
    }
    if history_type not in labels:
        return None

    return {
        "plot": plot,
        "history_label": labels[history_type],
        "columns": columns_map[history_type],
        "rows": rows_map[history_type],
    }


def get_inventory_rows():
    return [
        ["0000", "0", "€ 0,00", "Varieta 1", "Specie 1"],
        ["0000", "0", "€ 0,00", "Varieta 2", "Specie 2"],
        ["0000", "0", "€ 0,00", "Varieta 3", "Specie 3"],
    ]


def get_dashboard_data():
    terrains = get_terrains()
    plots = get_plots()
    subjects = get_subjects()
    online_orders = get_sales_orders("online")
    physical_orders = get_sales_orders("fisico")
    inventory_rows = get_inventory_rows()
    total_orders = len(online_orders) + len(physical_orders)
    total_plots = len(plots)

    terrain_cards = []
    for terrain in terrains:
        terrain_cards.append(
            {
                "id": terrain["id"],
                "name": terrain["description"],
                "surface": terrain["surface"],
                "type": terrain["terrain_type"],
                "plot_ids": terrain["plot_ids"],
            }
        )

    return {
        "summary_cards": [
            {
                "title": "Terreni",
                "value": len(terrains),
                "note": f"{total_plots} appezzamenti collegati",
                "icon": "fa-map-marked-alt",
                "color": "primary",
                "href": url_for("proprieta_terreni"),
            },
            {
                "title": "Soggetti",
                "value": len(subjects),
                "note": f"{sum(1 for subject in subjects if subject['external_company'] == 'Dipendente')} dipendenti",
                "icon": "fa-users",
                "color": "success",
                "href": url_for("soggetto"),
            },
            {
                "title": "Ordini",
                "value": total_orders,
                "note": f"{len(online_orders)} online · {len(physical_orders)} fisico",
                "icon": "fa-shopping-basket",
                "color": "info",
                "href": url_for("punto_vendita_online"),
            },
            {
                "title": "Risorse",
                "value": len(get_machinery_options()) + len(get_equipment_options()),
                "note": f"{len(get_machinery_options())} macchinari · {len(get_equipment_options())} attrezzature",
                "icon": "fa-tools",
                "color": "warning",
                "href": url_for("risorse_materiali"),
            },
        ],
        "quick_links": [
            {
                "title": "Proprietà",
                "description": "Apri stabilimenti e terreni aziendali.",
                "icon": "fa-building",
                "href": url_for("proprieta_stabilimenti"),
            },
            {
                "title": "Punto Vendita",
                "description": "Consulta ordini online e del punto fisico.",
                "icon": "fa-store",
                "href": url_for("punto_vendita_online"),
            },
            {
                "title": "Soggetto",
                "description": "Gestisci dipendenti e aziende esterne.",
                "icon": "fa-user-friends",
                "href": url_for("soggetto"),
            },
            {
                "title": "Scorte",
                "description": "Controlla le disponibilità di magazzino.",
                "icon": "fa-warehouse",
                "href": url_for("scorte"),
            },
            {
                "title": "Appezzamenti",
                "description": "Apri la lista completa con gli storici collegati.",
                "icon": "fa-map",
                "href": url_for("appezzamenti"),
            },
            {
                "title": "Interventi Operativi",
                "description": "Coordina soggetti, mezzi e appezzamenti.",
                "icon": "fa-clipboard-list",
                "href": url_for("interventi_operativi"),
            },
        ],
        "terrain_cards": terrain_cards,
        "recent_orders": online_orders[:2] + physical_orders[:2],
        "inventory_preview": inventory_rows,
    }


@app.before_request
def require_authentication():
    endpoint = request.endpoint
    if endpoint in PUBLIC_ENDPOINTS:
        return None
    if endpoint is None:
        if session.get("authenticated"):
            return None
        return redirect(url_for("login"))
    if session.get("authenticated"):
        return None
    return redirect(url_for("login"))

@app.route("/")
def home():
    return render_template("index.html", dashboard=get_dashboard_data())

@app.route("/tables")
def tables():
    return render_template("tables.html")

@app.route("/immobili")
def immobili():
    return redirect(url_for("proprieta_stabilimenti"))

@app.route("/proprieta")
def proprieta():
    return redirect(url_for("proprieta_stabilimenti"))

@app.route("/proprieta/stabilimenti")
def proprieta_stabilimenti():
    return render_template(
        "editable_table.html",
        title="Stabilimenti",
        subtitle="Visualizza o aggiungi gli stabilimenti aziendali.",
        table_id="stabilimenti-table",
        columns=["Latitudine", "Longitudine", "Anno", "Descrizione", "Estensione"],
    )

@app.route("/proprieta/terreni")
def proprieta_terreni():
    return render_template(
        "terrains_table.html",
        title="Terreni",
        subtitle="Visualizza, modifica o aggiungi i terreni e apri i relativi appezzamenti.",
        table_id="terreni-table",
        terrains=get_terrains(),
    )

@app.route("/soggetto")
def soggetto():
    return render_template(
        "subjects_table.html",
        title="Soggetto",
        subtitle="Gestisci persone e aziende esterne in un'unica tabella.",
        table_id="soggetto-table",
        subjects=get_subjects(),
    )

@app.route("/soggetto/dipendenti")
def soggetto_dipendenti():
    return redirect(url_for("soggetto"))

@app.route("/soggetto/dipendenti/ore/<int:employee_id>")
def soggetto_dipendente_ore(employee_id):
    return render_template(
        "employee_hours.html",
        title="Totale ore lavorate",
        employee_id=employee_id,
        total_hours="00:00",
        columns=["Data", "Ore", "ID"],
        rows=[
            ["00/00/0000", "00:00", str(employee_id)],
            ["00/00/0000", "00:00", str(employee_id)],
            ["00/00/0000", "00:00", str(employee_id)],
        ],
    )

@app.route("/soggetto/aziende-esterne")
def soggetto_aziende_esterne():
    return redirect(url_for("soggetto"))

@app.route("/risorse-materiali")
def risorse_materiali():
    return redirect(url_for("risorse_attrezzature"))

@app.route("/risorse-materiali/attrezzature")
def risorse_attrezzature():
    return render_template(
        "editable_table.html",
        title="Attrezzature",
        subtitle="Visualizza o aggiungi le attrezzature aziendali.",
        table_id="attrezzature-table",
        columns=["Marca", "Modello", "Anno", "Prezzo", "Quantità"],
    )

@app.route("/risorse-materiali/macchinari")
def risorse_macchinari():
    return render_template(
        "editable_table.html",
        title="Macchinari",
        subtitle="Visualizza o aggiungi i macchinari aziendali.",
        table_id="macchinari-table",
        columns=["Marca", "Modello", "Anno", "Targa", "Prezzo"],
    )

@app.route("/punto-vendita")
def punto_vendita():
    return redirect(url_for("punto_vendita_online"))

@app.route("/punto-vendita/online")
def punto_vendita_online():
    return render_template(
        "readonly_orders_table.html",
        title="Punto Vendita Online",
        subtitle="Elenco ordini clienti del canale online.",
        orders=get_sales_orders("online"),
        detail_endpoint="punto_vendita_online_cliente",
        order_detail_endpoint="punto_vendita_online_ordine",
        show_online_fields=True,
    )

@app.route("/punto-vendita/fisico")
def punto_vendita_fisico():
    return render_template(
        "readonly_orders_table.html",
        title="Punto Vendita Fisico",
        subtitle="Elenco ordini clienti del punto vendita fisico.",
        orders=get_sales_orders("fisico"),
        detail_endpoint="punto_vendita_fisico_cliente",
        order_detail_endpoint="punto_vendita_fisico_ordine",
        show_online_fields=False,
    )

@app.route("/punto-vendita/online/cliente/<int:client_id>")
def punto_vendita_online_cliente(client_id):
    client = get_client_detail("online", client_id)
    if client is None:
        return not_found(None)
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
        return not_found(None)
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
        return not_found(None)
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
        return not_found(None)
    return render_template(
        "order_detail.html",
        title=f"Ordine {order['order_id']}",
        subtitle="Scheda ordine in sola lettura.",
        order=order,
    )

@app.route("/scorte")
def scorte():
    return render_template(
        "readonly_inventory_table.html",
        title="Scorte",
        subtitle="Visualizza le disponibilita di magazzino senza possibilita di modifica.",
        columns=["Anno", "Quantità", "Prezzo", "Varietà", "Specie"],
        rows=get_inventory_rows(),
    )

@app.route("/appezzamenti")
def appezzamenti():
    return render_template(
        "plots_table.html",
        title="Appezzamenti",
        subtitle="Visualizza, modifica o aggiungi gli appezzamenti e apri lo storico dedicato.",
        plots=get_plots(),
    )

@app.route("/appezzamenti/<int:plot_id>/trattamenti")
def appezzamento_trattamenti(plot_id):
    history = get_plot_history(plot_id, "trattamenti")
    if history is None:
        return not_found(None)
    return render_template(
        "plot_history.html",
        title=f"Storico Trattamenti - Appezzamento {history['plot']['id']}",
        subtitle="Consultazione dello storico trattamenti del singolo appezzamento.",
        history=history,
    )

@app.route("/appezzamenti/<int:plot_id>/irrigazione")
def appezzamento_irrigazione(plot_id):
    history = get_plot_history(plot_id, "irrigazione")
    if history is None:
        return not_found(None)
    return render_template(
        "plot_history.html",
        title=f"Storico Irrigazione - Appezzamento {history['plot']['id']}",
        subtitle="Consultazione dello storico irrigazione del singolo appezzamento.",
        history=history,
    )

@app.route("/appezzamenti/<int:plot_id>/raccolta")
def appezzamento_raccolta(plot_id):
    history = get_plot_history(plot_id, "raccolta")
    if history is None:
        return not_found(None)
    return render_template(
        "plot_history.html",
        title=f"Storico Raccolta - Appezzamento {history['plot']['id']}",
        subtitle="Consultazione dello storico raccolta del singolo appezzamento.",
        history=history,
    )

@app.route("/interventi-operativi")
def interventi_operativi():
    return render_template(
        "operational_interventions.html",
        title="Interventi Operativi",
        subtitle="Visualizza, aggiungi o modifica gli interventi operativi.",
        table_id="interventi-operativi-table",
        machinery_options=get_machinery_options(),
        equipment_options=get_equipment_options(),
        plot_options=get_intervention_plot_options(),
        subject_options=get_subject_options(),
    )

@app.route("/charts")
def charts():
    return render_template("charts.html")

@app.route("/buttons")
def buttons():
    return render_template("buttons.html")

@app.route("/cards")
def cards():
    return render_template("cards.html")

@app.route("/blank")
def blank():
    return render_template("blank.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("home"))
    error_message = None
    if request.method == "POST":
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password", "")
        user = TEMP_USERS.get(email)
        if user is None or user["password"] != password:
            error_message = "Credenziali non valide. Controlla email e password."
        else:
            create_user_session(email)
            return redirect(url_for("home"))
    return render_template("login.html", error_message=error_message)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("authenticated"):
        return redirect(url_for("home"))
    error_message = None
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password", "")
        repeat_password = request.form.get("repeat_password", "")

        if not first_name or not last_name or not email or not password:
            error_message = "Compila tutti i campi richiesti."
        elif password != repeat_password:
            error_message = "Le password non coincidono."
        elif email in TEMP_USERS:
            error_message = "Esiste gia un utente con questa email."
        else:
            TEMP_USERS[email] = {
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
                "role": "user",
            }
            create_user_session(email)
            return redirect(url_for("home"))
    return render_template("register.html", error_message=error_message)

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    return render_template("forgot-password.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/utilities/color")
def utilities_color():
    return render_template("utilities-color.html")

@app.route("/utilities/border")
def utilities_border():
    return render_template("utilities-border.html")

@app.route("/utilities/animation")
def utilities_animation():
    return render_template("utilities-animation.html")

@app.route("/utilities/other")
def utilities_other():
    return render_template("utilities-other.html")

@app.route("/404")
def page_404():
    return render_template("404.html"), 404

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
