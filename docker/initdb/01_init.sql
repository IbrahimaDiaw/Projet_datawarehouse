-- Base applicative interne de Metabase (separee de l'entrepot)
CREATE DATABASE metabase;

-- Schemas de l'architecture en couches
\connect olist_dw
CREATE SCHEMA IF NOT EXISTS raw;         -- donnees brutes, aucune transformation
CREATE SCHEMA IF NOT EXISTS staging;     -- typage / nettoyage
CREATE SCHEMA IF NOT EXISTS intermediate;-- logique metier intermediaire
CREATE SCHEMA IF NOT EXISTS marts;       -- modele en etoile (dim_* / fct_*)
