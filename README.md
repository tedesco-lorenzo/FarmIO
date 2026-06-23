# FarmIO

Gestionale agricolo sviluppato con `Python`, `Flask`, `Flask-SQLAlchemy`, `MySQL/MariaDB`, `HTML`, `CSS` e `Bootstrap`.

Il progetto nasce da un template dashboard adattato a Flask, ma ora è organizzato come una vera applicazione web con autenticazione, route modulari, modelli separati e pagine collegate al database.

## Stato attuale del progetto

Attualmente FarmIO gestisce una singola sessione aziendale: dopo il login, ogni pagina mostra e modifica solo i dati dell'azienda autenticata tramite `session["azienda_email"]`.

Le tabelle principali sono già collegate al database sia in lettura sia, in molte sezioni, anche in modifica/salvataggio.

## Funzionalità disponibili

- autenticazione azienda:
  - login
  - registrazione
  - cambio password semplificato da pagina `forgot password`
  - logout
- dashboard iniziale aggiornata con riepiloghi reali
- proprietà:
  - stabilimenti
  - terreni
- soggetto:
  - dipendenti e aziende esterne in tabella unica
  - dettaglio totale ore lavorate del singolo dipendente
- risorse materiali:
  - attrezzature
  - macchinari
  - schede manutenzione
- punto vendita:
  - gestione punti vendita aziendali
  - ordini online
  - ordini fisici
  - filtro per singolo punto vendita
  - dettaglio cliente
  - dettaglio ordine
- scorte:
  - visualizzazione quantità
  - modifica prezzo unitario
  - evidenza prezzi ancora a zero
- colture:
  - archivio consultabile di specie, varietà e descrizioni
- appezzamenti:
  - elenco appezzamenti
  - collegamento ai terreni
  - storici per singolo appezzamento
- storico appezzamenti:
  - irrigazione
  - trattamenti
  - raccolta
- interventi operativi:
  - collegamento a soggetti
  - collegamento a macchinari
  - collegamento a attrezzature
  - collegamento a appezzamenti

## Comportamento dell'interfaccia

- le pagine protette richiedono login
- le tabelle modificabili partono bloccate
- per modificare una tabella bisogna usare `Modifica tabella`
- dopo il salvataggio la tabella torna bloccata
- i messaggi di successo/errore si chiudono automaticamente dopo pochi secondi
- le sezioni principali usano uno stile coerente con il tema dashboard

## Stack tecnico

- `Python 3`
- `Flask`
- `Flask-SQLAlchemy`
- `PyMySQL`
- `MySQL` / `MariaDB`
- `Bootstrap`
- `Jinja2`

## Struttura del progetto

- `/Users/lorenzotedesco/Downloads/farmio/app.py`
  - crea l'app Flask
  - configura il database
  - applica il controllo login sulle pagine protette
- `/Users/lorenzotedesco/Downloads/farmio/extensions.py`
  - inizializzazione estensioni Flask
- `/Users/lorenzotedesco/Downloads/farmio/models.py`
  - modelli SQLAlchemy delle tabelle principali
- `/Users/lorenzotedesco/Downloads/farmio/routes/`
  - route divise per area funzionale:
    - `auth.py`
    - `dashboard.py`
    - `proprieta.py`
    - `soggetto.py`
    - `risorse.py`
    - `punto_vendita.py`
    - `scorte.py`
    - `colture.py`
    - `appezzamenti.py`
    - `interventi.py`
- `/Users/lorenzotedesco/Downloads/farmio/services.py`
  - funzioni di lettura, aggregazione dati e supporto dashboard
- `/Users/lorenzotedesco/Downloads/farmio/utils.py`
  - helper per sessione, formattazione date/importi e parsing input
- `/Users/lorenzotedesco/Downloads/farmio/templates/`
  - pagine HTML Flask
- `/Users/lorenzotedesco/Downloads/farmio/templates/partials/`
  - componenti comuni come sidebar e navigazione pagina
- `/Users/lorenzotedesco/Downloads/farmio/static/`
  - CSS, JS e asset del tema
- `/Users/lorenzotedesco/Downloads/farmio/farmio_create.sql`
  - struttura database
- `/Users/lorenzotedesco/Downloads/farmio/farmio_insert.sql`
  - dati di esempio
- `/Users/lorenzotedesco/Downloads/farmio/requirements.txt`
  - dipendenze Python

## Avvio locale

1. Entra nella cartella del progetto.
2. Installa le dipendenze:

```bash
pip3 install -r requirements.txt
```

3. Avvia MySQL/MariaDB da XAMPP.
4. Crea il database e le tabelle:

```bash
/Applications/XAMPP/xamppfiles/bin/mysql -u root < farmio_create.sql
```

5. Carica i dati iniziali:

```bash
/Applications/XAMPP/xamppfiles/bin/mysql -u root < farmio_insert.sql
```

6. Avvia il server Flask:

```bash
python3 app.py
```

7. Apri il browser su:

```text
http://127.0.0.1:5000
```

## Configurazione database attuale

La connessione è configurata in `/Users/lorenzotedesco/Downloads/farmio/app.py`:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost:3306/farmio?charset=utf8mb4"
```

Configurazione attuale:

- host: `localhost`
- porta: `3306`
- database: `farmio`
- utente: `root`
- password: nessuna

Se cambi configurazione MySQL/MariaDB, aggiorna questa stringa.

## Account di esempio

Nel file `/Users/lorenzotedesco/Downloads/farmio/farmio_insert.sql` sono presenti due aziende di esempio:

- `info@verdemurlo.it` / `verdemurlo123`
- `amministrazione@bioroma.it` / `bioroma123`

## Note utili

- Flask parte con `use_reloader=False`, quindi il server non viene avviato due volte
- all'avvio viene fatto un test semplice di connessione MySQL
- i dati mostrati nelle pagine vengono filtrati in base all'azienda loggata
- `Colture` è pensata come archivio di consultazione
- `Scorte` aggiorna i prezzi, mentre le quantità possono essere influenzate dalla raccolta
- la dashboard mostra solo riepiloghi sintetici e accessi rapidi

