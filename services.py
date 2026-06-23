from collections import defaultdict
from decimal import Decimal

from flask import session, url_for

from models import (
    Appezzamento,
    Assegnazione,
    Cliente,
    Coltura,
    InterventoOperativo,
    Irrigazione,
    Ordine,
    Prelievo,
    PuntoVendita,
    Raccolta,
    RisorsaMateriale,
    Scorta,
    SchedaManutenzione,
    Soggetto,
    Stabilimento,
    TerrenoAgricolo,
    Trattamento,
    Utilizzo,
)
from extensions import db
from utils import (
    bool_to_si_no,
    format_currency,
    format_date,
    format_datetime,
    format_decimal,
    format_time,
    get_company_email,
)


ZERO_QUANTITY = Decimal("0.00")


def get_channel_label(channel):
    return "Online" if channel == "online" else "Punto Vendita Fisico"


def _get_harvest_stock_key(harvest_record):
    return (
        harvest_record.anno_scorta,
        harvest_record.varieta_coltura,
        harvest_record.specie_coltura,
    )


def _aggregate_harvest_totals(harvest_records):
    totals = defaultdict(lambda: ZERO_QUANTITY)
    for harvest_record in harvest_records:
        totals[_get_harvest_stock_key(harvest_record)] += Decimal(harvest_record.quantita_raccolta)
    return totals


def apply_harvest_changes_to_inventory(company_email, plot_id, new_harvest_records):
    existing_plot_harvests = Raccolta.query.filter_by(
        id_appezzamento=plot_id,
        email_azienda_agricola=company_email,
    ).all()

    existing_totals = _aggregate_harvest_totals(existing_plot_harvests)
    new_totals = _aggregate_harvest_totals(new_harvest_records)

    existing_stock_rows = Scorta.query.filter_by(email_azienda_agricola=company_email).all()
    stock_by_key = {
        (stock_row.anno, stock_row.varieta_coltura, stock_row.specie_coltura): stock_row
        for stock_row in existing_stock_rows
    }

    for stock_key in set(existing_totals) | set(new_totals):
        quantity_delta = new_totals.get(stock_key, ZERO_QUANTITY) - existing_totals.get(
            stock_key, ZERO_QUANTITY
        )
        if quantity_delta == ZERO_QUANTITY:
            continue

        stock_row = stock_by_key.get(stock_key)
        if stock_row is None:
            if quantity_delta < ZERO_QUANTITY:
                raise ValueError(
                    "Una raccolta sta provando a sottrarre quantità da una scorta inesistente."
                )

            stock_row = Scorta(
                email_azienda_agricola=company_email,
                anno=stock_key[0],
                varieta_coltura=stock_key[1],
                specie_coltura=stock_key[2],
                quantita_totale=ZERO_QUANTITY,
                prezzo_unitario=ZERO_QUANTITY,
            )
            db.session.add(stock_row)
            existing_stock_rows.append(stock_row)
            stock_by_key[stock_key] = stock_row

        updated_quantity = Decimal(stock_row.quantita_totale) + quantity_delta
        if updated_quantity < ZERO_QUANTITY:
            raise ValueError(
                "La modifica della raccolta porterebbe la scorta sotto zero. Controlla quantità raccolte e prelievi."
            )

        stock_row.quantita_totale = updated_quantity


def get_sales_channel_filter(channel):
    if channel == "online":
        return PuntoVendita.online.is_(True)
    return PuntoVendita.negozio_fisico.is_(True)


def get_sales_points(channel=None, point_vat=None):
    company_email = get_company_email()
    if not company_email:
        return []

    query = PuntoVendita.query.filter_by(email_azienda_agricola=company_email)
    if channel in {"online", "fisico"}:
        query = query.filter(get_sales_channel_filter(channel))
    if point_vat:
        query = query.filter(PuntoVendita.partita_iva == point_vat)

    sales_points = query.order_by(PuntoVendita.nome.asc(), PuntoVendita.partita_iva.asc()).all()

    return [
        {
            "vat_number": sales_point.partita_iva,
            "name": sales_point.nome,
            "address": sales_point.indirizzo,
            "opening_hours": sales_point.orari_apertura or "",
            "channel": "Online" if sales_point.online else "Fisico",
        }
        for sales_point in sales_points
    ]


