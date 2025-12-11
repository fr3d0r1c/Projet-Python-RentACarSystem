import json
import sys
import os
import time
from datetime import date, timedelta, datetime
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional

# =========================================================
# 1. UTILITAIRES (AFFICHAGE & SAISIE SÉCURISÉE)
# =========================================================

def clear_screen():
    """Nettoie la console selon le système d'exploitation."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Affiche un joli titre sans module externe."""
    print("\n" + "=" * 60)
    print(f"   {title.upper()}")
    print("=" * 60)

def ask_int(msg):
    """Demande un entier de manière robuste."""
    while True:
        try:
            user_input = input(f"{msg} : ").strip()
            return int(user_input)
        except ValueError:
            print("❌ Erreur : Veuillez entrer un nombre entier valide.")

def ask_float(msg):
    """Demande un nombre décimal."""
    while True:
        try:
            user_input = input(f"{msg} : ").replace(',', '.').strip()
            return float(user_input)
        except ValueError:
            print("❌ Erreur : Veuillez entrer un nombre (ex: 10.5).")

def ask_float_def(msg, default):
    """Demande un float avec valeur par défaut."""
    while True:
        try:
            user_input = input(f"{msg} [Défaut: {default}] : ").replace(',', '.').strip()
            if not user_input:
                return default
            return float(user_input)
        except ValueError:
            print("❌ Erreur de saisie.")

def ask_text(msg, default=None):
    """Demande du texte."""
    prompt = f"{msg} [Défaut: {default}] : " if default else f"{msg} : "
    val = input(prompt).strip()
    if not val and default:
        return default
    return val

def ask_bool(msg):
    """Demande Oui/Non."""
    while True:
        val = input(f"{msg} (O/N) : ").lower().strip()
        if val in ['o', 'oui', 'y', 'yes']: return True
        if val in ['n', 'non', 'no']: return False
        print("❌ Répondez par 'O' ou 'N'.")

def ask_date(msg, default_str=None):
    """Demande une date au format YYYY-MM-DD."""
    while True:
        prompt = f"{msg} (YYYY-MM-DD)"
        if default_str:
            prompt += f" [Défaut: {default_str}]"
        
        val = input(f"{prompt} : ").strip()
        if not val and default_str:
            return default_str # Retourne la string
        
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except ValueError:
            print("❌ Format invalide. Utilisez AAAA-MM-JJ (ex: 2024-05-20).")

# =========================================================
# 2. ENUMS & CONSTANTES
# =========================================================

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
    HULL_CLEANING = "Carénage (Coque)"
    SONAR_CHECK = "Calibrage Sonar"
    NUCLEAR_SERVICE = "Révision Réacteur"
    AVIONICS_CHECK = "Systèmes Avioniques"
    ROTOR_INSPECTION = "Inspection Rotor"
    WING_CARE = "Soin des Ailes"
    SCALE_POLISHING = "Lustrage Écailles"

DEFAULT_MAINT_COSTS = {
    MaintenanceType.MECHANICAL_CHECK: 50.0, MaintenanceType.CLEANING: 20.0,
    MaintenanceType.HOOF_CARE: 40.0, MaintenanceType.SADDLE_MAINTENANCE: 15.0,
    MaintenanceType.TIRE_CHANGE: 120.0, MaintenanceType.OIL_CHANGE: 89.0,
    MaintenanceType.AXLE_GREASING: 30.0, MaintenanceType.HULL_CLEANING: 500.0,
    MaintenanceType.SONAR_CHECK: 150.0, MaintenanceType.NUCLEAR_SERVICE: 5000.0,
    MaintenanceType.AVIONICS_CHECK: 300.0, MaintenanceType.ROTOR_INSPECTION: 200.0,
    MaintenanceType.WING_CARE: 60.0, MaintenanceType.SCALE_POLISHING: 100.0
}

