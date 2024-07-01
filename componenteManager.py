

import json
from configparser import ConfigParser
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions
from componenteImporter import ComponenteImporter
from componenteLLMCommunicator import ComponenteLLMCommunicator
import componenteQuestionMaker_extraccion
import componenteQuestionMaker_validacion
import componenteQuestionMaker_traduccion
import componenteExtractor_traduccionGlosa
import componenteExtractor_extraccion
import componenteExtractor_validacion
from componenteExporter import ComponenteExporter


def knowledge_exploitation_process():

    """
    Método para llevar a cabo el proceso completo de explotación de conocimiento en LLMs.
                    
        Retorna:
            - knowledge_table (dic): Diccionario que contiene el conocimiento extraído junto a otros atributos.
    """
    
    config = ConfigParser()
    config.read('./config.ini')
    
    print('Knowledge exploitation process STARTED')
    
    # Ruta del archivo donde escribir la estructura de datos 'knowledge_table'
    file_path_knowledge_table_json = config['file_path']['knowledge_table']
    
    # Ruta del archivo donde escribir la estructura de datos 'source_gloss_structure_eng'
    file_path_source_gloss_structure_eng = config['file_path']['source_gloss_structure_eng']
    
    # Componente Importer para importar los datos de las fuentes 
    componenteImporter = ComponenteImporter(config['file_path']['spa_variant_file'], config['file_path']['spa_synset_file'], config['file_path']['eng_synset_file'], config['file_path']['last_500_most_used_words_spa_file'])
    
    # Componente LLMCommunicator de la fase de extraccion
    componenteLLMCommunicator_extraccion = ComponenteLLMCommunicator(config['file_path']['extraction_results_language_model_path'])
    
    # Carga del LLM de la fase de extraccion
    componenteLLMCommunicator_extraccion.load_model()
    
    # Estructura de datos con la que realizar el proceso de explotación de conocimiento
    knowledge_table = componenteImporter.generate_data_structure()
    
    # Estructura de datos en ingles para poder conseguir sus glosas 
    source_gloss_structure_eng = componenteImporter.generate_eng_data_structure()
    
    # Recorrer el 'knowledge_table', para ver que si no tiene el gloss (NULL) acceder al de 'source_gloss_structure_eng' 
    # y traducirlo
    for (offset_word, attributes) in knowledge_table.items():
        if attributes[1] == 'NULL':
            offset = offset_word.split('_')[0]
            eng_gloss = source_gloss_structure_eng[offset]
            attributes[1] = eng_gloss
            prompt_translation_list = componenteQuestionMaker_traduccion.generate_prompts((offset_word, attributes))
            llm_answer = componenteLLMCommunicator_extraccion.run_the_model(prompt_translation_list[0])
            spa_gloss = componenteExtractor_traduccionGlosa.get_result(None, [llm_answer])
            knowledge_table[offset_word] = [attributes[0], spa_gloss, attributes[2], attributes[3]]         
    
    # Explotar conocimiento. Se recorre dos veces el knowledge_table para evitar que la carga 
    # consecutiva de dos LLM ocupe demasiada memoria y ralentize el proceso:
    #     Para conseguir los resultados de la fase de extracción
    #     Para validar las que tengan como resultado de la fase de extracción 'Femenino' o 'Masculino'
    
    for (offset_word,attributes) in knowledge_table.items():
        llm_answer_list = []
        prompt_list = componenteQuestionMaker_extraccion.generate_prompts((offset_word,attributes))
        for prompt in prompt_list:
            # Realizar la pregunta al modelo de lenguaje 
            llm_answer_list.append(componenteLLMCommunicator_extraccion.run_the_model(prompt))
        # Resultado de la fase de extraccion
        result = componenteExtractor_extraccion.get_result((offset_word,attributes),llm_answer_list)   
        # Añadirlo al knowledge_table
        if len(result) == 1:  
            item_list = [attributes[0], attributes[1], attributes[2], attributes[3], llm_answer_list, result[0]]
            knowledge_table[offset_word] = item_list 
        elif len(result) == 6:
            item_list = [attributes[0], attributes[1], attributes[2], attributes[3], llm_answer_list, result[0], result[1], result[2], result[3], result[4], result[5]]
            knowledge_table[offset_word] = item_list
        
    # Eliminar el LLM de la fase de extracción
    componenteLLMCommunicator_extraccion.llm = None
        
    # Componente LLMCommunicator de la fase de validación
    componenteLLMCommunicator_validacion = ComponenteLLMCommunicator(config['file_path']['validation_language_model_path'])
    
    # Carga del LLM de la fase de validación
    componenteLLMCommunicator_validacion.load_model()    
    
    for (offset_word,attributes) in knowledge_table.items(): 
        llm_answer_list = []
        if attributes[5] == "Femenino" or attributes[5] == "Masculino":
            prompt_list = componenteQuestionMaker_validacion.generate_prompts((offset_word,attributes))
            
            for prompt in prompt_list:
                # Reallizar la pregunta al modelo de lenguaje 
                llm_answer = llm_answer_list.append(componenteLLMCommunicator_validacion.run_the_model(prompt))
            
            # Conseguir el resultado de la fase de validación
            result = componenteExtractor_validacion.get_result((offset_word,attributes), llm_answer_list)
            
            if len(result) == 1:  
                item_list = [attributes[0], attributes[1], attributes[2], attributes[3], attributes[4], attributes[5], llm_answer_list, result[0]]
                knowledge_table[offset_word] = item_list
            elif len(result) == 6:
                item_list = [attributes[0], attributes[1], attributes[2], attributes[3], attributes[4], attributes[5], llm_answer_list, result[0], result[1], result[2], result[3], result[4], result[5]]
                knowledge_table[offset_word] = item_list
                
    print('Knowledge exploitation process FINISHED')
    
    # Generamos un JSON con la estructura de datos, para una mejor visualizacion
    json_knowledge_table = json.dumps(knowledge_table, indent=2, ensure_ascii=False)
    
    # Generar un JSON con la estructura de datos en ingles, para una mejor visualizacion
    json_source_gloss_structure_eng = json.dumps(source_gloss_structure_eng, indent=2, ensure_ascii=False)
    
    # Guardar el 'knowledge_table' en formato json en un archivo    
    auxFunctions.save_json(file_path_knowledge_table_json,json_knowledge_table)
    
    # Guardar el 'source_gloss_structure_eng' en formato json en un archivo    
    auxFunctions.save_json(file_path_source_gloss_structure_eng,json_source_gloss_structure_eng)
    
    # Inicializar la instancia del Componente Exporter con la ruta del archivo a exportar
    componenteExporter = ComponenteExporter(config['file_path']['exploited_information_file_path'])
    
    # Realizar la exportación
    print('Knowledge export process STARTED')
    componenteExporter.export_knowledge(knowledge_table)
    print('Knowledge export process FINISHED')
    
    return knowledge_table


if __name__ == "__main__":
    knowledge_exploitation_process()