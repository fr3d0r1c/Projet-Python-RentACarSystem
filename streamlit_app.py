import streamlit as st
import pandas as pd
import sys
import os
from datetime import date, timedelta

# --- 1. CONFIGURATION DU CHEMIN ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_dir, "CarRentalSystem")
if project_folder not in sys.path:
    sys.path.append(project_folder)

# --- 2. IMPORTS DU PROJET ---
from location.system import CarRentalSystem
from storage import StorageManager
from clients.customer import Customer
# Import de TOUTES les classes
from GestionFlotte.vehicles import *
from GestionFlotte.animals import *
from GestionFlotte.enums import VehicleStatus

# --- 3. CONFIGURATION DES PRIX PAR DÉFAUT (Pour l'interface Web) ---
# On mappe le Nom affiché -> Prix par défaut
PRICE_MAP = {
    "Voiture": 50.0, "Camion": 250.0, "Moto": 90.0, "Corbillard": 300.0, "Karting": 60.0,
    "Cheval": 35.0, "Âne": 25.0, "Chameau": 80.0,
    "Calèche": 120.0, "Charrette": 40.0,
    "Bateau": 400.0, "Sous-Marin": 2000.0, "Baleine": 200.0, "Dauphin": 100.0,
    "Avion": 1500.0, "Hélicoptère": 800.0, "Aigle": 150.0, "Dragon": 5000.0
}

# --- 4. SETUP STREAMLIT ---
st.set_page_config(page_title="CarRental Ultime", page_icon="🚗", layout="wide")

if 'system' not in st.session_state:
    st.session_state.system = CarRentalSystem()
    storage = StorageManager("ma_flotte.json")
    st.session_state.system.fleet = storage.load_fleet()
    st.session_state.storage = storage

system = st.session_state.system
storage = st.session_state.storage

def save_data():
    storage.save_fleet(system.fleet)
    st.toast("Sauvegarde effectuée !", icon="💾")

# --- 5. SIDEBAR ---
st.sidebar.header("🌍 Navigation")
menu = st.sidebar.radio("Menu", ["Tableau de Bord", "Ajouter Élément", "Clients", "Locations"])
st.sidebar.info(f"Flotte : {len(system.fleet)} véhicules")

