CREATE DATABASE IF NOT EXISTS farmio;
USE farmio;

-- 1. AZIENDA AGRICOLA
CREATE TABLE AZIENDA_AGRICOLA (
    email VARCHAR(100) PRIMARY KEY,
    denominazione_sociale VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    anno_fondazione INT NOT NULL
);

-- 2. STABILIMENTO
CREATE TABLE STABILIMENTO (
    email_azienda_agricola VARCHAR(100),
    latitudine DECIMAL(10, 8),
    longitudine DECIMAL(11, 8),
    anno_acquisto INT NOT NULL,
    descrizione TEXT NOT NULL,
    estensione DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (latitudine, longitudine),
    FOREIGN KEY (email_azienda_agricola) REFERENCES AZIENDA_AGRICOLA(email) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 3. TERRENO AGRICOLO
CREATE TABLE TERRENO_AGRICOLO (
    email_azienda_agricola VARCHAR(100),
    latitudine DECIMAL(10, 8),
    longitudine DECIMAL(11, 8),
    anno_acquisto INT NOT NULL,
    descrizione TEXT NOT NULL,
    tipologia_terreno VARCHAR(50) NOT NULL,
    estensione DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (latitudine, longitudine),
    FOREIGN KEY (email_azienda_agricola) REFERENCES AZIENDA_AGRICOLA(email) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 4. COLTURA
CREATE TABLE COLTURA (
    varieta VARCHAR(50),
    specie VARCHAR(50),
    descrizione TEXT NOT NULL,
    PRIMARY KEY (varieta, specie)
);

-- 5. SOGGETTO
CREATE TABLE SOGGETTO (
    id_soggetto INT AUTO_INCREMENT PRIMARY KEY,
    stipendio_orario DECIMAL(10, 2) NOT NULL,
    denominazione_sociale VARCHAR(100) NULL,
    azienda_esterna VARCHAR(100) NULL,
    partita_iva VARCHAR(11) NULL,
    nome VARCHAR(50) NULL,
    cognome VARCHAR(50) NULL,
    data_nascita DATE NULL,
    iban VARCHAR(27) NULL,
    codice_fiscale VARCHAR(16) NULL,
    manager VARCHAR(50) NULL,
    operaio VARCHAR(50) NULL,
    email_azienda_agricola VARCHAR(100) NOT NULL,
    FOREIGN KEY (email_azienda_agricola) REFERENCES AZIENDA_AGRICOLA(email) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 6. REGISTRAZIONE ORE
CREATE TABLE REGISTRAZIONE_ORE (
    id_soggetto INT,
    data DATE,
    ore DECIMAL(4, 2) NOT NULL,
    PRIMARY KEY (id_soggetto, data),
    FOREIGN KEY (id_soggetto) REFERENCES SOGGETTO(id_soggetto) ON DELETE CASCADE
);

-- 7. RISORSA MATERIALE
CREATE TABLE RISORSA_MATERIALE (
    email_azienda_agricola VARCHAR(100),
    id_risorsa_materiale INT,
    marca VARCHAR(50) NOT NULL,
    modello VARCHAR(50) NOT NULL,
    anno_acquisto INT NOT NULL,
    targa VARCHAR(20) NULL,
    prezzo DECIMAL(10, 2) NOT NULL,
    quantita INT NOT NULL,
    macchina_agricola VARCHAR(50) NULL,
    attrezzatura VARCHAR(50) NULL,
    PRIMARY KEY (email_azienda_agricola, id_risorsa_materiale),
    FOREIGN KEY (email_azienda_agricola) REFERENCES AZIENDA_AGRICOLA(email) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8. SCHEDA MANUTENZIONE
CREATE TABLE SCHEDA_MANUTENZIONE (
    email_azienda_agricola VARCHAR(100),
    id_risorsa_materiale INT,
    id_manutenzione INT,
    data DATE NOT NULL,
    costo_manutenzione DECIMAL(10, 2) NOT NULL,
    descrizione TEXT NOT NULL,
    PRIMARY KEY (email_azienda_agricola, id_risorsa_materiale, id_manutenzione),
    FOREIGN KEY (email_azienda_agricola, id_risorsa_materiale) REFERENCES RISORSA_MATERIALE(email_azienda_agricola, id_risorsa_materiale) ON DELETE CASCADE
);

-- 9. APPEZZAMENTO
CREATE TABLE APPEZZAMENTO (
    id_appezzamento INT AUTO_INCREMENT PRIMARY KEY,
    composizione_terreno VARCHAR(100) NOT NULL,
    estensione DECIMAL(10, 2) NOT NULL,
    tipologia_copertura VARCHAR(50) NULL,
    antigrandine BOOLEAN NULL,
    antibrina BOOLEAN NULL,
    copertura_assicurativa VARCHAR(100) NULL,
    email_azienda_agricola VARCHAR(100) NOT NULL,
    longitudine_terreno_agricolo DECIMAL(11, 8) NOT NULL,
    latitudine_terreno_agricolo DECIMAL(10, 8) NOT NULL,
    varieta_coltura VARCHAR(50) NOT NULL,
    specie_coltura VARCHAR(50) NOT NULL,
    FOREIGN KEY (email_azienda_agricola) REFERENCES AZIENDA_AGRICOLA(email),
    FOREIGN KEY (latitudine_terreno_agricolo, longitudine_terreno_agricolo) REFERENCES TERRENO_AGRICOLO(latitudine, longitudine),
    FOREIGN KEY (varieta_coltura, specie_coltura) REFERENCES COLTURA(varieta, specie)
);

-- 10. ASSEGNAZIONE
CREATE TABLE ASSEGNAZIONE (
    id_appezzamento INT,
    data_ora_inizio_intervento_operativo DATETIME,
    email_azienda_agricola VARCHAR(100),
    id_soggetto INT,
    PRIMARY KEY (id_appezzamento, data_ora_inizio_intervento_operativo, email_azienda_agricola, id_soggetto),
    FOREIGN KEY (id_appezzamento) REFERENCES APPEZZAMENTO(id_appezzamento),
    FOREIGN KEY (id_soggetto) REFERENCES SOGGETTO(id_soggetto)
);

-- 11. INTERVENTO OPERATIVO
CREATE TABLE INTERVENTO_OPERATIVO (
    data_ora_inizio DATETIME,
    data_ora_fine DATETIME NULL,
    descrizione TEXT NOT NULL,
    id_appezzamento INT,
    PRIMARY KEY (data_ora_inizio, id_appezzamento),
    FOREIGN KEY (id_appezzamento) REFERENCES APPEZZAMENTO(id_appezzamento) ON DELETE CASCADE
);

-- 12. UTILIZZO
CREATE TABLE UTILIZZO (
    email_azienda_agricola VARCHAR(100),
    id_risorsa_materiale INT,
    id_appezzamento INT,
    data_ora_inizio_intervento_operativo DATETIME,
    PRIMARY KEY (email_azienda_agricola, id_risorsa_materiale, id_appezzamento, data_ora_inizio_intervento_operativo),
    FOREIGN KEY (email_azienda_agricola, id_risorsa_materiale) REFERENCES RISORSA_MATERIALE(email_azienda_agricola, id_risorsa_materiale),
    FOREIGN KEY (id_appezzamento) REFERENCES APPEZZAMENTO(id_appezzamento)
);

-- 13. IRRIGAZIONE
CREATE TABLE IRRIGAZIONE (
    data DATE,
    ora_inizio TIME,
    nome_prodotto VARCHAR(100) NULL,
    quantita_prodotto DECIMAL(10, 2) NULL,
    id_appezzamento INT,
    PRIMARY KEY (data, ora_inizio, id_appezzamento),
    FOREIGN KEY (id_appezzamento) REFERENCES APPEZZAMENTO(id_appezzamento) ON DELETE CASCADE
);

-- 14. TRATTAMENTO
CREATE TABLE TRATTAMENTO (
    data DATE,
    quantita_acqua DECIMAL(10, 2) NOT NULL,
    nome_prodotto VARCHAR(100) NOT NULL,
    quantita_prodotto DECIMAL(10, 2) NOT NULL,
    id_appezzamento INT,
    PRIMARY KEY (data, id_appezzamento),
    FOREIGN KEY (id_appezzamento) REFERENCES APPEZZAMENTO(id_appezzamento) ON DELETE CASCADE
);

-- 15. SCORTA
CREATE TABLE SCORTA (
    email_azienda_agricola VARCHAR(100),
    anno INT,
    varieta_coltura VARCHAR(50),
    specie_coltura VARCHAR(50),
    quantita_totale DECIMAL(10, 2) NOT NULL,
    prezzo_unitario DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (email_azienda_agricola, anno, varieta_coltura, specie_coltura),
    FOREIGN KEY (email_azienda_agricola) REFERENCES AZIENDA_AGRICOLA(email),
    FOREIGN KEY (varieta_coltura, specie_coltura) REFERENCES COLTURA(varieta, specie)
);

-- 16. RACCOLTA
CREATE TABLE RACCOLTA (
    data DATE,
    id_appezzamento INT,
    quantita_raccolta DECIMAL(10, 2) NOT NULL,
    anno_scorta INT NOT NULL,
    email_azienda_agricola VARCHAR(100) NOT NULL,
    varieta_coltura VARCHAR(50) NOT NULL,
    specie_coltura VARCHAR(50) NOT NULL,
    PRIMARY KEY (data, id_appezzamento),
    FOREIGN KEY (id_appezzamento) REFERENCES APPEZZAMENTO(id_appezzamento),
    FOREIGN KEY (email_azienda_agricola, anno_scorta, varieta_coltura, specie_coltura) REFERENCES SCORTA(email_azienda_agricola, anno, varieta_coltura, specie_coltura)
);

-- 17. PUNTO VENDITA
CREATE TABLE PUNTO_VENDITA (
    email_azienda_agricola VARCHAR(100),
    partita_iva VARCHAR(11),
    nome VARCHAR(100) NOT NULL,
    indirizzo VARCHAR(150) NOT NULL,
    orari_apertura VARCHAR(100) NULL,
    negozio_fisico BOOLEAN NULL,
    online BOOLEAN NULL,
    PRIMARY KEY (email_azienda_agricola, partita_iva),
    FOREIGN KEY (email_azienda_agricola) REFERENCES AZIENDA_AGRICOLA(email) ON DELETE CASCADE
);

-- 18. PRELIEVO
CREATE TABLE PRELIEVO (
    varieta_coltura VARCHAR(50),
    specie_coltura VARCHAR(50),
    anno_scorta INT,
    email_azienda_agricola VARCHAR(100),
    id_ordine INT,
    quantita_prodotto_ordine DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (varieta_coltura, specie_coltura, anno_scorta, email_azienda_agricola, id_ordine),
    FOREIGN KEY (email_azienda_agricola, anno_scorta, varieta_coltura, specie_coltura) REFERENCES SCORTA(email_azienda_agricola, anno, varieta_coltura, specie_coltura)
);

-- 19. CLIENTE
CREATE TABLE CLIENTE (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    indirizzo VARCHAR(150) NULL,
    email VARCHAR(100) NULL,
    partita_iva VARCHAR(11) NULL,
    metodo_pagamento VARCHAR(50) NOT NULL
);

-- 20. ORDINE
CREATE TABLE ORDINE (
    id_ordine INT AUTO_INCREMENT PRIMARY KEY,
    data DATE NOT NULL,
    totale_ordine DECIMAL(10, 2) NOT NULL,
    id_cliente INT NULL,
    partita_iva_punto_vendita VARCHAR(11) NOT NULL,
    email_azienda_agricola VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente),
    FOREIGN KEY (email_azienda_agricola, partita_iva_punto_vendita) REFERENCES PUNTO_VENDITA(email_azienda_agricola, partita_iva)
);