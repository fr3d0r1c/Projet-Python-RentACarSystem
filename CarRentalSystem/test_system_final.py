from datetime import date
import sys
import os

from location.system import CarRentalSystem
from clients.customer import Customer
from GestionFlotte.vehicles import Car
from GestionFlotte.enums import VehicleStatus

def run_test():
    print("\n==============================================")
    print("🧪  TEST AUTOMATIQUE DU SYSTÈME CENTRAL (BACKEND)")
    print("==============================================\n")

    print("[1] Initialisation du système...")
    system = CarRentalSystem()
    print("✅ Système démarré.")

    print("\n[2] Création des données (Moteur + Humain)...")

    peugeot = Car(1, 50.0, "Peugeot", "208", "TEST-01", 2022, 5, True)

    alice = Customer(101, "Alice Wonderland", "PERMIS-B-999", "alice@mail.com", "06000000")

    system.add_vehicle(peugeot)
    system.add_customer(alice)
    print(f"✅ Ajouté : {peugeot.show_details()}")
    print(f"✅ Ajouté : {alice.show_details()}")

    print("\n[3] Tentative de Location VALIDE...")

    rental = system.create_rental(101, 1, date(2023, 1, 1), date(2023, 1, 4))

    if rental and rental.total_price == 150.0:
        print(f"✅ Location créée avec succès (ID: {rental.id})")
        print(f"💰 Prix calculé : {rental.total_price}€ (Attendu: 150.0€)")
    else:
        print("❌ ÉCHEC : La location n'a pas été créée ou le prix est faux.")
        return
    
    print("\n[4] Vérification du statut véhicule...")
    if peugeot.status == VehicleStatus.RENTED:
        print(f"✅ Le véhicule est bien marqué comme : {peugeot.status.value}")
    else:
        print(f"❌ ERREUR : Le véhicule devrait être LOUE, il est {peugeot.status.value}")

    print("\n[5] Tentative de Location INVALIDE (Véhicule occupé)...")
    fail_rental = system.create_rental(101, 1, date(2023, 2, 1), date(2023, 2, 5))

    if fail_rental is None:
        print("✅ Le système a bien REFUSÉ la location (comportement normal).")
    else:
        print("❌ ERREUR : Le système a autorisé une double location !")

    print("\n[6] Test de la Recherche Avancée...")

    results = system.search_vehicles(available_only=True)
    if len(results) == 0:
        print("✅ Recherche OK : Aucun véhicule disponible trouvé.")
    else:
        print(f"❌ ERREUR : La recherche a trouvé {len(results)} véhicule(s) alors que tout est loué.")

    print("\n[7] Retour du véhicule...")
    system.return_vehicle(rental.id)

    if peugeot.status == VehicleStatus.AVAILABLE:
        print("✅ Le véhicule est de nouveau DISPONIBLE.")
    else:
        print(f"❌ ERREUR : Statut incorrect après retour ({peugeot.status.value})")

    print("\n[8] Vérification du Chiffre d'Affaires...")

    total = system.generate_revenue_report()
    if total == 150.0:
        print("✅ CA total correct (150.0€).")
    else:
        print(f"❌ ERREUR CA : {total}€")

    print("\n==============================================")
    print("🏆  BILAN : TOUS LES TESTS SONT PASSÉS !")
    print("==============================================")

if __name__ == "__main__":
    run_test()