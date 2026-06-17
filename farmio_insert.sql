USE azienda_agricola_db;

-- 1. AZIENDA AGRICOLA
INSERT INTO AZIENDA_AGRICOLA VALUES 
('info@verdemurlo.it', 'Verde Murlo Srl', 'hash_pass_1', 2010),
('contatti@terradisiena.com', 'Terra di Siena Soc. Agr.', 'hash_pass_2', 2015),
('amministrazione@bioroma.it', 'Bio Roma Organic', 'hash_pass_3', 2018),
('f.lli_rossi@gmail.com', 'Fratelli Rossi Agricoltura', 'hash_pass_4', 2005);

-- 2. STABILIMENTO
INSERT INTO STABILIMENTO VALUES 
('info@verdemurlo.it', 43.769560, 11.255814, 2010, 'Sede centrale e uffici', 150.50),
('contatti@terradisiena.com', 43.318800, 11.330750, 2015, 'Deposito macchinari', 300.00),
('amministrazione@bioroma.it', 41.890251, 12.492373, 2019, 'Centro di confezionamento', 220.00),
('f.lli_rossi@gmail.com', 44.494887, 11.342616, 2006, 'Magazzino principale stoccaggio', 500.25);

-- 3. TERRENO AGRICOLO
INSERT INTO TERRENO_AGRICOLO VALUES 
('info@verdemurlo.it', 43.770000, 11.260000, 2011, 'Campo Nord - Collinare', 'Argilloso', 5.4),
('contatti@terradisiena.com', 43.320000, 11.340000, 2016, 'Valle del Sole', 'Sabbioso', 12.8),
('amministrazione@bioroma.it', 41.900000, 12.500000, 2018, 'Tenuta Appia Antica', 'Tufo', 8.3),
('f.lli_rossi@gmail.com', 44.500000, 11.350000, 2005, 'Pianura del Po', 'Alluvionale', 25.0);

-- 4. COLTURA
INSERT INTO COLTURA VALUES 
('Chianti', 'Vite', 'Uva da vino rosso DOCG'),
('Frantoio', 'Olivo', 'Oliva per olio extravergine'),
('San Marzano', 'Pomodoro', 'Pomodoro da industria/conserva'),
('Senatore Cappelli', 'Grano', 'Grano duro antico');

-- 5. SOGGETTO
INSERT INTO SOGGETTO VALUES 
(1, 12.50, NULL, NULL, NULL, 'Mario', 'Rossi', '1985-05-12', 'IT60A1234567890123456789012', 'RSSMRA85M12H501Z', 'No', 'Sì', 'info@verdemurlo.it'),
(2, 15.00, NULL, NULL, NULL, 'Luigi', 'Verdi', '1990-08-24', 'IT60B1234567890123456789012', 'VRDLGU90R24H501X', 'Sì', 'No', 'contatti@terradisiena.com'),
(3, 22.00, 'AgroServizi SRL', 'Esterna', '01234567890', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'amministrazione@bioroma.it'),
(4, 11.00, NULL, NULL, NULL, 'Anna', 'Bianchi', '1993-02-02', 'IT60C1234567890123456789012', 'BNCNNA93B42H501W', 'No', 'Sì', 'f.lli_rossi@gmail.com');

-- 6. REGISTRAZIONE ORE
INSERT INTO REGISTRAZIONE_ORE VALUES 
(1, '2026-06-15', 8.00),
(2, '2026-06-15', 7.50),
(4, '2026-06-16', 6.00),
(1, '2026-06-16', 8.00);

-- 7. RISORSA MATERIALE
INSERT INTO RISORSA_MATERIALE VALUES 
('info@verdemurlo.it', 1, 'John Deere', '5075E', 2020, 'AA123BB', 35000.00, 1, TRUE, FALSE),
('contatti@terradisiena.com', 1, 'New Holland', 'T4', 2021, 'CC456DD', 42000.00, 1, TRUE , FALSE),
('amministrazione@bioroma.it', 1, 'Arco', 'Eco-Zappa', 2022, NULL, 1500.00, 3, FALSE, TRUE),
('f.lli_rossi@gmail.com', 1, 'Claas', 'Lexion', 2019, 'EE789FF', 120000.00, 1, TRUE, FALSE);

