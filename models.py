from sqlalchemy import ForeignKeyConstraint

from extensions import db


class AziendaAgricola(db.Model):
    __tablename__ = "AZIENDA_AGRICOLA"

    email = db.Column(db.String(100), primary_key=True)
    denominazione_sociale = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    anno_fondazione = db.Column(db.Integer, nullable=False)


class Scorta(db.Model):
    __tablename__ = "SCORTA"

    email_azienda_agricola = db.Column(
        db.String(100),
        db.ForeignKey("AZIENDA_AGRICOLA.email"),
        primary_key=True,
    )
    anno = db.Column(db.Integer, primary_key=True)
    varieta_coltura = db.Column(db.String(50), primary_key=True)
    specie_coltura = db.Column(db.String(50), primary_key=True)
    quantita_totale = db.Column(db.Numeric(10, 2), nullable=False)
    prezzo_unitario = db.Column(db.Numeric(10, 2), nullable=False)


class Stabilimento(db.Model):
    __tablename__ = "STABILIMENTO"

    email_azienda_agricola = db.Column(
        db.String(100),
        db.ForeignKey("AZIENDA_AGRICOLA.email"),
        nullable=False,
    )
    latitudine = db.Column(db.Numeric(10, 8), primary_key=True)
    longitudine = db.Column(db.Numeric(11, 8), primary_key=True)
    anno_acquisto = db.Column(db.Integer, nullable=False)
    descrizione = db.Column(db.Text, nullable=False)
    estensione = db.Column(db.Numeric(10, 2), nullable=False)


class TerrenoAgricolo(db.Model):
    __tablename__ = "TERRENO_AGRICOLO"

    email_azienda_agricola = db.Column(
        db.String(100),
        db.ForeignKey("AZIENDA_AGRICOLA.email"),
        nullable=False,
    )
    latitudine = db.Column(db.Numeric(10, 8), primary_key=True)
    longitudine = db.Column(db.Numeric(11, 8), primary_key=True)
    anno_acquisto = db.Column(db.Integer, nullable=False)
    descrizione = db.Column(db.Text, nullable=False)
    tipologia_terreno = db.Column(db.String(50), nullable=False)
    estensione = db.Column(db.Numeric(10, 2), nullable=False)


class Coltura(db.Model):
    __tablename__ = "COLTURA"

    varieta = db.Column(db.String(50), primary_key=True)
    specie = db.Column(db.String(50), primary_key=True)
    descrizione = db.Column(db.Text, nullable=False)


class Appezzamento(db.Model):
    __tablename__ = "APPEZZAMENTO"

    id_appezzamento = db.Column(db.Integer, primary_key=True)
    composizione_terreno = db.Column(db.String(100), nullable=False)
    estensione = db.Column(db.Numeric(10, 2), nullable=False)
    tipologia_copertura = db.Column(db.String(50), nullable=True)
    antigrandine = db.Column(db.Boolean, nullable=True)
    antibrina = db.Column(db.Boolean, nullable=True)
    copertura_assicurativa = db.Column(db.String(100), nullable=True)
    email_azienda_agricola = db.Column(
        db.String(100),
        db.ForeignKey("AZIENDA_AGRICOLA.email"),
        nullable=False,
    )
    longitudine_terreno_agricolo = db.Column(db.Numeric(11, 8), nullable=False)
    latitudine_terreno_agricolo = db.Column(db.Numeric(10, 8), nullable=False)
    varieta_coltura = db.Column(db.String(50), nullable=False)
    specie_coltura = db.Column(db.String(50), nullable=False)


class Soggetto(db.Model):
    __tablename__ = "SOGGETTO"

    email_azienda_agricola = db.Column(
        db.String(100),
        db.ForeignKey("AZIENDA_AGRICOLA.email"),
        primary_key=True,
    )
    id_soggetto = db.Column(db.Integer, primary_key=True)
    stipendio_orario = db.Column(db.Numeric(10, 2), nullable=False)
    denominazione_sociale = db.Column(db.String(100), nullable=True)
    azienda_esterna = db.Column(db.Boolean, nullable=False)
    partita_iva = db.Column(db.String(11), nullable=True)
    nome = db.Column(db.String(50), nullable=True)
    cognome = db.Column(db.String(50), nullable=True)
    data_nascita = db.Column(db.Date, nullable=True)
    iban = db.Column(db.String(27), nullable=True)
    codice_fiscale = db.Column(db.String(16), nullable=True)
    manager = db.Column(db.Boolean, nullable=False)
    operaio = db.Column(db.Boolean, nullable=False)


class RegistrazioneOre(db.Model):
    __tablename__ = "REGISTRAZIONE_ORE"

    email_azienda_agricola = db.Column(db.String(100), primary_key=True)
    id_soggetto = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, primary_key=True)
    ore = db.Column(db.Numeric(4, 2), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["email_azienda_agricola", "id_soggetto"],
            ["SOGGETTO.email_azienda_agricola", "SOGGETTO.id_soggetto"],
            ondelete="CASCADE",
        ),
    )


class RisorsaMateriale(db.Model):
    __tablename__ = "RISORSA_MATERIALE"

    id_risorsa_materiale = db.Column(db.Integer, primary_key=True)
    email_azienda_agricola = db.Column(
        db.String(100),
        db.ForeignKey("AZIENDA_AGRICOLA.email"),
        nullable=False,
    )
    marca = db.Column(db.String(50), nullable=False)
    modello = db.Column(db.String(50), nullable=False)
    anno_acquisto = db.Column(db.Integer, nullable=False)
    targa = db.Column(db.String(20), nullable=True)
    prezzo = db.Column(db.Numeric(10, 2), nullable=False)
    quantita = db.Column(db.Integer, nullable=True)
    macchina_agricola = db.Column(db.Boolean, nullable=False)
    attrezzatura = db.Column(db.Boolean, nullable=False)


