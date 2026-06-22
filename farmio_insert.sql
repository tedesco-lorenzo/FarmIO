USE farmio;

-- 1. AZIENDA AGRICOLA
INSERT INTO AZIENDA_AGRICOLA (email, denominazione_sociale, password, anno_fondazione) VALUES
('info@verdemurlo.it', 'Verde Murlo Srl', 'verdemurlo123', 2010),
('amministrazione@bioroma.it', 'Bio Roma Organic', 'bioroma123', 2018);

-- 2. STABILIMENTO
INSERT INTO STABILIMENTO (
    email_azienda_agricola,
    latitudine,
    longitudine,
    anno_acquisto,
    descrizione,
    estensione
) VALUES
('info@verdemurlo.it', 43.76956000, 11.25581400, 2010, 'Sede centrale e uffici amministrativi', 150.50),
('info@verdemurlo.it', 43.77120000, 11.26350000, 2014, 'Magazzino attrezzi e ricambi', 210.00),
('info@verdemurlo.it', 43.76830000, 11.25190000, 2018, 'Locale vendita e confezionamento', 95.20),
('amministrazione@bioroma.it', 41.89025100, 12.49237300, 2019, 'Centro di confezionamento principale', 220.00),
('amministrazione@bioroma.it', 41.90180000, 12.50840000, 2020, 'Deposito mezzi agricoli', 310.40),
('amministrazione@bioroma.it', 41.88420000, 12.49790000, 2022, 'Laboratorio trasformazione ortaggi', 140.70);

-- 3. TERRENO AGRICOLO
INSERT INTO TERRENO_AGRICOLO (
    email_azienda_agricola,
    latitudine,
    longitudine,
    anno_acquisto,
    descrizione,
    tipologia_terreno,
    estensione
) VALUES
('info@verdemurlo.it', 43.77000000, 11.26000000, 2011, 'Vigneto Collina Nord', 'Argilloso', 5.40),
('info@verdemurlo.it', 43.76550000, 11.24890000, 2013, 'Oliveta Pian del Sole', 'Calcareo', 4.80),
('info@verdemurlo.it', 43.77420000, 11.26910000, 2017, 'Campo sperimentale ortaggi', 'Limoso', 3.20),
('amministrazione@bioroma.it', 41.90000000, 12.50000000, 2018, 'Tenuta Appia Antica', 'Tufo', 8.30),
('amministrazione@bioroma.it', 41.90750000, 12.51420000, 2021, 'Campo serre est', 'Sabbioso', 2.90),
('amministrazione@bioroma.it', 41.89670000, 12.48750000, 2022, 'Orto biologico urbano', 'Medio impasto', 4.10);

-- 4. COLTURA
INSERT INTO COLTURA (varieta, specie, descrizione) VALUES
('Chianti', 'Vite', 'Uva da vino rosso DOCG'),
('Vermentino', 'Vite', 'Uva a bacca bianca aromatica'),
('Frantoio', 'Olivo', 'Cultivar per olio extravergine'),
('Leccino', 'Olivo', 'Cultivar rustica ad alta resa'),
('San Marzano', 'Pomodoro', 'Pomodoro da industria e conserva'),
('Datterino', 'Pomodoro', 'Pomodoro da mensa dolce'),
('Romanesco', 'Zucchino', 'Zucchino verde chiaro'),
('Lattuga Gentile', 'Lattuga', 'Insalata da taglio');

