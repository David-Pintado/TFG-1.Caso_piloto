import random

class ComponenteImporter:
    
    def __init__(self, spa_variant_file, spa_synset_file, eng_synset_file, most_used_words_file):
        self.spa_variant_file = spa_variant_file 
        self.spa_synset_file = spa_synset_file
        self.eng_synset_file = eng_synset_file
        self.most_used_words_file = most_used_words_file


    def generate_data_structure(self):
        
        """
        Método para generar una estructura de datos del WordNet en castellano.
           
            Parámetros:
                - self: instancia de la clase que contiene este método.

            Retorna:
                - knowledge_table (dict): Un diccionario que contiene los datos necesarios del WordNet en castellano
                                          para llevar a cabo el proceso de explotación de conocimiento en LLMs
                        - key: offset_word
                        - attributes: [sense, gloss, part_of_speech, language]
        """
        
        knowledge_table = {}
        offsets_glosses_array = {}
        words_set = {}
        count = 0
        
        # Leer el archivo de las 1000 palabras más usadas y almacenar las palabras en un conjunto
        try:
            with open(self.most_used_words_file, "r", encoding="utf-8") as most_used_words_file:
                words_set = set(most_used_words_file.read().split())
                
        except FileNotFoundError:
            print(f'Archivo "{self.most_used_words_file}" no encontrado. Vuelve a introducir una nueva ruta') 
            
        # Leer el archivo que contiene los synset en español y almacenarlo en un diccionario auxiliar
        # llamado offsets_glosses_array. El esquema que sigue es: Key=offset. Value = [gloss]
        try:
            # Intentar abrir el archivo que se encuentra en la ruta proporcionada
            with open(self.spa_synset_file, 'r', encoding="utf-8") as archivo:
                # Recorremos cada línea
                for linea in archivo:
                    # Obtenemos una lista en la que cada elemento es una columna del synset
                    linea = linea.replace('"', '')
                    # Eliminamos las comillas de los elemento
                    synset = linea.strip().split(',')
                    # Añadimos a la lista una tupla (offset, gloss)
                    gloss = synset[6]
                    # Tratar el gloss
                    if gloss != "NULL":
                        if ":" in gloss:
                            gloss = gloss.split(':')[0]
                        gloss = gloss.strip().capitalize()
                        if not gloss.endswith('.'):
                            gloss += '.'
                    offsets_glosses_array[synset[0]] = gloss
        except FileNotFoundError:
            print(f'Archivo "{self.spa_synset_file}" no encontrado. Vuelve a introducir una nueva ruta')
        
        # Leer el archivo que contiene los variant en español y almacenarlo en un diccionario llamado knowledge_table
        # El esquema que sigue es: Key=offset_word. Value = [sense, part_of_speech, language]
        try:
            # Intentar abrir el archivo que se encuentra en la ruta proporcionada
            with open(self.spa_variant_file, 'r', encoding="utf-8") as archivo:
                # Recorremos cada línea
                for linea in archivo:
                    # Obtenemos una lista en la que cada elemento es una columna del synset
                    linea = linea.replace('"', '')
                    # Eliminamos las comillas de los elemento
                    synset = linea.strip().split(',')
                    # Obtenemos la palabra
                    word = synset[0]
                    # Si es una palabra compuesta eliminamos la barra baja ( '_' )
                    word = word.replace('_', ' ')
                    # Obtenemos el sense (sentido: indice de tasa de ocurrencia de la palabra en el synset)
                    sense = synset[1]
                    # Obtenemos el offset
                    offset = synset[2]
                    # Tipo de la palabra
                    part_of_speech = synset[3]
                    # Idioma del synset
                    language = offset.split('-')[0]
                    # Clave compuesta (offset_word)
                    offset_word = offset + '_' + word
                    # Si es un synset en español y el tipo de palabra es sustantivo (noun=n)
                    if language == "spa" and part_of_speech == "n" and word in words_set:

                        # # Generar un número aleatorio entre 1 y 10
                        # numero_aleatorio = random.randint(1, 10)

                        # # Verificar si el número aleatorio es 1
                        # if numero_aleatorio == 10:
                        # Añadimos al diccionario: Key=word. Value = [synset, sense, part_of_speech, language]
                        knowledge_table[offset_word] = [sense, part_of_speech, language]
                    #     count += 1
                    # if count > 19:
                    #     break
                        
        except FileNotFoundError:
            print(f'Archivo "{self.spa_variant_file}" no encontrado. Vuelve a introducir una nueva ruta')   
          
        # Definir los atributos de element que tienen un valor por defecto al inicio del proceso
        extraction_llm_answers = {
            "Extraction LLM answers": []
        }
        validation_llm_answers = {   
            "Validation LLM answers": []
        }
        extraction_gender = {
            "Extraction gender": "NULL"
        }
        validation_gender = {
            "Validation gender": "NULL"
        }  
        correct_phrases = {
            "Correctas": 0
        }
        incorrect_phrases_1 = {
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0
        }
        incorrect_phrases_2 = {
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0
        }
        incorrect_phrases_3 = {
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0
        }
        information_message = {
            "Mensaje de información": "NULL"
        }

        # Modificar el knowledge_table añadiendo los glosses del offsets_glosses_array
        # Sigue el siguiente esquema:  Key=offset_word. Value= [sense_index, gloss, part_of_speech, language, extraction_llm_answers, validation_llm_answers, extraction_gender, validation_gender, correct_phrases, incorrect_phrases_1, incorrect_phrases_2, incorrect_phrases_3, information_message]
        for word, element in knowledge_table.items():
            sense_index = element[0]
            gloss = offsets_glosses_array[word.split('_')[0]].replace('_', ' ')
            part_of_speech = element[1]
            language = element[2]
            
            # Crear el nuevo formato de diccionario
            item_dict = {
                "Sense index": sense_index,
                "Gloss": gloss,
                "Part of speech": part_of_speech,
                "Language": language,
                "Extraction LLM answers": extraction_llm_answers["Extraction LLM answers"],
                "Validation LLM answers": validation_llm_answers["Validation LLM answers"],
                "Extraction gender": extraction_gender["Extraction gender"],
                "Validation gender": validation_gender["Validation gender"],
                "Correctas": correct_phrases["Correctas"],
                "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": incorrect_phrases_1["Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase"],
                "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": incorrect_phrases_2["Incorrectas de tipo 2: la palabra a analizar no aparece en la frase"],
                "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": incorrect_phrases_3["Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género"],
                "Mensaje de información": information_message["Mensaje de información"]
            }
            
            # Actualizar el knowledge_table con el nuevo formato
            knowledge_table[word] = item_dict

        return knowledge_table

    def generate_eng_data_structure(self):
        
        """
        Método para generar una estructura de datos del WordNet en inglés.
           
            Parámetros:
                - self: instancia de la clase que contiene este método.

            Retorna:
                - eng_data_structure (dict): Un diccionario que contiene las glosas en inglés asociadas a cada synset.
                        Los 'keys' son los offsets modificados ('eng' por 'spa') y los valores (attributes)
                        son las glosas en inglés.
        """
          
        eng_data_structure = {}
        try:
            # Intentar abrir el archivo que se encuentra en la ruta proporcionada
            with open(self.eng_synset_file, 'r', encoding="utf-8") as archivo:
                # Recorremos cada línea
                for linea in archivo:
                    # Obtenemos una lista en la que cada elemento es una columna del synset
                    linea = linea.replace('"', '')
                    # Eliminamos las comillas de los elemento
                    synset = linea.strip().split(',')
                    # Añadimos a la lista una tupla (offset, gloss)
                    eng_data_structure[synset[0].replace('eng','spa')] = synset[6]
        except FileNotFoundError:
            print(f'Archivo "{self.eng_synset_file}" no encontrado. Vuelve a introducir una nueva ruta')
        
        return eng_data_structure   