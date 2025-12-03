#!/usr/bin/python3

# --------------------------------------------------
# Importations
# --------------------------------------------------

# remplacer VehicleMock et CustomerMock une fois faite 

from classes import Rental, VehicleMock, CustomerMock

# --------------------------------------------------
# Main file
# --------------------------------------------------

def main():
    try:
        print("\n----- 🏁 Démarrage du système -----")
        
        # Création des objets
        client = CustomerMock("Alpha")
        voiture = VehicleMock("Tesla", "Model S", 100)

        # Utilisation de ta classe Rental
        location = Rental(client, voiture, "2024-05-01", "2024-05-05")
        location.confirm_rental()

        # Retour
        location.return_vehicle("2024-05-06") # Un jour de retard
        
        # Facture
        print(location.generate_invoice())

    except Exception as e:
        print(f"\n----- ❌ Erreur : {e} -----")

# Point d'entrée du script
if __name__ == "__main__":
    main()
