
import re
from pythonLib import auxFunctions

def extract_llm_answers(llm_answer):

    # Extraer el texto devuelto
    return_answer_value = llm_answer['choices'][0]['text']
    # Dividirlo en dos partes (la parte de la pregunta, la parte de la respuesta)
    llm_extracted_answer = return_answer_value.split('Answer:')[1]
    # Eliminar los saltos de linea
    llm_extracted_answer = [llm_extracted_answer.replace('\n',' ').strip()]
    # Dividir el texto en frases utilizando cualquier secuencia de un número seguido de un punto como criterio de separación
    llm_extracted_answer = re.split(r'\d+\)|\d+\.', llm_extracted_answer[0])[1:]
    # Quitar los espacios blancos del principio y final de las frases 
    llm_extracted_answer = [answer.strip() for answer in llm_extracted_answer]
    # Quitar las comillas y barras de las frases
    llm_extracted_answer = [answer.replace('"', '').replace('\\', '') for answer in llm_extracted_answer]


    return llm_extracted_answer


def get_provisional_answer(word, llm_prompt_answer_list):
    
    """Función para la respuesta provisional al conocimiento a obtener en base a una palabra y una lista de frases
       con la palabra en varios géneros
    
       Parámetros:
        - word (string)= Palabra que se analiza en busca del conocimiento (género en este caso)
        - llm_prompt_answer_list (list) = Lista que se compone de dos listas de misma longud
                        - La primera contiene frases con la palabra en género maculino
                        - La segunda contiene frases con la palabra en género femenino
       Retorna:
        - provisional_answer (string)
                - "Masculino": La palabra es de género masculino
                - "Femenino": La palabra es de género femenino
                - "NULL": No se ha conseguido encontrar el género de la palabra
    """
    
    # Inicializamos las variables necesarias
    count_masculino = 0
    count_femenino = 0
    plural_word = auxFunctions.pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    provisional_answer = ""
    max_difference = len(llm_prompt_answer_list[0])-round((len(llm_prompt_answer_list[0])*2)/3) + 1
    list_minimum_appearences = len(llm_prompt_answer_list[0]) * 0.8
    array_fem = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
    array_mas = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_prompt_answer_list[0]:
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
    for element in llm_prompt_answer_list[1]:
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
    if count_masculino >=  list_minimum_appearences and 0 <= max_difference < abs(count_masculino-count_femenino) and count_masculino > count_femenino:
        provisional_answer = "Masculino"
    elif count_femenino >=  list_minimum_appearences and 0 <= max_difference < abs(count_masculino-count_femenino) and count_femenino > count_masculino:
        provisional_answer = "Femenino"
    else:
        provisional_answer = "NULL"
    return provisional_answer
    
# ///////////////////////////////////////////////////////////////////////////////////

