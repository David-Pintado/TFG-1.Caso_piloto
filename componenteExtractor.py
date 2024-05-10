
import re
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions
from unidecode import unidecode

def extract_llm_answers(llm_answer):

    # Extraer el texto devuelto
    return_answer_value = llm_answer['choices'][0]['text']
    # Dividirlo en dos partes (la parte de la pregunta, la parte de la respuesta)
    llm_extracted_answer = return_answer_value.split('Answer:')[1]
    # Eliminar los saltos de linea
    llm_extracted_answer = llm_extracted_answer.replace('\n',' ').strip()
    # Comprabar si tiene separadores de frases. Si no tiene es que es una traduccion
    if(re.split(r'\d+\)|\d+\.', llm_extracted_answer)[1:] != []):    
        # Dividir el texto en frases utilizando cualquier secuencia de un número seguido de un punto como criterio de separación
        llm_extracted_answer = re.split(r'\d+\)|\d+\.', llm_extracted_answer)[1:]
        # Quitar los espacios blancos del principio y final de las frases 
        llm_extracted_answer = [answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("\"", "").replace('\\', '').replace("\\\"", "") for answer in llm_extracted_answer]

    return llm_extracted_answer


def get_provisional_answer(element, llm_extracted_answer_list):
    
    """Función para la respuesta provisional al conocimiento a obtener en base a una palabra y una lista de frases
       con la palabra en varios géneros
    
       Parámetros:
        - element = Elemento de la estructura de datos source_information, compuesto por key + attributes
        - llm_extracted_answer_list (list) = Lista que se compone de dos listas de misma longud
                        - La primera contiene frases con la palabra en género maculino
                        - La segunda contiene frases con la palabra en género femenino
       Retorna:
        - provisional_answer (string)
                - "Masculino": La palabra es de género masculino
                - "Femenino": La palabra es de género femenino
                - "NULL": No se ha conseguido encontrar el género de la palabra
    """
    # Inicializamos las variables necesarias
    count_male = 0
    count_female = 0
    word = element[0].split('_')[1]
    plural_word = auxFunctions.pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    provisional_answer = ""
    max_difference = len(llm_extracted_answer_list[0])-round((len(llm_extracted_answer_list[0])*2)/3) + 1
    list_minimum_appearences = len(llm_extracted_answer_list[0]) * 0.8
    array_female = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
    array_male = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_extracted_answer_list[0]:
        male_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                male_word_appearence = element_copy[match.start():match.end()]
                break
        if male_word_appearence != "":
            search_article_phrase = element.split(male_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_male += 1
                elif search_article_phrase[-1].lower() in array_female:
                    count_female += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:4]
                for reversed_element in reversed_search_article_phrase:
                    if reversed_element.lower() in array_male:
                        count_male += 1
                        break
                    elif reversed_element.lower() in array_female:
                        count_female += 1
                        break
    for element in llm_extracted_answer_list[1]:
        female_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                female_word_appearence = element_copy[match.start():match.end()]
                break
        if female_word_appearence != "":
            search_article_phrase = element.split(female_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_male += 1
                elif search_article_phrase[-1].lower() in array_female:
                    count_female += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:4]
                for reversed_element in reversed_search_article_phrase:
                    if reversed_element.lower() in array_male:
                        count_male += 1
                        break
                    elif reversed_element.lower() in array_female:
                        count_female += 1
                        break

    # print(' ')
    # print('Puntos masculinos: ')
    # print(count_male) 
    # print(' ')
    # print('Puntos femeninos')
    # print(count_female)
    # print(' ')
    # print('Umbral para categoría (Femenino o masculino han de superar el umbral para obtener la respuesta): ')
    # print(list_minimum_appearences)
    # print('Umbra general (La diferencia entre las categorías tiene que superar este umbral para obtener un género): ')
    # print(max_difference)
    
    # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
    if count_male >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_male > count_female:
        provisional_answer = "Masculino"
    elif count_female >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_female > count_male:
        provisional_answer = "Femenino"
    else:
        provisional_answer = "NULL"
    return provisional_answer
    
# ///////////////////////////////////////////////////////////////////////////////////

