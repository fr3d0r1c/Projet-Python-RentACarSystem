import json
import sys
import os
import time
from datetime import date, timedelta, datetime
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional, Type

class VehicleStatus(Enum):
    AVAILABLE = "Disponible"
    RENTED = "Loué"
    UNDER_MAINTENANCE = "En Maintenance"
    OUT_OF_SERVICE = "Hors Service"

class MaintenanceType(Enum):
    MECHANICAL_CHECK = "Contrôle Mécanique"
    CLEANING = "Nettoyage"
    HOOF_CARE = "Soin Sabots/Griffes"
    SADDLE_MAINTENANCE = "Entretien Sellerie"
    TIRE_CHANGE = "Changement Pneus"
    OIL_CHANGE = "Vidange"
    AXLE_GREASING = "Graissage Essieux"
    
    # --- NOUVEAUX (MER/AIR/FANTASY) ---
    HULL_CLEANING = "Carénage (Coque)"       # Bateaux
    SONAR_CHECK = "Calibrage Sonar"          # Sous-marins/Bateaux
    NUCLEAR_SERVICE = "Révision Réacteur"    # Sous-marins
    AVIONICS_CHECK = "Systèmes Avioniques"   # Avions/Hélico
    ROTOR_INSPECTION = "Inspection Rotor"    # Hélico
    WING_CARE = "Soin des Ailes"             # Aigle/Dragon
    SCALE_POLISHING = "Lustrage Écailles"    # Dragon

class Maintenance:
    def __init__(self, m_id: int, date_m: date, m_type: MaintenanceType, cost: float, description: str, duration: float):
        self.id = m_id
        self.date = date_m
        self.type = m_type
        self.cost = cost
        self.description = description
        self.duration = duration # Durée en jours

    @property
    def end_date(self):
        days_int = int(self.duration) if self.duration >= 1 else 1
        return self.date + timedelta(days=days_int)

    def validate(self):
        print(f"✅ Maintenance #{self.id} ({self.type.value}) - Durée : {self.duration}j")

    def to_dict(self):
        return {
            "id": self.id,
            "date": str(self.date),
            "type": self.type.value,
            "cost": self.cost,
            "description": self.description,
            "duration": self.duration
        }
    
class TransportMode(ABC):
    def __init__(self, t_id: int, daily_rate: float):
        self.id = t_id
        self.daily_rate = daily_rate
        self.status = VehicleStatus.AVAILABLE
        self.maintenance_log: List[Maintenance] = []

    def add_maintenance(self, maintenance: Maintenance):
        self.maintenance_log.append(maintenance)

    def to_dict(self):
        m_logs = [m.to_dict() for m in self.maintenance_log]
        return {
            "type": self.__class__.__name__,
            "id": self.id,
            "daily_rate": self.daily_rate,
            "status": self.status.value,
            "maintenance_log": m_logs
        }

    @abstractmethod
    def show_details(self):
        pass

class MotorizedVehicle(TransportMode):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year):
        super().__init__(t_id, daily_rate)
        self.brand = brand
        self.model = model
        self.license_plate = license_plate
        self.year = year

    def to_dict(self):
        data = super().to_dict()
        data.update({"brand": self.brand, "model": self.model, "license_plate": self.license_plate, "year": self.year})
        return data

class TransportAnimal(TransportMode):
    def __init__(self, t_id, daily_rate, name, breed, birth_date):
        super().__init__(t_id, daily_rate)
        self.name = name
        self.breed = breed
        self.birth_date = birth_date # Gardé pour compatibilité, mais on utilise 'age' dans les enfants

    def to_dict(self):
        data = super().to_dict()
        data.update({"name": self.name, "breed": self.breed})
        return data

class TowedVehicle(TransportMode):
    def __init__(self, t_id, daily_rate, seat_count):
        super().__init__(t_id, daily_rate)
        self.seat_count = seat_count
        self.animals = [] 

    def harness_animal(self, animal):
        self.animals.append(animal)
        print(f"✅ {animal.name} a été attelé.")

    def to_dict(self):
        data = super().to_dict()
        # On sauvegarde les IDs pour reconstruire le lien plus tard
        data.update({
            "seat_count": self.seat_count,
            "animal_ids": [a.id for a in self.animals]
        })
        return data
    