def get_provisional_answer2(word, llm_prompt_answer_list):
    
    # Inicializamos las variables necesarias
    count_masculino = 0
    count_femenino = 0
    plural_word = auxFunctions.pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    provisional_answer = ""
    list_minimum_appearences = len(llm_prompt_answer_list[0])/2
    max_difference = list_minimum_appearences/2
    array_fem = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
    array_mas = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_prompt_answer_list[0]:
        male_word_appearence = ""
        for item in plural_word:
            pattern = r'\b' + re.escape(item) + r'(?=[^\w]|$)'
            if re.search(pattern, element):
                male_word_appearence = item
                break
        if male_word_appearence != "":
            search_article_phrase = element.split(male_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_mas:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_masculino += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_mas:
                    count_masculino += 1
                elif reversed_search_article_phrase[1].lower() in array_mas:
                    count_masculino += 0.5
    for element in llm_prompt_answer_list[1]:
        female_word_appearence = ""
        for item in plural_word:
            pattern = r'\b' + re.escape(item) + r'(?=[^\w]|$)'
            if re.search(pattern, element):
                female_word_appearence = item
                break
        if female_word_appearence != "":
            search_article_phrase = element.split(female_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_fem:
                    count_femenino += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_fem:
                    count_femenino += 1
                elif reversed_search_article_phrase[1].lower() in array_fem:
                    count_femenino += 0.5

    print(count_masculino)
    print(count_femenino)

    if count_masculino >=  list_minimum_appearences and 0 <= max_difference < abs(count_masculino-count_femenino) and count_masculino > count_femenino:
        provisional_answer = "Masculino"
    elif count_femenino >=  list_minimum_appearences and 0 <= max_difference < abs(count_masculino-count_femenino) and count_femenino > count_masculino:
        provisional_answer = "Femenino"
    else:
        provisional_answer = "NULL"
    return provisional_answer

def get_provisional_answer3(word, llm_prompt_answer_list):
    
    """Función para la respuesta provisional al conocimiento a obtener en base a una palabra y una lista de frases
       con la palabra en varios géneros
    
       Parámetros:
        - word (string)= Palabra que se analiza en busca del conocimiento (género en este caso)
        - llm_prompt_answer_list (list) = Lista que se compone de dos listas de misma longud
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
    count_masculino = 0
    count_femenino = 0
    plural_word = auxFunctions.pluralize_word(word)
    male_word_appearence = ""
    female_word_appearence = ""
    provisional_answer = ""
    max_difference = len(llm_prompt_answer_list[0])-round((len(llm_prompt_answer_list[0])*2)/3) + 1
    list_minimum_appearences = len(llm_prompt_answer_list[0]) * 0.8
    array_fem = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
    array_mas = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
    
    # Si una lista tiene más frases en un género que en otro, se acorta la lista a la cantidad mínima de frases
    minimun_number_of_sentences = min(len(llm_prompt_answer_list[0]), len(llm_prompt_answer_list[1]))
    maximun_number_of_sentences = max(len(llm_prompt_answer_list[0]), len(llm_prompt_answer_list[1]))
    llm_prompt_answer_list[0] = llm_prompt_answer_list[0][:minimun_number_of_sentences]
    llm_prompt_answer_list[1] = llm_prompt_answer_list[1][:minimun_number_of_sentences]
    
    # Contamos las apariciones de las palabras y articulos para saber su genero
    for element in llm_prompt_answer_list[0]:
        male_word_appearence = ""
        for item in plural_word:
            pattern = r'\b' + re.escape(item) + r'(?=[^\w]|$)'
            if re.search(pattern, element):
                male_word_appearence = item
                break
        if male_word_appearence != "":
            search_article_phrase = element.split(male_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_mas:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_masculino += 1
                elif search_article_phrase[-1].lower() in array_fem:
                    count_femenino += 0.5
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_mas:
                    count_masculino += 1
                elif reversed_search_article_phrase[1].lower() in array_mas:
                    count_masculino += 0.5
                elif reversed_search_article_phrase[0].lower() in array_fem:
                    count_femenino += 0.5
                elif reversed_search_article_phrase[1].lower() in array_fem:
                    count_femenino += 0.25
    for element in llm_prompt_answer_list[1]:
        female_word_appearence = ""
        for item in plural_word:
            pattern = r'\b' + re.escape(item) + r'(?=[^\w]|$)'
            if re.search(pattern, element):
                female_word_appearence = item
                break
        if female_word_appearence != "":
            search_article_phrase = element.split(female_word_appearence)[0].strip().split(' ')
            if len(search_article_phrase) == 1:
                if search_article_phrase[-1].lower() in array_mas:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                    count_masculino += 0.5
                elif search_article_phrase[-1].lower() in array_fem:
                    count_femenino += 1
            elif len(search_article_phrase) > 1:
                reversed_search_article_phrase = search_article_phrase[::-1][:2]
                if reversed_search_article_phrase[0].lower() in array_mas:
                    count_masculino += 0.5
                elif reversed_search_article_phrase[1].lower() in array_mas:
                    count_masculino += 0.25
                elif reversed_search_article_phrase[0].lower() in array_fem:
                    count_femenino += 1
                elif reversed_search_article_phrase[1].lower() in array_fem:
                    count_femenino += 0.5

    print(count_masculino)
    print(count_femenino)
    
    if len(llm_prompt_answer_list[0]) > 0 and len(llm_prompt_answer_list[0]) >= maximun_number_of_sentences/2:
        # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
        if count_masculino >=  list_minimum_appearences and 0 <= max_difference < abs(count_masculino-count_femenino) and count_masculino > count_femenino:
            provisional_answer = "Masculino"
        elif count_femenino >=  list_minimum_appearences and 0 <= max_difference < abs(count_masculino-count_femenino) and count_femenino > count_masculino:
            provisional_answer = "Femenino"
        else: 
            provisional_answer = "NULL"
    else:
        provisional_answer = "NULL"
    return provisional_answer