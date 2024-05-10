

class ComponenteExporter:
    
    def __init__(self, exploited_information_file_path):
        self.exploited_information_file_path = exploited_information_file_path

    def export_knowledge(self, exploited_information):
        
        with open(self.exploited_information_file_path, 'w', encoding='utf-8') as f:
            for (offset_word,attributes) in exploited_information.items():
                
                # Extraccion de los elementos que van a formar parte de la exportacion
                offset_word_splitted = offset_word.split('_')
                offset = offset_word_splitted[0]
                word = offset_word_splitted[1]
                sense = attributes[0]
                gloss = attributes[1]
                part_of_speech = attributes[2]
                language = attributes[3]
                knowledge = attributes[4]
                final_element = "------"
                
                # Almacenar los valores entre comillas en una lista
                valores_con_comillas = [f'"{offset}"', f'"{word}"', f'"{sense}"', f'"{gloss}"', f'"{part_of_speech}"', f'"{language}"', f'"{knowledge}"', f'"{final_element}"']

                # Unir los valores con comas
                line = ', '.join(valores_con_comillas) + ",\n"
                f.write(line)