-- 8. SCHEDA MANUTENZIONE
INSERT INTO SCHEDA_MANUTENZIONE VALUES 
('info@verdemurlo.it', 1, 101, '2026-03-10', 450.00, 'Cambio olio e filtri motore'),
('contatti@terradisiena.com', 1, 102, '2026-04-12', 1200.00, 'Sostituzione pneumatici posteriori'),
('amministrazione@bioroma.it', 1, 103, '2026-05-20', 80.00, 'Affilatura lame attrezzatura'),
('f.lli_rossi@gmail.com', 1, 104, '2026-01-15', 2500.00, 'Revisione totale testata mietitrebbia');

-- 9. APPEZZAMENTO
INSERT INTO APPEZZAMENTO VALUES 
(1, 'Medio impasto, ricco scheletro', 2.50, 'Rete', 1, 0, 'Polizza Grandine Unipol', 'info@verdemurlo.it', 11.260000, 43.770000, 'Chianti', 'Vite'),
(2, 'Argilloso-limoso', 4.10, NULL, 0, 0, NULL, 'contatti@terradisiena.com', 11.340000, 43.320000, 'Frantoio', 'Olivo'),
(3, 'Vulcanico, ricco di potassio', 1.80, 'Serra', 1, 1, 'Generali Agri', 'amministrazione@bioroma.it', 12.500000, 41.900000, 'San Marzano', 'Pomodoro'),
(4, 'Profondo, fertile', 15.00, NULL, 0, 0, NULL, 'f.lli_rossi@gmail.com', 11.350000, 44.500000, 'Senatore Cappelli', 'Grano');

-- 10. ASSEGNAZIONE
INSERT INTO ASSEGNAZIONE VALUES 
(1, '2026-06-17 07:00:00', 'info@verdemurlo.it', 1),
(2, '2026-06-17 08:00:00', 'contatti@terradisiena.com', 2),
(3, '2026-06-17 09:30:00', 'amministrazione@bioroma.it', 3),
(4, '2026-06-17 06:00:00', 'f.lli_rossi@gmail.com', 4);

-- 11. INTERVENTO OPERATIVO
INSERT INTO INTERVENTO_OPERATIVO VALUES 
('2026-06-17 07:00:00', '2026-06-17 11:00:00', 'Potatura verde e legatura viti', 1),
('2026-06-17 08:00:00', '2026-06-17 13:00:00', 'Trattamento preventivo mosca dell\'olivo', 2),
('2026-06-17 09:30:00', NULL, 'Diserbo manuale tra le file in serra', 3),
('2026-06-17 06:00:00', '2026-06-17 14:00:00', 'Mietitura del grano duro', 4);

-- 12. UTILIZZO
INSERT INTO UTILIZZO VALUES 
('info@verdemurlo.it', 1, 1, '2026-06-17 07:00:00'),
('contatti@terradisiena.com', 1, 2, '2026-06-17 08:00:00'),
('amministrazione@bioroma.it', 1, 3, '2026-06-17 09:30:00'),
('f.lli_rossi@gmail.com', 1, 4, '2026-06-17 06:00:00');

-- 13. IRRIGAZIONE
INSERT INTO IRRIGAZIONE VALUES 
('2026-06-10', '21:00:00', NULL, NULL, 1),
('2026-06-11', '22:00:00', NULL, NULL, 2),
('2026-06-12', '05:00:00', 'Fertirrigante NPK', 15.50, 3),
('2026-06-13', '20:30:00', NULL, NULL, 4);