DEFAULT_DURATIONS = {
    MaintenanceType.MECHANICAL_CHECK: 1.0, MaintenanceType.CLEANING: 0.5,
    MaintenanceType.HOOF_CARE: 0.5, MaintenanceType.SADDLE_MAINTENANCE: 2.0,
    MaintenanceType.TIRE_CHANGE: 0.5, MaintenanceType.OIL_CHANGE: 0.5,
    MaintenanceType.AXLE_GREASING: 1.0, MaintenanceType.HULL_CLEANING: 3.0,
    MaintenanceType.SONAR_CHECK: 1.0, MaintenanceType.NUCLEAR_SERVICE: 15.0,
    MaintenanceType.AVIONICS_CHECK: 2.0, MaintenanceType.ROTOR_INSPECTION: 1.0,
    MaintenanceType.WING_CARE: 1.0, MaintenanceType.SCALE_POLISHING: 0.5
}

# =========================================================
# 3. CLASSES MÉTIER (BACKEND)
# =========================================================

class Maintenance:
    def __init__(self, m_id: int, date_m: date, m_type: MaintenanceType, cost: float, description: str, duration: float):
        self.id = m_id
        self.date = date_m
        self.type = m_type
        self.cost = cost
        self.description = description
        self.duration = duration

    def to_dict(self):
        return {
            "id": self.id, "date": str(self.date), "type": self.type.value,
            "cost": self.cost, "description": self.description, "duration": self.duration
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
            "type": self.__class__.__name__, "id": self.id,
            "daily_rate": self.daily_rate, "status": self.status.value,
            "maintenance_log": m_logs
        }

    @abstractmethod
    def show_details(self): pass

# --- VÉHICULES MOTORISÉS ---
class MotorizedVehicle(TransportMode):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year):
        super().__init__(t_id, daily_rate)
        self.brand = brand; self.model = model; self.license_plate = license_plate; self.year = year
    def to_dict(self):
        d = super().to_dict()
        d.update({"brand": self.brand, "model": self.model, "license_plate": self.license_plate, "year": self.year})
        return d

class Car(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, door_count, has_ac):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.door_count = door_count; self.has_ac = has_ac
    def show_details(self): return f"[Voiture] {self.brand} {self.model} ({self.year}) - {self.door_count} portes"
    def to_dict(self): d=super().to_dict(); d.update({"door_count": self.door_count, "has_ac": self.has_ac}); return d

class Truck(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, cargo_volume, max_weight):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.cargo_volume = cargo_volume; self.max_weight = max_weight
    def show_details(self): return f"[Camion] {self.brand} {self.model} - {self.cargo_volume}m3"
    def to_dict(self): d=super().to_dict(); d.update({"cargo_volume": self.cargo_volume, "max_weight": self.max_weight}); return d

class Motorcycle(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, engine_displacement, has_top_case):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.engine_displacement = engine_displacement; self.has_top_case = has_top_case
    def show_details(self): return f"[Moto] {self.brand} {self.model} - {self.engine_displacement}cc"
    def to_dict(self): d=super().to_dict(); d.update({"engine_displacement": self.engine_displacement, "has_top_case": self.has_top_case}); return d

class Boat(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, length_meters, power_cv):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.length_meters = length_meters; self.power_cv = power_cv
    def show_details(self): return f"[Bateau] {self.brand} {self.model} - {self.length_meters}m"
    def to_dict(self): d=super().to_dict(); d.update({"length_meters": self.length_meters, "power_cv": self.power_cv}); return d

class Submarine(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, max_depth, is_nuclear):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.max_depth = max_depth; self.is_nuclear = is_nuclear
    def show_details(self): return f"[Sous-Marin] {self.brand} {self.model} - Profondeur {self.max_depth}m"
    def to_dict(self): d=super().to_dict(); d.update({"max_depth": self.max_depth, "is_nuclear": self.is_nuclear}); return d

