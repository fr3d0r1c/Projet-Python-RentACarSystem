from datetime import date
from vehicles import *
from animals import *
from maintenance import Maintenance
from enums import MaintenanceType, VehicleStatus
from transport_base import MotorizedVehicle, TransportAnimal, TowedVehicle

# --- PRIX PAR DÉFAUT ---
DEFAULT_RENTAL_PRICES = {
    '1': 50.0, '2': 250.0, '3': 90.0, '4': 300.0, '5': 60.0, # Moteurs Terre
    '6': 35.0, '7': 25.0, '8': 80.0,                         # Animaux Terre
    '9': 120.0, '10': 40.0,                                  # Attelages
    '11': 400.0, '12': 2000.0, '13': 200.0, '14': 100.0,     # Mer
    '15': 1500.0, '16': 800.0, '17': 150.0, '18': 5000.0     # Air
}

DEFAULT_MAINT_COSTS = {
    MaintenanceType.MECHANICAL_CHECK: 50.0, MaintenanceType.CLEANING: 20.0,
    MaintenanceType.HOOF_CARE: 40.0, MaintenanceType.SADDLE_MAINTENANCE: 15.0,
    MaintenanceType.TIRE_CHANGE: 120.0, MaintenanceType.OIL_CHANGE: 89.0,
    MaintenanceType.AXLE_GREASING: 30.0
}

DEFAULT_DURATIONS = {
    MaintenanceType.MECHANICAL_CHECK: 1.0, MaintenanceType.CLEANING: 0.5,
    MaintenanceType.HOOF_CARE: 0.5, MaintenanceType.SADDLE_MAINTENANCE: 2.0,
    MaintenanceType.TIRE_CHANGE: 0.5, MaintenanceType.OIL_CHANGE: 0.5,
    MaintenanceType.AXLE_GREASING: 1.0
}

# --- HELPERS ---
def ask_int(m):
    while True: 
        try: return int(input(m))
        except: print("❌ Entier svp")
def ask_float(m): 
    while True: 
        try: return float(input(m))
        except: print("❌ Float svp")
def ask_float_def(m,d):
    v=input(f"{m} (Entrée={d}): "); return float(v) if v.strip() else d
def ask_bool(m): return input(f"{m} (o/n): ").lower().startswith('o')

# --- MENU PRINCIPAL ---
def show_main_menu():
    print("\n" + "="*40)
    print("   GESTION FLOTTE (TERRE/AIR/MER)")
    print("="*40)
    print("1. 📋 Voir la flotte")
    print("2. ➕ Ajouter un élément (Par Environnement)")
    print("3. 🔧 Maintenance / Soins")
    print("4. 🐴 Atteler (Charrette/Calèche)")
    print("5. 🗑️ Supprimer")
    print("6. 💾 Sauvegarder et Quitter")

def list_fleet(fleet):
    if not fleet: print("Vide.")
    else:
        print(f"--- FLOTTE ({len(fleet)}) ---")
        for v in fleet: print(f"[{v.id}] {v.show_details()} | {v.status.value}")

