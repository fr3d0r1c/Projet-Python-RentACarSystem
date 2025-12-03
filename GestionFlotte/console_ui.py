from datetime import date
from vehicles import Car, Truck, Motorcycle, Hearse, GoKart, Carriage
from animals import Horse, Donkey, Camel

def ask_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("❌ Entier requis.")

def ask_float(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("❌ Décimal requis.")

def ask_bool(message):
    val = input(f"{message} (o/n) : ").lower()
    return val in ['o', 'oui', 'y', 'yes']

def show_main_menu():
    print("\n" + "="*30)
    print("   GESTION DE FLOTTE v2.0")
    print("="*30)
    print("1. 📋 Voir la flotte")
    print("2. ➕ Ajouter un véhicule")
    print("3. 🗑️ Supprimer un véhicule")
    print("4. 💾 Sauvegarder et Quitter")

def list_fleet(fleet):
    if not fleet:
        print("\n🚫 La flotte est vide.")
    else:
        print(f"\n--- ÉTAT DE LA FLOTTE ({len(fleet)} véhicules) ---")
        for v in fleet:
            print(f"[{v.id}] {v.show_details()} | Statut: {v.status.value}")

def add_vehicle_menu(fleet):
    print("\n--- AJOUT ---")
    print("1. Voiture | 2. Poney | 3. Camion | 4. Moto")
    print("0. Annuler")
    choice = input("Choix : ")
    
    if choice == '0': return

    new_id = 1
    if fleet: new_id = max(v.id for v in fleet) + 1
    rate = ask_float("Tarif (€) : ")

    if choice == '1':
        fleet.append(Car(new_id, rate, input("Marque: "), input("Modèle: "), input("Plaque: "), ask_int("Portes: "), ask_bool("Clim?")))
        print("✅ Voiture ajoutée !")
    elif choice == '2':
        fleet.append(Horse(new_id, rate, input("Nom: "), input("Race: "), date(2020,1,1), ask_int("Taille cm: "), ask_int("Fer: ")))
        print("✅ Poney ajouté !")
    elif choice == '3':
        fleet.append(Truck(new_id, rate, input("Marque: "), input("Modèle: "), input("Plaque: "), ask_float("Vol m3: "), ask_float("Poids T: ")))
        print("✅ Camion ajouté !")
    elif choice == '4':
        fleet.append(Motorcycle(new_id, rate, input("Marque: "), input("Modèle: "), input("Plaque: "), ask_int("CC: "), ask_bool("TopCase?")))
        print("✅ Moto ajoutée !")
    else:
        print("❌ Non implémenté ou invalide.")

def delete_vehicle_menu(fleet):
    tid = ask_int("ID à supprimer : ")
    found = next((v for v in fleet if v.id == tid), None)
    if found and ask_bool(f"Supprimer {found.show_details()} ?"):
        fleet.remove(found)
        print("🗑️ Supprimé.")
    else:
        print("Annulé ou introuvable.")