-- 14. TRATTAMENTO
INSERT INTO TRATTAMENTO VALUES 
('2026-05-14', 500.00, 'Rame Zolfo Polvere', 12.00, 1),
('2026-05-20', 1000.00, 'Bio-Insect Stop', 5.00, 2),
('2026-06-01', 200.00, 'Estratto d\'Ortica Bio', 20.00, 3),
('2026-04-18', 3000.00, 'Fungicida Cereali Ok', 45.00, 4);

-- 15. SCORTA
INSERT INTO SCORTA VALUES 
('info@verdemurlo.it', 2025, 'Chianti', 'Vite', 5000.00, 1.20),
('contatti@terradisiena.com', 2025, 'Frantoio', 'Olivo', 1200.00, 8.50),
('amministrazione@bioroma.it', 2026, 'San Marzano', 'Pomodoro', 800.00, 0.65),
('f.lli_rossi@gmail.com', 2025, 'Senatore Cappelli', 'Grano', 45000.00, 0.45);

-- 16. RACCOLTA
INSERT INTO RACCOLTA VALUES 
('2025-09-20', 1, 5200.00, 2025, 'info@verdemurlo.it', 'Chianti', 'Vite'),
('2025-11-05', 2, 1300.00, 2025, 'contatti@terradisiena.com', 'Frantoio', 'Olivo'),
('2026-06-15', 3, 850.00, 2026, 'amministrazione@bioroma.it', 'San Marzano', 'Pomodoro'),
('2025-07-10', 4, 46000.00, 2025, 'f.lli_rossi@gmail.com', 'Senatore Cappelli', 'Grano');

-- 17. PUNTO VENDITA
INSERT INTO PUNTO_VENDITA VALUES 
('info@verdemurlo.it', '01111111111', 'Bottega della Vite', 'Via del Campo 12, Firenze', '09:00-19:00', 1, 0),
('contatti@terradisiena.com', '02222222222', 'Frantoio Shop', 'Strada in Chianti 5, Siena', '08:30-18:00', 1, 1),
('amministrazione@bioroma.it', '03333333333', 'BioRoma Online Store', 'Via Tiburtina 40, Roma', '24/7 online', 0, 1),
('f.lli_rossi@gmail.com', '04444444444', 'Spaccio Agricolo Rossi', 'Via Emilia 100, Bologna', '08:00-12:30', 1, 0);

-- 18. PRELIEVO
INSERT INTO PRELIEVO VALUES 
('Chianti', 'Vite', 2025, 'info@verdemurlo.it', 1, 120.00),
('Frantoio', 'Olivo', 2025, 'contatti@terradisiena.com', 2, 10.00),
('San Marzano', 'Pomodoro', 2026, 'amministrazione@bioroma.it', 3, 50.00),
('Senatore Cappelli', 'Grano', 2025, 'f.lli_rossi@gmail.com', 4, 1000.00);

-- 19. CLIENTE
INSERT INTO CLIENTE VALUES 
(1, 'Giovanni', 'Pascoli', 'Via delle Ruote 5, Firenze', 'giovanni@gmail.com', NULL, 'Contanti'),
(2, 'Elena', 'Russo', 'Viale Europa 88, Siena', 'elena.russo@outlook.it', NULL, 'Carta di Credito'),
(3, 'Ristorante Da Mimmo', 'Esposito', 'Piazza Navona 3, Roma', 'info@damimmo.it', '09876543210', 'Bonifico'),
(4, 'Molino Padano', 'Galli', 'Via Ferrara 1, Ferrara', 'acquisti@molinopadano.it', '01239874561', 'Ri.Ba.');

-- 20. ORDINE
INSERT INTO ORDINE VALUES 
(1, '2026-06-17', 144.00, 1, '01111111111', 'info@verdemurlo.it'),
(2, '2026-06-17', 85.00, 2, '02222222222', 'contatti@terradisiena.com'),
(3, '2026-06-17', 32.50, 3, '03333333333', 'amministrazione@bioroma.it'),
(4, '2026-06-17', 450.00, 4, '04444444444', 'f.lli_rossi@gmail.com');