class Horse(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, wither_height, shoe_size_front, shoe_size_rear):
        super().__init__(t_id, daily_rate, name, breed, None)
        self.age = age; self.wither_height = wither_height
        self.shoe_size_front = shoe_size_front; self.shoe_size_rear = shoe_size_rear
    @property
    def category(self): return "Poney" if self.wither_height < 140 else "Cheval"
    
    def show_details(self): 
        return f"[{self.category}] {self.name} ({self.age} ans) - {self.wither_height}cm, Fers: {self.shoe_size_front}/{self.shoe_size_rear}mm"
    
    def to_dict(self): d=super().to_dict(); d.update({"age": self.age, "wither_height": self.wither_height, "shoe_size_front": self.shoe_size_front, "shoe_size_rear": self.shoe_size_rear}); return d

class Donkey(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, pack_capacity_kg, is_stubborn):
        super().__init__(t_id, daily_rate, name, breed, None)
        self.age = age; self.pack_capacity_kg = pack_capacity_kg; self.is_stubborn = is_stubborn
    
    def show_details(self): 
        caractere = "Têtu" if self.is_stubborn else "Docile"
        return f"[Âne] {self.name} ({self.age} ans) - Charge {self.pack_capacity_kg}kg, {caractere}"
    
    def to_dict(self): d=super().to_dict(); d.update({"age": self.age, "pack_capacity_kg": self.pack_capacity_kg, "is_stubborn": self.is_stubborn}); return d

class Camel(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, hump_count, water_reserve):
        super().__init__(t_id, daily_rate, name, breed, None)
        self.age = age; self.hump_count = hump_count; self.water_reserve = water_reserve
    
    def show_details(self): 
        return f"[Chameau] {self.name} ({self.age} ans) - {self.hump_count} bosses, {self.water_reserve}L eau"
    
    def to_dict(self): d=super().to_dict(); d.update({"age": self.age, "hump_count": self.hump_count, "water_reserve": self.water_reserve}); return d

# --- MER ---
class Whale(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, weight_tonnes, can_sing):
        super().__init__(t_id, daily_rate, name, breed, None)
        self.age = age; self.weight_tonnes = weight_tonnes; self.can_sing = can_sing
    
    def show_details(self): 
        chant = "Chanteuse" if self.can_sing else "Silencieuse"
        return f"[Baleine] {self.name} ({self.age} ans) - {self.weight_tonnes}T, {chant}"
    
    def to_dict(self): d=super().to_dict(); d.update({"age": self.age, "weight_tonnes": self.weight_tonnes, "can_sing": self.can_sing}); return d

class Dolphin(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, swim_speed, knows_tricks):
        super().__init__(t_id, daily_rate, name, breed, None)
        self.age = age; self.swim_speed = swim_speed; self.knows_tricks = knows_tricks
    
    def show_details(self): 
        trick = "Savant" if self.knows_tricks else "Sauvage"
        return f"[Dauphin] {self.name} ({self.age} ans) - {self.swim_speed}km/h, {trick}"
    
    def to_dict(self): d=super().to_dict(); d.update({"age": self.age, "swim_speed": self.swim_speed, "knows_tricks": self.knows_tricks}); return d

# --- AIR ---
class Eagle(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, wingspan_cm, max_altitude):
        super().__init__(t_id, daily_rate, name, breed, None)
        self.age = age; self.wingspan_cm = wingspan_cm; self.max_altitude = max_altitude
    
    def show_details(self): 
        return f"[Aigle] {self.name} ({self.age} ans) - Env. {self.wingspan_cm}cm, Alt. {self.max_altitude}m"
    
    def to_dict(self): d=super().to_dict(); d.update({"age": self.age, "wingspan_cm": self.wingspan_cm, "max_altitude": self.max_altitude}); return d

class Dragon(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, fire_range, scale_color):
        super().__init__(t_id, daily_rate, name, breed, None)
        self.age = age; self.fire_range = fire_range; self.scale_color = scale_color
    
    def show_details(self): 
        return f"[Dragon] {self.name} ({self.age} ans) - {self.scale_color}, Feu {self.fire_range}m"
    
    def to_dict(self): d=super().to_dict(); d.update({"age": self.age, "fire_range": self.fire_range, "scale_color": self.scale_color}); return d

class Car(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, door_count, has_ac):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.door_count = door_count; self.has_ac = has_ac
    
    def show_details(self): 
        clim = "Clim" if self.has_ac else "Pas de clim"
        return f"[Voiture {self.year}] {self.brand} {self.model} - {self.door_count} portes, {clim}"
    
    def to_dict(self): d=super().to_dict(); d.update({"door_count": self.door_count, "has_ac": self.has_ac}); return d