def get_sales_orders(channel, point_vat=None):
    company_email = get_company_email()
    if not company_email:
        return []

    query = (
        db.session.query(Ordine, Cliente, PuntoVendita)
        .join(PuntoVendita, Ordine.partita_iva_punto_vendita == PuntoVendita.partita_iva)
        .outerjoin(Cliente, Ordine.id_cliente == Cliente.id_cliente)
        .filter(
            PuntoVendita.email_azienda_agricola == company_email,
            get_sales_channel_filter(channel),
        )
    )
    if point_vat:
        query = query.filter(PuntoVendita.partita_iva == point_vat)

    order_rows = query.order_by(Ordine.data.desc(), Ordine.id_ordine.desc()).all()

    channel_label = get_channel_label(channel)
    orders = []
    for order_record, client_record, sales_point in order_rows:
        orders.append(
            {
                "order_id": order_record.id_ordine,
                "client_id": order_record.id_cliente,
                "client_name": client_record.nome if client_record else "Cliente",
                "client_surname": client_record.cognome if client_record else "",
                "client_address": client_record.indirizzo if client_record and client_record.indirizzo else "-",
                "client_vat": client_record.partita_iva if client_record else "",
                "date": format_date(order_record.data),
                "total": format_currency(order_record.totale_ordine),
                "point_name": sales_point.nome,
                "point_vat": sales_point.partita_iva,
                "channel_label": channel_label,
                "payment_method": client_record.metodo_pagamento if client_record else "-",
            }
        )
    return orders


def get_client_detail(channel, client_id):
    if not get_company_email():
        return None

    client_record = Cliente.query.filter_by(id_cliente=client_id).first()
    if client_record is None:
        return None

    orders = get_sales_orders(channel)
    client_orders = [order for order in orders if order["client_id"] == client_id]
    if not client_orders:
        return None

    return {
        "id": client_record.id_cliente,
        "name": client_record.nome,
        "surname": client_record.cognome,
        "channel_label": get_channel_label(channel),
        "address": client_record.indirizzo or "-",
        "vat_number": client_record.partita_iva or "",
        "payment_method": client_record.metodo_pagamento,
        "orders": client_orders,
    }


def get_order_detail(channel, order_id):
    company_email = get_company_email()
    if not company_email:
        return None

    try:
        order_id = int(order_id)
    except (TypeError, ValueError):
        return None

    order_row = (
        db.session.query(Ordine, Cliente, PuntoVendita)
        .join(PuntoVendita, Ordine.partita_iva_punto_vendita == PuntoVendita.partita_iva)
        .outerjoin(Cliente, Ordine.id_cliente == Cliente.id_cliente)
        .filter(
            Ordine.id_ordine == order_id,
            PuntoVendita.email_azienda_agricola == company_email,
            get_sales_channel_filter(channel),
        )
        .first()
    )
    if order_row is None:
        return None

    order_record, client_record, sales_point = order_row
    pickup_rows = (
        Prelievo.query.filter_by(
            id_ordine=order_record.id_ordine,
            email_azienda_agricola=company_email,
        )
        .order_by(Prelievo.specie_coltura.asc(), Prelievo.varieta_coltura.asc())
        .all()
    )

    items = []
    for pickup_row in pickup_rows:
        stock_record = Scorta.query.filter_by(
            email_azienda_agricola=pickup_row.email_azienda_agricola,
            anno=pickup_row.anno_scorta,
            varieta_coltura=pickup_row.varieta_coltura,
            specie_coltura=pickup_row.specie_coltura,
        ).first()
        items.append(
            [
                f"{pickup_row.specie_coltura} / {pickup_row.varieta_coltura}",
                format_decimal(pickup_row.quantita_prodotto_ordine),
                format_currency(stock_record.prezzo_unitario) if stock_record else "-",
            ]
        )

    return {
        "order_id": order_record.id_ordine,
        "client_id": client_record.id_cliente if client_record else "-",
        "client_name": client_record.nome if client_record else "Cliente",
        "client_surname": client_record.cognome if client_record else "",
        "client_address": client_record.indirizzo if client_record and client_record.indirizzo else "-",
        "client_vat": client_record.partita_iva if client_record else "",
        "date": format_date(order_record.data),
        "total": format_currency(order_record.totale_ordine),
        "point_name": sales_point.nome,
        "point_vat": sales_point.partita_iva,
        "channel_label": get_channel_label(channel),
        "payment_method": client_record.metodo_pagamento if client_record else "-",
        "address": client_record.indirizzo if client_record and client_record.indirizzo else "-",
        "items": items,
    }


