import re

# Supongamos que 'male_word_appearence' contiene la palabra que queremos dividir
male_word_appearence = 'error'  # Ejemplo: puedes cambiar esto por la palabra que desees

# Lista de frases de ejemplo
frases = [
    "El error de lógica en su argumento fue evidente.",
    "El error gramatical en el artículo de periodismo fue corregido por la revisión.",
    "El error obvio en la contabilidad llevó a una investigación interna.",
    "El error de pronunciación del actor fue criticado por los seguidores de la escuela de teatro clásica.",
    "El error de programación en la computadora llevó al sistema al caos."
]

# Expresión regular que captura la palabra rodeada de espacios y signos de puntuación
pattern = r'\s*[\.,;:!\?\(\)\[\]"\']?\b' + re.escape(male_word_appearence) + r'\b[\.,;:!\?\(\)\[\]"\']?\s*'

for frase in frases:
    # Realizar el split
    partes = re.split(pattern, frase)
    # Eliminamos espacios en blanco adicionales en cada parte
    partes = [parte.strip() for parte in partes if parte.strip()]
    print(partes)