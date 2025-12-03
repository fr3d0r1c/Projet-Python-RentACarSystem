from enum import Enum

class VehicleStatus(Enum):
    AVAILABLE = "Disponible"
    RENTED = "Loué"
    UNDER_MAINTENANCE = "En Maintenance"
    OUT_OF_SERVICE = "Hors Services"

class MaintenanceType(Enum):
    MECHANICAL_CHECK = "Contrôle Mécanique"
    CLEANING = "Nettoyage"
    HOOF_CARE = "Soin des sabots"
    SADDLE_MAINTENANCE = "Entretien Sellerie"
    TIRE_CHANGE = "Changement Pneus"
    OIL_CHANGE = "Vidange"
    AXLE_GREASING = "Graissage Essieux"