-- 5. SOGGETTO
INSERT INTO SOGGETTO (
    id_soggetto,
    stipendio_orario,
    denominazione_sociale,
    azienda_esterna,
    partita_iva,
    nome,
    cognome,
    data_nascita,
    iban,
    codice_fiscale,
    manager,
    operaio,
    email_azienda_agricola
) VALUES
(1, 18.50, NULL, 0, NULL, 'Marco', 'Bellucci', '1981-04-18', 'IT60A0306909606100000123456', 'BLLMRC81D18H501A', 1, 0, 'info@verdemurlo.it'),
(2, 13.20, NULL, 0, NULL, 'Luca', 'Rossi', '1992-09-10', 'IT60A0306909606100000123457', 'RSSLCU92P10H501B', 0, 1, 'info@verdemurlo.it'),
(3, 12.80, NULL, 0, NULL, 'Sara', 'Conti', '1996-02-27', 'IT60A0306909606100000123458', 'CNTSRA96B67H501C', 0, 1, 'info@verdemurlo.it'),
(4, 24.00, 'TecnoPotature SRL', 1, '03123456789', NULL, NULL, NULL, NULL, NULL, 0, 0, 'info@verdemurlo.it'),
(1, 19.80, NULL, 0, NULL, 'Paolo', 'Ferretti', '1984-11-02', 'IT60B0306909606100000223451', 'FRRPLA84S02H501D', 1, 0, 'amministrazione@bioroma.it'),
(2, 14.10, NULL, 0, NULL, 'Elisa', 'Marini', '1993-06-16', 'IT60B0306909606100000223452', 'MRNLSE93H56H501E', 0, 1, 'amministrazione@bioroma.it'),
(3, 13.90, NULL, 0, NULL, 'Davide', 'Greco', '1998-01-08', 'IT60B0306909606100000223453', 'GRCDVD98A08H501F', 0, 1, 'amministrazione@bioroma.it'),
(4, 27.50, 'AgroServizi SRL', 1, '01234567890', NULL, NULL, NULL, NULL, NULL, 0, 0, 'amministrazione@bioroma.it'),
(5, 22.00, 'Irriga Roma SRL', 1, '09876543210', NULL, NULL, NULL, NULL, NULL, 0, 0, 'amministrazione@bioroma.it');

-- 6. REGISTRAZIONE ORE
INSERT INTO REGISTRAZIONE_ORE (email_azienda_agricola, id_soggetto, data, ore) VALUES
('info@verdemurlo.it', 1, '2026-06-17', 8.00),
('info@verdemurlo.it', 2, '2026-06-17', 7.50),
('info@verdemurlo.it', 3, '2026-06-17', 6.00),
('info@verdemurlo.it', 2, '2026-06-18', 8.00),
('info@verdemurlo.it', 3, '2026-06-18', 7.00),
('amministrazione@bioroma.it', 1, '2026-06-17', 8.00),
('amministrazione@bioroma.it', 2, '2026-06-17', 7.00),
('amministrazione@bioroma.it', 3, '2026-06-17', 7.50),
('amministrazione@bioroma.it', 2, '2026-06-18', 8.00),
('amministrazione@bioroma.it', 3, '2026-06-18', 8.00);

-- 7. RISORSA MATERIALE
INSERT INTO RISORSA_MATERIALE (
    id_risorsa_materiale,
    email_azienda_agricola,
    marca,
    modello,
    anno_acquisto,
    targa,
    prezzo,
    quantita,
    macchina_agricola,
    attrezzatura
) VALUES
(1, 'info@verdemurlo.it', 'John Deere', '5075E', 2020, 'AA123BB', 35000.00, 1, 1, 0),
(2, 'info@verdemurlo.it', 'New Holland', 'T4.90', 2021, 'BB234CC', 46800.00, 1, 1, 0),
(3, 'info@verdemurlo.it', 'Cima', 'Atomizzatore 1000', 2019, NULL, 8200.00, 1, 0, 1),
(4, 'info@verdemurlo.it', 'Campagnola', 'Forbice Stark', 2023, NULL, 950.00, 6, 0, 1),
(5, 'info@verdemurlo.it', 'Beta', 'Cassetta Raccolta', 2022, NULL, 45.00, 40, 0, 1),
(6, 'amministrazione@bioroma.it', 'Kubota', 'M5091', 2022, 'DD456EE', 54000.00, 1, 1, 0),
(7, 'amministrazione@bioroma.it', 'Goldoni', 'Q-110', 2020, 'EE567FF', 28500.00, 1, 1, 0),
(8, 'amministrazione@bioroma.it', 'Arco', 'Eco-Zappa', 2022, NULL, 1500.00, 3, 0, 1),
(9, 'amministrazione@bioroma.it', 'Irritec', 'Kit ala gocciolante', 2024, NULL, 780.00, 12, 0, 1),
(10, 'amministrazione@bioroma.it', 'Bcs', 'Trincia Light', 2021, NULL, 4900.00, 1, 0, 1);