def get_provisional_answer2(element, llm_extracted_answer_list):
    
    # Inicializamos las variables necesarias
    count_male = 0
    count_female = 0
    word = element[0].split('_')[1]
    plural_word = auxFunctions.pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    provisional_answer = ""
    list_minimum_appearences = len(llm_extracted_answer_list[0])/2
    max_difference = list_minimum_appearences/2
    array_female = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
    array_male = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_extracted_answer_list[0]:
        male_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                male_word_appearence = element_copy[match.start():match.end()]
                break
        if male_word_appearence != "":
            search_article_phrase = element.split(male_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_male += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_male:
                    count_male += 1
                elif reversed_search_article_phrase[1].lower() in array_male:
                    count_male += 0.5
    for element in llm_extracted_answer_list[1]:
        female_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                female_word_appearence = element_copy[match.start():match.end()]
                break
        if female_word_appearence != "":
            search_article_phrase = element.split(female_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_female:
                    count_female += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_female:
                    count_female += 1
                elif reversed_search_article_phrase[1].lower() in array_female:
                    count_female += 0.5

    # print(' ')
    # print('Puntos masculinos: ')
    # print(count_male) 
    # print(' ')
    # print('Puntos femeninos')
    # print(count_female)
    # print(' ')
    # print('Umbral para categoría (Femenino o masculino han de superar el umbral para obtener la respuesta): ')
    # print(list_minimum_appearences)
    # print('Umbra general (La diferencia entre las categorías tiene que superar este umbral para obtener un género): ')
    # print(max_difference)

    if count_male >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_male > count_female:
        provisional_answer = "Masculino"
    elif count_female >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_female > count_male:
        provisional_answer = "Femenino"
    else:
        provisional_answer = "NULL"
    return provisional_answer

def get_provisional_answer3(element, llm_extracted_answer_list):
    
    """Función para la respuesta provisional al conocimiento a obtener en base a una palabra y una lista de frases
       con la palabra en varios géneros
    
       Parámetros:
        - element = Elemento de la estructura de datos source_information, compuesto por key + attributes
        - llm_extracted_answer_list (list) = Lista que se compone de dos listas de misma longud
                        - La primera contiene frases con la palabra en género maculino
                        - La segunda contiene frases con la palabra en género femenino
       Retorna:
        - provisional_answer (string)
                - "Neutro": La palabra es de género neutro
                - "Masculino": La palabra es de género masculino
                - "Femenino": La palabra es de género femenino
                - "NULL": No se ha conseguido encontrar el género de la palabra
    """
    
    # Inicializamos las variables necesarias
    count_male = 0
    count_female = 0
    word = element[0].split('_')[1]
    plural_word = auxFunctions.pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    provisional_answer = ""
    max_difference = len(llm_extracted_answer_list[0])-round((len(llm_extracted_answer_list[0])*2)/3) + 1
    list_minimum_appearences = len(llm_extracted_answer_list[0]) * 0.8
    array_female = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
    array_male = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
    
    # Si una lista tiene más frases en un género que en otro, se acorta la lista a la cantidad mínima de frases
    minimun_number_of_sentences = min(len(llm_extracted_answer_list[0]), len(llm_extracted_answer_list[1]))
    maximun_number_of_sentences = max(len(llm_extracted_answer_list[0]), len(llm_extracted_answer_list[1]))
    llm_extracted_answer_list[0] = llm_extracted_answer_list[0][:minimun_number_of_sentences]
    llm_extracted_answer_list[1] = llm_extracted_answer_list[1][:minimun_number_of_sentences]
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_extracted_answer_list[0]:
        male_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                male_word_appearence = element_copy[match.start():match.end()]
                break
        if male_word_appearence != "":
            search_article_phrase = element.split(male_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_male += 1
                elif search_article_phrase[-1].lower() in array_female:
                    count_female += 0.5
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_male:
                    count_male += 1
                elif reversed_search_article_phrase[1].lower() in array_male:
                    count_male += 0.5
                elif reversed_search_article_phrase[0].lower() in array_female:
                    count_female += 0.5
                elif reversed_search_article_phrase[1].lower() in array_female:
                    count_female += 0.25
    for element in llm_extracted_answer_list[1]:
        female_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                female_word_appearence = element_copy[match.start():match.end()]
                break
        if female_word_appearence != "":
            search_article_phrase = element.split(female_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_male += 0.5
                elif search_article_phrase[-1].lower() in array_female:
                    count_female += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_male:
                    count_male += 0.5
                elif reversed_search_article_phrase[1].lower() in array_male:
                    count_male += 0.25
                elif reversed_search_article_phrase[0].lower() in array_female:
                    count_female += 1
                elif reversed_search_article_phrase[1].lower() in array_female:
                    count_female += 0.5

    # print(' ')
    # print('Puntos masculinos: ')
    # print(count_male) 
    # print(' ')
    # print('Puntos femeninos')
    # print(count_female)
    # print(' ')
    # print('Umbral para categoría (Femenino o masculino han de superar el umbral para obtener la respuesta): ')
    # print(list_minimum_appearences)
    # print('Umbra general (La diferencia entre las categorías tiene que superar este umbral para obtener un género): ')
    # print(max_difference)
    
    if len(llm_extracted_answer_list[0]) > 0 and len(llm_extracted_answer_list[0]) >= maximun_number_of_sentences/2:
        # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
        if count_male >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_male > count_female:
            provisional_answer = "Masculino"
        elif count_female >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_female > count_male:
            provisional_answer = "Femenino"
        else: 
            provisional_answer = "NULL"
    else:
        provisional_answer = "NULL"
    return provisional_answer


def get_provisional_answer4(element, llm_extracted_answer_list):
    
    """Función para la respuesta provisional al conocimiento a obtener en base a una palabra y una lista de frases
       con la palabra en varios géneros
    
       Parámetros:
        - element = Elemento de la estructura de datos source_information, compuesto por key + attributes
        - llm_extracted_answer_list (list) = Lista que se compone de dos listas de misma longud
                        - La primera contiene frases con la palabra en género maculino
                        - La segunda contiene frases con la palabra en género femenino
       Retorna:
        - provisional_answer (string)
                - "Masculino": La palabra es de género masculino
                - "Femenino": La palabra es de género femenino
                - "NULL": No se ha conseguido encontrar el género de la palabra
    """
    
    # Inicializamos las variables necesarias
    count_male = 0
    count_female = 0
    word = element[0].split('_')[1]
    plural_word = auxFunctions.pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    provisional_answer = ""
    max_difference = len(llm_extracted_answer_list[0])-round((len(llm_extracted_answer_list[0])*2)/3) + 1
    list_minimum_appearences = len(llm_extracted_answer_list[0]) * 0.8
    array_female = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
    array_male = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
    
    # Si una lista tiene más frases en un género que en otro, se acorta la lista a la cantidad mínima de frases
    minimun_number_of_sentences = min(len(llm_extracted_answer_list[0]), len(llm_extracted_answer_list[1]))
    maximun_number_of_sentences = max(len(llm_extracted_answer_list[0]), len(llm_extracted_answer_list[1]))
    llm_extracted_answer_list[0] = llm_extracted_answer_list[0][:minimun_number_of_sentences]
    llm_extracted_answer_list[1] = llm_extracted_answer_list[1][:minimun_number_of_sentences]
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_extracted_answer_list[0]:
        male_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                male_word_appearence = element_copy[match.start():match.end()]
                break
        if male_word_appearence != "":
            search_article_phrase = element.split(male_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_male += 1
                elif search_article_phrase[-1].lower() in array_female:
                    count_male += -1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_male:
                    count_male += 1
                elif reversed_search_article_phrase[1].lower() in array_male:
                    count_male += 0.5
                elif reversed_search_article_phrase[0].lower() in array_female:
                    count_male += -1
                elif reversed_search_article_phrase[1].lower() in array_female:
                    count_male += -0.5
    for element in llm_extracted_answer_list[1]:
        female_word_appearence = ""
        element_copy = str(element)  # Crear una copia de element
        for item in plural_word:
            pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
            match = re.search(pattern, unidecode(element_copy))
            if match:
                female_word_appearence = element_copy[match.start():match.end()]
                break
        if female_word_appearence != "":
            search_article_phrase = element.split(female_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_male:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_female += -1
                elif search_article_phrase[-1].lower() in array_female:
                    count_female += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_male:
                    count_female += -1
                elif reversed_search_article_phrase[1].lower() in array_male:
                    count_female += -0.5
                elif reversed_search_article_phrase[0].lower() in array_female:
                    count_female += 1
                elif reversed_search_article_phrase[1].lower() in array_female:
                    count_female += 0.5

    # print(' ')
    # print('Puntos masculinos: ')
    # print(count_male) 
    # print(' ')
    # print('Puntos femeninos')
    # print(count_female)
    # print(' ')
    # print('Umbral para categoría (Femenino o masculino han de superar el umbral para obtener la respuesta): ')
    # print(list_minimum_appearences)
    # print('Umbra general (La diferencia entre las categorías tiene que superar este umbral para obtener un género): ')
    # print(max_difference)
    
    if len(llm_extracted_answer_list[0]) > 0 and len(llm_extracted_answer_list[0]) >= maximun_number_of_sentences/2:
        # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
        if count_male >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_male > count_female:
            provisional_answer = "Masculino"
        elif count_female >=  list_minimum_appearences and 0 <= max_difference < abs(count_male-count_female) and count_female > count_male:
            provisional_answer = "Femenino"
        else: 
            provisional_answer = "NULL"
    else:
        provisional_answer = "NULL"
    return provisional_answer