class Truck(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, cargo_volume, max_weight):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.cargo_volume = cargo_volume; self.max_weight = max_weight
    
    def show_details(self): 
        return f"[Camion {self.year}] {self.brand} {self.model} - {self.cargo_volume}m³, {self.max_weight}T"
    
    def to_dict(self): d=super().to_dict(); d.update({"cargo_volume": self.cargo_volume, "max_weight": self.max_weight}); return d

class Motorcycle(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, engine_displacement, has_top_case):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.engine_displacement = engine_displacement; self.has_top_case = has_top_case
    
    def show_details(self): 
        top = "Avec TopCase" if self.has_top_case else "Sans TopCase"
        return f"[Moto {self.year}] {self.brand} {self.model} - {self.engine_displacement}cc, {top}"
    
    def to_dict(self): d=super().to_dict(); d.update({"engine_displacement": self.engine_displacement, "has_top_case": self.has_top_case}); return d

class Hearse(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, max_coffin_length, has_refrigeration):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.max_coffin_length = max_coffin_length; self.has_refrigeration = has_refrigeration
    
    def show_details(self): 
        frigo = "Réfrigéré" if self.has_refrigeration else "Non réfrigéré"
        return f"[Corbillard {self.year}] {self.brand} {self.model} - Cercueil max {self.max_coffin_length}m, {frigo}"
    
    def to_dict(self): d=super().to_dict(); d.update({"max_coffin_length": self.max_coffin_length, "has_refrigeration": self.has_refrigeration}); return d

class GoKart(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, engine_type, is_indoor):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.engine_type = engine_type; self.is_indoor = is_indoor
    
    def show_details(self): 
        loc = "Indoor" if self.is_indoor else "Outdoor"
        return f"[Kart {self.year}] {self.brand} {self.model} - {self.engine_type}, {loc}"
    
    def to_dict(self): d=super().to_dict(); d.update({"engine_type": self.engine_type, "is_indoor": self.is_indoor}); return d

# --- MER ---
class Boat(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, length_meters, power_cv):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.length_meters = length_meters; self.power_cv = power_cv
    
    def show_details(self): 
        return f"[Bateau {self.year}] {self.brand} {self.model} - {self.length_meters}m, {self.power_cv}cv"
    
    def to_dict(self): d=super().to_dict(); d.update({"length_meters": self.length_meters, "power_cv": self.power_cv}); return d

class Submarine(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, max_depth, is_nuclear):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.max_depth = max_depth; self.is_nuclear = is_nuclear
    
    def show_details(self): 
        moteur = "Nucléaire" if self.is_nuclear else "Diesel/Élec"
        return f"[Sous-Marin {self.year}] {self.brand} {self.model} - Prof. -{self.max_depth}m, {moteur}"
    
    def to_dict(self): d=super().to_dict(); d.update({"max_depth": self.max_depth, "is_nuclear": self.is_nuclear}); return d

# --- AIR ---
class Plane(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, wingspan, engines_count):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.wingspan = wingspan; self.engines_count = engines_count
    
    def show_details(self): 
        return f"[Avion {self.year}] {self.brand} {self.model} - Env. {self.wingspan}m, {self.engines_count} moteurs"
    
    def to_dict(self): d=super().to_dict(); d.update({"wingspan": self.wingspan, "engines_count": self.engines_count}); return d

class Helicopter(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, rotor_count, max_altitude):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.rotor_count = rotor_count; self.max_altitude = max_altitude
    
    def show_details(self): 
        return f"[Hélico {self.year}] {self.brand} {self.model} - {self.rotor_count} pales, Alt. max {self.max_altitude}m"
    
    def to_dict(self): d=super().to_dict(); d.update({"rotor_count": self.rotor_count, "max_altitude": self.max_altitude}); return d

# --- ATTELAGES ---
class Carriage(TowedVehicle):
    def __init__(self, t_id, daily_rate, seat_count, has_roof):
        super().__init__(t_id, daily_rate, seat_count)
        self.has_roof = has_roof
    def harness_animal(self, animal):
        if isinstance(animal, Horse) and animal.wither_height >= 140: super().harness_animal(animal)
        else: print("❌ Seul un Cheval (>140cm) peut tirer une Calèche.")
    def show_details(self):
        toit = "Avec toit" if self.has_roof else "Décapotable"
        att = f" avec {len(self.animals)} chevaux" if self.animals else " (vide)"
        return f"[Calèche] {self.seat_count} places, {toit} {att}"
    def to_dict(self): d=super().to_dict(); d.update({"has_roof": self.has_roof}); return d