class SchedaManutenzione(db.Model):
    __tablename__ = "SCHEDA_MANUTENZIONE"

    id_risorsa_materiale = db.Column(
        db.Integer,
        db.ForeignKey("RISORSA_MATERIALE.id_risorsa_materiale"),
        primary_key=True,
    )
    id_manutenzione = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    costo_manutenzione = db.Column(db.Numeric(10, 2), nullable=False)
    descrizione = db.Column(db.Text, nullable=False)


class InterventoOperativo(db.Model):
    __tablename__ = "INTERVENTO_OPERATIVO"

    data_ora_inizio = db.Column(db.DateTime, primary_key=True)
    id_appezzamento = db.Column(
        db.Integer,
        db.ForeignKey("APPEZZAMENTO.id_appezzamento"),
        primary_key=True,
    )
    data_ora_fine = db.Column(db.DateTime, nullable=True)
    descrizione = db.Column(db.Text, nullable=False)


class Assegnazione(db.Model):
    __tablename__ = "ASSEGNAZIONE"

    id_appezzamento = db.Column(db.Integer, primary_key=True)
    data_ora_inizio_intervento_operativo = db.Column(db.DateTime, primary_key=True)
    email_azienda_agricola = db.Column(db.String(100), primary_key=True)
    id_soggetto = db.Column(db.Integer, primary_key=True)


class Utilizzo(db.Model):
    __tablename__ = "UTILIZZO"

    id_risorsa_materiale = db.Column(db.Integer, primary_key=True)
    id_appezzamento = db.Column(db.Integer, primary_key=True)
    data_ora_inizio_intervento_operativo = db.Column(db.DateTime, primary_key=True)


class Irrigazione(db.Model):
    __tablename__ = "IRRIGAZIONE"

    data = db.Column(db.Date, primary_key=True)
    id_appezzamento = db.Column(
        db.Integer,
        db.ForeignKey("APPEZZAMENTO.id_appezzamento"),
        primary_key=True,
    )
    ora_inizio = db.Column(db.Time, nullable=True)
    nome_prodotto = db.Column(db.String(100), nullable=True)
    quantita_prodotto = db.Column(db.Numeric(10, 2), nullable=True)


class Trattamento(db.Model):
    __tablename__ = "TRATTAMENTO"

    data = db.Column(db.Date, primary_key=True)
    id_appezzamento = db.Column(
        db.Integer,
        db.ForeignKey("APPEZZAMENTO.id_appezzamento"),
        primary_key=True,
    )
    quantita_acqua = db.Column(db.Numeric(10, 2), nullable=False)
    nome_prodotto = db.Column(db.String(100), nullable=False)
    quantita_prodotto = db.Column(db.Numeric(10, 2), nullable=False)


class Raccolta(db.Model):
    __tablename__ = "RACCOLTA"

    data = db.Column(db.Date, primary_key=True)
    id_appezzamento = db.Column(
        db.Integer,
        db.ForeignKey("APPEZZAMENTO.id_appezzamento"),
        primary_key=True,
    )
    quantita_raccolta = db.Column(db.Numeric(10, 2), nullable=False)
    anno_scorta = db.Column(db.Integer, nullable=False)
    email_azienda_agricola = db.Column(db.String(100), nullable=False)
    varieta_coltura = db.Column(db.String(50), nullable=False)
    specie_coltura = db.Column(db.String(50), nullable=False)


class PuntoVendita(db.Model):
    __tablename__ = "PUNTO_VENDITA"

    partita_iva = db.Column(db.String(11), primary_key=True)
    email_azienda_agricola = db.Column(
        db.String(100),
        db.ForeignKey("AZIENDA_AGRICOLA.email"),
        nullable=False,
    )
    nome = db.Column(db.String(100), nullable=False)
    indirizzo = db.Column(db.String(150), nullable=False)
    orari_apertura = db.Column(db.String(100), nullable=True)
    negozio_fisico = db.Column(db.Boolean, nullable=False)
    online = db.Column(db.Boolean, nullable=False)


class Cliente(db.Model):
    __tablename__ = "CLIENTE"

    id_cliente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    indirizzo = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    partita_iva = db.Column(db.String(11), nullable=True)
    metodo_pagamento = db.Column(db.String(50), nullable=False)


class Ordine(db.Model):
    __tablename__ = "ORDINE"

    id_ordine = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    totale_ordine = db.Column(db.Numeric(10, 2), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey("CLIENTE.id_cliente"), nullable=True)
    partita_iva_punto_vendita = db.Column(
        db.String(11),
        db.ForeignKey("PUNTO_VENDITA.partita_iva"),
        nullable=False,
    )


class Prelievo(db.Model):
    __tablename__ = "PRELIEVO"

    varieta_coltura = db.Column(db.String(50), primary_key=True)
    specie_coltura = db.Column(db.String(50), primary_key=True)
    anno_scorta = db.Column(db.Integer, primary_key=True)
    email_azienda_agricola = db.Column(db.String(100), primary_key=True)
    id_ordine = db.Column(db.Integer, primary_key=True)
    quantita_prodotto_ordine = db.Column(db.Numeric(10, 2), nullable=False)