class Plane(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, wingspan, engines_count):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.wingspan = wingspan; self.engines_count = engines_count
    def show_details(self): return f"[Avion] {self.brand} {self.model} - Env. {self.wingspan}m"
    def to_dict(self): d=super().to_dict(); d.update({"wingspan": self.wingspan, "engines_count": self.engines_count}); return d

class Helicopter(MotorizedVehicle):
    def __init__(self, t_id, daily_rate, brand, model, license_plate, year, rotor_count, max_altitude):
        super().__init__(t_id, daily_rate, brand, model, license_plate, year)
        self.rotor_count = rotor_count; self.max_altitude = max_altitude
    def show_details(self): return f"[Hélico] {self.brand} {self.model} - {self.rotor_count} pales"
    def to_dict(self): d=super().to_dict(); d.update({"rotor_count": self.rotor_count, "max_altitude": self.max_altitude}); return d

# --- ANIMAUX ---
class TransportAnimal(TransportMode):
    def __init__(self, t_id, daily_rate, name, breed, age):
        super().__init__(t_id, daily_rate)
        self.name = name; self.breed = breed; self.age = age
    def to_dict(self):
        d = super().to_dict()
        d.update({"name": self.name, "breed": self.breed, "age": self.age})
        return d

class Horse(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, wither_height, shoe_size_front, shoe_size_rear):
        super().__init__(t_id, daily_rate, name, breed, age)
        self.wither_height = wither_height; self.shoe_size_front = shoe_size_front; self.shoe_size_rear = shoe_size_rear
    def show_details(self): return f"[Cheval] {self.name} ({self.breed}) - {self.wither_height}cm"
    def to_dict(self): d=super().to_dict(); d.update({"wither_height": self.wither_height, "shoe_size_front": self.shoe_size_front, "shoe_size_rear": self.shoe_size_rear}); return d

class Dragon(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, fire_range, scale_color):
        super().__init__(t_id, daily_rate, name, breed, age)
        self.fire_range = fire_range; self.scale_color = scale_color
    def show_details(self): return f"[Dragon] {self.name} - Feu {self.fire_range}m ({self.scale_color})"
    def to_dict(self): d=super().to_dict(); d.update({"fire_range": self.fire_range, "scale_color": self.scale_color}); return d

class Donkey(TransportAnimal):
    def __init__(self, t_id, daily_rate, name, breed, age, pack_capacity_kg, is_stubborn):
        super().__init__(t_id, daily_rate, name, breed, age)
        self.pack_capacity_kg = pack_capacity_kg; self.is_stubborn = is_stubborn
    def show_details(self): return f"[Âne] {self.name} - Charge {self.pack_capacity_kg}kg"
    def to_dict(self): d=super().to_dict(); d.update({"pack_capacity_kg": self.pack_capacity_kg, "is_stubborn": self.is_stubborn}); return d

# --- ATTELAGES ---
class TowedVehicle(TransportMode):
    def __init__(self, t_id, daily_rate, seat_count):
        super().__init__(t_id, daily_rate)
        self.seat_count = seat_count; self.animals = []
    def harness_animal(self, animal):
        self.animals.append(animal)
        print(f"✅ {animal.name} a été attelé.")
    def to_dict(self):
        d = super().to_dict()
        d.update({"seat_count": self.seat_count, "animal_ids": [a.id for a in self.animals]})
        return d

class Carriage(TowedVehicle):
    def __init__(self, t_id, daily_rate, seat_count, has_roof):
        super().__init__(t_id, daily_rate, seat_count); self.has_roof = has_roof
    def show_details(self): return f"[Calèche] {self.seat_count} places"
    def to_dict(self): d=super().to_dict(); d.update({"has_roof": self.has_roof}); return d

class Cart(TowedVehicle):
    def __init__(self, t_id, daily_rate, seat_count, max_load_kg):
        super().__init__(t_id, daily_rate, seat_count); self.max_load_kg = max_load_kg
    def show_details(self): return f"[Charrette] Charge {self.max_load_kg}kg"
    def to_dict(self): d=super().to_dict(); d.update({"max_load_kg": self.max_load_kg}); return d