def get_inventory_rows():
    company_email = get_company_email()
    if not company_email:
        return []

    stock_records = (
        Scorta.query.filter_by(email_azienda_agricola=company_email)
        .order_by(Scorta.anno.desc(), Scorta.specie_coltura.asc(), Scorta.varieta_coltura.asc())
        .all()
    )
    return [
        [
            stock_record.specie_coltura,
            stock_record.varieta_coltura,
            stock_record.anno,
            format_decimal(stock_record.quantita_totale),
            format_currency(stock_record.prezzo_unitario),
        ]
        for stock_record in stock_records
    ]


def get_inventory_records():
    company_email = get_company_email()
    if not company_email:
        return []

    stock_records = (
        Scorta.query.filter_by(email_azienda_agricola=company_email)
        .order_by(Scorta.anno.desc(), Scorta.specie_coltura.asc(), Scorta.varieta_coltura.asc())
        .all()
    )
    return [
        {
            "year": str(stock_record.anno),
            "quantity": format_decimal(stock_record.quantita_totale),
            "price": format_decimal(stock_record.prezzo_unitario),
            "crop_variety": stock_record.varieta_coltura,
            "crop_species": stock_record.specie_coltura,
        }
        for stock_record in stock_records
    ]


def get_crop_rows():
    crop_records = Coltura.query.order_by(Coltura.varieta.asc(), Coltura.specie.asc()).all()
    return [[crop_record.specie, crop_record.varieta, crop_record.descrizione] for crop_record in crop_records]


def get_crop_selection_data():
    crop_records = Coltura.query.order_by(Coltura.varieta.asc(), Coltura.specie.asc()).all()
    crop_varieties = []
    crop_species_by_variety = {}

    for crop_record in crop_records:
        if crop_record.varieta not in crop_species_by_variety:
            crop_varieties.append(crop_record.varieta)
            crop_species_by_variety[crop_record.varieta] = []
        crop_species_by_variety[crop_record.varieta].append(crop_record.specie)

    return {
        "crop_varieties": crop_varieties,
        "crop_species_by_variety": crop_species_by_variety,
    }


def get_resources(resource_type):
    company_email = get_company_email()
    if not company_email:
        return []

    query = RisorsaMateriale.query.filter_by(email_azienda_agricola=company_email)
    if resource_type == "macchinari":
        query = query.filter_by(macchina_agricola=True)
    else:
        query = query.filter_by(attrezzatura=True)

    resource_rows = []
    for resource in query.order_by(RisorsaMateriale.id_risorsa_materiale.asc()).all():
        resource_rows.append(
            {
                "id": resource.id_risorsa_materiale,
                "brand": resource.marca,
                "model": resource.modello,
                "year": str(resource.anno_acquisto),
                "plate": resource.targa or "",
                "price": format_decimal(resource.prezzo),
                "quantity": "" if resource.quantita is None else str(resource.quantita),
            }
        )
    return resource_rows


def get_resource_by_id(resource_id, resource_type=None):
    company_email = get_company_email()
    if not company_email:
        return None

    resource = RisorsaMateriale.query.filter_by(
        id_risorsa_materiale=resource_id,
        email_azienda_agricola=company_email,
    ).first()
    if resource is None:
        return None

    if resource_type == "macchinari" and not resource.macchina_agricola:
        return None
    if resource_type == "attrezzature" and not resource.attrezzatura:
        return None

    return resource


def get_resource_label(resource):
    parts = [resource.marca, resource.modello]
    if resource.targa:
        parts.append(resource.targa)
    return " ".join(part for part in parts if part)


