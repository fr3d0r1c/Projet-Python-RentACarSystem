from datetime import date
from enums import MaintenanceType
from maintenance import Maintenance
from vehicles import Car, Carriage
from animals import Horse

def main():
    print("--- DÉMARRAGE SYSTÈME DE GESTION ---")

    voiture = Car(1, 100.0, "Toyota", "Yaris", "AA-123-BB", 5, True)
    print(voiture.show_details())

    poney = Horse(2, 40.0, "Eclair", "Shetland", date(2018, 5, 20), 100, 3)
    poney.check_hooves()

    caleche = Carriage(3, 120.0, 4, True)
    caleche.harness_animal(poney)
    print(caleche.show_details())

    maint = Maintenance(500, date.today(), MaintenanceType.OIL_CHANGE, 80.0, "Vidange annuelle")
    voiture.add_maintenance(maint)

if __name__ == "__main__":
    main()