-- 8. SCHEDA MANUTENZIONE
INSERT INTO SCHEDA_MANUTENZIONE (id_risorsa_materiale, id_manutenzione, data, costo_manutenzione, descrizione) VALUES
(1, 101, '2026-03-10', 450.00, 'Cambio olio e filtri motore'),
(2, 102, '2026-04-03', 620.00, 'Revisione impianto idraulico'),
(3, 103, '2026-05-12', 120.00, 'Sostituzione ugelli atomizzatore'),
(6, 104, '2026-02-18', 980.00, 'Tagliando completo trattore'),
(7, 105, '2026-04-27', 510.00, 'Sostituzione batteria e luci'),
(10, 106, '2026-05-30', 260.00, 'Affilatura coltelli trincia');

-- 9. APPEZZAMENTO
INSERT INTO APPEZZAMENTO (
    id_appezzamento,
    composizione_terreno,
    estensione,
    tipologia_copertura,
    antigrandine,
    antibrina,
    copertura_assicurativa,
    email_azienda_agricola,
    longitudine_terreno_agricolo,
    latitudine_terreno_agricolo,
    varieta_coltura,
    specie_coltura
) VALUES
(1, 'Medio impasto con scheletro', 2.50, 'Rete', 1, 0, 'Polizza grandine premium', 'info@verdemurlo.it', 11.26000000, 43.77000000, 'Chianti', 'Vite'),
(2, 'Calcareo drenante', 2.90, NULL, 0, 0, 'Polizza base uliveto', 'info@verdemurlo.it', 11.24890000, 43.76550000, 'Frantoio', 'Olivo'),
(3, 'Limoso fertile', 1.60, 'Tunnel', 0, 1, NULL, 'info@verdemurlo.it', 11.26910000, 43.77420000, 'Lattuga Gentile', 'Lattuga'),
(7, 'Franco sabbioso con ciottoli fini', 1.90, 'Rete', 1, 0, 'Polizza grandine premium', 'info@verdemurlo.it', 11.26000000, 43.77000000, 'Vermentino', 'Vite'),
(13, 'Argilloso sciolto con buon drenaggio', 1.35, 'Rete', 1, 0, 'Polizza grandine premium', 'info@verdemurlo.it', 11.26000000, 43.77000000, 'Chianti', 'Vite'),
(14, 'Medio impasto ricco di sostanza organica', 1.15, 'Rete', 1, 0, 'Polizza grandine premium', 'info@verdemurlo.it', 11.26000000, 43.77000000, 'Vermentino', 'Vite'),
(8, 'Calcareo profondo con buona drenanza', 1.40, NULL, 0, 0, 'Polizza base uliveto', 'info@verdemurlo.it', 11.24890000, 43.76550000, 'Leccino', 'Olivo'),
(9, 'Limoso soffice e ricco di sostanza organica', 1.10, 'Tunnel', 0, 1, NULL, 'info@verdemurlo.it', 11.26910000, 43.77420000, 'Romanesco', 'Zucchino'),
(4, 'Vulcanico ricco di potassio', 1.80, 'Serra', 1, 1, 'Generali Agri', 'amministrazione@bioroma.it', 12.50000000, 41.90000000, 'San Marzano', 'Pomodoro'),
(5, 'Sabbioso leggero', 1.10, 'Serra', 0, 0, 'All Risk Serra', 'amministrazione@bioroma.it', 12.51420000, 41.90750000, 'Datterino', 'Pomodoro'),
(6, 'Medio impasto ben lavorato', 2.20, NULL, 0, 0, NULL, 'amministrazione@bioroma.it', 12.48750000, 41.89670000, 'Romanesco', 'Zucchino'),
(10, 'Vulcanico drenante con ottima fertilità', 2.10, 'Serra', 1, 1, 'Generali Agri', 'amministrazione@bioroma.it', 12.50000000, 41.90000000, 'Datterino', 'Pomodoro'),
(11, 'Sabbioso leggero con irrigazione controllata', 0.95, 'Serra', 0, 0, 'All Risk Serra', 'amministrazione@bioroma.it', 12.51420000, 41.90750000, 'San Marzano', 'Pomodoro'),
(12, 'Medio impasto ad alta resa orticola', 1.30, NULL, 0, 0, NULL, 'amministrazione@bioroma.it', 12.48750000, 41.89670000, 'Lattuga Gentile', 'Lattuga');

