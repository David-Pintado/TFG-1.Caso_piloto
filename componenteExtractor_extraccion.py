
import re
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions
from unidecode import unidecode
from nltk.tokenize import RegexpTokenizer

def extract_llm_answers(llm_answer):
    
    """Función para extraer la respuesta del LLM. Si en la respuesta hay separadores de oraciones forma una lista con todas ellas.
        Si no contiene separadores, (es una única frase) devuelve un solo String
    
        Parámetros:
            - llm_answer = Respuesta del LLM sin tratar
        Retorna:
            - llm_extracted_answer (Lista o String). Respuesta del LLM extraída. 
            
    """

    # Extraer el texto devuelto
    return_answer_value = llm_answer['choices'][0]['text']
    # Dividirlo en dos partes (la parte de la pregunta, la parte de la respuesta)
    llm_extracted_answer = return_answer_value.split('Answer:')[1]
    # Eliminar los saltos de linea
    llm_extracted_answer = llm_extracted_answer.replace('\n',' ').replace('\n\n',' ').strip()
    # Comprabar si tiene separadores de frases. Si no tiene es que es una traduccion
    if(re.split(r'\d+\)|\d+\.', llm_extracted_answer)[1:] != [] and (len(re.split(r'\d+\)|\d+\.', llm_extracted_answer)) >= 4)):    
        # Dividir el texto en frases utilizando cualquier secuencia de un número seguido de un punto como criterio de separación
        llm_extracted_answer = re.split(r'\d+\)|\d+\.', llm_extracted_answer)[1:]
        # Quitar los espacios blancos del principio y final de las frases 
        llm_extracted_answer = [answer.strip() + '.' if not answer.strip().endswith('.') else answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("\"", "").replace('\\', '').replace("\\\"", "") for answer in llm_extracted_answer]
        return llm_extracted_answer
    # Comprobar si tiene más de una frase. En ese caso puede que no tenga separadores pero que sean un conjunto de frases
    elif(len(llm_extracted_answer.split('. ')) >= 4):
        # Compilar la expresión regular directamente sin escapar
        llm_extracted_answer = [phrase for phrase in llm_extracted_answer.split('. ')]
        # Quitar los espacios blancos del principio y final de las frases 
        llm_extracted_answer = [answer.strip() + '.' if not answer.strip().endswith('.') else answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("\"", "").replace('\\', '').replace("\\\"", "") for answer in llm_extracted_answer]
        return llm_extracted_answer
    # Comprobar si tiene más de una frase (; ). En ese caso puede que no tenga separadores pero que sean un conjunto de frases
    elif(len(llm_extracted_answer.split('; ')) >= 4):
        # Compilar la expresión regular directamente sin escapar
        llm_extracted_answer = [phrase for phrase in llm_extracted_answer.split('; ')]
        # Quitar los espacios blancos del principio y final de las frases 
        llm_extracted_answer = [answer.strip() + '.' if not answer.strip().endswith('.') else answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("\"", "").replace('\\', '').replace("\\\"", "") for answer in llm_extracted_answer]
        return llm_extracted_answer
    # Si es una traducción tratarla
    if type(llm_extracted_answer) is list:
        if len(llm_extracted_answer) > 0:
            llm_extracted_answer = llm_extracted_answer[0]
        elif len(llm_extracted_answer) == 0:
            llm_extracted_answer = ""
    llm_extracted_answer = llm_extracted_answer.split(". ")[0].strip()
    llm_extracted_answer = llm_extracted_answer.strip().replace('"', '').replace("\"", "").replace('\\', '').replace("\\\"", "").capitalize()
    if not llm_extracted_answer.endswith('.'):
        llm_extracted_answer += '.'
    print(llm_extracted_answer)
    return llm_extracted_answer


