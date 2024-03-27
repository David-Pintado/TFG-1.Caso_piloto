import random

class Componente1:
    
    def __init__(self, word_mcr_file, synset_mcr_file, synset_eng_mcr_file):
        self.word_mcr_file = word_mcr_file 
        self.synset_mcr_file = synset_mcr_file
        self.synset_eng_mcr_file = synset_eng_mcr_file

    # Método para generar el 'source_information_structure'
    # Esta estructura será un diccionario, la cual tendrá: Key=offset_word. Value = gloss, sense, part_of_speech, language
    def generate_data_structure(self):
        source_information_structure = {}
        offsets_glosses_array = {}
        count = 0
        try:
            # Intentar abrir el archivo que se encuentra en la ruta proporcionada
            with open(self.word_mcr_file, 'r', encoding="utf-8") as archivo:
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
                    if language == "spa" and part_of_speech == "n":
                        # Añadimos al diccionario: Key=word. Value = [synset, sense, part_of_speech, language]
                        # if round(random.random()*10) == 10:
                        source_information_structure[offset_word] = [sense, part_of_speech, language]
                        count += 1
                    if count > 0:
                        break
                        
        except FileNotFoundError:
            print(f'Archivo "{self.word_mcr_file}" no encontrado. Vuelve a introducir una nueva ruta')   
            
        try:
            # Intentar abrir el archivo que se encuentra en la ruta proporcionada
            with open(self.synset_mcr_file, 'r', encoding="utf-8") as archivo:
                # Recorremos cada línea
                for linea in archivo:
                    # Obtenemos una lista en la que cada elemento es una columna del synset
                    linea = linea.replace('"', '')
                    # Eliminamos las comillas de los elemento
                    synset = linea.strip().split(',')
                    # Añadimos a la lista una tupla (offset, gloss)
                    offsets_glosses_array[synset[0]] = synset[6]
        except FileNotFoundError:
            print(f'Archivo "{self.synset_mcr_file}" no encontrado. Vuelve a introducir una nueva ruta')
            
        for word, element in source_information_structure.items(): 
            item_list = []
            item_list = [element[0], offsets_glosses_array[word.split('_')[0]].replace('_',' '), element[1], element[2]]
            source_information_structure[word] = item_list
        
        return source_information_structure

    # Método para generar el data_structure del mcr en ingles. De esta manera las glosses que no tenga el de castellano
    # se conseguirán de aquí, siendo traducidos por un modelo de lenguaje.
    def generate_eng_data_structure(self):
        eng_data_structure = {}
        try:
            # Intentar abrir el archivo que se encuentra en la ruta proporcionada
            with open(self.synset_eng_mcr_file, 'r', encoding="utf-8") as archivo:
                # Recorremos cada línea
                for linea in archivo:
                    # Obtenemos una lista en la que cada elemento es una columna del synset
                    linea = linea.replace('"', '')
                    # Eliminamos las comillas de los elemento
                    synset = linea.strip().split(',')
                    # Añadimos a la lista una tupla (offset, gloss)
                    eng_data_structure[synset[0].replace('eng','spa')] = synset[6]
        except FileNotFoundError:
            print(f'Archivo "{self.synset_mcr_file}" no encontrado. Vuelve a introducir una nueva ruta')
        
        return eng_data_structure   

    # Método para guardar un archivo json en la ruta proporcionada
    def save_json(self, file_path, json):
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json)