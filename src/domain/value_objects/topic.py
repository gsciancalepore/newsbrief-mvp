class Topic:
    def __init__(self, value: str):
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("El tópico no puede estar vacío.")
        # Opcional: Limitar longitud o caracteres permitidos
        if len(cleaned) > 50:
            raise ValueError("El tópico es demasiado largo.")
        
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other):
        if isinstance(other, Topic):
            return self._value == other._value
        return False

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        return f"Topic('{self._value}')"