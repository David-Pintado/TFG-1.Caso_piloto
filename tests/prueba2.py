from itertools import product
import re

def pluralizar_palabra(palabra):
    """Función para obtener el plural de una palabra en español de forma manual"""
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

    palabras = re.findall(r"\b\w+\b", palabra)
    palabras_a_pluralizar = [p for p in palabras if p not in preposiciones]

    permutaciones_plurales = []
    for p in palabras_a_pluralizar:
        found = False
        for sufijo, plural in sufijos.items():
            if p.endswith(sufijo):
                permutaciones_plurales.append(p[:-1] + plural)
                found = True
        if not found:
            permutaciones_plurales.append(p + 's')

    permutaciones_compuestas = list(product(permutaciones_plurales, repeat=len(palabras_a_pluralizar)))

    resultados = []
    for permutacion in permutaciones_compuestas:
        resultado = []
        indice_palabra = 0
        for palabra_actual in palabras:
            if palabra_actual in preposiciones:
                resultado.append(palabra_actual)
            else:
                resultado.append(permutacion[indice_palabra])
                indice_palabra += 1
        resultados.append(" ".join(resultado))

    return resultados


    # if (len(palabra.split(' ')) > 0):
    #     for element in palabra.split(' '):
    #         if element not in preposiciones:
    #             for sufijo, plural in sufijos.items():
    #                 if palabra.endswith(sufijo):
    #                     return palabra[:-1] + plural

    #                 return palabra + 's'
    # else:
    #     # Buscar si la palabra termina en uno de los sufijos conocidos
    #     for sufijo, plural in sufijos.items():
    #         if palabra.endswith(sufijo):
    #             return palabra[:-1] + plural

    #     return palabra + 's'
    
def needs_accent(original_word, pluralized_word):
    """Determina si una palabra pluralizada necesita llevar tilde según las reglas de acentuación del español."""
    vowels = "aeiouáéíóú"
    
    # Verificar si la última letra antes de la terminación plural es una vocal
    for i in range(len(original_word) - 1, -1, -1):
        if original_word[i] in vowels:
            # Si es una vocal, verificar si la palabra original tenía tilde en esa posición
            if original_word[i] in "áéíóú":
                return False  # Si la palabra original tenía tilde, no se necesita tilde en la forma plural
            elif i == len(original_word) - 1:
                # Si la vocal está en la última posición, la palabra es aguda
                return original_word[i] not in "aeiouáéíóú"
            else:
                # Si la vocal está más hacia adelante, la palabra es llana
                return original_word[i] in "aeiouáéíóú"
    return False  # Si no hay vocales antes de la terminación plural, no se necesita tilde

    