# =========================================================
# PAGE 1 : TABLEAU DE BORD
# =========================================================
if menu == "Tableau de Bord":
    st.title("📊 État de la Flotte")
    
    if not system.fleet:
        st.warning("La flotte est vide.")
    else:
        # Transformation en données affichables
        data = []
        for v in system.fleet:
            # Icône Statut
            s_icon = "🟢"
            if v.status == VehicleStatus.RENTED: s_icon = "🟡"
            elif v.status == VehicleStatus.UNDER_MAINTENANCE: s_icon = "🔧"
            elif v.status == VehicleStatus.OUT_OF_SERVICE: s_icon = "💀"
            
            # Récupération infos génériques
            nom = getattr(v, 'brand', getattr(v, 'name', '?'))
            modele = getattr(v, 'model', getattr(v, 'breed', '-'))
            
            # Détails spécifiques pour le tableau
            details = "-"
            if isinstance(v, Car): details = f"{v.door_count}p {'❄️' if v.has_ac else ''}"
            elif isinstance(v, Dragon): details = f"Feu {v.fire_range}m"
            elif isinstance(v, Submarine): details = f"-{v.max_depth}m {'☢️' if v.is_nuclear else ''}"
            elif isinstance(v, Horse): details = f"{v.wither_height}cm"
            elif isinstance(v, Carriage): details = f"{v.seat_count}pl (Attelage)"

            data.append({
                "ID": v.id,
                "Type": v.__class__.__name__,
                "Identifiant": nom,
                "Description": modele,
                "Année/Âge": getattr(v, 'year', getattr(v, 'age', '-')),
                "Détails": details,
                "Prix/j": f"{v.daily_rate}€",
                "Statut": f"{s_icon} {v.status.value}"
            })
        
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# =========================================================
# PAGE 2 : AJOUTER UN VÉHICULE (AMÉLIORÉ)
# =========================================================
elif menu == "Ajouter Élément":
    st.title("➕ Ajouter à la Flotte")

    # 1. Choix de l'environnement
    env = st.selectbox("Environnement", ["Terre", "Mer", "Air"], index=0)
    
    # 2. Liste dynamique selon l'environnement
    if env == "Terre":
        type_options = ["Voiture", "Camion", "Moto", "Corbillard", "Karting", "Cheval", "Âne", "Chameau", "Calèche", "Charrette"]
    elif env == "Mer":
        type_options = ["Bateau", "Sous-Marin", "Baleine", "Dauphin"]
    else:
        type_options = ["Avion", "Hélicoptère", "Aigle", "Dragon"]

    v_type = st.selectbox("Type de véhicule/animal", type_options)

    # 3. Récupération du prix par défaut
    default_price = PRICE_MAP.get(v_type, 50.0)

    st.markdown("---")
    
    # 4. Formulaire dynamique
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        
        # Champs communs
        rate = col1.number_input("Tarif Journalier (€)", value=default_price)
        new_id = 1 if not system.fleet else max(v.id for v in system.fleet) + 1
        
        # --- LOGIQUE D'AFFICHAGE DES CHAMPS ---
        
        # A. VÉHICULES MOTEUR (Terre/Mer/Air)
        if v_type in ["Voiture", "Camion", "Moto", "Corbillard", "Karting", "Bateau", "Sous-Marin", "Avion", "Hélicoptère"]:
            # Labels intelligents
            lbl_brand = "Marque / Constructeur"
            lbl_model = "Modèle"
            lbl_id = "Plaque d'immatriculation"
            
            if v_type in ["Bateau", "Sous-Marin"]: lbl_id = "Nom du Vaisseau / Coque"
            if v_type == "Avion": lbl_id = "Immatriculation (F-XXXX)"
            
            brand = col1.text_input(lbl_brand)
            model = col2.text_input(lbl_model)
            plate = col1.text_input(lbl_id)
            year = col2.number_input("Année", value=2023, step=1)

            # Spécifiques Moteurs
            spec_col1, spec_col2 = st.columns(2)
            if v_type == "Voiture":
                arg1 = spec_col1.number_input("Nb Portes", 3, 5, 5)
                arg2 = spec_col2.checkbox("Climatisation ?", True)
            elif v_type == "Camion":
                arg1 = spec_col1.number_input("Volume (m3)", value=20.0)
                arg2 = spec_col2.number_input("Poids Max (T)", value=10.0)
            elif v_type == "Moto":
                arg1 = spec_col1.number_input("Cylindrée (cc)", value=500)
                arg2 = spec_col2.checkbox("TopCase ?", False)
            elif v_type == "Sous-Marin":
                arg1 = spec_col1.number_input("Profondeur Max (m)", value=500.0)
                arg2 = spec_col2.checkbox("Nucléaire ?", True)
            elif v_type == "Dragon": # Juste au cas où il passerait ici par erreur de logique
                pass 
            # (Vous pouvez compléter les autres ici : Avion, Hélico...)
            else:
                # Valeurs par défaut pour les types non détaillés ci-dessus dans l'exemple
                arg1 = 0; arg2 = False 

        # B. ANIMAUX
        elif v_type in ["Cheval", "Âne", "Chameau", "Baleine", "Dauphin", "Aigle", "Dragon"]:
            name = col1.text_input("Nom")
            breed = col2.text_input("Race / Espèce")
            age = col1.number_input("Âge", 1, 500, 5)
            
            # Spécifiques Animaux
            spec_col1, spec_col2 = st.columns(2)
            if v_type == "Dragon":
                arg1 = spec_col1.number_input("Portée du feu (m)", value=100.0)
                arg2 = spec_col2.text_input("Couleur écailles", "Rouge")
            elif v_type == "Cheval":
                arg1 = spec_col1.number_input("Taille (cm)", value=160)
                # Simplification pour l'interface : fers identiques av/arr
                arg2 = spec_col2.number_input("Taille Fers (mm)", value=100) 
            elif v_type == "Âne":
                arg1 = spec_col1.number_input("Capacité (kg)", value=50.0)
                arg2 = spec_col2.checkbox("Têtu ?", True)
            else:
                arg1 = 0; arg2 = 0

        # C. ATTELAGES
        elif v_type in ["Calèche", "Charrette"]:
            seats = col1.number_input("Nombre de places", 1, 10, 2)
            if v_type == "Calèche":
                arg1 = col2.checkbox("Avec Toit ?", True)
            else:
                arg1 = col2.number_input("Charge Max (kg)", value=200.0)

        # --- BOUTON DE VALIDATION ---
        if st.form_submit_button("Créer et Sauvegarder"):
            obj = None
            # Construction de l'objet
            if v_type == "Voiture": obj = Car(new_id, rate, brand, model, plate, year, arg1, arg2)
            elif v_type == "Camion": obj = Truck(new_id, rate, brand, model, plate, year, arg1, arg2)
            elif v_type == "Moto": obj = Motorcycle(new_id, rate, brand, model, plate, year, arg1, arg2)
            elif v_type == "Sous-Marin": obj = Submarine(new_id, rate, brand, model, plate, year, arg1, arg2)
            
            elif v_type == "Dragon": obj = Dragon(new_id, rate, name, breed, age, arg1, arg2)
            elif v_type == "Cheval": obj = Horse(new_id, rate, name, breed, age, arg1, arg2, arg2)
            elif v_type == "Âne": obj = Donkey(new_id, rate, name, breed, age, arg1, arg2)
            
            elif v_type == "Calèche": obj = Carriage(new_id, rate, seats, arg1)
            elif v_type == "Charrette": obj = Cart(new_id, rate, seats, arg1)
            
            # Fallback pour les types non implémentés complètement dans cet exemple (Avion, Bateau...)
            # Dans votre vrai code, ajoutez les elif manquants sur le modèle ci-dessus
            
            if obj:
                system.add_vehicle(obj)
                save_data()
                st.success(f"{v_type} ajouté avec succès ! (ID: {new_id})")
            else:
                st.error("Type de véhicule non encore implémenté dans le constructeur Web.")

