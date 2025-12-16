from datetime import date, timedelta, datetime
from fleet.transport_base import TransportMode, MotorizedVehicle, TransportAnimal
from clients.customer import Customer
from fleet.enums import VehicleStatus

from datetime import datetime

class Rental:
    def __init__(self, customer, vehicle, start_date_str, end_date_str, from_history=False):
        self.id = 0
        self.customer = customer
        self.vehicle = vehicle
        self.from_history = from_history

        try:
            self.start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            self.end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Format de date invalide. Utilisez AAAA-MM-JJ")
        
        self.actual_return_date = None
        self.total_cost = 0.0
        self.penalty = 0.0
        self.is_active = False

        self._validate_rental()
        
        self.is_active = True
        self.vehicle.status = VehicleStatus.RENTED

    def _validate_rental(self):

        if self.start_date > self.end_date:
            raise ValueError(f"Erreur: La date de fin ({self.end_date.date()}) est avant le début.")
        
        if not self.from_history and not self.vehicle.is_available:
            nom = getattr(self.vehicle, 'brand', getattr(self.vehicle, 'name', 'Véhicule'))
            modele = getattr(self.vehicle, 'model', getattr(self.vehicle, 'breed', ''))
            raise ValueError(f"Le véhicule {nom} {modele} est déjà loué !")
        
    def calculate_cost(self):
        """Calcule le coût théorique (avant retour réel)."""
        duration = (self.end_date - self.start_date).days
        days = max(1, duration)
        
        return days * self.vehicle.daily_rate
    
    def close_rental(self, return_date_str):
        """Clôture la location et calcule le prix final."""
        try:
            self.actual_return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date retour invalide.")
        
        delta_reel = (self.actual_return_date - self.start_date).days
        cout_base = max(1, delta_reel) * self.vehicle.daily_rate
        self.penalty = 0.0

        cout_base = max(1, delta_reel) * self.vehicle.daily_rate

        if self.actual_return_date > self.end_date:
            jours_retard = (self.actual_return_date - self.end_date).days
            self.penalty = (jours_retard * self.vehicle.daily_rate) * 0.10
            print(f"⚠️ Retard de {jours_retard} jours. Pénalité: {self.penalty}€")
        
        self.total_cost = cout_base + self.penalty

        self.is_active = False

        self.vehicle.status = VehicleStatus.AVAILABLE
        
        return self.total_cost
    
    def to_dict(self):
        return {
            "id": getattr(self, 'id', 0),
            "customer_id": self.customer.id, 
            "vehicle_id": self.vehicle.id,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "is_active": self.is_active, 
            "total_cost": self.total_cost
        }

    def generate_invoice(self):
        """Génère une facture détaillée sous forme de texte."""
        if self.is_active:
            return "❌ La location est encore en cours. Impossible de générer la facture finale."

        days_base = max(1, (self.actual_return_date - self.start_date).days)
        base_cost = days_base * self.vehicle.daily_rate

        invoice =  "========================================\n"
        invoice += f"       FACTURE FINALE #{self.id:04d}\n"
        invoice += "========================================\n"
        invoice += f"CLIENT   : {self.customer.last_name} {self.customer.first_name}\n"
        invoice += f"VÉHICULE : {getattr(self.vehicle, 'brand', getattr(self.vehicle, 'name', 'Véhicule'))} {getattr(self.vehicle, 'model', getattr(self.vehicle, 'breed', ''))}\n"
        invoice += "----------------------------------------\n"
        invoice += f"Début    : {self.start_date.date()}\n"
        invoice += f"Fin      : {self.actual_return_date.date()}\n"
        invoice += f"Durée    : {days_base} jours\n"
        invoice += "----------------------------------------\n"
        invoice += f"Tarif journalier : {self.vehicle.daily_rate} €\n"
        invoice += f"Sous-total       : {base_cost:.2f} €\n"

        if self.penalty > 0:
            invoice += f"PÉNALITÉ RETARD  : +{self.penalty:.2f} €\n"
        
        invoice += "========================================\n"
        invoice += f"TOTAL À PAYER    : {self.total_cost:.2f} €\n"
        invoice += "========================================\n"
        
        return invoice