# --- CLIENTS & LOCATIONS ---
class Customer:
    def __init__(self, c_id, name, driver_license, email, phone, username, password):
        self.id = c_id; self.name = name; self.driver_license = driver_license
        self.email = email; self.phone = phone; self.username = username; self.password = password
    def to_dict(self):
        return {"id": self.id, "name": self.name, "driver_license": self.driver_license, "email": self.email, "phone": self.phone, "username": self.username, "password": self.password}

class Rental:
    def __init__(self, customer, vehicle, start_date_str, end_date_str):
        self.customer = customer; self.vehicle = vehicle
        try:
            self.start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            self.end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError: raise ValueError("Date invalide.")
        self.actual_return_date = None; self.total_cost = 0.0; self.penalty = 0.0; self.is_active = True
        self.vehicle.is_available = False

    def calculate_cost(self):
        days = max(1, (self.end_date - self.start_date).days)
        return days * self.vehicle.daily_rate

    def close_rental(self, return_date_str):
        try: self.actual_return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
        except ValueError: raise ValueError("Date retour invalide.")
        
        cout_base = max(1, (self.actual_return_date - self.start_date).days) * self.vehicle.daily_rate
        if self.actual_return_date > self.end_date:
            jours_retard = (self.actual_return_date - self.end_date).days
            self.penalty = (jours_retard * self.vehicle.daily_rate) * 0.10
            print(f"⚠️ Retard de {jours_retard} jours. Pénalité: {self.penalty}€")
        
        self.total_cost = cout_base + self.penalty
        self.is_active = False; self.vehicle.status = VehicleStatus.AVAILABLE
        return self.total_cost

    def to_dict(self):
        return {
            "customer_id": self.customer.id, "vehicle_id": self.vehicle.id,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "is_active": self.is_active, "total_cost": self.total_cost
        }

# =========================================================
# 4. SYSTÈME ET STOCKAGE
# =========================================================

class CarRentalSystem:
    def __init__(self):
        self.fleet: List[TransportMode] = []
        self.customers: List[Customer] = []
        self.rentals: List[Rental] = []

    def add_vehicle(self, v): self.fleet.append(v)
    def add_customer(self, c): self.customers.append(c)

