from itertools import product

def pluralizar_palabras(palabra_compuesta):
    """Función para obtener las permutaciones plurales de una palabra compuesta en español"""
    # Lista de sufijos comunes para la formación del plural en español
    sufijos = {
        'z': 'ces',
        'l': 'les',
        'r': 'res',
        'n': 'nes',
        'y': 'yes',
        'j': 'jes',
        'd': 'des',
        's': 'ses',
        'x': 'xes'
    }

    preposiciones = ["a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "durante", "en", "entre", "hacia", "hasta", "mediante", "para", "por", "según", "sin", "so", "sobre", "tras"]

    palabras = palabra_compuesta.split()

    # Función para pluralizar una palabra individual
    def pluralizar(palabra):
        for sufijo, plural in sufijos.items():
            if palabra.endswith(sufijo):
                return palabra[:-1] + plural
        return palabra + 's'

    permutaciones_plurales = []
    for palabra in palabras:
        if palabra in preposiciones:
            permutaciones_plurales.append([palabra])
        else:
            plural = pluralizar(palabra)
            if plural != palabra:
                permutaciones_plurales.append([palabra, plural])
            else:
                permutaciones_plurales.append([palabra])

    permutaciones_compuestas = product(*permutaciones_plurales)
    resultados = []
    for permutacion in permutaciones_compuestas:
        resultados.append(" ".join(permutacion))

    return resultados

# Ejemplos de uso
palabras = ['luz', 'perro', 'luces', 'mes', 'animal', 'Ciudad', 'peluca de pelo de caballo', 'albergue de juventud']
for palabra in palabras:
    plurales = pluralizar_palabras(palabra)
    print(f"Permutaciones plurales de '{palabra}':")
    for plural in plurales:
        print(f"- {plural}")
