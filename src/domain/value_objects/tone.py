from enum import Enum

class Tone(str, Enum):
    FORMAL = "formal"       # Profesional, directo.
    INFORMAL = "informal"   # Amigable, cercano.
    SARCASTIC = "sarcastic" # Irónico, divertido.
    ELI5 = "eli5"           # "Explícamelo como si tuviera 5 años".

    def __str__(self):
        return self.value