class Cart(TowedVehicle):
    def __init__(self, t_id, daily_rate, seat_count, max_load_kg):
        super().__init__(t_id, daily_rate, seat_count)
        self.max_load_kg = max_load_kg
    def harness_animal(self, animal):
        if isinstance(animal, Donkey): super().harness_animal(animal)
        else: print("❌ Seul un Âne peut tirer une Charrette.")
    def show_details(self):
        att = f" avec {len(self.animals)} ânes" if self.animals else " (vide)"
        return f"[Charrette] {self.max_load_kg}kg max {att}"
    def to_dict(self): d=super().to_dict(); d.update({"max_load_kg": self.max_load_kg}); return d

class Customer:
    def __init__(self, c_id: int, name: str, driver_license: str, email: str, phone: str, username: str, password: str):
        self.id = c_id
        self.name = name
        self.driver_license = driver_license
        self.email = email
        self.phone = phone
        self.username = username # Nouveau
        self.password = password

    def show_details(self):
        return f"[Client #{self.id}] {self.name} (Permis: {self.driver_license})"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "driver_license": self.driver_license,
            "email": self.email,
            "phone": self.phone,
            "username": self.username, # Sauvegarde
            "password": self.password  # Sauvegarde
        }
    
    def to_table_row(self):
        return {
            "ID": self.id,
            "Nom": self.name,
            "Utilisateur": self.username,
            "Permis": self.driver_license,
            "Email": self.email
        }
    
class Rental:
    def __init__(self, customer, vehicle, start_date_str, end_date_str):
        self.customer = customer
        self.vehicle = vehicle

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
        self.vehicle.is_available = False

    def _validate_rental(self):
        if self.start_date > self.end_date:
            raise ValueError(f"Erreur: La date de fin ({self.end_date.date()}) est avant le début.")
        
        if not self.vehicle.is_available:
            raise ValueError(f"Le véhicule {self.vehicle.brand} {self.vehicle.model} est déjà loué !")
        
    def calculate_cost(self):
        """Calcule le coût théorique (avant retour réel)."""
        duration = (self.end_date - self.start_date).days
        days = max(1, duration) # Minimum 1 jour facturé
        
        # On récupère le prix journalier du véhicule
        return days * self.vehicle.daily_rate
    
    def close_rental(self, return_date_str):
        """Clôture la location et calcule le prix final."""
        try:
            self.actual_return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Format date retour invalide.")
        
        delta_prevu = (self.end_date - self.start_date).days
        delta_reel = (self.actual_return_date - self.start_date).days

        cout_base = max(1, delta_reel) * self.vehicle.daily_rate

        if self.actual_return_date > self.end_date:
            jours_retard = (self.actual_return_date - self.end_date).days

            self.penalty = (jours_retard * self.vehicle.daily_rate) * 0.10
            print(f"⚠️ Retard de {jours_retard} jours détecté. Pénalité appliquée.")

        self.total_cost = cout_base + self.penalty

        self.is_active = False
        self.vehicle.is_available = True

        return self.total_cost
    
from datetime import date
from typing import List, Optional, Type

DEFAULT_RENTAL_PRICES = {
    '1': 50.0, '2': 250.0, '3': 90.0, '4': 300.0, '5': 60.0,
    '6': 35.0, '7': 25.0, '8': 80.0, '9': 120.0, '10': 40.0,
    '11': 400.0, '12': 1500.0, '13': 200.0, '14': 150.0,
    '15': 800.0, '16': 2000.0, '17': 5000.0, '18': 10000.0
}

DEFAULT_MAINT_COSTS = {
    # Basiques
    MaintenanceType.MECHANICAL_CHECK: 50.0, 
    MaintenanceType.CLEANING: 20.0,
    MaintenanceType.HOOF_CARE: 40.0, 
    MaintenanceType.SADDLE_MAINTENANCE: 15.0,
    MaintenanceType.TIRE_CHANGE: 120.0, 
    MaintenanceType.OIL_CHANGE: 89.0,
    MaintenanceType.AXLE_GREASING: 30.0,
    
    # Spécifiques (MER / AIR / FANTASY)
    MaintenanceType.HULL_CLEANING: 500.0,    # Bateau
    MaintenanceType.SONAR_CHECK: 150.0,      # Sous-marin
    MaintenanceType.NUCLEAR_SERVICE: 5000.0, # Sous-marin
    MaintenanceType.AVIONICS_CHECK: 300.0,   # Avion
    MaintenanceType.ROTOR_INSPECTION: 200.0, # Hélico
    MaintenanceType.WING_CARE: 60.0,         # Aigle/Dragon
    MaintenanceType.SCALE_POLISHING: 100.0   # Dragon
}

