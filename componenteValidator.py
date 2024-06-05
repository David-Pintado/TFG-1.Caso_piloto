
import re
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions
from unidecode import unidecode
from nltk.tokenize import RegexpTokenizer

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
                - ["Masculino"]: La palabra es de género masculino
                - ["Femenino"]: La palabra es de género femenino
                - ["NULL", errores, mensajes]: No se ha conseguido encontrar el género de la palabra
        """
        
        # Inicializamos las variables necesarias
        # Crear la lista del contenido completo del final_answer
        final_answer = []
        # Crear el mensaje de información del estado de la entrada: 
        #   - Si es NULL, no se ha podido obtner un resultado a partir de la entrada, y la ejecución queda en provisional
        #       message: "La entrada ha terminado su ejecución en la validación de la respuesta provisional"
        #   - Si no es NULL, no se añade ningún mensaje
        message = "La entrada ha terminado su ejecución en la validación de la respuesta provisional."
        # Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.
        count_error_1 = 0
        # Error 2: La palabra que buscamos no aparece en la frase.
        count_error_2 = 0
        # Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
        count_error_3 = 0
        gender_points = 0
        word = element[0].split('_')[1]
        plural_word = auxFunctions.pluralize_word(word)
        word_appearence = ""
        answer = ""
        gender_terms = []
        # Crear un tokenizador personalizado con una expresión regular
        tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')
        if provisional_answer.lower() == "femenino":
            gender_terms = ['la', 'las', 'una', 'unas','esa', 'esta', 'esas', 'estas', 'otra', 'otras']
        elif provisional_answer.lower() == "masculino":
            gender_terms = ['el', 'del', 'los', 'un', 'unos', 'al', 'ese', 'este', 'esos', 'estos', 'otro', 'otros']
            
        # Si las listas de conseguir la respuesta provisionale tienen menos frases, se acorta la lista a la cantidad mínima de frases
        llm_extracted_answer_list[0] = llm_extracted_answer_list[0][:self.minimun_number_of_sentences]
        list_minimum_appearences = 3
        
        # Contamos las apariciones de las palabras y articulos para saber su genero
        for phrase in llm_extracted_answer_list[0]:
            # Si tenemos una lista en vez de frases las tratamos quedandonos con el primero elemento / frase de las listas
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
                word_position_list = list(position for (noun, position, _, _) in nouns_with_positions if noun in list_of_word_appearences)
                if len(word_position_list) >= 1:
                    word_position = word_position_list[0]
                    new_phrase = auxFunctions.destokenize(tokenize_phrase[:word_position])
                    search_article_phrase = new_phrase.strip().split(' ')
                    if len(search_article_phrase) == 1:
                        if search_article_phrase[-1].lower() in gender_terms:  # Comparar en minúsculas para hacerlo insensible a mayúsculas/minúsculas
                            gender_points += 1
                        elif search_article_phrase[-1].lower() in gender_terms:
                            gender_points += 0.5
                        else:
                            # Sumar Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                            count_error_3 += 1
                    elif len(search_article_phrase) > 1:
                        reversed_search_article_phrase = search_article_phrase[::-1][:2]
                        if reversed_search_article_phrase[0].lower() in gender_terms:
                            gender_points += 1
                        elif reversed_search_article_phrase[1].lower() in gender_terms:
                            gender_points += 0.5
                        else:
                            # Sumar Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.
                            count_error_3 += 1
                else:
                    # Sumar Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase. en caso de que no haya nouns
                    count_error_1 += 1
            else:
                # Sumamos a Error 2: La palabra que buscamos no aparece en la frase.
                count_error_2 += 1
            # Vaciar la lista
            list_of_word_appearences = []

        if (self.minimun_number_of_sentences+1) >= len(llm_extracted_answer_list[0]) >= (self.minimun_number_of_sentences-1):
            # Calculamos la diferencia maxima que pueden tener los distintos generos en base a la longitud de la lamina de pruebas 
            if gender_points >=  list_minimum_appearences:
                answer = provisional_answer
            else:
                answer = "NULL"
        else: 
            answer = "NULL"
            # Devolver el contenido completo de la respuesta provisional
        if answer == "NULL":
            # Crea el segundo elemento como un diccionario
            error_message_1 = {
                "Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": count_error_1
            }
            # Crea el tercer elemento como un diccionario
            error_message_2 = {
                "Error 2: La palabra que buscamos no aparece en la frase.": count_error_2
            }
            # Crea el cuarto elemento como un diccionario
            error_message_3 = {
                "Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": count_error_3
            }
            # Crea el quinto elemento como un diccionario
            information_message = {
                "Mensaje de información" : message
            }
            final_answer = [answer, error_message_1, error_message_2, error_message_3, information_message]
        else:
            final_answer = [answer]
        return final_answer