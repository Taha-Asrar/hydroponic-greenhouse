-- Schema SQL pour la Serre Hydroponique Urbaine
-- Version 1.0

-- 1. Utilisateur
CREATE TABLE utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operateur',
    actif BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Variété de Plante
CREATE TABLE variete_plante (
    id_variete SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    duree_croissance_jours INTEGER,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Recette de Culture
CREATE TABLE recette_culture (
    id_recette SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    id_variete INTEGER REFERENCES variete_plante(id_variete),
    temp_eau_min FLOAT,
    temp_eau_max FLOAT,
    ph_min FLOAT,
    ph_max FLOAT,
    ec_min FLOAT,
    ec_max FLOAT,
    luminosite_min FLOAT,
    cycle_eclairage_heures INTEGER,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Cycle de Culture
CREATE TABLE cycle_culture (
    id_cycle SERIAL PRIMARY KEY,
    id_recette INTEGER REFERENCES recette_culture(id_recette),
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur),
    date_debut TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_fin_prevue TIMESTAMP,
    statut VARCHAR(20) DEFAULT 'en_cours'
);

-- 5. Capteur
CREATE TABLE capteur (
    id_capteur SERIAL PRIMARY KEY,
    type_capteur VARCHAR(50) NOT NULL,
    nom VARCHAR(100),
    unite VARCHAR(20),
    actif BOOLEAN DEFAULT TRUE,
    dernier_releve FLOAT,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Lecture Capteur (Historique)
CREATE TABLE lecture_capteur (
    id_lecture SERIAL PRIMARY KEY,
    id_capteur INTEGER REFERENCES capteur(id_capteur),
    valeur FLOAT NOT NULL,
    date_lecture TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Actionneur
CREATE TABLE actionneur (
    id_actionneur SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    nom VARCHAR(100),
    actif BOOLEAN DEFAULT FALSE,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Commande Actionneur (Logs)
CREATE TABLE commande_actionneur (
    id_commande SERIAL PRIMARY KEY,
    id_actionneur INTEGER REFERENCES actionneur(id_actionneur),
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur),
    action VARCHAR(20) NOT NULL,
    date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) DEFAULT 'execute'
);

-- 9. Alerte
CREATE TABLE alerte (
    id_alerte SERIAL PRIMARY KEY,
    id_capteur INTEGER REFERENCES capteur(id_capteur),
    message TEXT NOT NULL,
    niveau VARCHAR(20) DEFAULT 'info',
    date_alerte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acquittee BOOLEAN DEFAULT FALSE
);

-- 10. Notification
CREATE TABLE notification (
    id_notification SERIAL PRIMARY KEY,
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur),
    id_alerte INTEGER REFERENCES alerte(id_alerte),
    message TEXT NOT NULL,
    envoye BOOLEAN DEFAULT FALSE,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Suivi Croissance
CREATE TABLE suivi_croissance (
    id_suivi SERIAL PRIMARY KEY,
    id_cycle INTEGER REFERENCES cycle_culture(id_cycle),
    id_utilisateur INTEGER REFERENCES utilisateur(id_utilisateur),
    taille_cm FLOAT,
    ph_mesure FLOAT,
    ec_mesure FLOAT,
    observations TEXT,
    photo_url VARCHAR(255),
    date_suivi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
