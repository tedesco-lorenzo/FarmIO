# FarmIO

Gestionale agricolo sviluppato con `Python`, `Flask`, `Flask-SQLAlchemy`, `MySQL/MariaDB`, `HTML`, `CSS` e `Bootstrap`.

Il progetto parte da un template dashboard adattato a Flask, ma oggi contiene una struttura applicativa dedicata alla gestione di aziende agricole, con autenticazione, pagine protette e tabelle collegate al database.

## Funzionalità attuali

- login e registrazione azienda
- accesso filtrato per azienda tramite `session`
- dashboard iniziale
- proprietà:
  - stabilimenti
  - terreni
- soggetto
- risorse materiali:
  - attrezzature
  - macchinari
  - schede manutenzione
- punto vendita:
  - online
  - fisico
  - dettaglio ordini
- scorte
- appezzamenti
- storico appezzamenti:
  - irrigazione
  - trattamenti
  - raccolta
- interventi operativi

## Stack tecnico

- `Python 3`
- `Flask`
- `Flask-SQLAlchemy`
- `PyMySQL`
- `MySQL`
- `Bootstrap`

## Struttura principale

- `app.py` → logica Flask, route, modelli SQLAlchemy e salvataggi
- `templates/` → pagine HTML Flask
- `templates/partials/` → sidebar e componenti comuni
- `static/` → CSS, JS, immagini e asset del template adattato
- `farmio_create.sql` → struttura del database
- `farmio_insert.sql` → dati di esempio
- `requirements.txt` → dipendenze Python

## Avvio locale

1. Crea ed entra nella cartella del progetto.
2. Installa le dipendenze:

```bash
pip3 install -r requirements.txt
```

3. Avvia MySQL da XAMPP.
4. Crea la struttura del database:

```bash
/Applications/XAMPP/xamppfiles/bin/mysql -u root < farmio_create.sql
```

5. Carica i dati di esempio:

```bash
/Applications/XAMPP/xamppfiles/bin/mysql -u root < farmio_insert.sql
```

6. Avvia il progetto:

```bash
python3 app.py
```

7. Apri il browser su:

```text
http://127.0.0.1:5000
```

## Connessione database attuale

In `app.py` la connessione è configurata così:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost:3306/farmio?charset=utf8mb4"
```

Quindi al momento il progetto usa:

- host: `localhost`
- porta: `3306`
- database: `farmio`
- utente: `root`
- password: nessuna

Se cambi configurazione MySQL, aggiorna questa riga in `app.py`.

## Account demo

Nel file `farmio_insert.sql` sono presenti due aziende di esempio:

- `info@verdemurlo.it` / `verdemurlo123`
- `amministrazione@bioroma.it` / `bioroma123`

## Note utili

- il progetto usa `use_reloader=False`, quindi Flask non parte due volte
- dopo una modifica a `app.py`, riavvia manualmente il server
- i dati mostrati nelle pagine vengono filtrati in base all'email dell'azienda loggata
- alcune tabelle sono già collegate al database anche in inserimento/modifica, altre potranno essere completate progressivamente

## Obiettivo del progetto

L'obiettivo è costruire un gestionale agricolo grafico e operativo, pronto per essere completato lato database e logiche applicative, mantenendo una dashboard chiara, coerente e facilmente estendibile.