class StorageManager:
    def __init__(self, filename="data.json"): self.filename = filename
    
    def save_system(self, system):
        data = {
            "fleet": [v.to_dict() for v in system.fleet],
            "customers": [c.to_dict() for c in system.customers],
            "rentals": [r.to_dict() for r in system.rentals]
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_system(self):
        system = CarRentalSystem()
        if not os.path.exists(self.filename): return system
        with open(self.filename, 'r', encoding='utf-8') as f: data = json.load(f)
        
        # 1. Flotte
        fleet_map = {}
        for item in data.get("fleet", []):
            typ = item.get("type")
            tid = item["id"]; rate = item["daily_rate"]
            obj = None
            
            if typ=="Car": obj=Car(tid,rate,item["brand"],item["model"],item["license_plate"],item["year"],item["door_count"],item["has_ac"])
            elif typ=="Truck": obj=Truck(tid,rate,item["brand"],item["model"],item["license_plate"],item["year"],item["cargo_volume"],item["max_weight"])
            elif typ=="Dragon": obj=Dragon(tid,rate,item["name"],item["breed"],item["age"],item["fire_range"],item["scale_color"])
            elif typ=="Horse": obj=Horse(tid,rate,item["name"],item["breed"],item["age"],item["wither_height"],0,0)
            elif typ=="Boat": obj=Boat(tid,rate,item["brand"],item["model"],item["license_plate"],item["year"],item["length_meters"],item["power_cv"])
            elif typ=="Submarine": obj=Submarine(tid,rate,item["brand"],item["model"],item["license_plate"],item["year"],item["max_depth"],item["is_nuclear"])
            elif typ=="Plane": obj=Plane(tid,rate,item["brand"],item["model"],item["license_plate"],item["year"],item["wingspan"],item["engines_count"])
            elif typ=="Helicopter": obj=Helicopter(tid,rate,item["brand"],item["model"],item["license_plate"],item["year"],item["rotor_count"],item["max_altitude"])
            
            if obj:
                for s in VehicleStatus:
                    if s.value == item.get("status"): obj.status = s
                system.fleet.append(obj)
                fleet_map[obj.id] = obj

        # 2. Clients
        cust_map = {}
        for c in data.get("customers", []):
            new_c = Customer(c["id"], c["name"], c["driver_license"], c["email"], c["phone"], c["username"], c["password"])
            system.customers.append(new_c)
            cust_map[new_c.id] = new_c

        # 3. Locations
        for r in data.get("rentals", []):
            veh = fleet_map.get(r["vehicle_id"])
            cust = cust_map.get(r["customer_id"])
            if veh and cust:
                new_r = Rental(cust, veh, r["start_date"], r["end_date"])
                new_r.is_active = r["is_active"]
                new_r.total_cost = r["total_cost"]
                system.rentals.append(new_r)
        
        return system

# =========================================================
# 5. MENUS CONSOLE (SANS RICH)
# =========================================================

def list_fleet(fleet):
    print_header("ÉTAT DE LA FLOTTE")
    if not fleet: print("Aucun véhicule."); return
    
    print(f"{'ID':<4} | {'Type':<12} | {'Description':<30} | {'Prix/j':<8} | {'Statut'}")
    print("-" * 80)
    for v in fleet:
        desc = getattr(v, 'brand', getattr(v, 'name', '')) + " " + getattr(v, 'model', getattr(v, 'breed', ''))
        print(f"{v.id:<4} | {v.__class__.__name__:<12} | {desc:<30} | {v.daily_rate:<8} | {v.status.value}")
    input("\nEntrée pour continuer...")

def add_menu(fleet):
    print_header("AJOUT DE VÉHICULE")
    print("1. Voiture  2. Camion  3. Dragon  4. Cheval  5. Bateau")
    c = input("Choix : ").strip()
    
    new_id = 1 if not fleet else max(v.id for v in fleet) + 1
    rate = ask_float_def("Prix journalier", 50.0)
    
    if c == '1':
        fleet.append(Car(new_id, rate, ask_text("Marque"), ask_text("Modèle"), ask_text("Plaque"), ask_int("Année"), ask_int("Portes"), ask_bool("Clim")))
    elif c == '2':
        fleet.append(Truck(new_id, rate, ask_text("Marque"), ask_text("Modèle"), ask_text("Plaque"), ask_int("Année"), ask_float("Volume"), ask_float("Poids")))
    elif c == '3':
        fleet.append(Dragon(new_id, rate, ask_text("Nom"), "Dragon", ask_int("Âge"), ask_float("Feu (m)"), ask_text("Couleur")))
    elif c == '4':
        fleet.append(Horse(new_id, rate, ask_text("Nom"), ask_text("Race"), ask_int("Âge"), ask_int("Taille (cm)"), 0, 0))
    elif c == '5':
        fleet.append(Boat(new_id, rate, ask_text("Marque"), ask_text("Modèle"), ask_text("Nom"), ask_int("Année"), ask_float("Longueur"), ask_float("CV")))
    
    print("✅ Ajouté !")
    time.sleep(1)

def maint_menu(fleet):
    list_fleet(fleet)
    vid = ask_int("ID Véhicule")
    v = next((x for x in fleet if x.id == vid), None)
    if v:
        print("Types : 1.Nettoyage 2.Mécanique 3.Soin")
        t = input("Choix : ")
        mt = MaintenanceType.CLEANING
        if t=='2': mt = MaintenanceType.MECHANICAL_CHECK
        elif t=='3': mt = MaintenanceType.HOOF_CARE
        
        cost = ask_float("Coût")
        v.add_maintenance(Maintenance(len(v.maintenance_log)+1, date.today(), mt, cost, "Entretien", 1))
        v.status = VehicleStatus.UNDER_MAINTENANCE
        print("✅ Maintenance enregistrée.")
    input("Entrée...")

def client_menu(system):
    while True:
        print_header("GESTION CLIENTS")
        print("1. Liste  2. Nouveau  0. Retour")
        c = input("Choix : ")
        if c == '0': break
        elif c == '1':
            for cu in system.customers: print(f"{cu.id}. {cu.name} ({cu.email})")
            input("Entrée...")
        elif c == '2':
            nid = len(system.customers)+1
            system.add_customer(Customer(nid, ask_text("Nom"), ask_text("Permis"), ask_text("Email"), "0000", ask_text("User"), "123"))
            print("✅ Client ajouté.")

def rental_menu(system):
    while True:
        print_header("LOCATIONS")
        print("1. Nouvelle  2. Retour  3. Liste  0. Retour")
        c = input("Choix : ")
        if c == '0': break
        elif c == '1':
            cid = ask_int("ID Client")
            vid = ask_int("ID Véhicule")
            cust = next((x for x in system.customers if x.id == cid), None)
            veh = next((x for x in system.fleet if x.id == vid), None)
            
            if cust and veh and veh.status == VehicleStatus.AVAILABLE:
                d1 = ask_date("Début")
                d2 = ask_date("Fin")
                try:
                    r = Rental(cust, veh, d1, d2)
                    system.rentals.append(r)
                    veh.status = VehicleStatus.RENTED
                    print(f"✅ Location validée. Coût estimé: {r.calculate_cost()}€")
                except ValueError as e: print(f"Erreur: {e}")
            else: print("❌ Impossible (Client/Véhicule introuvable ou indisponible)")
            input("Entrée...")
            
        elif c == '2':
            # Liste des locations actives
            actives = [r for r in system.rentals if r.is_active]
            for i, r in enumerate(actives):
                print(f"{i}. {r.vehicle.id} - {r.customer.name}")
            
            idx = ask_int("Numéro de la location")
            if 0 <= idx < len(actives):
                loc = actives[idx]
                dret = ask_date("Date retour réel")
                prix = loc.close_rental(dret)
                loc.vehicle.status = VehicleStatus.AVAILABLE
                print(f"✅ Retourné. Prix final: {prix}€")
            input("Entrée...")

def fleet_menu_loop(system, storage):
    while True:
        print_header("GESTION FLOTTE")
        print("1. Liste  2. Ajout  3. Maintenance  8. Sauver  0. Retour")
        c = input("Choix : ")
        if c=='0': break
        elif c=='1': list_fleet(system.fleet)
        elif c=='2': add_menu(system.fleet)
        elif c=='3': maint_menu(system.fleet)
        elif c=='8': storage.save_system(system); print("Sauvegardé !")

def main():
    storage = StorageManager("data.json")
    system = storage.load_system()
    
    while True:
        clear_screen()
        print_header("RENT-A-DREAM (CONSOLE)")
        print("1. 🚗 Flotte")
        print("2. 👥 Clients")
        print("3. 📝 Locations")
        print("4. 💾 Sauvegarder")
        print("0. ❌ Quitter")
        
        c = input("\nVotre choix : ").strip()
        
        if c == '1': fleet_menu_loop(system, storage)
        elif c == '2': client_menu(system)
        elif c == '3': rental_menu(system)
        elif c == '4': 
            storage.save_system(system)
            print("Sauvegarde OK.")
            time.sleep(1)
        elif c == '0': sys.exit()

if __name__ == "__main__":
    main()