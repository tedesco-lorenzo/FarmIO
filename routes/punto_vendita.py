from flask import abort, redirect, render_template, url_for

from services import get_client_detail, get_order_detail, get_sales_orders


def register_punto_vendita_routes(app):
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