def get_maintenance_rows(resource_id):
    maintenance_rows = []
    maintenance_records = (
        SchedaManutenzione.query.filter_by(id_risorsa_materiale=resource_id)
        .order_by(SchedaManutenzione.data.desc(), SchedaManutenzione.id_manutenzione.desc())
        .all()
    )
    for maintenance_record in maintenance_records:
        maintenance_rows.append(
            {
                "maintenance_id": maintenance_record.id_manutenzione,
                "date": format_date(maintenance_record.data),
                "cost": format_decimal(maintenance_record.costo_manutenzione),
                "description": maintenance_record.descrizione,
            }
        )
    return maintenance_rows


def get_next_maintenance_id(resource_id):
    last_maintenance = (
        SchedaManutenzione.query.filter_by(id_risorsa_materiale=resource_id)
        .order_by(SchedaManutenzione.id_manutenzione.desc())
        .first()
    )
    if last_maintenance is None:
        return 1
    return last_maintenance.id_manutenzione + 1


def get_machinery_options():
    return [
        {
            "id": str(resource["id"]),
            "label": " ".join(
                part for part in [resource["brand"], resource["model"], resource["plate"]] if part
            ),
        }
        for resource in get_resources("macchinari")
    ]


def get_equipment_options():
    return [
        {
            "id": str(resource["id"]),
            "label": " ".join(part for part in [resource["brand"], resource["model"]] if part),
        }
        for resource in get_resources("attrezzature")
    ]


def get_intervention_plot_options():
    return [{"id": str(plot["id"]), "label": f'Appezzamento {plot["id"]}'} for plot in get_plots()]


def get_terrains():
    company_email = get_company_email()
    if not company_email:
        return []

    terrain_records = (
        TerrenoAgricolo.query.filter_by(email_azienda_agricola=company_email)
        .order_by(TerrenoAgricolo.anno_acquisto.desc())
        .all()
    )
    plot_records = Appezzamento.query.filter_by(email_azienda_agricola=company_email).all()

    plots_by_terrain = {}
    for plot_record in plot_records:
        key = (
            str(plot_record.latitudine_terreno_agricolo),
            str(plot_record.longitudine_terreno_agricolo),
        )
        plots_by_terrain.setdefault(key, []).append(plot_record.id_appezzamento)

    terrain_rows = []
    for terrain_record in terrain_records:
        key = (str(terrain_record.latitudine), str(terrain_record.longitudine))
        terrain_rows.append(
            {
                "id": f"{terrain_record.latitudine}-{terrain_record.longitudine}",
                "latitude": format_decimal(terrain_record.latitudine, 8),
                "longitude": format_decimal(terrain_record.longitudine, 8),
                "year": str(terrain_record.anno_acquisto),
                "description": terrain_record.descrizione,
                "terrain_type": terrain_record.tipologia_terreno,
                "surface": format_decimal(terrain_record.estensione),
                "plot_ids": sorted(plots_by_terrain.get(key, [])),
            }
        )
    return terrain_rows


def get_subjects():
    company_email = get_company_email()
    if not company_email:
        return []

    subject_records = (
        Soggetto.query.filter_by(email_azienda_agricola=company_email)
        .order_by(Soggetto.id_soggetto.asc())
        .all()
    )

    subject_rows = []
    for subject_record in subject_records:
        is_external = bool(subject_record.azienda_esterna)
        subject_rows.append(
            {
                "id": subject_record.id_soggetto,
                "hourly_pay": format_decimal(subject_record.stipendio_orario),
                "company_name": subject_record.denominazione_sociale or "",
                "external_company": "Azienda esterna" if is_external else "Dipendente",
                "vat_number": subject_record.partita_iva or "",
                "name": subject_record.nome or "",
                "surname": subject_record.cognome or "",
                "birth_date": format_date(subject_record.data_nascita),
                "iban": subject_record.iban or "",
                "tax_code": subject_record.codice_fiscale or "",
                "manager": "Sì" if subject_record.manager else "No",
                "worker": "Sì" if subject_record.operaio else "No",
            }
        )
    return subject_rows


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
    company_email = get_company_email()
    if not company_email:
        return []

    plot_records = (
        Appezzamento.query.filter_by(email_azienda_agricola=company_email)
        .order_by(Appezzamento.id_appezzamento.asc())
        .all()
    )

    plot_rows = []
    for plot_record in plot_records:
        plot_rows.append(
            {
                "id": plot_record.id_appezzamento,
                "soil_composition": plot_record.composizione_terreno,
                "surface": format_decimal(plot_record.estensione),
                "cover_type": bool_to_si_no(bool(plot_record.tipologia_copertura)),
                "antigrandine": bool_to_si_no(plot_record.antigrandine),
                "antibrina": bool_to_si_no(plot_record.antibrina),
                "insurance_cover": bool_to_si_no(bool(plot_record.copertura_assicurativa)),
                "company_email": plot_record.email_azienda_agricola,
                "terrain_longitude": format_decimal(plot_record.longitudine_terreno_agricolo, 8),
                "terrain_latitude": format_decimal(plot_record.latitudine_terreno_agricolo, 8),
                "crop_variety": plot_record.varieta_coltura,
                "crop_species": plot_record.specie_coltura,
            }
        )
    return plot_rows