-- 10. INTERVENTO OPERATIVO
INSERT INTO INTERVENTO_OPERATIVO (data_ora_inizio, data_ora_fine, descrizione, id_appezzamento) VALUES
('2026-06-17 07:00:00', '2026-06-17 11:00:00', 'Potatura verde e legatura filari', 1),
('2026-06-18 06:30:00', '2026-06-18 10:30:00', 'Controllo fitosanitario oliveto', 2),
('2026-06-18 07:15:00', '2026-06-18 09:45:00', 'Raccolta insalata e pulizia tunnel', 3),
('2026-06-19 07:00:00', '2026-06-19 10:00:00', 'Diradamento grappoli e sistemazione fili', 7),
('2026-06-20 07:10:00', '2026-06-20 10:20:00', 'Spollonatura e controllo tralci giovani', 13),
('2026-06-20 10:40:00', '2026-06-20 13:00:00', 'Legatura finale e sistemazione rete antigrandine', 14),
('2026-06-19 06:45:00', '2026-06-19 09:30:00', 'Sfalcio erba e controllo impianto oliveto', 8),
('2026-06-19 07:20:00', '2026-06-19 10:10:00', 'Trapianto zucchine e pacciamatura filari', 9),
('2026-06-17 09:30:00', '2026-06-17 13:00:00', 'Diserbo manuale e legatura pomodoro', 4),
('2026-06-18 05:45:00', '2026-06-18 08:30:00', 'Irrigazione e controllo ali gocciolanti', 5),
('2026-06-18 07:00:00', '2026-06-18 11:30:00', 'Trinciatura interfila e manutenzione campo', 6),
('2026-06-19 08:00:00', '2026-06-19 12:00:00', 'Scacchiatura e tutoraggio pomodoro datterino', 10),
('2026-06-19 06:30:00', '2026-06-19 10:30:00', 'Raccolta selettiva San Marzano', 11),
('2026-06-19 07:10:00', '2026-06-19 09:00:00', 'Trapianto lattuga e controllo irrigazione', 12);

-- 11. ASSEGNAZIONE
INSERT INTO ASSEGNAZIONE (id_appezzamento, data_ora_inizio_intervento_operativo, email_azienda_agricola, id_soggetto) VALUES
(1, '2026-06-17 07:00:00', 'info@verdemurlo.it', 1),
(1, '2026-06-17 07:00:00', 'info@verdemurlo.it', 2),
(2, '2026-06-18 06:30:00', 'info@verdemurlo.it', 2),
(2, '2026-06-18 06:30:00', 'info@verdemurlo.it', 4),
(3, '2026-06-18 07:15:00', 'info@verdemurlo.it', 3),
(7, '2026-06-19 07:00:00', 'info@verdemurlo.it', 1),
(7, '2026-06-19 07:00:00', 'info@verdemurlo.it', 2),
(13, '2026-06-20 07:10:00', 'info@verdemurlo.it', 1),
(13, '2026-06-20 07:10:00', 'info@verdemurlo.it', 3),
(14, '2026-06-20 10:40:00', 'info@verdemurlo.it', 1),
(14, '2026-06-20 10:40:00', 'info@verdemurlo.it', 2),
(8, '2026-06-19 06:45:00', 'info@verdemurlo.it', 2),
(8, '2026-06-19 06:45:00', 'info@verdemurlo.it', 3),
(9, '2026-06-19 07:20:00', 'info@verdemurlo.it', 3),
(4, '2026-06-17 09:30:00', 'amministrazione@bioroma.it', 1),
(4, '2026-06-17 09:30:00', 'amministrazione@bioroma.it', 2),
(5, '2026-06-18 05:45:00', 'amministrazione@bioroma.it', 3),
(5, '2026-06-18 05:45:00', 'amministrazione@bioroma.it', 5),
(6, '2026-06-18 07:00:00', 'amministrazione@bioroma.it', 1),
(6, '2026-06-18 07:00:00', 'amministrazione@bioroma.it', 4),
(10, '2026-06-19 08:00:00', 'amministrazione@bioroma.it', 1),
(10, '2026-06-19 08:00:00', 'amministrazione@bioroma.it', 2),
(11, '2026-06-19 06:30:00', 'amministrazione@bioroma.it', 3),
(11, '2026-06-19 06:30:00', 'amministrazione@bioroma.it', 4),
(12, '2026-06-19 07:10:00', 'amministrazione@bioroma.it', 2),
(12, '2026-06-19 07:10:00', 'amministrazione@bioroma.it', 5);