# --- 🌍 MENU AJOUT PAR ENVIRONNEMENT ---
def add_menu_by_environment(fleet):
    print("\n--- CHOIX DE L'ENVIRONNEMENT ---")
    print("1. ⛰️ TERRE (Route, Écurie, Piste)")
    print("2. 🌊 MER   (Port, Bassin)")
    print("3. ☁️ AIR   (Héliport, Nid)")
    print("0. Retour")
    
    env = input("Votre choix : ")
    if env == '0': return

    new_id = 1 if not fleet else max(v.id for v in fleet) + 1

    # ================= TERRE =================
    if env == '1':
        print("\n--- ⛰️ TERRE ---")
        print("--- Moteurs ---")
        print("1.Voiture | 2.Camion | 3.Moto | 4.Corbillard | 5.Kart")
        print("--- Animaux ---")
        print("6.Cheval  | 7.Âne    | 8.Chameau")
        print("--- Attelages ---")
        print("9.Calèche | 10.Charrette")
        
        c = input("Type : ")
        
        # Récupération prix par défaut
        rate = ask_float_def("Tarif", DEFAULT_RENTAL_PRICES.get(c, 50.0))

        if c=='1': fleet.append(Car(new_id,rate,input("Marque: "),input("Modèle: "),input("Plaque: "),ask_int("Année: "),5,True))
        elif c=='2': fleet.append(Truck(new_id,rate,input("Marque: "),input("Modèle: "),input("Plaque: "),ask_int("Année: "),ask_float("Vol: "),ask_float("Poids: ")))
        elif c=='3': fleet.append(Motorcycle(new_id,rate,input("Marque: "),input("Modèle: "),input("Plaque: "),ask_int("Année: "),ask_int("CC: "),ask_bool("TopCase?")))
        elif c=='4': fleet.append(Hearse(new_id,rate,input("Marque: "),input("Modèle: "),input("Plaque: "),ask_int("Année: "),ask_float("Long: "),ask_bool("Frigo?")))
        elif c=='5': fleet.append(GoKart(new_id,rate,input("Marque: "),input("Modèle: "),input("Plaque: "),ask_int("Année: "),input("Moteur: "),True))
        
        elif c=='6': fleet.append(Horse(new_id,rate,input("Nom: "),"Std",5,ask_int("Taille cm: "),100,100))
        elif c=='7': fleet.append(Donkey(new_id,rate,input("Nom: "),"Gris",5,50,True))
        elif c=='8': fleet.append(Camel(new_id,rate,input("Nom: "),"Sable",5,2,100))
        
        elif c=='9': fleet.append(Carriage(new_id,rate,4,True))
        elif c=='10': fleet.append(Cart(new_id,rate,1,200))
        else: print("❌ Choix invalide."); return

    # ================= MER =================
    elif env == '2':
        print("\n--- 🌊 MER ---")
        print("1.Bateau  | 2.Sous-Marin")
        print("3.Baleine | 4.Dauphin")
        c = input("Type : ")

        # Mapping prix : 1->11(Bateau), 2->12(Sub), 3->13(Whale), 4->14(Dolphin)
        key_map = {'1':'11', '2':'12', '3':'13', '4':'14'}
        rate = ask_float_def("Tarif", DEFAULT_RENTAL_PRICES.get(key_map.get(c), 200.0))

        if c=='1': fleet.append(Boat(new_id,rate,input("Marque: "),"Mod","BAT",2020,10,200))
        elif c=='2': fleet.append(Submarine(new_id,rate,"Nautilus","Nuc","SUB",2020,500,True))
        elif c=='3': fleet.append(Whale(new_id,rate,input("Nom: "),"Bleue",10,100,True))
        elif c=='4': fleet.append(Dolphin(new_id,rate,input("Nom: "),"Flipper",5,40,True))
        else: print("❌ Choix invalide."); return

    # ================= AIR =================
    elif env == '3':
        print("\n--- ☁️ AIR ---")
        print("1.Avion | 2.Hélico")
        print("3.Aigle | 4.Dragon")
        c = input("Type : ")

        # Mapping prix : 1->15, 2->16, 3->17, 4->18
        key_map = {'1':'15', '2':'16', '3':'17', '4':'18'}
        rate = ask_float_def("Tarif", DEFAULT_RENTAL_PRICES.get(key_map.get(c), 500.0))

        if c=='1': fleet.append(Plane(new_id,rate,"Boeing","747","AIR",2010,60,4))
        elif c=='2': fleet.append(Helicopter(new_id,rate,"Airbus","H160","HEL",2022,5,3000))
        elif c=='3': fleet.append(Eagle(new_id,rate,input("Nom: "),"Royal",5,200,2000))
        elif c=='4': fleet.append(Dragon(new_id,rate,input("Nom: "),"Rouge",200,50,"Rouge"))
        else: print("❌ Choix invalide."); return

    print(f"✅ Élément ajouté avec succès (ID: {new_id}) !")

# --- MAINTENANCE ---
def maintenance_menu(fleet):
    tid=ask_int("ID: "); obj=next((v for v in fleet if v.id==tid),None)
    if not obj: return print("❌ Introuvable.")
    print(f"Sélection : {obj.show_details()}")
    
    if isinstance(obj, TransportAnimal):
        print("1.Sabots 2.Nettoyage")
        t = MaintenanceType.HOOF_CARE if input("Choix: ")=='1' else MaintenanceType.CLEANING
    else:
        print("1.Vidange 2.Méca 3.Nettoyage")
        c = input("Choix: ")
        t = MaintenanceType.OIL_CHANGE if c=='1' else MaintenanceType.MECHANICAL_CHECK if c=='2' else MaintenanceType.CLEANING
    
    cost = DEFAULT_MAINT_COSTS.get(t, 50.0)
    time = DEFAULT_DURATIONS.get(t, 1.0)
    obj.add_maintenance(Maintenance(len(obj.maintenance_log)+1,date.today(),t,cost,"Entretien",time))
    if ask_bool("Indispo?"): obj.status=VehicleStatus.UNDER_MAINTENANCE
    print("✅ Fait.")

# --- ATTELAGE ---
def harness_menu(fleet):
    vid=ask_int("ID Charrette/Calèche: "); v=next((x for x in fleet if x.id==vid),None)
    if not isinstance(v, TowedVehicle): return print("❌ Erreur Véhicule")
    aid=ask_int("ID Animal: "); a=next((x for x in fleet if x.id==aid),None)
    if not isinstance(a, TransportAnimal): return print("❌ Pas un animal")
    v.harness_animal(a)

# --- SUPPRESSION ---
def delete_menu(fleet):
    tid=ask_int("ID: "); f=next((v for v in fleet if v.id==tid),None)
    if f: fleet.remove(f); print("🗑️ Fait.")