def get_next_plot_id():
    company_email = get_company_email()
    if not company_email:
        return 1

    last_plot = (
        Appezzamento.query.filter_by(email_azienda_agricola=company_email)
        .order_by(Appezzamento.id_appezzamento.desc())
        .first()
    )
    if last_plot is None:
        return 1
    return last_plot.id_appezzamento + 1


def get_plot_history(plot_id, history_type):
    plot = next((item for item in get_plots() if item["id"] == plot_id), None)
    if plot is None:
        return None

    company_email = get_company_email()
    if not company_email:
        return None

    labels = {
        "trattamenti": "Trattamenti",
        "irrigazione": "Irrigazione",
        "raccolta": "Raccolta",
    }
    columns_map = {
        "trattamenti": ["Data", "Prodotto", "Qtà prodotto", "Qtà acqua", "Azioni"],
        "irrigazione": ["Data", "Ora inizio", "Prodotto", "Qtà prodotto", "Azioni"],
        "raccolta": ["Data", "Qtà raccolta", "Anno scorta", "Specie", "Varietà", "Azioni"],
    }
    save_endpoints = {
        "trattamenti": "appezzamento_trattamenti_salva",
        "irrigazione": "appezzamento_irrigazione_salva",
        "raccolta": "appezzamento_raccolta_salva",
    }
    empty_messages = {
        "trattamenti": 'Nessun trattamento inserito. Usa "Aggiungi riga" per iniziare.',
        "irrigazione": 'Nessuna irrigazione inserita. Usa "Aggiungi riga" per iniziare.',
        "raccolta": 'Nessuna raccolta inserita. Usa "Aggiungi riga" per iniziare.',
    }
    if history_type not in labels:
        return None

    history_rows = []
    if history_type == "trattamenti":
        records = (
            Trattamento.query.filter_by(id_appezzamento=plot_id)
            .order_by(Trattamento.data.desc())
            .all()
        )
        history_rows = [
            {
                "date": format_date(record.data),
                "water_quantity": format_decimal(record.quantita_acqua),
                "product_name": record.nome_prodotto,
                "product_quantity": format_decimal(record.quantita_prodotto),
            }
            for record in records
        ]
    elif history_type == "irrigazione":
        records = (
            Irrigazione.query.filter_by(id_appezzamento=plot_id)
            .order_by(Irrigazione.data.desc())
            .all()
        )
        history_rows = [
            {
                "date": format_date(record.data),
                "start_time": format_time(record.ora_inizio),
                "product_name": record.nome_prodotto or "",
                "product_quantity": (
                    format_decimal(record.quantita_prodotto)
                    if record.quantita_prodotto is not None
                    else ""
                ),
            }
            for record in records
        ]
    elif history_type == "raccolta":
        records = (
            Raccolta.query.filter_by(
                id_appezzamento=plot_id,
                email_azienda_agricola=company_email,
            )
            .order_by(Raccolta.data.desc())
            .all()
        )
        history_rows = [
            {
                "date": format_date(record.data),
                "harvest_quantity": format_decimal(record.quantita_raccolta),
                "stock_year": str(record.anno_scorta),
                "crop_variety": record.varieta_coltura,
                "crop_species": record.specie_coltura,
            }
            for record in records
        ]

    return {
        "history_type": history_type,
        "plot": plot,
        "history_label": labels[history_type],
        "columns": columns_map[history_type],
        "rows": history_rows,
        "save_action": url_for(save_endpoints[history_type], plot_id=plot_id),
        "empty_message": empty_messages[history_type],
        "empty_colspan": 6 if history_type == "raccolta" else 5,
    }


