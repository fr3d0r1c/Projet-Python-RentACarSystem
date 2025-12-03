from datetime import date
from enums import MaintenanceType

class Maintenance:
    def __init__(self, m_id: int, date_m: date, m_type: MaintenanceType, cost: float, description: str):
        self.id = m_id
        self.date = date_m
        self.type = m_type
        self.cost = cost
        self.description = description

    def validate(self):
        print(f"Maintenance #{self.id} ({self.type.value}) validée pour {self.cost}€.")