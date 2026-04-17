from uuid import UUID
from src.domain.value_objects.email import Email

class User:
    def __init__(self, id: UUID, email: Email, is_active: bool = True):
        self.id = id
        self.email = email
        self.is_active = is_active

    def deactivate(self):
        self.is_active = False

    def __repr__(self):
        return f"User(id={self.id}, email={self.email})"