def get_intervention_rows():
    company_email = get_company_email()
    if not company_email:
        return []

    plot_ids = [
        plot.id_appezzamento
        for plot in Appezzamento.query.filter_by(email_azienda_agricola=company_email).all()
    ]
    if not plot_ids:
        return []

    interventions = (
        InterventoOperativo.query.filter(InterventoOperativo.id_appezzamento.in_(plot_ids))
        .order_by(InterventoOperativo.data_ora_inizio.desc())
        .all()
    )

    intervention_rows = []
    for intervention in interventions:
        assignments = Assegnazione.query.filter_by(
            id_appezzamento=intervention.id_appezzamento,
            data_ora_inizio_intervento_operativo=intervention.data_ora_inizio,
            email_azienda_agricola=company_email,
        ).all()
        subject_ids = [str(assignment.id_soggetto) for assignment in assignments]

        usage_rows = Utilizzo.query.filter_by(
            id_appezzamento=intervention.id_appezzamento,
            data_ora_inizio_intervento_operativo=intervention.data_ora_inizio,
        ).all()
        resource_ids = [usage.id_risorsa_materiale for usage in usage_rows]

        machinery_ids = []
        equipment_ids = []
        if resource_ids:
            resources = RisorsaMateriale.query.filter(
                RisorsaMateriale.id_risorsa_materiale.in_(resource_ids),
                RisorsaMateriale.email_azienda_agricola == company_email,
            ).all()
            for resource in resources:
                if resource.macchina_agricola:
                    machinery_ids.append(str(resource.id_risorsa_materiale))
                if resource.attrezzatura:
                    equipment_ids.append(str(resource.id_risorsa_materiale))

        intervention_rows.append(
            {
                "start_at": format_datetime(intervention.data_ora_inizio),
                "end_at": format_datetime(intervention.data_ora_fine),
                "description": intervention.descrizione,
                "subjects": sorted(subject_ids, key=lambda value: int(value)),
                "machinery": sorted(machinery_ids, key=lambda value: int(value)),
                "equipment": sorted(equipment_ids, key=lambda value: int(value)),
                "plot": str(intervention.id_appezzamento),
            }
        )

    return intervention_rows


