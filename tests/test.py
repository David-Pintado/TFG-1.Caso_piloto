

from io import StringIO
import json
from configparser import ConfigParser
import re
import sys
sys.path.append('..')  # Agrega la carpeta superior al sys.path
sys.path.append("../auxFunctionLibrary") #Agrega la carpeta superior al sys.path
from pythonLib import auxFunctions
from componenteImporter import ComponenteImporter
import componenteQuestionMaker_traduccion
import componenteQuestionMaker_extraccion
import componenteQuestionMaker_validacion
import componenteExtractor_traduccionGlosa
import componenteExtractor_extraccion
import componenteExtractor_validacion
from componenteLLMCommunicator import ComponenteLLMCommunicator
from componenteExporter import ComponenteExporter


def component_importer_test():
    
    config = ConfigParser()
    config.read('./config.ini')
    
    # Inicializamos el componenteImporter para importar los datos de las fuentes 
    component1 = ComponenteImporter(config['file_path']['spa_variant_file'], config['file_path']['spa_synset_file'], config['file_path']['eng_synset_file'], config['file_path']['words_spa_file'])
    
    # Guarda el flujo original de salida estándar
    stdout_orig = sys.stdout

    # Define un archivo para redirigir la salida estándar
    archivo_salida = open("./test.txt", "w")

    # Redirige la salida estándar al archivo
    sys.stdout = archivo_salida

    # Si el path no es correcto debe entrar en la excepcion
    component1_test = ComponenteImporter(config['file_path']['spa_variant_file'], config['file_path']['spa_synset_file'], config['file_path']['eng_synset_file'], config['file_path']['words_spa_file_test'])
    test_data_structure = component1_test.generate_data_structure()

    # Cierra el archivo
    archivo_salida.close()
    
    # Restaura la salida estándar
    sys.stdout = stdout_orig
    
    # Abre el archivo de salida en modo lectura
    with open("./test.txt", "r") as archivo:
        # Lee todas las líneas del archivo
        lines = archivo.readlines()

        # Itera sobre cada línea
        for line in lines:
            # Verifica si la línea contiene el mensaje que estás buscando
            if "Archivo \"./files/words1.txt\" no encontrado. Vuelve a introducir una nueva ruta" in line:
                assert True, "Should be there"
                break
        else:
            # Si no se encuentra el mensaje
            assert False, "Should be there"
    
    # Generar la estructura de datos con la que realizar el proceso de explotación de conocimiento
    knowledge_table = component1.generate_data_structure()
    
    # Después de comprobar en spa_variant_file las palabras a analizar, en total debe haber 33 elementos
    assert len(knowledge_table) == 32, "Should be 32"
    
    # Contador para contar cuántos elementos tienen una clave
    appearences_tierra = 0
    appearences_mareo = 0

    # Iterar sobre los elementos del diccionario
    for key, _ in knowledge_table.items():
        if "tierra" in key:  # Verificar si la clave contiene "tierra"
            appearences_tierra += 1
        elif "mareo" in key: # Verificar si la clave contiene "mareo"
            appearences_mareo += 1
            
    # knowledge_table debe contener 11 elementos con "tierra"
    assert appearences_tierra == 11, "Should be 11"
    
    # knowledge_table debe contener 11 elementos con "mareo"
    assert appearences_mareo == 4, "Should be 4"
    
    # Elemento que debe contener el knowledge_table
    element_piloto = ("spa-30-10433164-n_piloto", {
            "Sense index": "2",
            "Gloss": "NULL",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    assert (element_piloto[0], element_piloto[1]) in knowledge_table.items(), "Should appear"
    
    # Elemento que debe contener el knowledge_table
    element_tierra = ("spa-30-09334396-n_tierra", {
            "Sense index": "2",
            "Gloss": "La parte sólida de la superficie de la tierra.",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    assert (element_tierra[0], element_tierra[1]) in knowledge_table.items(), "Should appear"
    
    # Creamos la estructura de datos donde guardar las glosas
    eng_data_structure = component1.generate_eng_data_structure()
    
    # Los dos offsets anteriores deben estar, y no deben ser NULL
    offset_piloto = element_piloto[0].split('_')[0]
    assert offset_piloto in eng_data_structure.keys() and eng_data_structure[offset_piloto] != "NULL", "Should be"
    offset_tierra = element_tierra[0].split('_')[0]
    assert offset_tierra in eng_data_structure.keys() and eng_data_structure[offset_tierra] != "NULL", "Should be"
    
    # print the output
    # print(json.dumps(knowledge_table, indent=2, ensure_ascii=False))
    
def component_question_maker_traduction_test():
    
    # Elementos de prueba
    element_1 = ("spa-30-00001740-n_entidad", {
            "Sense index": "1",
            "Gloss": "that which is perceived or known or inferred to have its own distinct existence (living or nonliving)  ",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    element_2 = ("spa-30-00001930-n_entidad_física", {
            "Sense index": "1",
            "Gloss": "an entity that has physical existence  ",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    element_3 = ("spa-30-00002137-n_abstracción", {
            "Sense index": "2",
            "Gloss": "a general concept formed by extracting common features from specific examples  ",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    prompts_element_1 = [f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: 'that which is perceived or known or inferred to have its own distinct existence (living or nonliving)  '."]
    prompts_element_2 = [f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: 'an entity that has physical existence  '."]
    prompts_element_3 = [f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: 'a general concept formed by extracting common features from specific examples  '."]
     
    assert prompts_element_1 == componenteQuestionMaker_traduccion.generate_prompts(element_1), "Should be true"
    assert prompts_element_2 == componenteQuestionMaker_traduccion.generate_prompts(element_2), "Should be true"
    assert prompts_element_3 == componenteQuestionMaker_traduccion.generate_prompts(element_3), "Should be true"
    
def component_question_maker_extraction_test():
    
    # Elementos de prueba
    element_piloto = ("spa-30-10433164-n_piloto", {
            "Sense index": "2",
            "Gloss": "NULL",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    element_tierra = ("spa-30-09334396-n_tierra", {
            "Sense index": "2",
            "Gloss": "la parte sólida de la superficie de la Tierra",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    prompts_piloto = componenteQuestionMaker_extraccion.generate_prompts(element_piloto)
    prompts_tierra = componenteQuestionMaker_extraccion.generate_prompts(element_tierra)
    
    assert prompts_piloto == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género masculino con el sentido de 'NULL'.", 
                                          f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género femenino con el sentido de 'NULL'."], "Shold be true"
    assert prompts_tierra == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género masculino con el sentido de 'la parte sólida de la superficie de la Tierra'.", 
                                          f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género femenino con el sentido de 'la parte sólida de la superficie de la Tierra'."], "Shold be true"  
  
def component_question_maker_validation_test():  
    
    # Elementos de prueba
    element_piloto = ("spa-30-10433164-n_piloto", {
            "Sense index": "2",
            "Gloss": "NULL",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [
              "1. El piloto nulo es una persona que no tiene la capacidad o la experiencia necesaria para volar un avión.\n2. El piloto nulo es un concepto teórico utilizado en simulaciones de vuelo para representar a un piloto inexperto o incapaz.\n3. El piloto nulo es una situación hipotética en la que se supone que el piloto no está presente o no tiene control del avión.\n4. El piloto nulo es un concepto utilizado en la investigación de accidentes aéreos para identificar al piloto que no pudo haber actuado correctamente en el momento del accidente.\n5. El piloto nulo es una situación hipotética en la que se supone que el piloto ha abandonado el avión o ha sido incapacitado de alguna manera, dej",
              "La pilota es una bola pequeña y redonda utilizada en deportes como tenis o fútbol. Sin embargo, en este contexto, la palabra \"pilota\" se usa como un sustantivo femenino que significa \"nulo\", \"ninguno\", \"cero\".\n\nEjemplos:\n- La pilota de votos fue nula en el distrito electoral.\n- El resultado final del partido fue 3-0, con una pilota de goles en contra para el equipo perdedor.\n- En la prueba de matemáticas, la pilota de puntuaciones fue cero para todos los estudiantes.\n\n2. La pilota es un personaje secundario en la serie de televisión \"Friends\". Sin embargo, en este contexto, la palabra \"pilota\" se usa"
            ],
            "Validation LLM answers": [],
            "Extraction gender": "Masculino",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    element_tierra = ("spa-30-09334396-n_tierra", {
            "Sense index": "2",
            "Gloss": "la parte sólida de la superficie de la Tierra",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [             
              "\n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras.",
              "1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."
            ],
            "Validation LLM answers": [],
            "Extraction gender": "Femenino",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    prompts_piloto = componenteQuestionMaker_validacion.generate_prompts(element_piloto)
    prompts_tierra = componenteQuestionMaker_validacion.generate_prompts(element_tierra)
    
    assert prompts_piloto == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género masculino con el sentido de 'NULL'."], "Shold be true"
    assert prompts_tierra == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género femenino con el sentido de 'la parte sólida de la superficie de la Tierra'."], "Shold be true"
        
    
def component_llm_communicator_test():
    
    config = ConfigParser()
    config.read('./config.ini')
    
    # Guarda el flujo original de salida estándar
    stdout_orig = sys.stdout

    # Define un archivo para redirigir la salida estándar
    archivo_salida = open("./test.txt", "w")

    # Redirige la salida estándar al archivo
    sys.stdout = archivo_salida

    # Si el path del modelo no es correcto no debe dar error, si no indicar el motivo por consola
    componenteLLMCommunicator_test = ComponenteLLMCommunicator(config['file_path']['extraction_results_language_model_path_test']) 
    componenteLLMCommunicator_test.load_model()

    # Cierra el archivo
    archivo_salida.close()
    
    # Restaura la salida estándar
    sys.stdout = stdout_orig
    
    # Abre el archivo de salida en modo lectura
    with open("./test.txt", "r") as archivo:
        # Lee todas las líneas del archivo
        lines = archivo.readlines()

        # Itera sobre cada línea
        for line in lines:
            # Verifica si la línea contiene el mensaje que estás buscando
            if "LLM \"../../models/zephyr-7b-alpha.Q5_K_M.gguf\" no encontrado. Vuelve a introducir una nueva ruta" in line:
                assert True, "Should be there"
                break
        else:
            # Si no se encuentra el mensaje
            assert False, "Should be there"
            
    # Guarda el flujo original de salida estándar
    stdout_orig = sys.stdout

    # Define un archivo para redirigir la salida estándar
    archivo_salida = open("./test.txt", "w")

    # Guarda los flujos originales de salida estándar y de error
    stdout_orig = sys.stdout
    stderr_orig = sys.stderr
    
    # Abre el archivo de salida en modo lectura
    with open("./test.txt", "r") as archivo:
        
        # Redirige la salida estándar al archivo
        sys.stdout = archivo_salida
        # Redirige la salida de error al archivo
        sys.stderr = archivo_salida
        
        # Inicializamos el componenteLLMCommunicator con el llm que vamos a utilizar para conseguir las respuestas provisionales
        componenteLLMCommunicator = ComponenteLLMCommunicator(config['file_path']['extraction_results_language_model_path'])
        
        # Cargamos el modelo de lenguaje que vamos a utilizar para conseguir las respuestas provisionales
        componenteLLMCommunicator.load_model()
        
        # Elementos de prueba
        element_piloto = ("spa-30-10433164-n_piloto", {
                "Sense index": "2",
                "Gloss": "NULL",
                "Part of speech": "n",
                "Language": "spa",
                "Extraction LLM answers": [],
                "Validation LLM answers": [],
                "Extraction gender": "NULL",
                "Validation gender": "NULL",
                "Correctas": 0,
                "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
                "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
                "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
                "Mensaje de información": "NULL"
        })
        element_tierra = ("spa-30-09334396-n_tierra", {
                "Sense index": "2",
                "Gloss": "la parte sólida de la superficie de la Tierra",
                "Part of speech": "n",
                "Language": "spa",
                "Extraction LLM answers": [],
                "Validation LLM answers": [],
                "Extraction gender": "NULL",
                "Validation gender": "NULL",
                "Correctas": 0,
                "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
                "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
                "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
                "Mensaje de información": "NULL"
        })
                
        # Pruebas de preguntas
        provisional_prompts_piloto = componenteQuestionMaker_extraccion.generate_prompts(element_tierra)
        provisional_prompts_tierra = componenteQuestionMaker_extraccion.generate_prompts(element_piloto)
        for element in provisional_prompts_piloto:
            componenteLLMCommunicator.run_the_model(element) 
        for element in provisional_prompts_tierra:
            componenteLLMCommunicator.run_the_model(element) 
        
        # Lee todas las líneas del archivo
        lines = archivo.readlines()

        # Inicializa banderas para cada mensaje buscado
        mensajes_encontrados = {
            "llama_model_loader: loaded meta data with": False,
            "llama_new_context_with_model:": False,
            "Model loaded": False
        }

        # Itera sobre cada línea
        for line in lines:
            # Verifica si la línea contiene alguno de los mensajes buscados
            for mensaje in mensajes_encontrados:
                if mensaje in line:
                    mensajes_encontrados[mensaje] = True

        # Verifica si todos los mensajes buscados se encontraron
        for mensaje, encontrado in mensajes_encontrados.items():
            assert encontrado, f"El mensaje '{mensaje}' no se encontró en el archivo."

        # Verifica la cantidad de veces que aparecen ciertos mensajes específicos
        # Contar cuántas veces aparece la parte en cada elemento de la lista
        assert sum(1 for elemento in lines if "llama_print_timings:        load time =" in elemento) == 4, "Should be 4"
        assert sum(1 for elemento in lines if "llama_print_timings:      sample time =" in elemento) == 4, "Should be 4"
        assert sum(1 for elemento in lines if "llama_print_timings: prompt eval time =" in elemento) == 4, "Should be 4"
        assert sum(1 for elemento in lines if "llama_print_timings:        eval time =" in elemento) == 4, "Should be 4"
        assert sum(1 for elemento in lines if "llama_print_timings:       total time =" in elemento) == 4, "Should be 4"
        assert sum(1 for elemento in lines if "Llama.generate: prefix-match hit" in elemento) == 3, "Should be 3"
        
        
        # Restaura la salida estándar y de error
        sys.stdout = stdout_orig
        sys.stderr = stderr_orig     
        
    # Cierra el archivo
    archivo_salida.close()
    
def component_extractor_gloss_translation_test():
  
    element_motivo = ('spa-30-00023773-n_motivo', {
          'Sense index': '1',
          'Gloss': 'the psychological feature that arouses an organism to action toward a desired goal; the reason for the action; that which gives purpose and direction to behavior',
          'Part of speech': 'n',
          'Language': 'spa',
          'Extraction LLM answers': [],
          'Validation LLM answers': [],
          'Extraction result': 'NULL',
          'Validation result': 'NULL',
          'Correctas': 0,
          'Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase': 0,
          'Incorrectas de tipo 2: la palabra a analizar no aparece en la frase': 0,
          'Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género': 0,
          'Mensaje de información': 'NULL'
    })

    llm_answer_list = [' La característica psicológica que desencadena en un organismo la acción hacia un objetivo deseado; el motivo de la acción; lo que da sentido y dirección a la conducta.']
    
    result_motivo = componenteExtractor_traduccionGlosa.get_result(element_motivo, llm_answer_list)
    
    expected_element_motivo = ('spa-30-00023773-n_motivo', {
          'Sense index': '1',
          'Gloss': 'La característica psicológica que desencadena en un organismo la acción hacia un objetivo deseado; el motivo de la acción; lo que da sentido y dirección a la conducta.',
          'Part of speech': 'n',
          'Language': 'spa',
          'Extraction LLM answers': [],
          'Validation LLM answers': [],
          'Extraction result': 'NULL',
          'Validation result': 'NULL',
          'Correctas': 0,
          'Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase': 0,
          'Incorrectas de tipo 2: la palabra a analizar no aparece en la frase': 0,
          'Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género': 0,
          'Mensaje de información': 'NULL'
    })
    
    assert result_motivo == expected_element_motivo, "Should be true"
    
    element_fenomeno = ('spa-30-00034213-n_fenómeno', {
          'Sense index': '1',
          'Gloss': 'any state or process known through the senses rather than by intuition or reasoning  ',
          'Part of speech': 'n',
          'Language': 'spa',
          'Extraction LLM answers': [],
          'Validation LLM answers': [],
          'Extraction result': 'NULL',
          'Validation result': 'NULL',
          'Correctas': 0,
          'Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase': 0,
          'Incorrectas de tipo 2: la palabra a analizar no aparece en la frase': 0,
          'Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género': 0,
          'Mensaje de información': 'NULL'
    })

    llm_answer_list_2 = [" 'cualquier estado o proceso conocido a través del sentido, en lugar de por intuición o razonamiento'."]
    
    result_fenomeno = componenteExtractor_traduccionGlosa.get_result(element_fenomeno, llm_answer_list_2)
    
    expected_element_fenomeno = ('spa-30-00034213-n_fenómeno', {
          'Sense index': '1',
          'Gloss': 'Cualquier estado o proceso conocido a través del sentido, en lugar de por intuición o razonamiento.',
          'Part of speech': 'n',
          'Language': 'spa',
          'Extraction LLM answers': [],
          'Validation LLM answers': [],
          'Extraction result': 'NULL',
          'Validation result': 'NULL',
          'Correctas': 0,
          'Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase': 0,
          'Incorrectas de tipo 2: la palabra a analizar no aparece en la frase': 0,
          'Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género': 0,
          'Mensaje de información': 'NULL'
    })
    
    assert result_fenomeno == expected_element_fenomeno, "Should be true"
    
def component_extractor_extraccion_test(): 
    # --------------------------------------   Prueba 1   -------------------------------------------
        
    element_tierra = ("spa-30-09334396-n_tierra", {
            "Sense index": "2",
            "Gloss": "La parte sólida de la superficie de la tierra.",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [
              "\n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras."
              "1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."
            ],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    llm_answer_list_1 = [
      "\n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras.",
      "1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."
    ]
    
    result_tierra = componenteExtractor_extraccion.get_result(element_tierra, llm_answer_list_1)
    
    expected_element_tierra = ("spa-30-09334396-n_tierra", {
            "Sense index": "2",
            "Gloss": "La parte sólida de la superficie de la tierra.",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [
              "\n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras."
              "1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."
            ],
            "Validation LLM answers": [],
            "Extraction gender": "Femenino",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    assert result_tierra == expected_element_tierra, "Should be true"
    
    # --------------------------------------   Prueba 2   -------------------------------------------
    
    element_objeto =  ("spa-30-00002684-n_objeto", {
            "Sense index": "1",
            "Gloss": "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [
              " 1. El objeto reflejaba su forma en la superficie del agua.\n2. La luna era un objeto brillante en el cielo.\n3. El espejo mostraba un objeto aterrador.\n4. El sombrero de papel que estaba colgando del árbol era un objeto curioso.\n5. El reflejo en la ventana era un objeto que parecía haberse deslizado de otro mundo.",
              " 1. La piedra es un objeto tangible y visible, capaz de proyectar una sombra larga en la pared.\n2. El vase de cristal es un objeto delicado y elegante, que refleja la luz con una belleza incomparable.\n3. La escultura de bronce es un objeto artístico y valioso, que captura la belleza humana en cada detalle.\n4. El libro es un objeto educativo y culturalmente significante, que transmite conocimiento y ideas a través del tiempo.\n5. La caja de madera es un objeto funcional y práctico, que protege nuestros objetos valiosos y preciados."
            ],
            "Validation LLM answers": [],
            "Extraction gender": "NULL",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    
    llm_answer_list_2 =   [
      " 1. El objeto reflejaba su forma en la superficie del agua.\n2. La luna era un objeto brillante en el cielo.\n3. El espejo mostraba un objeto aterrador.\n4. El sombrero de papel que estaba colgando del árbol era un objeto curioso.\n5. El reflejo en la ventana era un objeto que parecía haberse deslizado de otro mundo.",
      " 1. La piedra es un objeto tangible y visible, capaz de proyectar una sombra larga en la pared.\n2. El vase de cristal es un objeto delicado y elegante, que refleja la luz con una belleza incomparable.\n3. La escultura de bronce es un objeto artístico y valioso, que captura la belleza humana en cada detalle.\n4. El libro es un objeto educativo y culturalmente significante, que transmite conocimiento y ideas a través del tiempo.\n5. La caja de madera es un objeto funcional y práctico, que protege nuestros objetos valiosos y preciados."
    ]
    
    result_objeto = componenteExtractor_extraccion.get_result(element_objeto, llm_answer_list_2)
    
    expected_element_objeto =  ("spa-30-00002684-n_objeto", {
            "Sense index": "1",
            "Gloss": "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
            "Part of speech": "n",
            "Language": "spa",
            "Extraction LLM answers": [
              " 1. El objeto reflejaba su forma en la superficie del agua.\n2. La luna era un objeto brillante en el cielo.\n3. El espejo mostraba un objeto aterrador.\n4. El sombrero de papel que estaba colgando del árbol era un objeto curioso.\n5. El reflejo en la ventana era un objeto que parecía haberse deslizado de otro mundo.",
              " 1. La piedra es un objeto tangible y visible, capaz de proyectar una sombra larga en la pared.\n2. El vase de cristal es un objeto delicado y elegante, que refleja la luz con una belleza incomparable.\n3. La escultura de bronce es un objeto artístico y valioso, que captura la belleza humana en cada detalle.\n4. El libro es un objeto educativo y culturalmente significante, que transmite conocimiento y ideas a través del tiempo.\n5. La caja de madera es un objeto funcional y práctico, que protege nuestros objetos valiosos y preciados."
            ],
            "Validation LLM answers": [],
            "Extraction gender": "Masculino",
            "Validation gender": "NULL",
            "Correctas": 0,
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
            "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
            "Mensaje de información": "NULL"
    })
    
    assert expected_element_objeto == result_objeto, "Should be true"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_ser = ("spa-30-00004258-n_ser", {
        "Sense index": "4",
        "Gloss": "Una entidad viva.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El león es un animal salvaje y poderoso.\n2. El árbol es una entidad viva que crece y se desarrolla a lo largo del tiempo.\n3. El hombre es una criatura compleja, con muchas facetas y cualidades.\n4. El río es un ser vivo que fluye y cambia constantemente.\n5. El sol es una entidad viva que ilumina nuestro planeta y nos da calor y luz.",
          " 1. La madre es la fuente de vida para sus hijos.\n2. La flor es la belleza natural del jardín.\n3. La luna es la guía nocturna de los viajeros.\n4. La lluvia es la fuente de vida para las plantas.\n5. La paz es el objetivo más deseado por los humanos."
        ],
        "Validation LLM answers": [],
        "Extraction gender": "NULL",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    llm_answer_list_3 = [
        " 1. El león es un animal salvaje y poderoso.\n2. El árbol es una entidad viva que crece y se desarrolla a lo largo del tiempo.\n3. El hombre es una criatura compleja, con muchas facetas y cualidades.\n4. El río es un ser vivo que fluye y cambia constantemente.\n5. El sol es una entidad viva que ilumina nuestro planeta y nos da calor y luz.",
        " 1. La madre es la fuente de vida para sus hijos.\n2. La flor es la belleza natural del jardín.\n3. La luna es la guía nocturna de los viajeros.\n4. La lluvia es la fuente de vida para las plantas.\n5. La paz es el objetivo más deseado por los humanos."
    ]
    
    result_ser = componenteExtractor_extraccion.get_result(element_ser, llm_answer_list_3)
    
    expected_element_ser = ("spa-30-00004258-n_ser", {
        "Sense index": "4",
        "Gloss": "Una entidad viva.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El león es un animal salvaje y poderoso.\n2. El árbol es una entidad viva que crece y se desarrolla a lo largo del tiempo.\n3. El hombre es una criatura compleja, con muchas facetas y cualidades.\n4. El río es un ser vivo que fluye y cambia constantemente.\n5. El sol es una entidad viva que ilumina nuestro planeta y nos da calor y luz.",
          " 1. La madre es la fuente de vida para sus hijos.\n2. La flor es la belleza natural del jardín.\n3. La luna es la guía nocturna de los viajeros.\n4. La lluvia es la fuente de vida para las plantas.\n5. La paz es el objetivo más deseado por los humanos."
        ],
        "Validation LLM answers": [],
        "Extraction gender": "NULL",
        "Validation gender": "NULL",
        "Correctas": 1,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 9,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
    })
    
    assert expected_element_ser == result_ser, "Should be true"
    
    # --------------------------------------   Prueba 4   -------------------------------------------
    
    element_vida = ("spa-30-00006269-n_vida", {
        "Sense index": "12",
        "Gloss": "Cosas vivas en su conjunto.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. La vida animal es una variedad maravillosa y compleja.\n2. El mundo vegetal es un mosaico de colores y texturas.\n3. Los seres humanos son la creación más compleja del universo.\n4. La fauna marina es una comunidad intrincada e interdependiente.\n5. El bosque tropical es un mundo en constante cambio y evolución.",
          " 1. La vida marina es un mundo misterioso y atractivo.\n2. La vida vegetal es la base de la cadena alimentaria.\n3. La vida animal es una variedad infinita de formas y tamaños.\n4. La vida en el desierto es difícil y exigente.\n5. La vida en la selva es rica y variada."
        ],
        "Validation LLM answers": [],
        "Extraction gender": "NULL",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    llm_answer_list_4 = [
      " 1. La vida animal es una variedad maravillosa y compleja.\n2. El mundo vegetal es un mosaico de colores y texturas.\n3. Los seres humanos son la creación más compleja del universo.\n4. La fauna marina es una comunidad intrincada e interdependiente.\n5. El bosque tropical es un mundo en constante cambio y evolución.",
      " 1. La vida marina es un mundo misterioso y atractivo.\n2. La vida vegetal es la base de la cadena alimentaria.\n3. La vida animal es una variedad infinita de formas y tamaños.\n4. La vida en el desierto es difícil y exigente.\n5. La vida en la selva es rica y variada."
    ]
    
    result_vida = componenteExtractor_extraccion.get_result(element_vida, llm_answer_list_4)
    
    expected_element_vida = ("spa-30-00006269-n_vida", {
        "Sense index": "12",
        "Gloss": "Cosas vivas en su conjunto.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. La vida animal es una variedad maravillosa y compleja.\n2. El mundo vegetal es un mosaico de colores y texturas.\n3. Los seres humanos son la creación más compleja del universo.\n4. La fauna marina es una comunidad intrincada e interdependiente.\n5. El bosque tropical es un mundo en constante cambio y evolución.",
          " 1. La vida marina es un mundo misterioso y atractivo.\n2. La vida vegetal es la base de la cadena alimentaria.\n3. La vida animal es una variedad infinita de formas y tamaños.\n4. La vida en el desierto es difícil y exigente.\n5. La vida en la selva es rica y variada."
        ],
        "Validation LLM answers": [],
        "Extraction gender": "Femenino",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    assert result_vida == expected_element_vida, "Should be True"
    
def component_extractor_validacion_test():
        
    # --------------------------------------   Prueba 1   -------------------------------------------
    
    element_articulo = ("spa-30-00022903-n_artículo", {
        "Sense index": "3",
        "Gloss": "En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " En la teoría de conjuntos, el artículo n es una variable que representa cualquier subconjunto de un conjunto dado. En la lógica proposicional, el artículo n es una variable que representa cualquier proposición. En la geometría euclidiana, el artículo n es una variable que representa cualquier punto en el espacio. En la teoría de números, el artículo n es una variable que representa cualquier número entero positivo. En la física, el artículo n es una variable que representa cualquier cantidad de materia o energía.",
          " En la teoría de conjuntos, la intersección de dos conjuntos se denota por la letra 'n'.\n\n1. La palabra \"artículo\" es un sustantivo femenino en español que significa \"un elemento o parte de una clase o grupo\".\n\n2. En el campo de lingüística, la definición de \"artículo\" como un elemento gramatical se refiere a palabras como \"el\", \"la\", y \"un\" en inglés, que se utilizan para indicar la especificación o referencia de un objeto o concepto.\n\n3. En el contexto de la literatura, \"artículo\" también puede referirse a una pieza escrita publicada en una revista o periódico, como \"la revista científica Nature\".\n\n4. En la"
        ],
        "Validation LLM answers": [
          "\n\n1. El artículo de entrada en el curso de lingüística es fundamental para comprender las diferencias entre los idiomas.\n2. El artículo definido en español se utiliza para indicar que el sustantivo a la que se refiere es conocido por ambos interlocutores.\n3. El artículo indefinido en inglés se emplea para expresar una cantidad no especificada de elementos.\n4. El artículo en francés se escribe como \"le\" o \"la\", dependiendo del género y número del sustantivo al que se refiere.\n5. El artículo en alemán es un signo de puntuación que indica el inicio de una oración.\n\nEn resumen, los artículos son elementos gramaticales importantes en muchas lengu"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    llm_answer_list = [
      "\n\n1. El artículo de entrada en el curso de lingüística es fundamental para comprender las diferencias entre los idiomas.\n2. El artículo definido en español se utiliza para indicar que el sustantivo a la que se refiere es conocido por ambos interlocutores.\n3. El artículo indefinido en inglés se emplea para expresar una cantidad no especificada de elementos.\n4. El artículo en francés se escribe como \"le\" o \"la\", dependiendo del género y número del sustantivo al que se refiere.\n5. El artículo en alemán es un signo de puntuación que indica el inicio de una oración.\n\nEn resumen, los artículos son elementos gramaticales importantes en muchas lengu"
    ]
    
    result_articulo = componenteExtractor_validacion.get_result(element_articulo, llm_answer_list)
    
    expected_element_articulo = ("spa-30-00022903-n_artículo", {
        "Sense index": "3",
        "Gloss": "En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " En la teoría de conjuntos, el artículo n es una variable que representa cualquier subconjunto de un conjunto dado. En la lógica proposicional, el artículo n es una variable que representa cualquier proposición. En la geometría euclidiana, el artículo n es una variable que representa cualquier punto en el espacio. En la teoría de números, el artículo n es una variable que representa cualquier número entero positivo. En la física, el artículo n es una variable que representa cualquier cantidad de materia o energía.",
          " En la teoría de conjuntos, la intersección de dos conjuntos se denota por la letra 'n'.\n\n1. La palabra \"artículo\" es un sustantivo femenino en español que significa \"un elemento o parte de una clase o grupo\".\n\n2. En el campo de lingüística, la definición de \"artículo\" como un elemento gramatical se refiere a palabras como \"el\", \"la\", y \"un\" en inglés, que se utilizan para indicar la especificación o referencia de un objeto o concepto.\n\n3. En el contexto de la literatura, \"artículo\" también puede referirse a una pieza escrita publicada en una revista o periódico, como \"la revista científica Nature\".\n\n4. En la"
        ],
        "Validation LLM answers": [
          "\n\n1. El artículo de entrada en el curso de lingüística es fundamental para comprender las diferencias entre los idiomas.\n2. El artículo definido en español se utiliza para indicar que el sustantivo a la que se refiere es conocido por ambos interlocutores.\n3. El artículo indefinido en inglés se emplea para expresar una cantidad no especificada de elementos.\n4. El artículo en francés se escribe como \"le\" o \"la\", dependiendo del género y número del sustantivo al que se refiere.\n5. El artículo en alemán es un signo de puntuación que indica el inicio de una oración.\n\nEn resumen, los artículos son elementos gramaticales importantes en muchas lengu"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "Masculino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    assert result_articulo == expected_element_articulo, "Should be True"
    
    # --------------------------------------   Prueba 2   -------------------------------------------
    
    element_cosa = ("spa-30-00002684-n_cosa", {
        "Sense index": "2",
        "Gloss": "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. La cosa que se proyecta en la pared es un objeto real, no una ilusión.\n2. El sol, una cosa brillante y caliente, está afligido por el eclipse.\n3. La cosa que se mueve lentamente en el río es un barco.\n4. La cosa que se ve en la noche oscura es una sombra.\n5. El objeto que se desliza por el suelo es una cosa pesada y fría.",
          " 1. La cosa que creó la luna es un reflejo de su propia belleza.\n2. La cosa que flota en el aire es solo una sombra de lo real.\n3. La cosa que se mueve en la oscuridad es solo una imagen de la verdad.\n4. La cosa que se ve en el espejo es solo una reflexión de la realidad.\n5. La cosa que se siente en tu corazón es solo un eco de la verdad."
        ],
        "Validation LLM answers": [
          " 1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando, pero se sentía incómoda. 3) Aunque la cosa parecía difícil, finalmente logró hacerla. 4) La cosa más importante era mantenerse unido a su familia. 5) Al ver la cosa que había hecho, sintió una gran sensación de orgullo.\n\n¿Qué frases podrías crear utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'?\n\n1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando,"
        ],
        "Extraction gender": "Femenino",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    llm_answer_list_2 = [
      " 1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando, pero se sentía incómoda. 3) Aunque la cosa parecía difícil, finalmente logró hacerla. 4) La cosa más importante era mantenerse unido a su familia. 5) Al ver la cosa que había hecho, sintió una gran sensación de orgullo.\n\n¿Qué frases podrías crear utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'?\n\n1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando,"
    ]
    
    result_cosa = componenteExtractor_validacion.get_result(element_cosa, llm_answer_list_2)
    
    expected_element_cosa = ("spa-30-00002684-n_cosa", {
        "Sense index": "2",
        "Gloss": "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. La cosa que se proyecta en la pared es un objeto real, no una ilusión.\n2. El sol, una cosa brillante y caliente, está afligido por el eclipse.\n3. La cosa que se mueve lentamente en el río es un barco.\n4. La cosa que se ve en la noche oscura es una sombra.\n5. El objeto que se desliza por el suelo es una cosa pesada y fría.",
          " 1. La cosa que creó la luna es un reflejo de su propia belleza.\n2. La cosa que flota en el aire es solo una sombra de lo real.\n3. La cosa que se mueve en la oscuridad es solo una imagen de la verdad.\n4. La cosa que se ve en el espejo es solo una reflexión de la realidad.\n5. La cosa que se siente en tu corazón es solo un eco de la verdad."
        ],
        "Validation LLM answers": [
          " 1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando, pero se sentía incómoda. 3) Aunque la cosa parecía difícil, finalmente logró hacerla. 4) La cosa más importante era mantenerse unido a su familia. 5) Al ver la cosa que había hecho, sintió una gran sensación de orgullo.\n\n¿Qué frases podrías crear utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'?\n\n1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando,"
        ],
        "Extraction gender": "Femenino",
        "Validation gender": "Femenino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    assert result_cosa == expected_element_cosa, "Should be True"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_son = ("spa-30-00546389-n_son", {
        "Sense index": "3",
        "Gloss": "Acto de cantar.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El son de la soprano era impresionante.\n2. El son de los niños en la escuela de música era agradable.\n3. El son de la guitarra fue muy bien interpretado.\n4. El son de la canción favorita del compositor es un clásico.\n5. El son de la cantante en el concierto fue magnífico.",
          " 1. La canción es un son hermoso.\n2. El concierto fue un gran son.\n3. La soprano interpretó un son magnífico.\n4. La melodía es un son agradable.\n5. La canción de la noche fue un son encantador."
        ],
        "Validation LLM answers": [
          " 1) El son es un arte muy antiguo. 2) El son mejilla la voz de los cantantes. 3) El son es una forma de expresión cultural. 4) El son puede ser un medio para comunicarse con Dios. 5) El son es una parte importante de la música tradicional.\n\n"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
    })
    
    llm_answer_list_3 =   [
      " 1) El son es un arte muy antiguo. 2) El son mejilla la voz de los cantantes. 3) El son es una forma de expresión cultural. 4) El son puede ser un medio para comunicarse con Dios. 5) El son es una parte importante de la música tradicional.\n\n"
    ]
    
    result_son = componenteExtractor_validacion.get_result(element_son, llm_answer_list_3)
    
    expected_element_son = ("spa-30-00546389-n_son", {
        "Sense index": "3",
        "Gloss": "Acto de cantar.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El son de la soprano era impresionante.\n2. El son de los niños en la escuela de música era agradable.\n3. El son de la guitarra fue muy bien interpretado.\n4. El son de la canción favorita del compositor es un clásico.\n5. El son de la cantante en el concierto fue magnífico.",
          " 1. La canción es un son hermoso.\n2. El concierto fue un gran son.\n3. La soprano interpretó un son magnífico.\n4. La melodía es un son agradable.\n5. La canción de la noche fue un son encantador."
        ],
        "Validation LLM answers": [
          " 1) El son es un arte muy antiguo. 2) El son mejilla la voz de los cantantes. 3) El son es una forma de expresión cultural. 4) El son puede ser un medio para comunicarse con Dios. 5) El son es una parte importante de la música tradicional.\n\n"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 5,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "La entrada ha terminado su ejecución en la fase de validación."
    })
    
    assert result_son == expected_element_son, "Should be True"
    
def component_exporter_test():
    
    knowledge_table = {
      "spa-30-00001740-n_entidad": {
        "Sense index": "1",
        "Gloss": "Aquello que se percibe o se sabe o se infiere que tiene su existencia propia distinta (viva o no viva).",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. La montaña es una entidad natural.\n2. El río es una entidad hidrológica.\n3. El estado es una entidad política.\n4. El planeta es una entidad astronómica.\n5. El concepto es una entidad mental.",
          " 1. La entidad política es un conjunto de normas y principios que rigen la organización social y política de una nación.\n2. La entidad económica es el sistema de producción, distribución y consumo de bienes y servicios en una sociedad.\n3. La entidad cultural es un conjunto de valores, creencias, tradiciones y costumbres que definen la identidad de una comunidad o nación.\n4. La entidad natural es el conjunto de procesos y fenómenos que se desarrollan en el medio ambiente sin la intervención directa del ser humano.\n5. La entidad espiritual es un concepto abstracto que representa la existencia de una realidad superior a la física, como por ejemplo la religión o la filosofía."
        ],
        "Validation LLM answers": [
          " 1. La entidad jurídica es independiente del Estado. 2. La entidad económica es un conjunto de recursos y actividades. 3. La entidad física es un ser con vida propia. 4. La entidad social es un grupo de personas que comparten intereses comunes. 5. La entidad política es una organización que busca influir en la toma de decisiones.\n\n"
        ],
        "Extraction gender": "Femenino",
        "Validation gender": "Femenino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
      },
      "spa-30-00004258-n_organismo": {
        "Sense index": "2",
        "Gloss": "Una entidad viva.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El organismo humano es una entidad compleja y maravillosa que funciona de manera intrincada.\n2. El organismo celular es la unidad básica de todos los seres vivos, incluyendo a los humanos.\n3. El organismo vegetal es una entidad viva que se alimenta mediante la absorción de nutrientes a través de sus raíces.\n4. El organismo animal es una entidad viva compleja y adaptable que puede cambiar su comportamiento en respuesta a las circunstancias.\n5. El organismo microscópico es una entidad viva muy pequeña, invisible al ojo humano, que juega un papel importante en la ecología de los ecosistemas.",
          " 1. La planta es un orgánimo viviente que necesita agua y luz para crecer.\n2. El coral es un orgánomo complejo formado por numerosas colonias de pólipos.\n3. La bacteria es un orgánomo microscópico que se encuentra en la mayoría de los ecosistemas terrestres y acuáticos.\n4. El árbol es un orgánomo que proporciona alimento, oxígeno y refugio a una gran variedad de animales.\n5. La columna vertebral es un orgánomo importante en la estructura del cuerpo humano, que ayuda a mantener la postura y protege el sistema nervioso."
        ],
        "Validation LLM answers": [
          " 1) El organismo humano es un ser complejo y maravilloso. 2) Los organismos marinos son muy sensibles a la contaminación. 3) El organismo celular se divide para formar tejidos y órganos. 4) El estudio del organismo en su entorno es fundamental para la ecología. 5) La investigación sobre el organismo viral ha permitido avances importantes en medicina.\n\n"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "Masculino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
      },
      "spa-30-00004475-n_organismo": {
        "Sense index": "1",
        "Gloss": "Un ser vivo que tiene (o puede desarrollar) la capacidad de actuar o funcionar de manera independiente.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El organismo humano es un ser complejo y multifuncional, capaz de realizar una gran variedad de acciones y procesos biológicos.\n2. La bacteria es un organismo microscópico que puede causar enfermedades graves en los humanos y otros animales.\n3. El árbol es un organismo vegetal que crece y se desarrolla a lo largo de su vida, absorbiendo nutrientes del suelo y produciendo oxígeno.\n4. La hormona es un organismo químico que actúa como mensajero en el cuerpo humano, regulando la actividad de otros órganos y sistemas biológicos.\n5. El virus es un organismo microscópico y parásito que depende de otro organismo para sobrevivir y reproducirse",
          " 1. La planta es un orgánimo viviente que posee la capacidad de absorber nutrientes y convertirlos en energía a través del proceso fotosintético.\n2. El sistema nervioso humano es un orgánomo complejo que permite al ser humano percibir, procesar y responder a estímulos sensoriales.\n3. La bacteria Escherichia coli es un orgánomo microscópico que puede causar enfermedades graves en humanos y animales.\n4. El corazón humano es un orgánomo muscular que bombea sangre a lo largo de los vasos sanguíneos, permitiendo al cuerpo distribuir nutrientes y eliminar desechos.\n5. La mente humana es un orgánomo complejo que permite al ser hum"
        ],
        "Validation LLM answers": [
          " 1. El organismo humano es un sistema complejo y altamente adaptable. 2. Los organismos marinos son muy sensibles a las variaciones en el clima. 3. Un organismo puede desarrollar la capacidad de sobrevivir en condiciones extremas. 4. Los organismos microscópicos desempeñan un papel crucial en el equilibrio ecológico. 5. El estudio del organismo celular ha permitido avances significativos en la medicina moderna.\n\n"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "Masculino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
      },
      "spa-30-00007846-n_alguno": {
        "Sense index": "1",
        "Gloss": "Un ser humano.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. Alguien caminaba por la calle.\n2. Un hombre estaba leyendo un libro en la plaza.\n3. Algún tipo de persona siempre llega tarde a las reuniones.\n4. Un hombre con una bolsa de compras se acercó al banco.\n5. Alguien llamó desde el teléfono público.",
          " 1. Alguien llegó a la reunión tarde.\n\n2. Alguna mujer se quedó atrás para ayudar al niño que había caído.\n\n3. Alguna persona me llamó hoy por teléfono, pero no pude hablarme con ella.\n\n4. Alguna chica me pidió si podía usar mi bicicleta para ir a la tienda.\n\n5. Alguna mujer se quedó atrás para ayudar al niño que había caído, pero no pudo hacer nada porque ella también tenía un hijo pequeño con ella."
        ],
        "Validation LLM answers": [],
        "Extraction gender": "NULL",
        "Validation gender": "NULL",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 10,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
      },
      "spa-30-00007846-n_alma": {
        "Sense index": "1",
        "Gloss": "Un ser humano.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El alma es la parte más profunda y sagrada del hombre.\n2. La alma es lo que hace a un ser humano único e incomparable.\n3. El alma es la parte más importante de una persona, ya que es lo que la hace vivir.\n4. El alma es el centro de las emociones y los sentimientos humanos.\n5. El alma es lo que hace a un ser humano más que solo una mera suma de partes físicas.",
          " 1. La alma es la parte más profunda y espiritual del hombre.\n2. La alma es lo que hace a un ser humano único e incomparable.\n3. La alma es la parte de nosotros que se conecta con el mundo espiritual.\n4. La alma es lo que nos permite sentir emociones y pasiones intensas.\n5. La alma es la parte de nosotros que sigue viviendo después de nuestra muerte."
        ],
        "Validation LLM answers": [],
        "Extraction gender": "NULL",
        "Validation gender": "NULL",
        "Correctas": 10,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
      },
      "spa-30-00007846-n_individuo": {
        "Sense index": "1",
        "Gloss": "Un ser humano.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. Un hombre es un individuo único y valioso.\n2. El individuo es la unidad básica de la sociedad humana.\n3. Cada individuo tiene derechos humanos inalienables.\n4. Los individuos son responsables de sus acciones.\n5. La educación es una herramienta clave para el desarrollo del individuo.",
          " 1. La mujer es un individuo único y valiosa.\n2. El doctor examinó a la paciente, una individuo que había estado sufriendo dolor intensísimo en el abdomen.\n3. La estudiante es un individuo con muchas habilidades y talentos.\n4. La mujer es un individuo que ha luchado por sus derechos y ha logrado mucho en la comunidad.\n5. La mujer es un individuo que merece ser tratada con respeto y dignidad."
        ],
        "Validation LLM answers": [
          " 1) El individuo es un ser único y distinto. 2) Cada individuo tiene sus propias características. 3) Los individuos son importantes para la sociedad. 4) Un individuo puede tener múltiples roles en la vida. 5) El individuo es un ser complejo y multifacético.\n\n"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "Masculino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
      },
      "spa-30-00015388-n_animal": {
        "Sense index": "1",
        "Gloss": "Un organismo vivo dotado de movimiento voluntario.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El leopardo es un animal carnívoro y depredador.\n2. La cebra es un animal herbívoro y ruminante.\n3. El elefante es un animal grande, herbívoro y terrestre.\n4. El tigre es un animal felino, carnívoro y solitario.\n5. El panda rojo es un animal mamífero, herbívoro y en peligro de extinción.",
          " 1. La elefanta es un animal grande y hermosa que habita en los bosques tropicales.\n2. La gacela es un animal rápido y delicado que corre a gran velocidad en las praderas.\n3. La orca es un animal inteligente y social que vive en grupos en el océano.\n4. La tigresa es un animal poderoso y solitario que caza en la selva.\n5. La ballena jorobada es un animal pacífico y grande que habita en los océanos profundos."
        ],
        "Validation LLM answers": [
          " El animal es un ser capaz de moverse libremente. Los animales son seres vivos que pueden caminar y correr. Un animal puede tener patas para caminar o nadar. Los animales pueden comer, beber y dormir. Los animales pueden ser amigables o peligrosos.\n\n"
        ],
        "Extraction gender": "Masculino",
        "Validation gender": "Masculino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
      },
      "spa-30-00017222-n_planta": {
        "Sense index": "1",
        "Gloss": "(botánica) un organismo vivo que carece del poder de la locomoción.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El árbol es una planta con raíces, tronco, y ramas.\n2. La flor es una pequeña planta herbácea que produce pétalos y frutas.\n3. La hierba es una planta de crecimiento rápido y sin tallo leñoso.\n4. El arbusto es una planta con ramas cortas y gruesas, pero no tan largas como las de un árbol.\n5. La planta acuática es una especie de vegetación que crece en el agua o en la orilla del río.",
          " 1. La planta tiene raíces, tallos y hojas.\n2. La planta absorbe agua y nutrientes a través de sus raíces.\n3. La planta produce energía mediante la fotosíntesis.\n4. La planta no tiene un sistema circulatorio ni una respiración pulmonar.\n5. La planta es una parte importante de la ecología y el medio ambiente."
        ],
        "Validation LLM answers": [
          " 1. La planta es un organismo vivo que no tiene piernas para caminar. 2. Las plantas son capaces de realizar la fotosíntesis para obtener energía. 3. La planta se alimenta a través del suelo y la agua. 4. Las plantas tienen raíces, tallos y hojas como partes principales de su cuerpo. 5. La planta es un organismo que produce oxígeno a través de la fotosíntesis.\n\n"
        ],
        "Extraction gender": "Femenino",
        "Validation gender": "Femenino",
        "Correctas": 0,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 0,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "NULL"
      },
      "spa-30-00021265-n_comida": {
        "Sense index": "7",
        "Gloss": "Cualquier sustancia que puede ser metabolizado por un animal para dar energía y construir tejido.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. La comida es una sustancia alimenticia que contiene nutrientes necesarios para la supervivencia del organismo.\n2. El alimento es una mezcla de materias orgánicas y inorgánicas que se consume por los seres vivos.\n3. La ingesta de comida es un proceso vital que permite a los animales obtener energía y nutrientes para su crecimiento y desarrollo.\n4. El consumo de alimentos es una necesidad biológica que garantiza la supervivencia del organismo en el medio ambiente.\n5. La comida es un producto natural o artificial que se consume por los seres vivos como fuente de energía y nutrientes.",
          " 1. La comida es una sustancia orgánica compleja que contiene carbohidratos, proteínas, grasas, vitaminas y minerales.\n2. El consumo de comida equilibrada es esencial para la salud humana.\n3. La falta de comida adecuada puede llevar a deficiencias nutricionales y enfermedades crónicas.\n4. La comida es una necesidad primaria para los animales, sin la cual no pueden sobrevivir.\n5. La comida es un producto natural que se produce en el cuerpo de las plantas y los animales y se consume por otros organismos como fuente de energía y nutrientes."
        ],
        "Validation LLM answers": [
          " La comida es esencial para la supervivencia de los animales, ya que proporciona energía y nutrientes necesarios para su crecimiento y desarrollo. Las aves necesitan una dieta equilibrada con una variedad de alimentos para mantenerse saludables. Los peces se alimentan principalmente de plancton y crustáceos, pero también pueden consumir carne de otros peces. Los animales herbívoros dependen de plantas como fuente de nutrientes y energía. Los insectos se alimentan de una variedad de sustancias, incluyendo frutas, hojas y semillas."
        ],
        "Extraction gender": "Femenino",
        "Validation gender": "NULL",
        "Correctas": 1,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 4,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 0,
        "Mensaje de información": "La entrada ha terminado su ejecución en la fase de validación."
      },
      "spa-30-00023773-n_motivo": {
        "Sense index": "1",
        "Gloss": "La característica psicológica que desencadena en un organismo la acción hacia un objetivo deseado; el motivo de la acción; lo que da sentido y dirección a la conducta.",
        "Part of speech": "n",
        "Language": "spa",
        "Extraction LLM answers": [
          " 1. El motivo del asesinato fue la envidia.\n2. Su motivo para abandonar la empresa fue la falta de perspectivas profesionales.\n3. La principal motivación de los estudiantes es obtener un título universitario.\n4. El motivo de su éxito es su perseverancia y dedicación.\n5. Su motivo para no asistir a la reunión fue el malestar causado por la enfermedad.",
          " 1. El motivo de su éxito es su pasión por la excelencia.\n2. La falta de confianza es el motivo principal de su fracaso.\n3. Su amor por la justicia es el motivo que la lleva a luchar contra la injusticia.\n4. El miedo al rechazo es el motivo que impide a muchos expresar sus verdaderas opiniones.\n5. La necesidad de superación es el motivo que la lleva a trabajar duro y con dedicación en todo lo que hace."
        ],
        "Validation LLM answers": [],
        "Extraction gender": "NULL",
        "Validation gender": "NULL",
        "Correctas": 7,
        "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase": 0,
        "Incorrectas de tipo 2: la palabra a analizar no aparece en la frase": 1,
        "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género": 2,
        "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
      }
    }
    
    config = ConfigParser()
    config.read('./config.ini')
    
    componenteExporter = ComponenteExporter(config['file_path']['knowledge_table_file_path'])
    
    componenteExporter.export_knowledge(knowledge_table)
    
    # Abrir el archivo en modo lectura
    try:
        with open(config['file_path']['knowledge_table_file_path'], 'r') as archivo:
            # Leer el archivo línea por línea
            for linea in archivo:
                # Comprobar si la línea cumple con los criterios
                if validar_linea(linea):
                    assert True
                else:
                    assert False
    except FileNotFoundError:
        print(f'Archivo "{config["file_path"]["knowledge_table_file_path"]}" no encontrado. Vuelve a introducir una nueva ruta')
        
def validar_linea(linea):
    # Patrón de expresión regular para verificar cada elemento de la línea
    patron = r'^"spa-30-\d{8}-n", "[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+", "\d+", ".+", "n", "spa", "(Femenino|Masculino|NULL)", "------",$'
    # Comprobar si la línea coincide con el patrón
    if re.match(patron, linea.strip()):
        return True
    else:
        return False
    
def auxiliar_functions_test():

    # -----------------------------------   destokenize()   ---------------------------------------
    
    print('Testing destokenize() function')
    
    tokens = []
    new_tokens = []
    assert "" == auxFunctions.destokenize(tokens, new_tokens), "Should be ''"
    
    tokens_2 = ['Hola',',','soy','David''.']
    new_tokens_2 = ['Hola',',','soy','David''.']
    assert "Hola, soy David." == auxFunctions.destokenize(tokens_2, new_tokens_2), "Should be 'Hola, soy David.'"
    
    tokens_3 = ['Hola',',','soy','David''.']
    new_tokens_3 = ['Hola',',','soy']
    assert "Hola, soy" == auxFunctions.destokenize(tokens_3, new_tokens_3), "Should be 'Hola, soy David.'"
    
    print('destokenize() function tested correctly') 
    
    # -----------------------------------   extract_nouns_with_positions()   ---------------------------------------
    
    print('Testing extract_nouns_with_positions() function')
    
    phrase_5 = "La fábrica de papel había estado en funcionamiento durante más de un siglo, proporcionando oportunidades de empleo a generaciones de familias en la zona."
    expected_output_5 = [('fábrica', 1, 'nsubj', 'funcionamiento'), ('papel', 3, 'nmod', 'fábrica'), ('funcionamiento', 7, 'ROOT', 'funcionamiento'), ('siglo', 12, 'nmod', 'funcionamiento'), ('oportunidades', 15, 'obj', 'proporcionando'), ('empleo', 17, 'nmod', 'oportunidades'), ('generaciones', 19, 'nmod', 'oportunidades'), ('familias', 21, 'nmod', 'generaciones'), ('zona', 24, 'nmod', 'familias')]
    assert expected_output_5 == auxFunctions.extract_nouns_with_positions(phrase_5), "Should be true"

    phrase_6 = "El papel es un material muy utilizado para la impresión y la escritura."
    expected_output_6 = [('papel', 1, 'nsubj', 'material'), ('material', 4, 'ROOT', 'material'), ('impresión', 9, 'obl', 'utilizado'), ('escritura', 12, 'conj', 'impresión')]
    assert expected_output_6 == auxFunctions.extract_nouns_with_positions(phrase_6), "Should be true"
  
    phrase_7 = "El árbol más grande del bosque es un roble americano de más de 30 metros de altura."
    expected_output_7 = [('árbol', 1, 'nsubj', 'roble'), ('metros', 14, 'nmod', 'roble'), ('altura', 16, 'nmod', 'metros')]
    assert expected_output_7 == auxFunctions.extract_nouns_with_positions(phrase_7), "Should be true"

    phrase_8 = ""
    expected_output_8 = []
    assert expected_output_8 == auxFunctions.extract_nouns_with_positions(phrase_8), "Should be true"
    
    print('extract_nouns_with_positions() function tested correctly') 
    
    # -----------------------------------   pluralize_word()   ---------------------------------------
    
    print('Testing pluralize_word() function')
    
    # Primer conjunto de palabras en español
    spanish_words_1 = "casa"
    expected_spanish_words_1 = ['casa', 'casas']
    assert expected_spanish_words_1 == auxFunctions.pluralize_word(spanish_words_1), "Should be true"

    # Segundo conjunto de palabras en español
    spanish_words_2 = "perro"
    expected_spanish_words_2 = ['perro', 'perros']
    assert expected_spanish_words_2 == auxFunctions.pluralize_word(spanish_words_2), "Should be true"

    # Tercer conjunto de palabras en español
    spanish_words_3 = "gato"
    expected_spanish_words_3 = ['gato', 'gatos']
    assert expected_spanish_words_3 == auxFunctions.pluralize_word(spanish_words_3), "Should be true"

    # Cuarto conjunto de palabras en español
    spanish_words_4 = "libro"
    expected_spanish_words_4 = ['libro', 'libros']
    assert expected_spanish_words_4 == auxFunctions.pluralize_word(spanish_words_4), "Should be true"

    # Quinto conjunto de palabras en español
    spanish_words_5 = "mesa"
    expected_spanish_words_5 = ['mesa', 'mesas']
    assert expected_spanish_words_5 == auxFunctions.pluralize_word(spanish_words_5), "Should be true"

    # Sexto conjunto de palabras en español
    spanish_words_6 = "flor"
    expected_spanish_words_6 = ['flor', 'flores']
    assert expected_spanish_words_6 == auxFunctions.pluralize_word(spanish_words_6), "Should be true"

    # Séptimo conjunto de palabras en español
    spanish_words_7 = "niño"
    expected_spanish_words_7 = ['niño', 'niños']
    assert expected_spanish_words_7 == auxFunctions.pluralize_word(spanish_words_7), "Should be true"

    # Octavo conjunto de palabras en español
    spanish_words_8 = "mujer"
    expected_spanish_words_8 = ['mujer', 'mujeres']
    assert expected_spanish_words_8 == auxFunctions.pluralize_word(spanish_words_8), "Should be true"

    # Noveno conjunto de palabras en español
    spanish_words_9 = "hombre"
    expected_spanish_words_9 = ['hombre', 'hombres']
    assert expected_spanish_words_9 == auxFunctions.pluralize_word(spanish_words_9), "Should be true"

    # Décimo conjunto de palabras en español
    spanish_words_10 = "juego"
    expected_spanish_words_10 = ['juego', 'juegos']
    assert expected_spanish_words_10 == auxFunctions.pluralize_word(spanish_words_10), "Should be true"

    # Undécimo conjunto de palabras en español
    spanish_words_11 = "pelota"
    expected_spanish_words_11 = ['pelota', 'pelotas']
    assert expected_spanish_words_11 == auxFunctions.pluralize_word(spanish_words_11), "Should be true"

    # Duodécimo conjunto de palabras en español
    spanish_words_12 = "árbol"
    expected_spanish_words_12 = ['árbol', 'árboles']
    assert expected_spanish_words_12 == auxFunctions.pluralize_word(spanish_words_12), "Should be true"

    # Decimotercer conjunto de palabras en español
    spanish_words_13 = "coche"
    expected_spanish_words_13 = ['coche', 'coches']
    assert expected_spanish_words_13 == auxFunctions.pluralize_word(spanish_words_13), "Should be true"

    # Decimocuarto conjunto de palabras en español
    spanish_words_14 = "manzana"
    expected_spanish_words_14 = ['manzana', 'manzanas']
    assert expected_spanish_words_14 == auxFunctions.pluralize_word(spanish_words_14), "Should be true"

    # Decimoquinto conjunto de palabras en español
    spanish_words_15 = "camino"
    expected_spanish_words_15 = ['camino', 'caminos']
    assert expected_spanish_words_15 == auxFunctions.pluralize_word(spanish_words_15), "Should be true"

    # Decimosexto conjunto de palabras en español
    spanish_words_16 = "hijo"
    expected_spanish_words_16 = ['hijo', 'hijos']
    assert expected_spanish_words_16 == auxFunctions.pluralize_word(spanish_words_16), "Should be true"

    # Decimoséptimo conjunto de palabras en español
    spanish_words_17 = "ciudad"
    expected_spanish_words_17 = ['ciudad', 'ciudades']
    assert expected_spanish_words_17 == auxFunctions.pluralize_word(spanish_words_17), "Should be true"

    # Decimoctavo conjunto de palabras en español
    spanish_words_18 = "animal"
    expected_spanish_words_18 = ['animal', 'animales']
    assert expected_spanish_words_18 == auxFunctions.pluralize_word(spanish_words_18), "Should be true"

    # Decimonoveno conjunto de palabras en español
    spanish_words_19 = "reloj"
    expected_spanish_words_19 = ['reloj', 'relojes']
    assert expected_spanish_words_19 == auxFunctions.pluralize_word(spanish_words_19), "Should be true"

    # Vigésimo conjunto de palabras en español
    spanish_words_20 = "luz"
    expected_spanish_words_20 = ['luz', 'luces']
    assert expected_spanish_words_20 == auxFunctions.pluralize_word(spanish_words_20), "Should be true"

    # Vigésimo primer conjunto de palabras en español
    spanish_words_21 = "rey"
    expected_spanish_words_21 = ['rey', 'reyes']
    assert expected_spanish_words_21 == auxFunctions.pluralize_word(spanish_words_21), "Should be true"

    # Vigésimo segundo conjunto de palabras en español
    spanish_words_22 = "cielo"
    expected_spanish_words_22 = ['cielo', 'cielos']
    assert expected_spanish_words_22 == auxFunctions.pluralize_word(spanish_words_22), "Should be true"

    # Vigésimo tercer conjunto de palabras en español
    spanish_words_23 = "flor"
    expected_spanish_words_23 = ['flor', 'flores']
    assert expected_spanish_words_23 == auxFunctions.pluralize_word(spanish_words_23), "Should be true"

    # Vigésimo cuarto conjunto de palabras en español
    spanish_words_24 = "café"
    expected_spanish_words_24 = ['café', 'cafés']
    assert expected_spanish_words_24 == auxFunctions.pluralize_word(spanish_words_24), "Should be true"
    
    # Vigésimo quinto conjunto de palabras en español
    spanish_words_25 = "voz"
    expected_spanish_words_25 = ['voz', 'voces']
    assert expected_spanish_words_25 == auxFunctions.pluralize_word(spanish_words_25), "Should be true"
    
    print('pluralize_word() function tested correctly') 
    
    
    # -----------------------------------   is_possessive()   ---------------------------------------
    
    print('Testing is_possessive() function')
    
      # Primer conjunto de palabras en inglés
    tokens_1 = ["John", "'", "s", "book"]
    index_1 = 0
    expected_1 = True
    assert expected_1 == auxFunctions.is_possessive(tokens_1, index_1), "Test 1 failed"

    # Segundo conjunto de palabras en inglés
    tokens_2 = ["The", "cat", "'", "s", "tail"]
    index_2 = 1
    expected_2 = False
    assert expected_2 == auxFunctions.is_possessive(tokens_2, index_2), "Test 2 failed"

    # Tercer conjunto de palabras en inglés
    tokens_3 = ["This", "is", "Sarah", "'", "s", "pen"]
    index_3 = 2
    expected_3 = True
    assert expected_3 == auxFunctions.is_possessive(tokens_3, index_3), "Test 3 failed"

    # Cuarto conjunto de palabras en inglés
    tokens_4 = ["This", "is", "the", "book"]
    index_4 = 2
    expected_4 = False
    assert expected_4 == auxFunctions.is_possessive(tokens_4, index_4), "Test 4 failed"

    # Quinto conjunto de palabras en inglés
    tokens_5 = ["The", "dogs", "are", "playing"]
    index_5 = 1
    expected_5 = False
    assert expected_5 == auxFunctions.is_possessive(tokens_5, index_5), "Test 5 failed"

    print('is_possessive() function tested correctly')
    
    
    # -----------------------------------   extract_llm_answers_set_of_phrases()   ---------------------------------------
    
    print('Testing extract_llm_answers_set_of_phrases() function')
    
    elemento_prueba_piloto_masculino = "\n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras."

    expected_output_piloto_masculino = ["El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.",
                              "La tierra está siendo devastada por los cambios climáticos y la deforestación.",
                              "La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.",
                              "El hombre ha estado explotando y devastando la tierra durante siglos.",
                              "La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.",
                              "La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.",
                              "La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.",
                              "La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.",
                              "La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.",
                              "La tierra es un legado que debemos preservar para las generaciones futuras."]
    
    assert expected_output_piloto_masculino == auxFunctions.extract_llm_answers_set_of_phrases(elemento_prueba_piloto_masculino), "Should be true"
    
    elemento_prueba_piloto_femenino = "1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."

    expected_output_piloto_femenino = ["La tierra es una madre generosa que nos da sustento.",
                                       "La tierra es una hermosa dama que necesita nuestra atención y amor.",
                                       "La tierra es una piel que nos cubre y protege.",
                                       "La tierra es una madre que nos guía y nos da vida.",
                                       "La tierra es una madre que nos da alimentos y agua.",
                                       "La tierra es una madre que nos da un lugar en la que vivir y crecer.",
                                       "La tierra es una madre que nos da un hogar y una casa.",
                                       "La tierra es una madre que nos da un lugar en la que compartir nuestras vidas.",
                                       "La tierra es una madre que nos da un lugar en la que vivir y crecer juntos.",
                                       "La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."]
    
    assert expected_output_piloto_femenino == auxFunctions.extract_llm_answers_set_of_phrases(elemento_prueba_piloto_femenino), "Should be true"
    
    print('extract_llm_answers_set_of_phrases() function tested correctly')
    
    # -----------------------------------   extract_llm_answers_translation()   ---------------------------------------
    
    print('Testing extract_llm_answers_translation() function')
    
    elemento_prueba_piloto = "Alguien que posee una licencia para operar un avión en vuelo."

    expected_output_piloto = "Alguien que posee una licencia para operar un avión en vuelo."
    assert expected_output_piloto == auxFunctions.extract_llm_answers_translation(elemento_prueba_piloto), "Should be true"

    elemento_prueba_accion = "'una acción'\n\n"

    expected_output_accion = "Una acción."
    assert expected_output_accion == auxFunctions.extract_llm_answers_translation(elemento_prueba_accion), "Should be true"


    print('extract_llm_answers_translation() function tested correctly')

# Método main
if __name__ == "__main__":
    print("Test started: first pilot case")
    print("Testing over Importer component...")
    component_importer_test() # Tested correctly
    print("Everything in Importer component passed")
    print("Testing over Question Maker Traduction component...")
    component_question_maker_traduction_test() # Tested correctly
    print("Everything in Question Maker Traduction component passed")
    print("Testing over Question Maker Extraction component...")
    component_question_maker_extraction_test() # Tested correctly
    print("Everything in Question Maker Extraction component passed")
    print("Testing over Question Maker Validation component...")
    component_question_maker_validation_test() # Tested correctly
    print("Everything in Question Maker Validation component passed")
    print("Testing over LLM Communicator component...")
    component_llm_communicator_test() # Tested correctly
    print("Everything in LLM Communicator component passed")
    print("Testing over Extractor gloss translation component...")
    component_extractor_gloss_translation_test() # Tested correctly
    print("Everything in Extractor gloss translation component passed")
    print("Testing over Extractor extraccion component...")
    component_extractor_extraccion_test() # Tested correctly
    print("Everything in Extractor extraccion component passed")
    print("Testing over Extractor validacion component...")
    component_extractor_validacion_test() # Tested correctly
    print("Everything in Validator validacion component passed")
    print("Testing over Exporter component...")
    component_exporter_test() # Tested correctly
    print("Everything in Exporter component passed")
    print("Testing over Auxiliar funcitions...")
    auxiliar_functions_test() # Tested correctly
    print("Everything in Auxiliar funcitions passed")
    print("Everything passed")