
import re
from itertools import product

def extract_llm_answers(llm_answer):

    # Extraer el texto devuelto
    return_answer_value = llm_answer['choices'][0]['text']
    # Dividirlo en dos partes (la parte de la pregunta, la parte de la respuesta)
    llm_extracted_answer = return_answer_value.split('Answer:')[1]


    return llm_extracted_answer


def pluralize_word(word):
    """Función para obtener la forma plural de una palabra (En el caso de que esta sea plural, devolverá su plural)
       En el caso de que la palabra sea compuesta, devolverá las permutaciones plurales de esa palabra en español
       
       Parámetros:
        - word (string)= Palabra a pluralizar (Puede ser simple o compuesta)
        
       Retorna:
        - pluralize_word_list (Array<string>)
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
    pluralize_word_list = []
    for permutation in composite_permutations:
        pluralize_word_list.append(" ".join(permutation))

    return pluralize_word_list


def get_preliminar_answer(word, llm_prompt_asnwer_list):
    
    """Función para la respuesta preliminar al conocimiento a obtener en base a una palabra y una lista de frases
       con la palabra en varios géneros
    
       Parámetros:
        - word (string)= Palabra que se analiza en busca del conocimiento (género en este caso)
        - llm_prompt_asnwer_list (list) = Lista que se compone de dos listas de misma longud
                        - La primera contiene frases con la palabra en género maculino
                        - La segunda contiene frases con la palabra en género femenino
       Retorna:
        - preliminar_answer (string)
                - "Neutro": La palabra es de género neutro
                - "Masculino": La palabra es de género masculino
                - "Femenino": La palabra es de género femenino
                - "NULL": No se ha conseguido encontrar el género de la palabra
    """
    
    # Inicializamos las variables necesarias
    count_masculino = 0
    count_femenino = 0
    plural_word = pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    preliminar_answer = ""
    max_difference = len(llm_prompt_asnwer_list[0])-round((len(llm_prompt_asnwer_list[0])*2)/3) + 1
    list_minimum_appearences = len(llm_prompt_asnwer_list[0]) * 0.8
    array_fem = ['la','las','una','unas']
    array_mas = ['el', 'del', 'los', 'un', 'unos', 'al']
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_prompt_asnwer_list[0]:
        male_word_appearence = ""
        for item in plural_word:
            pattern = r'\b' + re.escape(item) + r'(?=[^\w]|$)'
            if re.search(pattern, element):
                count_masculino += 1
                male_word_appearence = item
                break
        if male_word_appearence != "":
            search_article_phrase = element.split(male_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_mas:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_masculino += 1
                elif search_article_phrase[-1].lower() in array_fem:
                    count_femenino += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:4]
                for reversed_element in reversed_search_article_phrase:
                    if reversed_element.lower() in array_mas:
                        count_masculino += 1
                        break
                    elif reversed_element.lower() in array_fem:
                        count_femenino += 1
                        break
    for element in llm_prompt_asnwer_list[1]:
        female_word_appearence = ""
        for item in plural_word:
            pattern = r'\b' + re.escape(item) + r'(?=[^\w]|$)'
            if re.search(pattern, element):
                count_femenino += 1
                female_word_appearence = item
                break
        if female_word_appearence != "":
            search_article_phrase = element.split(female_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_mas:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_masculino += 1
                elif search_article_phrase[-1].lower() in array_fem:
                    count_femenino += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:4]
                for reversed_element in reversed_search_article_phrase:
                    if reversed_element.lower() in array_mas:
                        count_masculino += 1
                        break
                    elif reversed_element.lower() in array_fem:
                        count_femenino += 1
                        break

    print(count_masculino)
    print(count_femenino)
    
    # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
    if 0 <= abs(count_masculino-count_femenino) <= max_difference and count_masculino > (list_minimum_appearences + max_difference) and count_femenino > (list_minimum_appearences + max_difference):
        preliminar_answer = "Neutro"
    elif 0 <= abs(count_masculino-count_femenino) <= max_difference and count_masculino > (list_minimum_appearences + max_difference):
        preliminar_answer = "Masculino"
    elif 0 <= abs(count_masculino-count_femenino) <= max_difference and count_femenino > (list_minimum_appearences + max_difference):
        preliminar_answer = "Femenino"
    elif 0 <= abs(count_masculino-count_femenino) <= max_difference and count_masculino <= (list_minimum_appearences + max_difference) and count_femenino <= (list_minimum_appearences + max_difference):
        preliminar_answer = "NULL"
    elif max_difference < abs(count_masculino-count_femenino):
        if count_masculino > count_femenino and count_masculino > (list_minimum_appearences + max_difference):
           preliminar_answer = "Masculino"
        elif count_femenino > count_masculino and count_femenino > (list_minimum_appearences + max_difference):
           preliminar_answer = "Femenino"
        else:
           preliminar_answer = "NULL"
    return preliminar_answer
    