def get_dashboard_data():
    company_email = get_company_email()
    terrains = get_terrains()
    plots = get_plots()
    subjects = get_subjects()
    sales_points = get_sales_points()
    online_orders = get_sales_orders("online")
    physical_orders = get_sales_orders("fisico")
    inventory_records = get_inventory_records()
    crop_rows = get_crop_rows()
    interventions = get_intervention_rows()
    machinery_options = get_machinery_options()
    equipment_options = get_equipment_options()
    facilities_count = (
        Stabilimento.query.filter_by(email_azienda_agricola=company_email).count() if company_email else 0
    )

    total_orders = len(online_orders) + len(physical_orders)
    total_plots = len(plots)
    employee_count = sum(1 for subject in subjects if subject["external_company"] == "Dipendente")
    external_subject_count = len(subjects) - employee_count
    online_points = sum(1 for point in sales_points if point["channel"] == "Online")
    physical_points = sum(1 for point in sales_points if point["channel"] == "Fisico")
    pending_inventory = [
        record
        for record in inventory_records
        if Decimal(record["price"] or "0") == ZERO_QUANTITY
    ]
    recent_orders = sorted(
        online_orders + physical_orders,
        key=lambda order: int(order["order_id"]),
        reverse=True,
    )[:6]
    recent_interventions = interventions[:5]

    terrain_cards = [
        {
            "id": terrain["id"],
            "name": terrain["description"],
            "surface": terrain["surface"],
            "type": terrain["terrain_type"],
            "plot_ids": terrain["plot_ids"],
        }
        for terrain in terrains
    ]

    return {
        "company_name": session.get("user_name", "FarmIO"),
        "company_email": company_email or "",
        "main_cards": [
            {
                "title": "Proprietà",
                "value": facilities_count + len(terrains),
                "note": f"{facilities_count} stabilimenti · {len(terrains)} terreni",
                "icon": "fa-building",
                "color": "success",
                "href": url_for("proprieta_stabilimenti"),
            },
            {
                "title": "Soggetti",
                "value": len(subjects),
                "note": f"{employee_count} dipendenti · {external_subject_count} esterni",
                "icon": "fa-users",
                "color": "primary",
                "href": url_for("soggetto"),
            },
            {
                "title": "Punto Vendita",
                "value": total_orders,
                "note": f"{online_points} online · {physical_points} fisici",
                "icon": "fa-store",
                "color": "info",
                "href": url_for("punto_vendita_online"),
            },
            {
                "title": "Risorse",
                "value": len(machinery_options) + len(equipment_options),
                "note": f"{len(machinery_options)} macchinari · {len(equipment_options)} attrezzature",
                "icon": "fa-tools",
                "color": "warning",
                "href": url_for("risorse_materiali"),
            },
        ],
        "secondary_cards": [
            {
                "title": "Appezzamenti",
                "value": len(plots),
                "note": "Storici irrigazione, trattamenti e raccolta",
                "icon": "fa-map",
                "href": url_for("appezzamenti"),
            },
            {
                "title": "Interventi",
                "value": len(interventions),
                "note": "Operazioni collegate a soggetti e risorse",
                "icon": "fa-clipboard-list",
                "href": url_for("interventi_operativi"),
            },
            {
                "title": "Scorte",
                "value": len(inventory_records),
                "note": f"{len(pending_inventory)} prezzi da controllare",
                "icon": "fa-warehouse",
                "href": url_for("scorte"),
            },
            {
                "title": "Colture",
                "value": len(crop_rows),
                "note": "Archivio consultabile di specie e varietà",
                "icon": "fa-leaf",
                "href": url_for("colture"),
            },
        ],
        "quick_links": [
            {
                "title": "Proprietà",
                "description": "Stabilimenti e terreni",
                "icon": "fa-building",
                "href": url_for("proprieta_stabilimenti"),
            },
            {
                "title": "Risorse Materiali",
                "description": "Attrezzature e macchinari",
                "icon": "fa-tools",
                "href": url_for("risorse_materiali"),
            },
            {
                "title": "Punto Vendita",
                "description": "Ordini online e fisici",
                "icon": "fa-store",
                "href": url_for("punto_vendita_online"),
            },
            {
                "title": "Soggetto",
                "description": "Dipendenti e aziende esterne",
                "icon": "fa-user-friends",
                "href": url_for("soggetto"),
            },
            {
                "title": "Scorte",
                "description": "Quantità e prezzi",
                "icon": "fa-warehouse",
                "href": url_for("scorte"),
            },
            {
                "title": "Colture",
                "description": "Archivio di specie e varietà",
                "icon": "fa-leaf",
                "href": url_for("colture"),
            },
            {
                "title": "Appezzamenti",
                "description": "Storici per singolo appezzamento",
                "icon": "fa-map",
                "href": url_for("appezzamenti"),
            },
            {
                "title": "Interventi Operativi",
                "description": "Soggetti, mezzi e appezzamenti",
                "icon": "fa-clipboard-list",
                "href": url_for("interventi_operativi"),
            },
        ],
        "status_items": [
            {"label": "Stabilimenti", "value": facilities_count},
            {"label": "Terreni", "value": len(terrains)},
            {"label": "Appezzamenti", "value": total_plots},
            {"label": "Punti vendita", "value": len(sales_points)},
        ],
        "terrain_cards": terrain_cards[:4],
        "recent_orders": recent_orders,
        "pending_inventory_count": len(pending_inventory),
        "pending_inventory": pending_inventory[:6],
        "inventory_preview": inventory_records[:5],
        "crop_preview": crop_rows[:12],
        "recent_interventions": recent_interventions,
    }