def get_result(element, llm_answer_list):
    
    """Función para el obtener el resultado (género de las palabras) de la fase de extracción.
    
       Parámetros:
        - element = Elemento de la estructura de datos knowledge_table, compuesto por key + attributes
        - llm_answer_list (list) = Lista que se compone de respuestas del LLM que necesitan ser extraídas
       Retorna:
        - result (Lista)
                - ["Masculino"]: La palabra es de género masculino
                - ["Femenino"]: La palabra es de género femenino
                - ["NULL", correctas, tipos_incorrectas, mensajes]: No se ha conseguido encontrar el género de la palabra
    """
    
    # Lista de respuesta extraídas del LLM
    llm_extracted_answer_list = []
    for llm_answer in llm_answer_list:
        llm_extracted_answer_list.append(extract_llm_answers(llm_answer))

    # Mensaje de información del estado de la entrada: 
    message = "La entrada ha terminado su ejecución en la extracción del resultado provisional."
    # Correctas: Frases correctas en las que se suman puntos.
    count_correct = 0
    # Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.
    count_incorrect_1 = 0
    # Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.
    count_incorrect_2 = 0
    # Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
    count_incorrect_3 = 0
    # Variables de puntuación de las dos categorías
    count_male = 0
    count_female = 0
    # Palabra
    word = element[0].split('_')[1]
    # Lista de plurales de 'word'. Incluye la forma singular
    plural_word = auxFunctions.pluralize_word(word)
    # Resultado de la fase
    answer = ""
    # Resultado del método
    result = []
    # Umbral general 
    max_difference = 3
    # Umbral por categorías
    list_minimum_appearences = 3
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
    
    # Tokenizador personalizado con una expresión regular
    tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')
    
    for phrase in llm_extracted_answer_list[0]:
        if type(phrase) is list:
            phrase = phrase[0]
        phrase = phrase.lower()
        tokenize_phrase = tokenizer.tokenize(phrase)
        male_word_appearence = ""
        list_of_male_word_appearences = []
        phrase_copy = str(phrase)  # Crear una copia de phrase
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(phrase_copy))
            if match:
                male_word_appearence = phrase_copy[match.start():match.end()]
                list_of_male_word_appearences.append(male_word_appearence)
        if len(list_of_male_word_appearences) != 0:
            nouns_with_positions = auxFunctions.extract_nouns_with_positions(phrase)
            word_position_list = list(position for (noun, position, _, _) in nouns_with_positions if noun in list_of_male_word_appearences)
            if len(word_position_list) >= 1:
                word_position = word_position_list[0]
                new_phrase = auxFunctions.destokenize(tokenize_phrase, tokenize_phrase[:word_position])
                search_article_phrase = new_phrase.strip().split(' ')
                if len(search_article_phrase) == 1:
                    if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                        count_male += 1
                        count_correct += 1
                    elif search_article_phrase[-1].lower() in array_female:
                        count_male += -1
                        count_correct += 1
                    else:
                        # Sumar Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                        count_incorrect_3 += 1                  
                elif len(search_article_phrase) > 1:
                    reversed_search_article_phrase = search_article_phrase[::-1][:2]
                    if reversed_search_article_phrase[0].lower() in array_male:
                        count_correct += 1
                        count_male += 1
                    elif reversed_search_article_phrase[1].lower() in array_male:
                        count_correct += 1
                        count_male += 0.5
                    elif reversed_search_article_phrase[0].lower() in array_female:
                        count_correct += 1
                        count_male += -1
                    elif reversed_search_article_phrase[1].lower() in array_female:
                        count_correct += 1
                        count_male += -0.5
                    else:
                        # Sumar Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                        count_incorrect_3 += 1
            else:
                # Sumar Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase. en caso de que no haya nouns
                count_incorrect_1 += 1
        else:
            # Sumamos a Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.
            count_incorrect_2 += 1
        # Vaciar la lista
        list_of_male_word_appearences = []
    for phrase in llm_extracted_answer_list[1]:
        if type(phrase) is list:
            phrase = phrase[0]
        phrase = phrase.lower()
        tokenize_phrase = tokenizer.tokenize(phrase)
        female_word_appearence = ""
        list_of_female_word_appearences = []
        phrase_copy = str(phrase)  # Crear una copia de phrase
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(phrase_copy))
            if match:
                female_word_appearence = phrase_copy[match.start():match.end()]
                list_of_female_word_appearences.append(female_word_appearence)
        if len(list_of_female_word_appearences) != 0:
            nouns_with_positions = auxFunctions.extract_nouns_with_positions(phrase)
            word_position_list = list(position for (noun, position, _, _) in nouns_with_positions if noun in list_of_female_word_appearences)
            if len(word_position_list) >= 1:
                word_position = word_position_list[0]
                new_phrase = auxFunctions.destokenize(tokenize_phrase, tokenize_phrase[:word_position])
                search_article_phrase = new_phrase.strip().split(' ')
                if len(search_article_phrase) == 1:
                    if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                        count_female += -1
                        count_correct += 1
                    elif search_article_phrase[-1].lower() in array_female:
                        count_correct += 1
                        count_female += 1
                    else:
                        # Sumar Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                        count_incorrect_3 += 1
                elif len(search_article_phrase) > 1:
                    reversed_search_article_phrase = search_article_phrase[::-1][:2]
                    if reversed_search_article_phrase[0].lower() in array_male:
                        count_correct += 1
                        count_female += -1
                    elif reversed_search_article_phrase[1].lower() in array_male:
                        count_correct += 1
                        count_female += -0.5
                    elif reversed_search_article_phrase[0].lower() in array_female:
                        count_correct += 1
                        count_female += 1
                    elif reversed_search_article_phrase[1].lower() in array_female:
                        count_correct += 1
                        count_female += 0.5
                    else:
                        # Sumar Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                        count_incorrect_3 += 1
            else:
                # Sumar Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase. en caso de que no haya nouns
                count_incorrect_1 += 1
        else:
            # Sumamos a Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.
            count_incorrect_2 += 1
        # Vaciar la lista
        list_of_female_word_appearences = []
    
    # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
    if count_male >=  list_minimum_appearences and 0 <= max_difference <= abs(count_male-count_female) and count_male > count_female:
        answer = "Masculino"
    elif count_female >=  list_minimum_appearences and 0 <= max_difference <= abs(count_male-count_female) and count_female > count_male:
        answer = "Femenino"
    else: 
        answer = "NULL"
    # Contenido completo del resultado de la fase de extracción
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