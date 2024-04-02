

import json
from configparser import ConfigParser
import re
import sys
sys.path.append("./auxFunctionLibrary")

from componente1 import Componente1
import componente2
from componente3 import Componente3
import componente4
from componente5 import Componente5
from componente6 import Componente6


def knowledge_exploitation():
    
    config = ConfigParser()
    config.read('./config.ini')
    
    # Ruta del archivo donde escribir la estructura de datos 'source_information'
    file_path_source_information_json = config['file_path']['source_information']
    
    # Ruta del archivo donde escribir la estructura de datos 'source_gloss_structure_eng'
    file_path_source_gloss_structure_eng = config['file_path']['source_gloss_structure_eng']
    
    # Inicializamos el componente1 para importar los datos de las fuentes 
    componente1 = Componente1(config['file_path']['word_mcr_file'], config['file_path']['synset_mcr_file'], config['file_path']['synset_eng_mcr_file'], config['file_path']['500_most_used_words_spa_file'])
    
    # Inicializamos el componente3 con el llm que vamos a utilizar para conseguir las respuestas provisionales
    componente3_provisional = Componente3(config['file_path']['provisional_answers_language_model_path'])
    
    # Cargamos el modelo de lenguaje que vamos a utilizar para conseguir las respuestas provisionales
    componente3_provisional.load_model()
    
    # Generar la estructura de datos con la que realizar el proceso de explotación de conocimiento
    source_information = componente1.generate_data_structure()
    
    # Creamos la estructura de datos que guardará el conocimiento que se haya explotado en los modelos de lenguaje, 
    # junto con la información extraída de la(s) fuente(s).
    exploited_information = {}
    
    # Generar la estructura de datos en ingles para poder conseguir sus glosses 
    source_gloss_structure_eng = componente1.generate_eng_data_structure()
    
    # Recorrer el 'source_information', para ver que si no tiene el gloss (está NULL) accder al de
    # 'source_gloss_structure_eng' y traducirlo
    for offset_word, element in source_information.items():
        if element[1] == 'NULL':
            offset = offset_word.split('_')[0]
            eng_gloss = source_gloss_structure_eng[offset]
            llm_answer = componente3_provisional.run_the_model('Como experto en traducción, cual es la traducción de la siguiente frase en ingles al español : "' + eng_gloss +'"?  Responde solamente con la traducción.')
            spa_gloss = componente4.extract_llm_answers(llm_answer).replace("\\", "").replace("\"", "")
            spa_gloss = spa_gloss.strip().split("\n")[0]
            if ": " in spa_gloss and ": " not in eng_gloss:
                spa_gloss = spa_gloss.split(': ')[1]
            source_information[offset_word] = [element[0], spa_gloss.capitalize(), element[2], element[3]]
            
    
    # Explotar conocimiento (Al parecer da problemas si se cargan dos modelos a la vez, 
    # ya que ocupa demasiada memoria y ralentiza el proceso de forma importante)
    # Es por ello que se recorrerá el source_information dos veces:
    #     La primera para conseguir las respuesta provisionales, y para validar las que tienen 'Neutro' como resultado provisional
    #     La segunda para validar las que tienen el valor del resultado provisional 'Femenino' o 'Masculino'
    
    for (offset_word,attributes) in source_information.items():
        llm_extracted_provisional_answers_list = []  
        llm_extracted_final_answers_list = []
        provisional_answer = ""
        final_answer = ""
        
        # (respuesta provisional)
        provisional_prompt_list = componente2.generate_provisional_prompts((offset_word,attributes))
        word = offset_word.split('_')[1]
        for prompt in provisional_prompt_list:
            # Reallizar la pregunta al modelo de lenguaje 
            llm_answer = componente3_provisional.run_the_model(prompt)
            # Extraer la parte de la respuesta para su posterior tratado
            llm_extracted_answer = componente4.extract_llm_answers(llm_answer)
            # Añadir la lista de las respuestas al data structure
            llm_extracted_provisional_answers_list.append(llm_extracted_answer)
        # Conseguir la respuesta provisional en base a lo devuelto por el modelo de lenguaje
        provisional_answer = componente4.get_provisional_answer3(word,llm_extracted_provisional_answers_list)
            
        # Añadirlo al source_information
        item_list = [attributes[0], attributes[1], attributes[2], attributes[3], llm_extracted_provisional_answers_list, provisional_answer]
        exploited_information[offset_word] = item_list
        
    componente3_provisional.llm = None
        
    # Inicializamos el componente3 con el llm que vamos a utilizar para validar las respuestas provisionales
    componente3_final = Componente3(config['file_path']['final_answers_language_model_path'])
    
    # Cargamos el modelo de lenguaje que vamos a utilizar para validar las respuestas provisionales
    componente3_final.load_model()    
    
    for (offset_word,attributes) in source_information.items():    
        # (validacion de 'Femenino' o 'Masculino')
        final_answer = ""
        llm_extracted_final_answers_list = []
        word = offset_word.split('_')[1]
        if attributes[4] == "Femenino" or attributes[4] == "Masculino":
            final_prompt_list = componente2.generate_validation_prompts((offset_word,attributes), attributes[5])
            
            for prompt in final_prompt_list:
                # Reallizar la pregunta al modelo de lenguaje 
                llm_answer = componente3_final.run_the_model(prompt)
                # Extraer la parte de la respuesta para su posterior tratado
                llm_extracted_answer = componente4.extract_llm_answers(llm_answer)
                # Añadir la lista de las respuestas al data structure
                llm_extracted_final_answers_list.append(llm_extracted_answer)
            
            # Inicializamos la clase 5 con los datos necesarios
            componente5 = Componente5(len(attributes[4][0]))
            # Conseguir la respuesta provisional en base a lo devuelto por el modelo de lenguaje
            final_answer = componente5.get_final_answer(word, llm_extracted_final_answers_list, attributes[5])

            
        answer = ""
        if final_answer == "":
            answer = attributes[5]
        else:
            answer = final_answer
        
        # Añadirlo al exploited_information
        item_list = [attributes[0], attributes[1], attributes[2], attributes[3], answer]
        exploited_information[offset_word] = item_list
    
    # Generamos un JSON con la estructura de datos, para una mejor visualizacion
    json_exploited_information = json.dumps(exploited_information, indent=2, ensure_ascii=False)
    
    # Generamos un JSON con la estructura de datos en ingles, para una mejor visualizacion
    json_source_gloss_structure_eng = json.dumps(source_gloss_structure_eng, indent=2, ensure_ascii=False)
    
    # Guardar el 'source_information' en formato json en un archivo    
    componente1.save_json(file_path_source_information_json,json_exploited_information)
    
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