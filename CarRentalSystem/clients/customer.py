class Customer:
    def __init__(self, c_id: int, last_name: str, first_name: str, age: int, driver_license: str, email: str, phone: str, username: str, password: str):
        self.id = c_id
        self.last_name = last_name
        self.first_name = first_name
        self.age = age
        self.driver_license = driver_license
        self.email = email
        self.phone = phone
        self.username = username
        self.password = password

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def show_details(self):
        return f"[Client #{self.id}] {self.name} ({self.age} ans)"
    
    def to_dict(self):
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "age": self.age,
            "driver_license": self.driver_license,
            "email": self.email,
            "phone": self.phone,
            "username": self.username,
            "password": self.password
        }