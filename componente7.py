

import json
from configparser import ConfigParser
import re

from componente1 import Componente1
import componente2
from componente3 import Componente3
import componente4
from componente6 import Componente6


def knowledge_exploitation():
    
    config = ConfigParser()
    config.read('./config.ini')
    
    # Ruta del archivo donde escribir la estructura de datos 'source_information_structure'
    file_path_source_information_structure_json = config['file_path']['source_information_structure']
    
    # Ruta del archivo donde escribir la estructura de datos 'source_gloss_structure_eng'
    file_path_source_gloss_structure_eng = config['file_path']['source_gloss_structure_eng']
    
    # Inicializamos la clase para importar los datos de las fuentes 
    componente1 = Componente1(config['file_path']['word_mcr_file'], config['file_path']['synset_mcr_file'], config['file_path']['synset_eng_mcr_file'])
    
    # Inicializamos la clase con el llm que vamos a utilizar
    componente3 = Componente3(config['file_path']['language_model_path'])
    
    # Cargamos el modelo de lenguaje
    componente3.load_model()
    
    # Generar la estructura de datos con la que realizar el proceso de explotación de conocimiento
    source_information_structure = componente1.generate_data_structure()
    
    # Creamos la estructura de datos que guardará el conocimiento que se haya explotado en los modelos de lenguaje, 
    # junto con la información extraída de la(s) fuente(s).
    exploited_information = {}
    
    # Generar la estructura de datos en ingles para poder conseguir sus glosses 
    source_gloss_structure_eng = componente1.generate_eng_data_structure()
    
    # Recorrer el 'source_information_structure', para ver que si no tiene el gloss (está NULL) accder al de
    # 'source_gloss_structure_eng' y traducirlo
    for offset_word, element in source_information_structure.items():
        if element[1] == 'NULL':
            offset = offset_word.split('_')[0]
            eng_gloss = source_gloss_structure_eng[offset]
            llm_answer = componente3.run_the_model('Como experto en traducción, cual es la traducción de la siguiente frase en ingles al español : "' + eng_gloss +'"?  Responde solamente con la traducción.')
            spa_gloss = componente4.extract_llm_answers(llm_answer).replace("\\", "").replace("\"", "")
            spa_gloss = spa_gloss.strip().split("\n")[0]
            if ": " in str and ": " not in eng_gloss:
                spa_gloss = spa_gloss.split(': ')[1]
            source_information_structure[offset_word] = [element[0], spa_gloss.capitalize(), element[2], element[3]]
            
    
    # Explotar conocimiento 
    for (offset_word,attributes) in source_information_structure.items():
        
        # (Preliminar)
        preliminar_prompt_list = componente2.generate_preliminar_prompts((offset_word,attributes))
        llm_extracted_answers_list = []
        word = offset_word.split('_')[1]
        for prompt in preliminar_prompt_list:
            # Reallizar la pregunta al modelo de lenguaje 
            llm_answer = componente3.run_the_model(prompt)
            # Extraer la parte de la respuesta para su posterior tratado
            llm_extracted_answer = componente4.extract_llm_answers(llm_answer)
            # Eliminar los saltos de linea
            llm_extracted_answer = [llm_extracted_answer.replace('\n',' ').strip()]
            # Dividir el texto en frases utilizando cualquier secuencia de un número seguido de un punto como criterio de separación
            llm_extracted_answer_list = re.split(r'\d+\.', llm_extracted_answer[0])[1:]
            # Quitar los espacios blancos del principio y final de las frases 
            llm_extracted_answer_list = [answer.strip() for answer in llm_extracted_answer_list]
            # Añadir la lista de las respuestas al data structure
            llm_extracted_answers_list.append(llm_extracted_answer_list)
        preliminar_answer = componente4.get_preliminar_answer(word,llm_extracted_answers_list)
        item_list = [attributes[0], attributes[1], attributes[2], attributes[3], llm_extracted_answers_list, preliminar_answer]
        exploited_information[offset_word] = item_list
    
    # Generamos un JSON con la estructura de datos, para una mejor visualizacion
    json_exploited_information = json.dumps(exploited_information, indent=2, ensure_ascii=False)
    
    # Generamos un JSON con la estructura de datos en ingles, para una mejor visualizacion
    json_source_gloss_structure_eng = json.dumps(source_gloss_structure_eng, indent=2, ensure_ascii=False)
    
    # Guardar el 'source_information_structure' en formato json en un archivo    
    componente1.save_json(file_path_source_information_structure_json,json_exploited_information)
    
    # Guardar el 'source_gloss_structure_eng' en formato json en un archivo    
    componente1.save_json(file_path_source_gloss_structure_eng,json_source_gloss_structure_eng)
    
    return exploited_information

def knowledge_exploitation_process():
    
    config = ConfigParser()
    config.read('./config.ini')
    
    print('Knowledge exploitation process STARTED')
    exploited_information = knowledge_exploitation() 
    print('Knowledge exploitation process FINISHED')
    
    # Inicializamos la clase para con la ruta del archivo a exportar
    componente6 = Componente6(config['file_path']['exploited_information_file_path'])
    
    print('Knowledge export process STARTED')
    componente6.export_knowledge(exploited_information)
    print('Knowledge export process FINISHED')


if __name__ == "__main__":
    knowledge_exploitation_process()