
import re
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions
from unidecode import unidecode

class ComponenteValidator:
    
    def __init__(self, minimun_number_of_sentences):
        self.minimun_number_of_sentences = minimun_number_of_sentences 

    def get_final_answer(self, element, llm_extracted_answer_list, provisional_answer):
        
        """Función para la respuesta final al conocimiento a obtener en base a una palabra y una lista de frases
        con la palabra en el género de provisional_answer
        
        Parámetros:
            - element = Elemento de la estructura de datos source_information, compuesto por key + attributes
            - llm_extracted_answer_list (list) = Lista que se compone de una lista
                            - Contiene frases con la palabra en género provisional_answer
        Retorna:
            - final_answer (string)
                    - "Masculino": La palabra es de género masculino
                    - "Femenino": La palabra es de género femenino
                    - "NULL": No se ha validado. provisional_answer y final_answer son distintos
        """
        
        # Inicializamos las variables necesarias
        gender_points = 0
        word = element[0].split('_')[1]
        plural_word = auxFunctions.pluralize_word(word)
        word_appearence = ""
        final_answer = ""
        gender_terms = []
        if provisional_answer.lower() == "femenino":
            gender_terms = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
        elif provisional_answer.lower() == "masculino":
            gender_terms = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
            
        # Si las listas de conseguir la respuesta provisionale tienen menos frases, se acorta la lista a la cantidad mínima de frases
        llm_extracted_answer_list[0] = llm_extracted_answer_list[0][:self.minimun_number_of_sentences]
        list_minimum_appearences = len(llm_extracted_answer_list[0]) * 0.7
        
        # Contamos las apariciones de las palabras y articulos para saber su genero
        for element in llm_extracted_answer_list[0]:
            word_appearence = ""
            element_copy = str(element)  # Crear una copia de element
            for item in plural_word:
                pattern = r'\b' + re.escape(unidecode(item)) + r'(?=[^\w]|$)'
                match = re.search(pattern, unidecode(element_copy))
                if match:
                    word_appearence = element_copy[match.start():match.end()]
                    break
            if word_appearence != "":
                search_article_phrase = element.split(word_appearence)[0].strip().split(' ')
                if len(search_article_phrase) == 1:
                    if search_article_phrase[-1].lower() in gender_terms:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                        gender_points += 1
                    elif search_article_phrase[-1].lower() in gender_terms:
                        gender_points += 0.5
                elif len(search_article_phrase) > 1:
                    reversed_search_article_phrase = search_article_phrase[::-1][:2]
                    if reversed_search_article_phrase[0].lower() in gender_terms:
                        gender_points += 1
                    elif reversed_search_article_phrase[1].lower() in gender_terms:
                        gender_points += 0.5

        if len(llm_extracted_answer_list[0]) >= self.minimun_number_of_sentences:
            # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
            if gender_points >=  list_minimum_appearences:
                final_answer = provisional_answer
            else:
                final_answer = "NULL"
        else: 
            final_answer = "NULL"
        
        return final_answer