import re

class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise ValueError(f"Email inválido: {value}")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    @staticmethod
    def _is_valid(email: str) -> bool:
        # Regex simple para validación básica
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def __eq__(self, other):
        if isinstance(other, Email):
            return self._value == other._value
        return False

    def __repr__(self):
        return f"Email('{self._value}')"