-- 12. UTILIZZO
INSERT INTO UTILIZZO (id_risorsa_materiale, id_appezzamento, data_ora_inizio_intervento_operativo) VALUES
(1, 1, '2026-06-17 07:00:00'),
(3, 1, '2026-06-17 07:00:00'),
(4, 2, '2026-06-18 06:30:00'),
(5, 3, '2026-06-18 07:15:00'),
(1, 7, '2026-06-19 07:00:00'),
(3, 7, '2026-06-19 07:00:00'),
(1, 13, '2026-06-20 07:10:00'),
(3, 13, '2026-06-20 07:10:00'),
(1, 14, '2026-06-20 10:40:00'),
(4, 14, '2026-06-20 10:40:00'),
(2, 8, '2026-06-19 06:45:00'),
(4, 8, '2026-06-19 06:45:00'),
(4, 9, '2026-06-19 07:20:00'),
(5, 9, '2026-06-19 07:20:00'),
(6, 4, '2026-06-17 09:30:00'),
(8, 4, '2026-06-17 09:30:00'),
(9, 5, '2026-06-18 05:45:00'),
(7, 6, '2026-06-18 07:00:00'),
(10, 6, '2026-06-18 07:00:00'),
(6, 10, '2026-06-19 08:00:00'),
(8, 10, '2026-06-19 08:00:00'),
(7, 11, '2026-06-19 06:30:00'),
(8, 11, '2026-06-19 06:30:00'),
(9, 12, '2026-06-19 07:10:00');

-- 13. IRRIGAZIONE
INSERT INTO IRRIGAZIONE (data, ora_inizio, nome_prodotto, quantita_prodotto, id_appezzamento) VALUES
('2026-06-09', '20:30:00', NULL, NULL, 1),
('2026-06-11', '21:00:00', 'Biostimolante vite', 8.00, 1),
('2026-06-12', '06:15:00', NULL, NULL, 2),
('2026-06-13', '20:45:00', 'Biostimolante uva', 5.00, 7),
('2026-06-14', '21:10:00', 'Biostimolante vite', 6.50, 13),
('2026-06-15', '20:50:00', NULL, NULL, 14),
('2026-06-14', '06:10:00', NULL, NULL, 8),
('2026-06-18', '05:30:00', 'Fertirrigante ortaggi', 4.50, 9),
('2026-06-16', '05:00:00', 'Fertirrigante NPK', 15.50, 4),
('2026-06-17', '05:45:00', 'Calcio liquido', 6.20, 5),
('2026-06-18', '06:00:00', NULL, NULL, 6),
('2026-06-17', '05:30:00', 'Potassio liquido', 7.00, 10),
('2026-06-18', '06:10:00', 'NPK Bio', 9.50, 11),
('2026-06-19', '05:50:00', NULL, NULL, 12);