DEFAULT_DURATIONS = {
    MaintenanceType.MECHANICAL_CHECK: 1.0, 
    MaintenanceType.CLEANING: 0.5,
    MaintenanceType.HOOF_CARE: 0.5, 
    MaintenanceType.SADDLE_MAINTENANCE: 2.0,
    MaintenanceType.TIRE_CHANGE: 0.5, 
    MaintenanceType.OIL_CHANGE: 0.5,
    MaintenanceType.AXLE_GREASING: 1.0,
    
    # Spécifiques
    MaintenanceType.HULL_CLEANING: 3.0,
    MaintenanceType.SONAR_CHECK: 1.0,
    MaintenanceType.NUCLEAR_SERVICE: 15.0,
    MaintenanceType.AVIONICS_CHECK: 2.0,
    MaintenanceType.ROTOR_INSPECTION: 1.0,
    MaintenanceType.WING_CARE: 1.0,
    MaintenanceType.SCALE_POLISHING: 0.5
}

class CarRentalSystem:
    def __init__(self):
        # Les 3 listes principales (Base de données en mémoire)
        self.fleet: List[TransportMode] = []
        self.customers: List[Customer] = []
        self.rentals: List[Rental] = []

    # ==========================================
    # 1. GESTION (CRUD)
    # ==========================================
    
    def add_vehicle(self, vehicle: TransportMode):
        self.fleet.append(vehicle)
        # Pas de print ici pour ne pas polluer l'interface, on laisse l'UI gérer

    def find_vehicle(self, v_id: int) -> Optional[TransportMode]:
        return next((v for v in self.fleet if v.id == v_id), None)

    def add_customer(self, customer: Customer):
        self.customers.append(customer)

    def find_customer(self, c_id: int) -> Optional[Customer]:
        return next((c for c in self.customers if c.id == c_id), None)

    # ==========================================
    # 2. GESTION DES LOCATIONS (CORE)
    # ==========================================

    def create_rental(self, customer_id: int, vehicle_id: int, start: date, end: date) -> Optional[Rental]:
        """Crée un contrat de location si tout est valide."""
        client = self.find_customer(customer_id)
        vehicule = self.find_vehicle(vehicle_id)

        # Vérifications
        if not client:
            print("❌ Erreur : Client introuvable.")
            return None
        if not vehicule:
            print("❌ Erreur : Véhicule introuvable.")
            return None
        if vehicule.status != VehicleStatus.AVAILABLE:
            print(f"❌ Indisponible : Ce véhicule est actuellement {vehicule.status.value}.")
            return None

        # Création
        new_id = len(self.rentals) + 1
        rental = Rental(new_id, vehicule, client, start, end)
        
        # Enregistrement
        self.rentals.append(rental)
        
        # Mise à jour du statut du véhicule
        vehicule.status = VehicleStatus.RENTED
        
        print(f"✅ Location validée pour {rental.total_price}€")
        return rental

    def return_vehicle(self, rental_id: int):
        """Clôture une location."""
        rental = next((r for r in self.rentals if r.id == rental_id), None)

        if rental and rental.is_active:
            rental.close_rental()
            rental.vehicle.status = VehicleStatus.AVAILABLE

            if hasattr(rental.vehicle, 'brand'):
                nom_vehicule = f"{rental.vehicle.brand} {rental.vehicle.model}"
            elif hasattr(rental.vehicle, 'name'):
                nom_vehicule = f"{rental.vehicle.name} ({rental.vehicle.breed})"
            else:
                nom_vehicule = "Véhicule/Attelage"

            print(f"🚗 Retour confirmé pour {nom_vehicule}.")
        else:
            print("❌ Erreur : Location introuvable ou déjà terminée.")

    # ==========================================
    # 3. RECHERCHE (SEARCH)
    # ==========================================

    def search_vehicles(self, 
                        vehicle_type: Type[TransportMode] = None, 
                        available_only: bool = True, 
                        max_price: float = None) -> List[TransportMode]:
        """
        Filtre la flotte selon plusieurs critères.
        Ex: Trouver toutes les Voitures disponibles à moins de 100€.
        """
        results = []
        for v in self.fleet:
            # Critère 1 : Disponibilité
            if available_only and v.status != VehicleStatus.AVAILABLE:
                continue
            
            # Critère 2 : Type (ex: chercher que les Bateaux)
            if vehicle_type and not isinstance(v, vehicle_type):
                continue

            # Critère 3 : Prix max
            if max_price and v.daily_rate > max_price:
                continue
            
            results.append(v)
        
        return results

    # ==========================================
    # 4. RAPPORTS (REPORTS)
    # ==========================================

    def generate_active_rentals_report(self):
        """Affiche toutes les locations en cours."""
        print("\n--- 📄 RAPPORT : LOCATIONS ACTIVES ---")
        active_rentals = [r for r in self.rentals if r.is_active]
        
        if not active_rentals:
            print("Aucune location en cours.")
        else:
            for r in active_rentals:
                print(r.show_details())
        print("--------------------------------------")

    def generate_revenue_report(self):
        """Calcule le chiffre d'affaires total."""
        total_revenue = sum(r.total_price for r in self.rentals)
        print(f"\n--- 💰 RAPPORT FINANCIER ---")
        print(f"Nombre total de contrats : {len(self.rentals)}")
        print(f"Chiffre d'Affaires Total : {total_revenue}€")
        print("----------------------------")
        return total_revenue
    