def pluralize_word(word):
    """Función para obtener la forma plural de una palabra (En el caso de que esta sea plural, devolverá su plural)
       En el caso de que la palabra sea compuesta, devolverá las permutaciones plurales de esa palabra en español
       
       Parámetros:
        - word (string)= Palabra a pluralizar (Puede ser simple o compuesta)
        
       Retorna:
        - pluralize_words_list (Array<string>)
                - Si la palabra es simple la lista contendrá solo un elemento
                - Si la palabra es compuesta la lista contendrá las permutaciones plurales de la palabra
                    () 
    """
    # Lista de sufijos comunes para la formación del plural en español
    suffixes = {
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

    prepositions = ["a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "durante", "en", "entre", "hacia", "hasta", "mediante", "para", "por", "según", "sin", "so", "sobre", "tras"]

    words = word.split()

    # Función para pluralizar una palabra individual
    def pluralize(word):
        for suffix, plural in suffixes.items():
            if word.endswith(suffix):
                return word[:-1] + plural
        return word + 's'

    plural_permutations = []
    for word in words:
        if word in prepositions:
            plural_permutations.append([word])
        else:
            plural = pluralize(word)
            if plural != word:
                plural_permutations.append([word, plural])
            else:
                plural_permutations.append([word])

    composite_permutations = product(*plural_permutations)
    pluralize_words_list = []
    for permutation in composite_permutations:
        pluralized_word = " ".join(permutation)
        if needs_accent(word, pluralized_word):
            pluralized_word = pluralized_word[:-2] + 'és'  # Agregar tilde y la "s" final
        pluralize_words_list.append(pluralized_word)

    return pluralize_words_list

# Ejemplos de uso
palabras = ['luz', 'perro', 'luces', 'mes', 'animal', 'Ciudad', 'peluca de pelo de caballo', 'relación social']
for palabra in palabras:
    plurales = pluralize_word(palabra)
    print(f"Permutaciones plurales de '{palabra}':")
    for plural in plurales:
        print(f"- {plural}")
    
    
# Funcion v1 para detectar los generos a partir de los dos array
# -----------------------
# array = ['La abstracción de amistad es un principio fundamental para la vida humana.', 'El proceso de formación de abstracciones es fundamental para la comprensión de los idiomas.', 'El conocimiento científico se basa principalmente en abstracciones matemáticas.', 'El estudio de las abstracciones lingüísticas es una parte importante del estudio de la sintaxis.', 'La abstracción de la belleza es un tema recurrente en la literatura y las artes.','La abstracción de amistad es un principio fundamental para la vida humana.', 'El proceso de formación de abstracciones es fundamental para la comprensión de los idiomas.', 'El conocimiento científico se basa principalmente en abstracciones matemáticas.', 'El estudio de las abstracciones lingüísticas es una parte importante del estudio de la sintaxis.', 'La abstracción de la belleza es un tema recurrente en la literatura y las artes.']

# array2 = ['La abstracción clave del proceso es la idea de uniformidad', 'La abstracción central del tema es la definición del término', 'La abstracción principal del concepto es su aplicación práctica', 'La abstracción más importante del método es su efectividad', 'La abstracción fundamental del proceso es su capacidad para satisfacer las necesidades.','La abstracción clave del proceso es la idea de uniformidad', 'La abstracción central del tema es la definición del término', 'La abstracción principal del concepto es su aplicación práctica', 'La abstracción más importante del método es su efectividad', 'La abstracción fundamental del proceso es su capacidad para satisfacer las necesidades.']

# frases1 = [
#     "El estudiante de segundo curso asiste a todas las clases de lógica matemática y trabaja diligentemente en sus ejercicios.",
#     "Durante el semestre, el estudiante de segundo año ha demostrado un gran avance en el aprendizaje de la lengua extranjera y esperamos que continúe así.",
#     "El estudiante de segundo año ha realizado excelentes presentaciones en todas sus clases de ciencias sociales y ha demostrado un gran interés en las cuestiones internacionales.",
#     "El estudiante de segundo año ha elegido una tesis sobre la historia de la música clásica y se está preparando para presentarla en la reunión de estudiantes de segundo año.",
#     "El estudiante de segundo año trabaja en equipo con sus compañeros en la preparación de la presentación final del semestre y se espera que lleve la presentación de forma profesional."
# ]

# frases2 = [
#     "La estudiante de segundo curso asiste a todas las clases de historia antigua y trabaja diligentemente en sus tareas.",
#     "Durante el semestre, la estudiante de segundo año ha demostrado un gran avance en el aprendizaje de la matemática aplicada y esperamos que continúe así.",
#     "La estudiante de segundo año ha realizado excelentes presentaciones en todas sus clases de ciencias naturales y ha demostrado un gran interés en la ecología.",
#     "La estudiante de segundo año ha elegido una tesis sobre la historia de la literatura y se está preparando para presentarla en la reunión de estudiantes de segundo año.",
#     "La estudiante de segundo año trabaja en equipo con sus compañeros en la preparación de la presentación final del semestre y se espera que lleve la presentación de forma profesional."
# ]

# uno = [
#     "El novio de María se prepara para su boda en dos meses.",
#     "El padre de Laura está buscando un novio adecuado para su hija.",
#     "El novio de Marta ha propuesto matrimonio y ella aceptó con alegría.",
#     "El novio de Sofía está ayudando a planificar su propia boda.",
#     "El novio de Ana está gestionando todos los detalles de su matrimonio, desde la decoración de la iglesia hasta el menú de la recepción."
# ]

# dos = [
#     "La novia de Isabel se está preparando para su boda en dos meses.",
#     "La madre de Lucía está buscando una novia adecuada para su hija.",
#     "La novia de María ha aceptado la propuesta de matrimonio con alegría.",
#     "La novia de Sofía está ayudando a planificar su propia boda.",
#     "La novia de Ana está gestionando todos los detalles de su matrimonio, desde la decoración de la iglesia hasta el menú de la recepción."
# ]



# def return_answers(word, array):
#     count_masculino = 0
#     count_femenino = 0
#     count_neutro = 0
#     for element in array[0]:
#         if " " + word + " " in element:
#            count_masculino += 1
#         for articleM in array_mas:
#                 if articleM.lower() in element.split(word)[0].strip().split(' ')[-1].lower():  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
#                     count_masculino += 1
#     for element in array[1]:
#         if " " + word + " " in element:
#            count_femenino += 1
#         for articleF in array_fem:
#            if articleF.lower() in element.split(word)[0].strip().split(' ')[-1].lower():  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
#                 count_femenino += 1
#     max_difference = len(array[0])-round((len(array[0])*2)/3) + 1
#     list_minimum_appearences = len(array[0]) * 0.8
#     gender = ""
#     if 0 <= abs(count_masculino-count_femenino) <= max_difference:
#     	gender = "Neutro"
#     elif max_difference < abs(count_masculino-count_femenino):
#         if count_masculino > count_femenino and count_masculino > (list_minimum_appearences + max_difference):
#            gender = "Masculino"
#         elif count_femenino > count_masculino and count_femenino > (list_minimum_appearences + max_difference):
#            gender = "Femenino"
#         else:
#            gender = "NULL"
#     return gender
    
# print('abstracción')
# print(return_answers('abstracción', [array, array2]))
# print('estudiante')
# print(return_answers('estudiante', [frases1,frases2]))
# print('novio')
# print(return_answers('novio', [uno,dos]))