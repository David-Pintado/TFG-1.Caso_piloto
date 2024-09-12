

class ComponenteExporter:
    
    def __init__(self, knowledge_table_file_path):
        self.knowledge_table_file_path = knowledge_table_file_path

    def export_knowledge(self, knowledge_table):
            
        """
        Método para exportar los resultados almacenados en `knowledge_table` a un archivo específico.

            Parámetros:
                - self: instancia de la clase que contiene este método.
                - knowledge_table (dict): Un diccionario que contiene la información a exportar, compuesto por key + attributes.
            Retorna:
                - None: Este método no retorna ningún valor, pero crea un fichero con los datos del proceso.

        """
        
        with open(self.knowledge_table_file_path, 'w', encoding='utf-8') as f:
            for (offset_word,attributes) in knowledge_table.items():
                
                # Extraccion de los elementos que van a formar parte de la exportacion
                offset_word_splitted = offset_word.split('_')
                offset = offset_word_splitted[0]
                word = offset_word_splitted[1]
                sense_index = attributes["Sense index"]
                gloss = attributes["Gloss"]
                part_of_speech = attributes["Part of speech"]
                language = attributes["Language"]
                gender = attributes["Validation gender"]
                final_element = "------"
                
                # Almacenar los valores entre comillas en una lista
                valores_con_comillas = [f'"{offset}"', f'"{word}"', f'"{sense_index}"', f'"{gloss}"', f'"{part_of_speech}"', f'"{language}"', f'"{gender}"', f'"{final_element}"']

                # Unir los valores con comas
                line = ', '.join(valores_con_comillas) + ",\n"
                f.write(line)