class StorageManager:
    def __init__(self, filename="data.json"):
        self.filename = filename

    def save_system(self, system):
        """Sauvegarde tout : Flotte, Clients, Locations"""
        data = {
            "fleet": [v.to_dict() for v in system.fleet],
            "customers": [c.to_dict() for c in system.customers],
            "rentals": [r.to_dict() for r in system.rentals]
        }
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur Save : {e}")

    def load_system(self):
        """Charge tout et retourne un objet CarRentalSystem prêt à l'emploi"""
        system = CarRentalSystem()

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return system
        
        # ==========================================
        # 1. CHARGEMENT DE LA FLOTTE
        # ==========================================
        fleet_data = data.get("fleet", [])
        fleet_map = {}

        for item in fleet_data:
            typ = item.get("type")
            tid = item["id"]
            rate = item["daily_rate"]
            obj = None

            if typ=="Car": obj=Car(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["door_count"],item["has_ac"])
            elif typ=="Truck": obj=Truck(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["cargo_volume"],item["max_weight"])
            elif typ=="Motorcycle": obj=Motorcycle(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["engine_displacement"],item["has_top_case"])
            elif typ=="Hearse": obj=Hearse(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["max_coffin_length"],item["has_refrigeration"])
            elif typ=="GoKart": obj=GoKart(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["engine_type"],item["is_indoor"])
            elif typ=="Boat": obj=Boat(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["length_meters"],item["power_cv"])
            elif typ=="Submarine": obj=Submarine(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["max_depth"],item["is_nuclear"])
            elif typ=="Plane": obj=Plane(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["wingspan"],item["engines_count"])
            elif typ=="Helicopter": obj=Helicopter(tid,rate,item["brand"],item["model"],item["license_plate"],item.get("year",2020),item["rotor_count"],item["max_altitude"])

            elif typ=="Horse": obj=Horse(tid,rate,item["name"],item["breed"],item.get("age",5),item["wither_height"],item.get("shoe_size_front",0),item.get("shoe_size_rear",0))
            elif typ=="Donkey": obj=Donkey(tid,rate,item["name"],item["breed"],item.get("age",5),item["pack_capacity_kg"],item["is_stubborn"])
            elif typ=="Camel": obj=Camel(tid,rate,item["name"],item["breed"],item.get("age",5),item["hump_count"],item["water_reserve"])
            elif typ=="Whale": obj=Whale(tid,rate,item["name"],item["breed"],item.get("age",10),item["weight_tonnes"],item["can_sing"])
            elif typ=="Dolphin": obj=Dolphin(tid,rate,item["name"],item["breed"],item.get("age",5),item["swim_speed"],item["knows_tricks"])
            elif typ=="Eagle": obj=Eagle(tid,rate,item["name"],item["breed"],item.get("age",5),item["wingspan_cm"],item["max_altitude"])
            elif typ=="Dragon": obj=Dragon(tid,rate,item["name"],item["breed"],item.get("age",100),item["fire_range"],item["scale_color"])

            elif typ=="Carriage": obj=Carriage(tid,rate,item["seat_count"],item["has_roof"])
            elif typ=="Cart": obj=Cart(tid,rate,item["seat_count"],item["max_load_kg"])

            if obj:
                for s in VehicleStatus:
                    if s.value == item.get("status"): obj.status = s

                for l in item.get("maintenance_log",[]):
                    y,m,d = map(int, l["date"].split('-'))
                    mt = next((t for t in MaintenanceType if t.value==l["type"]), None)
                    if mt: obj.add_maintenance(Maintenance(l["id"], date(y,m,d), mt, l["cost"], l["description"], l.get("duration",1.0)))

                system.fleet.append(obj)
                fleet_map[obj.id] = obj
        
        for item in fleet_data:
            if item.get("animal_ids"):
                vehicle = fleet_map.get(item["id"])
                if vehicle:
                    for aid in item["animal_ids"]:
                        anim = fleet_map.get(aid)
                        if anim: vehicle.animals.append(anim)

        # ==========================================
        # 2. CHARGEMENT DES CLIENTS
        # ==========================================
        cust_data = data.get("customers", [])
        customer_map = {}

        for c in cust_data:
            user = c.get("username", f"user{c['id']}")
            pwd = c.get("password", "1234")

            new_c = Customer(c["id"], c["name"], c["driver_license"], c["email"], c["phone"], user, pwd)
            system.customers.append(new_c)
            customer_map[new_c.id] = new_c

        # ==========================================
        # 3. CHARGEMENT DES LOCATIONS
        # ==========================================
        rent_data = data.get("rentals", [])

        for r in rent_data:
            veh = fleet_map.get(r["vehicle_id"])
            cust = customer_map.get(r["customer_id"])

            if veh and cust:
                y1, m1, d1 = map(int, r["start_date"].split('-'))
                y2, m2, d2 = map(int, r["end_date"].split('-'))

                new_rental = Rental(r["id"], veh, cust, date(y1,m1,d1), date(y2,m2,d2))
                new_rental.is_active = r["is_active"]
                system.rentals.append(new_rental)

        print(f"📂 Chargement complet OK")
        return system
    
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ask_int(msg):
    while True:
        try:
            return int(input(f"{msg} (Entier): "))
        except ValueError:
            print("❌ Saisie invalide. Veuillez entrer un nombre entier.")

