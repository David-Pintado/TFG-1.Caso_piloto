import random

class ComponenteImporter:
    
    def __init__(self, spa_variant_file, spa_synset_file, eng_synset_file, most_used_words_file):
        self.spa_variant_file = spa_variant_file 
        self.spa_synset_file = spa_synset_file
        self.eng_synset_file = eng_synset_file
        self.most_used_words_file = most_used_words_file

    # Método para generar el 'source_information'
    # Esta estructura será un diccionario, la cual seguirá el siguiente esquema: 
    # Key=offset_word. Value = gloss, sense, part_of_speech, language
    def generate_data_structure(self):
        source_information = {}
        offsets_glosses_array = {}
        words_set = {}
        
        # Leer el archivo de las 1000 palabras más usadas y almacenar las palabras en un conjunto
        try:
            with open(self.most_used_words_file, "r", encoding="utf-8") as most_used_words_file:
                words_set = set(most_used_words_file.read().split())
                
        except FileNotFoundError:
            print(f'Archivo "{self.most_used_words_file}" no encontrado. Vuelve a introducir una nueva ruta') 
            
        # Leer el archivo que contiene los synset en español y almacenarlo en un diccionario llamado offsets_glosses_array
        # El esquema de este es: Key=offset. Value = gloss
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
                    offsets_glosses_array[synset[0]] = synset[6]
        except FileNotFoundError:
            print(f'Archivo "{self.spa_synset_file}" no encontrado. Vuelve a introducir una nueva ruta')
        
        # Leer el archivo que contiene los variant en español y almacenarlo en un diccionario llamado source_information
        # El esquema de este es: Key=offset_word. Value = sense, part_of_speech, language
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
                        # Añadimos al diccionario: Key=word. Value = [synset, sense, part_of_speech, language]
                        source_information[offset_word] = [sense, part_of_speech, language]
                        
        except FileNotFoundError:
            print(f'Archivo "{self.spa_variant_file}" no encontrado. Vuelve a introducir una nueva ruta')   
          
        # Modificar el source_information añadiendo los glosses del offsets_glosses_array
        # El esquema del source_information será:  Key=offset_word. Value = sense, gloss, part_of_speech, language
        for word, element in source_information.items(): 
            item_list = []
            item_list = [element[0], offsets_glosses_array[word.split('_')[0]].replace('_',' '), element[1], element[2]]
            source_information[word] = item_list
        
        return source_information

    # Método para generar el data_structure del mcr en ingles. De esta manera las glosses que no tenga el de castellano
    # se conseguirán de aquí, siendo traducidos por un modelo de lenguaje.
    def generate_eng_data_structure(self):
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
            print(f'Archivo "{self.spa_synset_file}" no encontrado. Vuelve a introducir una nueva ruta')
        
        return eng_data_structure   

    # Método para guardar un archivo json en la ruta proporcionada
    def save_json(self, file_path, json):
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json)