-- 14. TRATTAMENTO
INSERT INTO TRATTAMENTO (data, quantita_acqua, nome_prodotto, quantita_prodotto, id_appezzamento) VALUES
('2026-05-14', 500.00, 'Rame e zolfo', 12.00, 1),
('2026-05-25', 320.00, 'Caolino', 9.00, 2),
('2026-06-03', 180.00, 'Macerato ortica', 14.00, 3),
('2026-05-21', 420.00, 'Rame leggero', 10.00, 7),
('2026-05-23', 390.00, 'Zolfo ventilato', 8.00, 13),
('2026-05-27', 410.00, 'Rame bio', 9.50, 14),
('2026-05-29', 260.00, 'Sapone molle', 6.00, 8),
('2026-06-08', 140.00, 'Propoli bio', 4.00, 9),
('2026-05-20', 1000.00, 'Bio-Insect Stop', 5.00, 4),
('2026-06-01', 240.00, 'Estratto algale', 11.00, 5),
('2026-06-07', 350.00, 'Antioidico bio', 7.50, 6),
('2026-05-28', 300.00, 'Estratto equiseto', 8.00, 10),
('2026-06-04', 360.00, 'Rame bio', 9.00, 11),
('2026-06-10', 110.00, 'Sapone potassico', 3.50, 12);

-- 15. SCORTA
INSERT INTO SCORTA (email_azienda_agricola, anno, varieta_coltura, specie_coltura, quantita_totale, prezzo_unitario) VALUES
('info@verdemurlo.it', 2025, 'Chianti', 'Vite', 5200.00, 1.20),
('info@verdemurlo.it', 2025, 'Vermentino', 'Vite', 3100.00, 1.35),
('info@verdemurlo.it', 2025, 'Frantoio', 'Olivo', 1450.00, 8.50),
('info@verdemurlo.it', 2025, 'Leccino', 'Olivo', 980.00, 8.10),
('info@verdemurlo.it', 2026, 'Lattuga Gentile', 'Lattuga', 680.00, 1.90),
('info@verdemurlo.it', 2026, 'Romanesco', 'Zucchino', 540.00, 1.60),
('amministrazione@bioroma.it', 2026, 'San Marzano', 'Pomodoro', 800.00, 0.65),
('amministrazione@bioroma.it', 2026, 'Datterino', 'Pomodoro', 620.00, 1.10),
('amministrazione@bioroma.it', 2026, 'Romanesco', 'Zucchino', 910.00, 1.45),
('amministrazione@bioroma.it', 2026, 'Lattuga Gentile', 'Lattuga', 430.00, 1.75);

-- 16. RACCOLTA
INSERT INTO RACCOLTA (data, id_appezzamento, quantita_raccolta, anno_scorta, email_azienda_agricola, varieta_coltura, specie_coltura) VALUES
('2025-09-20', 1, 5200.00, 2025, 'info@verdemurlo.it', 'Chianti', 'Vite'),
('2025-09-28', 7, 3100.00, 2025, 'info@verdemurlo.it', 'Vermentino', 'Vite'),
('2025-10-02', 13, 2100.00, 2025, 'info@verdemurlo.it', 'Chianti', 'Vite'),
('2025-10-05', 14, 1650.00, 2025, 'info@verdemurlo.it', 'Vermentino', 'Vite'),
('2025-11-05', 2, 1450.00, 2025, 'info@verdemurlo.it', 'Frantoio', 'Olivo'),
('2025-11-09', 8, 980.00, 2025, 'info@verdemurlo.it', 'Leccino', 'Olivo'),
('2026-06-15', 3, 680.00, 2026, 'info@verdemurlo.it', 'Lattuga Gentile', 'Lattuga'),
('2026-06-16', 9, 540.00, 2026, 'info@verdemurlo.it', 'Romanesco', 'Zucchino'),
('2026-06-15', 4, 850.00, 2026, 'amministrazione@bioroma.it', 'San Marzano', 'Pomodoro'),
('2026-06-16', 5, 620.00, 2026, 'amministrazione@bioroma.it', 'Datterino', 'Pomodoro'),
('2026-06-17', 6, 910.00, 2026, 'amministrazione@bioroma.it', 'Romanesco', 'Zucchino'),
('2026-06-18', 10, 410.00, 2026, 'amministrazione@bioroma.it', 'Datterino', 'Pomodoro'),
('2026-06-19', 11, 390.00, 2026, 'amministrazione@bioroma.it', 'San Marzano', 'Pomodoro'),
('2026-06-19', 12, 430.00, 2026, 'amministrazione@bioroma.it', 'Lattuga Gentile', 'Lattuga');