def ask_float(msg):
    while True:
        try:
            # Remplace la virgule par un point si l'utilisateur est en configuration FR
            val = input(f"{msg} (Nombre décimal): ").replace(',', '.')
            return float(val)
        except ValueError:
            print("❌ Saisie invalide. Veuillez entrer un nombre décimal.")

def ask_float_def(msg, default):
    while True:
        try:
            val = input(f"{msg} (Défaut {default:.2f}): ").strip()
            if not val: return default
            return float(val.replace(',', '.'))
        except ValueError:
            print("❌ Saisie invalide.")

def ask_bool(msg):
    while True:
        response = input(f"{msg} (o/n): ").lower().strip()
        if response in ('o', 'oui'): return True
        if response in ('n', 'non'): return False
        print("Veuillez répondre par 'o' ou 'n'.")

def ask_text(msg, default=""):
    return input(f"{msg} (Défaut: {default}): ")

# =========================================================
# GESTION FLOTTE UI (SANS RICH)
# =========================================================

def show_main_menu(system, storage):
    menu_text = """
================ GESTION DE FLOTTE ================
[1] Voir la flotte (Tableau)
[2] Ajouter un élément
[3] Maintenance / Soins
[4] Atteler (Charrette/Calèche)
[5] Supprimer un élément
[6] Voir Détails (Fiche)
[7] Stats & Recherche
[8] Sauvegarder et Quitter
[0] Retour
===================================================
"""
    fleet = system.fleet
    while True:
        clear_screen()
        print(menu_text)
        choice = input("Votre choix (0-8): ").strip()

        if choice == '0': break
        elif choice == '1' : list_fleet(fleet)
        elif choice == '2' : add_menu_by_environment(fleet)
        elif choice == '3' : maintenance_menu(fleet)
        elif choice == '4' : harness_menu(fleet)
        elif choice == '5' : delete_menu(fleet)
        elif choice == '6' : show_single_vehicle_details(fleet)
        elif choice == '7' : statistics_menu(fleet)
        elif choice == '8':
            storage.save_system(system)
            print("\n💾 Système sauvegardé ! Retour au menu principal.")
            input("Appuyez sur Entrée pour continuer...")
            break
        else:
            print("Choix invalide. Réessayez.")
            time.sleep(0.5)

