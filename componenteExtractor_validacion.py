
import re
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions
from unidecode import unidecode
from nltk.tokenize import RegexpTokenizer


def get_result(element, llm_answer_list):
    
    """
    Método para obtener el resultado (género de las palabras) de la fase de validación.
        
        Parámetros:
            - element (dict): Elemento de la estructura de datos 'knowledge_table', compuesto por key + attributes
            - llm_answer_list (List[str]) = Lista que se compone de respuestas del LLM que necesitan ser tratadas

        Retorna:
            -  result (List[str])
                - ["Masculino"]: La palabra es de género masculino
                - ["Femenino"]: La palabra es de género femenino
                - ["NULL", correct (dict), incorrect_1 (dict), incorrect_2 (dict), incorrect_3 (dict), message (dict)]: 
                        No se ha conseguido encontrar el género de la palabra
    """

    # Lista de respuesta extraídas del LLM
    llm_extracted_answer_list = []
    for llm_answer in llm_answer_list:
        llm_extracted_answer_list.append(auxFunctions.extract_llm_answers_set_of_phrases(llm_answer))

    # Mensaje de información del estado de la entrada
    message = "La entrada ha terminado su ejecución en la fase de validación."
    # Correctas: Frases correctas en las que se suman puntos.
    count_correct = 0
    # Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.
    count_incorrect_1 = 0
    # Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.
    count_incorrect_2 = 0
    # Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
    count_incorrect_3 = 0
    # Variables de puntuación de la categoría del resultado de la fase de extracción
    gender_points = 0
    # Palabra
    word = element[0].split('_')[1]
    # Lista de plurales de 'word'. Incluye la forma singular
    plural_word = auxFunctions.pluralize_word(word)
    # Resultado de la fase
    answer = ""
    # Resultado del método
    result = []
    # Marcadores de género femenino
    array_female = [
        'la', 'las', 'una', 'unas', 'esa', 'esta', 'esas', 'estas', 
        'otra', 'otras', 'muchas', 'varias', 'nuevas', 'toda', 'todas', 
        'alguna', 'algunas', 'aquella', 'aquellas', 'ninguna', 'ningunas', 
        'cierta', 'ciertas', 'nuestra', 'nuestras', 'vuestra', 'vuestras', 
        'suya', 'suyas'
    ]
    # Marcadores de género masculino
    array_male = [
        'el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 
        'estos', 'otro', 'otros', 'muchos', 'varios', 'nuevos', 'todo', 
        'todos', 'algún', 'algunos', 'aquel', 'aquellos', 'ningún', 
        'ningunos', 'cierto', 'ciertos', 'nuestro', 'nuestros', 'vuestro', 
        'vuestros', 'suyo', 'suyos'
    ]
    # Marcadores del género del resultado de la fase de extracción
    gender_terms = []
    if element[1][5].lower() == "femenino":
        gender_terms = array_female
    elif element[1][5].lower() == "masculino":
        gender_terms = array_male  
        
    # Umbral general    
    list_minimum_appearences = 3
    
    # Crear un tokenizador personalizado con una expresión regular
    tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for phrase in llm_extracted_answer_list[0]:
        if type(phrase) is list:
            phrase = phrase[0]
        phrase = phrase.lower()
        word_appearence = ""
        tokenize_phrase = tokenizer.tokenize(phrase)
        list_of_word_appearences = []
        phrase_copy = str(phrase)  # Crear una copia de phrase
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(phrase_copy))
            if match:
                word_appearence = phrase_copy[match.start():match.end()]
                list_of_word_appearences.append(word_appearence)
        if len(list_of_word_appearences) != 0:
            nouns_with_positions = auxFunctions.extract_nouns_with_positions(phrase)
            print(nouns_with_positions)
            word_position_list = list(position for (noun, position, _, _) in nouns_with_positions if noun in list_of_word_appearences)
            if len(word_position_list) >= 1:
                word_position = word_position_list[0]
                new_phrase = auxFunctions.destokenize(tokenize_phrase, tokenize_phrase[:word_position])
                search_article_phrase = new_phrase.strip().split(' ')
                if len(search_article_phrase) == 1:
                    if search_article_phrase[-1].lower() in gender_terms:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                        gender_points += 1
                        count_correct += 1
                    elif search_article_phrase[-1].lower() in gender_terms:
                        count_correct += 1
                        gender_points += 0.5
                    else:
                        # Sumar Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                        count_incorrect_3 += 1
                elif len(search_article_phrase) > 1:
                    reversed_search_article_phrase = search_article_phrase[::-1][:2]
                    if reversed_search_article_phrase[0].lower() in gender_terms:
                        count_correct += 1
                        gender_points += 1
                    elif reversed_search_article_phrase[1].lower() in gender_terms:
                        count_correct += 1
                        gender_points += 0.5
                    else:
                        # Sumar Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                        count_incorrect_3 += 1
            else:
                # Sumar Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase. en caso de que no haya nouns
                count_incorrect_1 += 1
        else:
            # Sumar Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.
            count_incorrect_2 += 1
        # Vaciar la lista
        list_of_word_appearences = []

    # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
    if gender_points >=  list_minimum_appearences:
        answer = element[1][5]
    else:
        answer = "NULL"
        
    # Devolver el contenido completo del resultado de la fase de validación
    if answer == "NULL":
        # Primer elemento
        correct_message = {
            "Correctas.": count_correct
        }
        # Segundo elemento
        incorrect_message_1 = {
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": count_incorrect_1
        }
        # Tercer elemento
        incorrect_message_2 = {
            "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": count_incorrect_2
        }
        # Cuarto elemento
        incorrect_message_3 = {
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": count_incorrect_3
        }
        # Quinto elemento
        information_message = {
            "Mensaje de información" : message
        }
        result = [answer, correct_message, incorrect_message_1, incorrect_message_2, incorrect_message_3, information_message]
    else:
        result = [answer]
    return result