-- 17. PUNTO VENDITA
INSERT INTO PUNTO_VENDITA (partita_iva, email_azienda_agricola, nome, indirizzo, orari_apertura, negozio_fisico, online) VALUES
('01111111111', 'info@verdemurlo.it', 'Bottega della Vite', 'Via del Campo 12, Firenze', '09:00-19:00', 1, 0),
('01111111112', 'info@verdemurlo.it', 'Verde Murlo Shop', 'https://shop.verdemurlo.it', '24/7 online', 0, 1),
('03333333333', 'amministrazione@bioroma.it', 'BioRoma Store Online', 'https://shop.bioroma.it', '24/7 online', 0, 1),
('03333333334', 'amministrazione@bioroma.it', 'Mercato BioRoma', 'Via Appia Nuova 88, Roma', '08:30-18:30', 1, 0);

-- 18. CLIENTE
INSERT INTO CLIENTE (id_cliente, nome, cognome, indirizzo, email, partita_iva, metodo_pagamento) VALUES
(1, 'Giovanni', 'Pascoli', 'Via delle Ruote 5, Firenze', 'giovanni@gmail.com', NULL, 'Contanti'),
(2, 'Elena', 'Russo', 'Viale Europa 88, Siena', 'elena.russo@outlook.it', NULL, 'Carta di Credito'),
(3, 'Marta', 'Neri', 'Via Gioberti 14, Firenze', 'marta.neri@gmail.com', NULL, 'Carta di Credito'),
(4, 'Ristorante Da Mimmo', 'Esposito', 'Piazza Navona 3, Roma', 'info@damimmo.it', '09876543210', 'Bonifico'),
(5, 'Paolo', 'Seri', 'Via Tiburtina 120, Roma', 'paolo.seri@gmail.com', NULL, 'PayPal'),
(6, 'Market Verde', 'Bassi', 'Via Salaria 45, Roma', 'acquisti@marketverde.it', '05432167890', 'Bonifico');

-- 19. ORDINE
INSERT INTO ORDINE (id_ordine, data, totale_ordine, id_cliente, partita_iva_punto_vendita) VALUES
(1, '2026-06-17', 144.00, 1, '01111111111'),
(2, '2026-06-17', 96.00, 2, '01111111112'),
(3, '2026-06-18', 58.50, 3, '01111111112'),
(4, '2026-06-17', 32.50, 4, '03333333333'),
(5, '2026-06-18', 71.00, 5, '03333333333'),
(6, '2026-06-18', 188.40, 6, '03333333334');

-- 20. PRELIEVO
INSERT INTO PRELIEVO (varieta_coltura, specie_coltura, anno_scorta, email_azienda_agricola, id_ordine, quantita_prodotto_ordine) VALUES
('Chianti', 'Vite', 2025, 'info@verdemurlo.it', 1, 120.00),
('Frantoio', 'Olivo', 2025, 'info@verdemurlo.it', 2, 8.00),
('Lattuga Gentile', 'Lattuga', 2026, 'info@verdemurlo.it', 3, 30.00),
('San Marzano', 'Pomodoro', 2026, 'amministrazione@bioroma.it', 4, 50.00),
('Datterino', 'Pomodoro', 2026, 'amministrazione@bioroma.it', 5, 40.00),
('Romanesco', 'Zucchino', 2026, 'amministrazione@bioroma.it', 6, 96.00);