def list_fleet(fleet, title_str="État de la Flotte"):
    if not fleet:
        print(f"\n--- {title_str} : Aucun élément trouvé. ---")
        return
    
    print("\n" + "="*90)
    print(f"| {'ID'.ljust(2)} | {'Type'.ljust(11)} | {'Identifiant'.ljust(15)} | {'Description'.ljust(24)} | {'Tarif'.ljust(5)} | {'Statut'.ljust(15)} |")
    print("-" * 90)

    for v in fleet:
        obj_type = v.__class__.__name__.ljust(11)
        ident = getattr(v, 'license_plate', getattr(v, 'name', '---')).ljust(15)
        desc = getattr(v, 'model', getattr(v, 'breed', '---')).ljust(24)[:24]
        status_txt = v.status.value.ljust(15)
        
        print(f"| {str(v.id).ljust(2)} | {obj_type} | {ident} | {desc} | {str(v.daily_rate).ljust(5)}€ | {status_txt}|")
        
    print("="*90)
    input("Appuyez sur Entrée pour continuer...")

def show_single_vehicle_details(fleet):
    target_id = ask_int("Entrez l'ID de l'élément à inspecter")
    obj = next((v for v in fleet if v.id == target_id), None)

    if not obj:
        print("❌ ID introuvable.")
        return
    
    print("\n=============================================")
    print(f"FICHE TECHNIQUE : {obj.__class__.__name__}")
    print("=============================================")
    print(f"ID Unique: {obj.id}")
    print(f"Statut Actuel: {obj.status.value}")
    print(f"Tarif Journalier: {obj.daily_rate}€")
    
    # Affichage des attributs spécifiques
    ignored_keys = ['id', 'status', 'daily_rate', 'maintenance_log', 'animals', 'animal_ids']

    for key, value in obj.__dict__.items():
        if key not in ignored_keys:
            pretty_key = key.replace("_", " ").title()
            pretty_value = str(value)
            if isinstance(value, bool): pretty_value = "Oui" if value else "Non"
            print(f"{pretty_key.ljust(20)}: {pretty_value}")

    input("\nAppuyez sur Entrée pour revenir au menu...")

# --- Ajoutez ici les fonctions add_menu_by_environment, maintenance_menu, harness_menu, delete_menu, statistics_menu ---
# (Elles doivent être refaites en utilisant print/input/ask_int etc.)
def add_menu_by_environment(fleet):
    print("\n--- MENU AJOUT (TERRE/MER/AIR) ---")
    input("Logique d'ajout simplifiée. Appuyez sur Entrée...")

def maintenance_menu(fleet):
    print("\n--- MENU MAINTENANCE ---")
    input("Logique de maintenance simplifiée. Appuyez sur Entrée...")

def harness_menu(fleet):
    print("\n--- MENU ATTELAGE ---")
    input("Logique d'attelage simplifiée. Appuyez sur Entrée...")

def delete_menu(fleet):
    print("\n--- MENU SUPPRESSION ---")
    input("Logique de suppression simplifiée. Appuyez sur Entrée...")

def statistics_menu(fleet):
    print("\n--- MENU STATISTIQUES ---")
    input("Logique des statistiques simplifiée. Appuyez sur Entrée...")


# =========================================================
# MAIN LOOP (Point d'entrée du programme)
# =========================================================
def show_global_menu():
    text = """
================ CAR RENTAL SYSTEM ================
[1] GESTION FLOTTE
[2] GESTION CLIENTS
[3] LOCATIONS
[4] SAUVEGARDER
[0] QUITTER
===================================================
    """
    clear_screen()
    print(text)

def main():
    storage = StorageManager("data.json")
    system = storage.load_system()
    if system is None: system = CarRentalSystem()
    
    while True:
        show_global_menu()
        choice = input("Votre choix (0-4): ").strip()
        
        if choice == "1":
            show_main_menu(system, storage)
            
        elif choice == "2":
            # menu_clients(system)
            print("Menu Clients...")
            input("Appuyez sur Entrée...")
            
        elif choice == "3":
            # menu_locations(system)
            print("Menu Locations...")
            input("Appuyez sur Entrée...")
            
        elif choice == "4":
            storage.save_system(system)
            print("\n💾 Sauvegarde effectuée !")
            input("Appuyez sur Entrée...")
            
        elif choice == "0":
            if input("Voulez-vous vraiment quitter ? (o/n): ").lower().strip() in ('o', 'oui'):
                sys.exit()

if __name__ == "__main__":
    main()