# =========================================================
# PAGE 3 : CLIENTS (Simple)
# =========================================================
elif menu == "Clients":
    st.title("Gestion Clients")
    with st.form("client_form"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Nom Complet")
        permis = c2.text_input("Permis")
        if st.form_submit_button("Ajouter"):
            system.add_customer(Customer(len(system.customers)+1, nom, permis, "mail", "tel"))
            st.success("Client ajouté !")
    
    if system.customers:
        st.dataframe(pd.DataFrame([c.__dict__ for c in system.customers]))

# =========================================================
# PAGE 4 : LOCATIONS
# =========================================================
elif menu == "Locations":
    st.title("Comptoir Locations")
    
    # On filtre pour ne montrer que les dispos
    dispos = [v for v in system.fleet if v.status == VehicleStatus.AVAILABLE]
    
    if not dispos or not system.customers:
        st.warning("Il faut des véhicules disponibles et des clients.")
    else:
        c1, c2 = st.columns(2)
        cli_name = c1.selectbox("Client", [c.name for c in system.customers])
        # Affiche le nom ET le prix dans la liste
        veh_label = c2.selectbox("Véhicule", [f"{v.id}: {getattr(v,'brand', getattr(v,'name',''))} - {v.daily_rate}€" for v in dispos])
        
        days = st.slider("Durée (jours)", 1, 30, 1)
        
        if st.button("Valider la location"):
            # Retrouver les IDs (Logique simplifiée pour l'exemple)
            cid = next(c.id for c in system.customers if c.name == cli_name)
            vid = int(veh_label.split(":")[0])
            
            rental = system.create_rental(cid, vid, date.today(), date.today()+timedelta(days=days))
            if rental:
                save_data()
                st.balloons()
                st.success(f"Location validée ! Montant: {rental.total_price}€")