# Mini Projet Python : Système de Location de Voitures

## Objectif Général 

Développer une application de gestion de location de voitures basée sur les principes de la programmation orientée objet.

Cette application doit permettre à une agence de location de : 
* gérer son parc automobile,
* gérer ses clients
* effectuer et suivre les locations
* calculer le coût d'une location
* générer des rapports

## Fonctionnalités attendues

### 1. Gestion de la flotte automobile

- Hiérarchie de classes : Vehicle, Car, Truck, Motorcycle
- Attributs : id, marque, modèle, catégorie, tarif, état
- Option avancée : entretien

### 2. Gestion des clients

- Classe Customer : id, nom, prénom, âge, permis, historique
- Règles : âge minimum selon véhicule

### 3. Système de réservation (Rental)

- Données : client, véhicule, dates, coût total
- Règles : disponibilité, dates valides, pénalités

### 4. Classe centrale CarRentalSystem

- Gestion : véhicules, clients, locations, recherche, rapports

## Rapport

- Véhicules disponibles
- Locations en cours
- Chiffre d’affaires
- Statistiques

## Livrable

- Code en modules (repo GitHub)
- UML de calsses
- README
- Tests unitaires
