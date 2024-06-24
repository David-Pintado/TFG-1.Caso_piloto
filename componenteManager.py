

import json
from configparser import ConfigParser
import re
import sys
sys.path.append("./auxFunctionLibrary")
from componenteImporter import ComponenteImporter
import componenteQuestionMaker
from componenteLLMCommunicator import ComponenteLLMCommunicator
import componenteExtractor
import componenteValidator
from componenteExporter import ComponenteExporter


def knowledge_exploitation():
    
    config = ConfigParser()
    config.read('./config.ini')
    
    # Ruta del archivo donde escribir la estructura de datos 'source_information'
    file_path_source_information_json = config['file_path']['source_information']
    
    # Ruta del archivo donde escribir la estructura de datos 'source_gloss_structure_eng'
    file_path_source_gloss_structure_eng = config['file_path']['source_gloss_structure_eng']
    
    # Inicializamos el ComponenteImporter para importar los datos de las fuentes 
    componenteImporter = ComponenteImporter(config['file_path']['spa_variant_file'], config['file_path']['spa_synset_file'], config['file_path']['eng_synset_file'], config['file_path']['first_500_most_used_words_spa_file'])
    
    # Inicializamos el componenteLLMCommunicator con el llm que vamos a utilizar para conseguir las respuestas provisionales
    componenteLLMCommunicator_provisional = ComponenteLLMCommunicator(config['file_path']['provisional_results_language_model_path'])
    
    # Cargamos el modelo de lenguaje que vamos a utilizar para conseguir las respuestas provisionales
    componenteLLMCommunicator_provisional.load_model()
    
    # Generar la estructura de datos con la que realizar el proceso de explotación de conocimiento
    source_information = componenteImporter.generate_data_structure()
    
    # Generar la estructura de datos en ingles para poder conseguir sus glosses 
    source_gloss_structure_eng = componenteImporter.generate_eng_data_structure()
    
    # Recorrer el 'source_information', para ver que si no tiene el gloss (está NULL) accder al de
    # 'source_gloss_structure_eng' y traducirlo
    for offset_word, element in source_information.items():
        if element[1] == 'NULL':
            offset = offset_word.split('_')[0]
            eng_gloss = source_gloss_structure_eng[offset]
            llm_answer = componenteLLMCommunicator_provisional.run_the_model('Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: "' + eng_gloss +'".')
            spa_gloss = componenteExtractor.extract_llm_answers(llm_answer)
            source_information[offset_word] = [element[0], spa_gloss, element[2], element[3]]
            
    
    # Explotar conocimiento (Al parecer da problemas si se cargan dos modelos a la vez, 
    # ya que ocupa demasiada memoria y ralentiza el proceso de forma importante)
    # Es por ello que se recorrerá el source_information dos veces:
    #     La primera para conseguir las respuesta provisionales, y para validar las que tienen 'Neutro' como resultado provisional
    #     La segunda para validar las que tienen el valor del resultado provisional 'Femenino' o 'Masculino'
    
    for (offset_word,attributes) in source_information.items():
        llm_extracted_provisional_results_list = []  
        llm_extracted_final_results_list = []
        provisional_result = ""
        final_result = ""
        
        # (respuesta provisional)
        provisional_prompt_list = componenteQuestionMaker.generate_provisional_prompts((offset_word,attributes))
        for prompt in provisional_prompt_list:
            # Reallizar la pregunta al modelo de lenguaje 
            llm_answer = componenteLLMCommunicator_provisional.run_the_model(prompt)
            # Extraer la parte de la respuesta para su posterior tratado
            llm_extracted_answer = componenteExtractor.extract_llm_answers(llm_answer)
            # Añadir la lista de las respuestas al data structure
            llm_extracted_provisional_results_list.append(llm_extracted_answer)
        # Conseguir el resultado provisional en base a lo devuelto por el modelo de lenguaje
        provisional_result = componenteExtractor.get_provisional_result4((offset_word,attributes),llm_extracted_provisional_results_list)   
        # Añadirlo al source_information
        if len(provisional_result) == 1:  
            item_list = [attributes[0], attributes[1], attributes[2], attributes[3], llm_extracted_provisional_results_list, provisional_result[0]]
            source_information[offset_word] = item_list 
        elif len(provisional_result) == 6:
            item_list = [attributes[0], attributes[1], attributes[2], attributes[3], llm_extracted_provisional_results_list, provisional_result[0], provisional_result[1], provisional_result[2], provisional_result[3], provisional_result[4], provisional_result[5]]
            source_information[offset_word] = item_list
        
    componenteLLMCommunicator_provisional.llm = None
        
    # Inicializamos el componenteLLMCommunicator con el llm que vamos a utilizar para validar las respuestas provisionales
    componenteLLMCommunicator_final = ComponenteLLMCommunicator(config['file_path']['final_results_language_model_path'])
    
    # Cargamos el modelo de lenguaje que vamos a utilizar para validar las respuestas provisionales
    componenteLLMCommunicator_final.load_model()    
    
    for (offset_word,attributes) in source_information.items():    
        # (validacion de 'Femenino' o 'Masculino')
        final_result = ""
        llm_extracted_final_results_list = []
        if attributes[5] == "Femenino" or attributes[5] == "Masculino":
            final_prompt_list = componenteQuestionMaker.generate_validation_prompts((offset_word,attributes), attributes[5])
            
            for prompt in final_prompt_list:
                # Reallizar la pregunta al modelo de lenguaje 
                llm_answer = componenteLLMCommunicator_final.run_the_model(prompt)
                # Extraer la parte de la respuesta para su posterior tratado
                llm_extracted_answer = componenteExtractor.extract_llm_answers(llm_answer)
                # Añadir la lista de las respuestas al data structure
                llm_extracted_final_results_list.append(llm_extracted_answer)
            
            # Conseguir el resultado provisional en base a lo devuelto por el modelo de lenguaje
            final_result = componenteValidator.get_final_result((offset_word,attributes), llm_extracted_final_results_list, attributes[5])
            
            if len(final_result) == 1:  
                item_list = [attributes[0], attributes[1], attributes[2], attributes[3], attributes[4], attributes[5], llm_extracted_final_results_list, final_result[0]]
                source_information[offset_word] = item_list
            elif len(final_result) == 6:
                item_list = [attributes[0], attributes[1], attributes[2], attributes[3], attributes[4], attributes[5], llm_extracted_final_results_list, final_result[0], final_result[1], final_result[2], final_result[3], final_result[4], final_result[5]]
                source_information[offset_word] = item_list
    
    # Generamos un JSON con la estructura de datos, para una mejor visualizacion
    json_source_information = json.dumps(source_information, indent=2, ensure_ascii=False)
    
    # Generamos un JSON con la estructura de datos en ingles, para una mejor visualizacion
    json_source_gloss_structure_eng = json.dumps(source_gloss_structure_eng, indent=2, ensure_ascii=False)
    
    # Guardar el 'source_information' en formato json en un archivo    
    componenteImporter.save_json(file_path_source_information_json,json_source_information)
    
    # Guardar el 'source_gloss_structure_eng' en formato json en un archivo    
    componenteImporter.save_json(file_path_source_gloss_structure_eng,json_source_gloss_structure_eng)
    
    return source_information

def knowledge_exploitation_process():
    
    config = ConfigParser()
    config.read('./config.ini')
    
    print('Knowledge exploitation process STARTED')
    source_information = knowledge_exploitation() 
    print('Knowledge exploitation process FINISHED')
    
    # Inicializamos la clase para con la ruta del archivo a exportar
    componenteExporter = ComponenteExporter(config['file_path']['exploited_information_file_path'])
    
    print('Knowledge export process STARTED')
    componenteExporter.export_knowledge(source_information)
    print('Knowledge export process FINISHED')


if __name__ == "__main__":
    knowledge_exploitation_process()