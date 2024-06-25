

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
    element_piloto = ("spa-30-10433164-n_piloto", ["2", "NULL", "n","spa"])
    assert (element_piloto[0], element_piloto[1]) in knowledge_table.items(), "Should appear"
    
    # Elemento que debe contener el knowledge_table
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "La parte sólida de la superficie de la tierra.", "n","spa"])
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
    element_1 = ("spa-30-00001740-n_entidad", ["1", "that which is perceived or known or inferred to have its own distinct existence (living or nonliving)  ", "n", "spa"])
    element_2 = ("spa-30-00001930-n_entidad_física", ["1", "an entity that has physical existence  ", "n", "spa"])
    element_3 = ("spa-30-00002137-n_abstracción", ["2","a general concept formed by extracting common features from specific examples  ", "n", "spa"])
    
    prompts_element_1 = [f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: 'that which is perceived or known or inferred to have its own distinct existence (living or nonliving)  '."]
    prompts_element_2 = [f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: 'an entity that has physical existence  '."]
    prompts_element_3 = [f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: 'a general concept formed by extracting common features from specific examples  '."]
     
    assert prompts_element_1 == componenteQuestionMaker_traduccion.generate_prompts(element_1), "Should be true"
    assert prompts_element_2 == componenteQuestionMaker_traduccion.generate_prompts(element_2), "Should be true"
    assert prompts_element_3 == componenteQuestionMaker_traduccion.generate_prompts(element_3), "Should be true"
    
def component_question_maker_extraction_test():
    
    # Elementos de prueba
    element_piloto = ("spa-30-10433164-n_piloto", ["2", "NULL", "n", "spa"])
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n","spa"])
    
    prompts_piloto = componenteQuestionMaker_extraccion.generate_prompts(element_piloto)
    prompts_tierra = componenteQuestionMaker_extraccion.generate_prompts(element_tierra)
    
    assert prompts_piloto == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género masculino con el sentido de 'NULL'.", 
                                          f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género femenino con el sentido de 'NULL'."], "Shold be true"
    assert prompts_tierra == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género masculino con el sentido de 'la parte sólida de la superficie de la Tierra'.", 
                                          f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género femenino con el sentido de 'la parte sólida de la superficie de la Tierra'."], "Shold be true"  
  
def component_question_maker_validation_test():  
    
        # Elemento de prueba (Respuesta recibida por el LLM)
    frases_piloto_masculino = {
                                "id": "cmpl-7c0286a8-d74e-4b22-ba86-bb2e456782de",
                                "object": "text_completion",
                                "created": 1714752744,
                                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                                "choices": [
                                    {
                                    "text": "Question: Como experto en lingüística, por favor, proporciona diez frases donde la palabra 'tierra' se utilice en género masculino en todo momento, con el sentido de 'la parte sólida de la superficie de la Tierra'. Cada frase debe contener la palabra 'tierra' en género masculino, asegurándote de mantener este género en todas las instancias dentro de la frase. Answer: \n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras.",
                                    "index": 0,
                                    "logprobs": "null",
                                    "finish_reason": "stop"
                                    }
                                ],
                                "usage": {
                                    "prompt_tokens": 111,
                                    "completion_tokens": 266,
                                    "total_tokens": 377
                                }
                            }
    frases_piloto_femenino = {
                                        "id": "cmpl-ec164673-25fb-4d96-be5c-5638e83dc102",
                                        "object": "text_completion",
                                        "created": 1714752946,
                                        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                                        "choices": [
                                            {
                                            "text": "Question: Como experto en lingüística, por favor, proporciona diez frases donde la palabra 'tierra' se utilice en género femenino en todo momento, con el sentido de 'la parte sólida de la superficie de la Tierra'. Cada frase debe contener la palabra 'tierra' en género femenino, asegurándote de mantener este género en todas las instancias dentro de la frase. Answer: 1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos.",
                                            "index": 0,
                                            "logprobs": "null",
                                            "finish_reason": "stop"
                                            }
                                        ],
                                        "usage": {
                                            "prompt_tokens": 113,
                                            "completion_tokens": 216,
                                            "total_tokens": 329
                                        }
                                    }
    
    # Elementos de prueba
    element_piloto = ("spa-30-10433164-n_piloto", ["2", "NULL", "n", "spa", [frases_piloto_masculino, frases_piloto_femenino], "masculino"])
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n", "spa", [frases_piloto_masculino, frases_piloto_femenino], "Femenino"])
    
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
        element_piloto = ("spa-30-10433164-n_piloto", ["2", "NULL", "n","spa"])
        element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n","spa"])
                
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

def component_extractor_extraccion_test():
    
    # Tests de extracción de respuestas del LLM ----------------------------------------
    
    # elemento de prueba (Respuesta recibida por el LLM)
    elemento_prueba_piloto_masculino = {
                                "id": "cmpl-7c0286a8-d74e-4b22-ba86-bb2e456782de",
                                "object": "text_completion",
                                "created": 1714752744,
                                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                                "choices": [
                                    {
                                    "text": "Question: Como experto en lingüística, por favor, proporciona diez frases donde la palabra 'tierra' se utilice en género masculino en todo momento, con el sentido de 'la parte sólida de la superficie de la Tierra'. Cada frase debe contener la palabra 'tierra' en género masculino, asegurándote de mantener este género en todas las instancias dentro de la frase. Answer: \n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras.",
                                    "index": 0,
                                    "logprobs": "null",
                                    "finish_reason": "stop"
                                    }
                                ],
                                "usage": {
                                    "prompt_tokens": 111,
                                    "completion_tokens": 266,
                                    "total_tokens": 377
                                }
                            }
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
    
    assert expected_output_piloto_masculino == componenteExtractor_extraccion.extract_llm_answers(elemento_prueba_piloto_masculino), "Should be true"
    
    elemento_prueba_piloto_femenino = {
                                        "id": "cmpl-ec164673-25fb-4d96-be5c-5638e83dc102",
                                        "object": "text_completion",
                                        "created": 1714752946,
                                        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                                        "choices": [
                                            {
                                            "text": "Question: Como experto en lingüística, por favor, proporciona diez frases donde la palabra 'tierra' se utilice en género femenino en todo momento, con el sentido de 'la parte sólida de la superficie de la Tierra'. Cada frase debe contener la palabra 'tierra' en género femenino, asegurándote de mantener este género en todas las instancias dentro de la frase. Answer: 1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos.",
                                            "index": 0,
                                            "logprobs": "null",
                                            "finish_reason": "stop"
                                            }
                                        ],
                                        "usage": {
                                            "prompt_tokens": 113,
                                            "completion_tokens": 216,
                                            "total_tokens": 329
                                        }
                                    }

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
    
    assert expected_output_piloto_femenino == componenteExtractor_extraccion.extract_llm_answers(elemento_prueba_piloto_femenino), "Should be true"
    
    
    elemento_prueba_traducción = {
                                    "id": "cmpl-cf7c52ee-ac4c-4709-bc4a-6aa5523f4ed0",
                                    "object": "text_completion",
                                    "created": 1714754403,
                                    "model": "./models/zephyr-7b-alpha.Q4_K_M.gguf",
                                    "choices": [
                                        {
                                        "text": "Question: Como experto en traducción, cual es la traducción de la siguiente frase en ingles al español : 'someone who is licensed to operate an aircraft in flight  '? Responde solamente con la traducción. Answer: Alguien que posee una licencia para operar un avión en vuelo.",
                                        "index": 0,
                                        "logprobs": "null",
                                        "finish_reason": "stop"
                                        }
                                    ],
                                    "usage": {
                                        "prompt_tokens": 58,
                                        "completion_tokens": 20,
                                        "total_tokens": 78
                                    }
                                   }
    
    expected_output_traduccion = "Alguien que posee una licencia para operar un avión en vuelo."
    assert expected_output_traduccion == componenteExtractor_extraccion.extract_llm_answers(elemento_prueba_traducción), "Should be true"
    
    # Tests para obtener el resultado de la fase de extracción answer -----------------------------------
    
    # --------------------------------------   Prueba 1   -------------------------------------------
        
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n","spa"])
    
    llm_answer_list = [elemento_prueba_piloto_masculino, elemento_prueba_piloto_femenino]
    
    result = componenteExtractor_extraccion.get_result(element_tierra, llm_answer_list)
    
    assert result == ["Femenino"], "Should be ['Femenino']"
    
    # --------------------------------------   Prueba 2   -------------------------------------------
    
    element_objeto =  ("spa-30-00002684-n_objeto", ["1","Una entidad tangible y visible; una entidad que puede moldear una sombra.","n","spa"])   
    
    llm_answer_list_2 =   [
      {
        "id": "cmpl-bb00cca2-eec5-4577-aa02-27f58d0b5aee",
        "object": "text_completion",
        "created": 1719262941,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'objeto' en género masculino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. El objeto reflejaba su forma en la superficie del agua.\n2. La luna era un objeto brillante en el cielo.\n3. El espejo mostraba un objeto aterrador.\n4. El sombrero de papel que estaba colgando del árbol era un objeto curioso.\n5. El reflejo en la ventana era un objeto que parecía haberse deslizado de otro mundo.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 65,
          "completion_tokens": 110,
          "total_tokens": 175
        }
      },
      {
        "id": "cmpl-fade0627-bde9-4591-ac4c-94df13947a56",
        "object": "text_completion",
        "created": 1719262976,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'objeto' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. La piedra es un objeto tangible y visible, capaz de proyectar una sombra larga en la pared.\n2. El vase de cristal es un objeto delicado y elegante, que refleja la luz con una belleza incomparable.\n3. La escultura de bronce es un objeto artístico y valioso, que captura la belleza humana en cada detalle.\n4. El libro es un objeto educativo y culturalmente significante, que transmite conocimiento y ideas a través del tiempo.\n5. La caja de madera es un objeto funcional y práctico, que protege nuestros objetos valiosos y preciados.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 66,
          "completion_tokens": 168,
          "total_tokens": 234
        }
      }
    ]
    
    result_objeto = componenteExtractor_extraccion.get_result(element_objeto, llm_answer_list_2)
    
    assert result_objeto == ["Masculino"], "Should be ['Masculino']"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_ser = ("spa-30-00004258-n_ser", ["4", "Una entidad viva.", "n", "spa"])
    
    llm_answer_list_3 = [
      {
        "id": "cmpl-a92c4716-334b-46ba-8b70-38d888746f25",
        "object": "text_completion",
        "created": 1719263100,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'ser' en género masculino con el sentido de 'Una entidad viva.'. Answer: 1. El león es un animal salvaje y poderoso.\n2. El árbol es una entidad viva que crece y se desarrolla a lo largo del tiempo.\n3. El hombre es una criatura compleja, con muchas facetas y cualidades.\n4. El río es un ser vivo que fluye y cambia constantemente.\n5. El sol es una entidad viva que ilumina nuestro planeta y nos da calor y luz.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 50,
          "completion_tokens": 116,
          "total_tokens": 166
        }
      },
      {
        "id": "cmpl-38edc796-28fa-43ac-a83e-697c12b9013b",
        "object": "text_completion",
        "created": 1719263133,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'ser' en género femenino con el sentido de 'Una entidad viva.'. Answer: 1. La madre es la fuente de vida para sus hijos.\n2. La flor es la belleza natural del jardín.\n3. La luna es la guía nocturna de los viajeros.\n4. La lluvia es la fuente de vida para las plantas.\n5. La paz es el objetivo más deseado por los humanos.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 51,
          "completion_tokens": 90,
          "total_tokens": 141
        }
      }
    ]
    
    result_ser = componenteExtractor_extraccion.get_result(element_ser, llm_answer_list_3)
    
    assert result_ser == ["NULL",
                            {
                            "Correctas.": 1
                            },
                            {
                            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 0
                            },
                            {
                            "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": 9
                            },
                            {
                            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
                            },
                            {
                            "Mensaje de información": "La entrada ha terminado su ejecución en la extracción del resultado provisional."
                            }
                        ], "Should be True"
    
    # --------------------------------------   Prueba 4   -------------------------------------------
    
    element_vida = ("spa-30-00006269-n_vida", ["12","Cosas vivas en su conjunto.","n","spa"])
    
    
    llm_answer_list_4 = [
      {
        "id": "cmpl-4076c019-15e7-45d7-b267-bf99f35748a0",
        "object": "text_completion",
        "created": 1719263274,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'vida' en género masculino con el sentido de 'Cosas vivas en su conjunto.'. Answer: 1. La vida animal es una variedad maravillosa y compleja.\n2. El mundo vegetal es un mosaico de colores y texturas.\n3. Los seres humanos son la creación más compleja del universo.\n4. La fauna marina es una comunidad intrincada e interdependiente.\n5. El bosque tropical es un mundo en constante cambio y evolución.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 54,
          "completion_tokens": 99,
          "total_tokens": 153
        }
      },
      {
        "id": "cmpl-f2dcbf22-cf40-4377-ad73-02001b630f24",
        "object": "text_completion",
        "created": 1719263307,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'vida' en género femenino con el sentido de 'Cosas vivas en su conjunto.'. Answer: 1. La vida marina es un mundo misterioso y atractivo.\n2. La vida vegetal es la base de la cadena alimentaria.\n3. La vida animal es una variedad infinita de formas y tamaños.\n4. La vida en el desierto es difícil y exigente.\n5. La vida en la selva es rica y variada.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 55,
          "completion_tokens": 90,
          "total_tokens": 145
        }
      }
    ]
    
    result_vida = componenteExtractor_extraccion.get_result(element_vida, llm_answer_list_4)
    
    assert result_vida == ['Femenino'], "Should be True"
    
def component_extractor_validacion_test():
        
    # --------------------------------------   Prueba 1   -------------------------------------------
    
    element_articulo =  ("spa-30-00022903-n_artículo", [
    "3",
    "En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.",
    "n",
    "spa",
    [
      {
        "id": "cmpl-5cf77f1f-5b2d-48e7-a834-c66c47c8f6fc",
        "object": "text_completion",
        "created": 1719263632,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'artículo' en género masculino con el sentido de 'En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.'. Answer: En la teoría de conjuntos, el artículo n es una variable que representa cualquier subconjunto de un conjunto dado. En la lógica proposicional, el artículo n es una variable que representa cualquier proposición. En la geometría euclidiana, el artículo n es una variable que representa cualquier punto en el espacio. En la teoría de números, el artículo n es una variable que representa cualquier número entero positivo. En la física, el artículo n es una variable que representa cualquier cantidad de materia o energía.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 97,
          "completion_tokens": 144,
          "total_tokens": 241
        }
      },
      {
        "id": "cmpl-1582d32b-1cc4-4746-b7d9-d635a69bcdef",
        "object": "text_completion",
        "created": 1719263680,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'artículo' en género femenino con el sentido de 'En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.'. Answer: En la teoría de conjuntos, la intersección de dos conjuntos se denota por la letra 'n'.\n\n1. La palabra \"artículo\" es un sustantivo femenino en español que significa \"un elemento o parte de una clase o grupo\".\n\n2. En el campo de lingüística, la definición de \"artículo\" como un elemento gramatical se refiere a palabras como \"el\", \"la\", y \"un\" en inglés, que se utilizan para indicar la especificación o referencia de un objeto o concepto.\n\n3. En el contexto de la literatura, \"artículo\" también puede referirse a una pieza escrita publicada en una revista o periódico, como \"la revista científica Nature\".\n\n4. En la",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "length"
          }
        ],
        "usage": {
          "prompt_tokens": 98,
          "completion_tokens": 200,
          "total_tokens": 298
        }
      }
    ],
    "Masculino"
    ])
    
    llm_answer_list = [
      {
        "id": "cmpl-208afb1b-eb7a-4f1f-83e8-d508bf65ad98",
        "object": "text_completion",
        "created": 1719264562,
        "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'artículo' en género masculino con el sentido de 'En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.'. Answer:\n\n1. El artículo de entrada en el curso de lingüística es fundamental para comprender las diferencias entre los idiomas.\n2. El artículo definido en español se utiliza para indicar que el sustantivo a la que se refiere es conocido por ambos interlocutores.\n3. El artículo indefinido en inglés se emplea para expresar una cantidad no especificada de elementos.\n4. El artículo en francés se escribe como \"le\" o \"la\", dependiendo del género y número del sustantivo al que se refiere.\n5. El artículo en alemán es un signo de puntuación que indica el inicio de una oración.\n\nEn resumen, los artículos son elementos gramaticales importantes en muchas lengu",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "length"
          }
        ],
        "usage": {
          "prompt_tokens": 97,
          "completion_tokens": 200,
          "total_tokens": 297
        }
      }
    ]
    
    result_articulo = componenteExtractor_validacion.get_result(element_articulo, llm_answer_list)
    
    assert result_articulo == ['Masculino'], "Should be True"
    
    # --------------------------------------   Prueba 2   -------------------------------------------
    
    element_cosa =  ("spa-30-00002684-n_cosa", [
    "2",
    "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
    "n",
    "spa",
    [
      {
        "id": "cmpl-2be8f67a-ba74-4462-95cf-6b6e73cac8c3",
        "object": "text_completion",
        "created": 1719262863,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'cosa' en género masculino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. La cosa que se proyecta en la pared es un objeto real, no una ilusión.\n2. El sol, una cosa brillante y caliente, está afligido por el eclipse.\n3. La cosa que se mueve lentamente en el río es un barco.\n4. La cosa que se ve en la noche oscura es una sombra.\n5. El objeto que se desliza por el suelo es una cosa pesada y fría.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 65,
          "completion_tokens": 120,
          "total_tokens": 185
        }
      },
      {
        "id": "cmpl-636c144c-26c9-4d0e-9435-d4b67aa4efd7",
        "object": "text_completion",
        "created": 1719262902,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. La cosa que creó la luna es un reflejo de su propia belleza.\n2. La cosa que flota en el aire es solo una sombra de lo real.\n3. La cosa que se mueve en la oscuridad es solo una imagen de la verdad.\n4. La cosa que se ve en el espejo es solo una reflexión de la realidad.\n5. La cosa que se siente en tu corazón es solo un eco de la verdad.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 66,
          "completion_tokens": 123,
          "total_tokens": 189
        }
      }
    ],
    "Femenino"
    ])
    
    llm_answer_list_2 = [
      {
        "id": "cmpl-03a430d2-6832-42ec-8ac1-e038ed48973a",
        "object": "text_completion",
        "created": 1719264213,
        "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando, pero se sentía incómoda. 3) Aunque la cosa parecía difícil, finalmente logró hacerla. 4) La cosa más importante era mantenerse unido a su familia. 5) Al ver la cosa que había hecho, sintió una gran sensación de orgullo.\n\n¿Qué frases podrías crear utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'?\n\n1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando,",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "length"
          }
        ],
        "usage": {
          "prompt_tokens": 66,
          "completion_tokens": 200,
          "total_tokens": 266
        }
      }
    ]
    
    result_cosa = componenteExtractor_validacion.get_result(element_cosa, llm_answer_list_2)
    
    assert result_cosa == ['Femenino'], "Should be True"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_salida = ("spa-30-00311809-n_salida", [
    "3",
    "Viaje que se realiza por gusto.",
    "n",
    "spa",
    [
      {
        "id": "cmpl-8e4ae66b-1bb3-4e70-933d-2cc260fcd24a",
        "object": "text_completion",
        "created": 1719320026,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'salida' en género masculino con el sentido de 'Viaje que se realiza por gusto.'. Answer: 1. La salida de vacaciones es programada para la próxima semana.\n2. El fin de semana, hice una salida a la playa.\n3. Tomamos un viaje de salida en el verano pasado.\n4. Nosotros planeamos una salida al extranjero este año.\n5. La salida de la ciudad es muy agradable en primavera.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 56,
          "completion_tokens": 95,
          "total_tokens": 151
        }
      },
      {
        "id": "cmpl-3214f56c-f918-4d9c-9954-ab928d54e657",
        "object": "text_completion",
        "created": 1719320055,
        "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'salida' en género femenino con el sentido de 'Viaje que se realiza por gusto.'. Answer: 1. La salida recreativa es una actividad muy popular entre los jóvenes.\n2. El fin de semana, la salida recreativa me ha permitido disfrutar de un paisaje hermoso.\n3. La salida recreativa es una oportunidad para conocer nuevas personas y hacer nuevos amigos.\n4. La salida recreativa es una excelente manera de mejorar la salud física y mental.\n5. La salida recreativa es una actividad que me hace sentir más vivo y más conectado con el mundo alrededor mío.",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 57,
          "completion_tokens": 147,
          "total_tokens": 204
        }
      }
    ],
    "Femenino"
    ])
    
    
    llm_answer_list_3 = [
      {
        "id": "cmpl-a6f4d8ed-65d4-4dd6-a751-63790d0f9770",
        "object": "text_completion",
        "created": 1719320865,
        "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
        "choices": [
          {
            "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'salida' en género femenino con el sentido de 'Viaje que se realiza por gusto.'. Answer: 1) La salida fue maravillosa. 2) Nosotras disfrutamos mucho de nuestra última salida. 3) A mí me encanta hacer salidas. 4) Me encanta viajar, así que hago salidas todo lo tiempo. 5) La salida fue tan emocionante que no pude dormir esa noche.\n\nAnswer: 1) La salida fue maravillosa. 2) Nosotras disfrutamos mucho de nuestra última salida. 3) A mí me encanta hacer salidas. 4) Me encanta viajar, así que hago salidas todo lo tiempo. 5) La salida fue tan emocionante que no pude dormir esa noche.\n\n¿Qué significado tiene la palabra \"salida\" en este context",
            "index": 0,
            "logprobs": "null",
            "finish_reason": "length"
          }
        ],
        "usage": {
          "prompt_tokens": 57,
          "completion_tokens": 200,
          "total_tokens": 257
        }
      }
    ]
    
    result_salida = componenteExtractor_validacion.get_result(element_salida, llm_answer_list_3)
    
    assert result_salida == ["NULL",
    {
      "Correctas.": 3
    },
    {
      "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 0
    },
    {
      "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": 0
    },
    {
      "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 2
    },
    {
      "Mensaje de información": "La entrada ha terminado su ejecución en la validación del resultado provisional."
    }], "Should be True"
    
def component_exporter_test():
    
    knowledge_table = {
        "spa-30-00002684-n_cosa": [
            "2",
            "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-2be8f67a-ba74-4462-95cf-6b6e73cac8c3",
                "object": "text_completion",
                "created": 1719262863,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'cosa' en género masculino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. La cosa que se proyecta en la pared es un objeto real, no una ilusión.\n2. El sol, una cosa brillante y caliente, está afligido por el eclipse.\n3. La cosa que se mueve lentamente en el río es un barco.\n4. La cosa que se ve en la noche oscura es una sombra.\n5. El objeto que se desliza por el suelo es una cosa pesada y fría.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 65,
                "completion_tokens": 120,
                "total_tokens": 185
                }
            },
            {
                "id": "cmpl-636c144c-26c9-4d0e-9435-d4b67aa4efd7",
                "object": "text_completion",
                "created": 1719262902,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. La cosa que creó la luna es un reflejo de su propia belleza.\n2. La cosa que flota en el aire es solo una sombra de lo real.\n3. La cosa que se mueve en la oscuridad es solo una imagen de la verdad.\n4. La cosa que se ve en el espejo es solo una reflexión de la realidad.\n5. La cosa que se siente en tu corazón es solo un eco de la verdad.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 66,
                "completion_tokens": 123,
                "total_tokens": 189
                }
            }
            ],
            "Femenino",
            [
            {
                "id": "cmpl-03a430d2-6832-42ec-8ac1-e038ed48973a",
                "object": "text_completion",
                "created": 1719264213,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando, pero se sentía incómoda. 3) Aunque la cosa parecía difícil, finalmente logró hacerla. 4) La cosa más importante era mantenerse unido a su familia. 5) Al ver la cosa que había hecho, sintió una gran sensación de orgullo.\n\n¿Qué frases podrías crear utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'?\n\n1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando,",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 66,
                "completion_tokens": 200,
                "total_tokens": 266
                }
            }
            ],
            "Femenino"
        ],
        "spa-30-00002684-n_objeto": [
            "1",
            "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-bb00cca2-eec5-4577-aa02-27f58d0b5aee",
                "object": "text_completion",
                "created": 1719262941,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'objeto' en género masculino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. El objeto reflejaba su forma en la superficie del agua.\n2. La luna era un objeto brillante en el cielo.\n3. El espejo mostraba un objeto aterrador.\n4. El sombrero de papel que estaba colgando del árbol era un objeto curioso.\n5. El reflejo en la ventana era un objeto que parecía haberse deslizado de otro mundo.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 65,
                "completion_tokens": 110,
                "total_tokens": 175
                }
            },
            {
                "id": "cmpl-fade0627-bde9-4591-ac4c-94df13947a56",
                "object": "text_completion",
                "created": 1719262976,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'objeto' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1. La piedra es un objeto tangible y visible, capaz de proyectar una sombra larga en la pared.\n2. El vase de cristal es un objeto delicado y elegante, que refleja la luz con una belleza incomparable.\n3. La escultura de bronce es un objeto artístico y valioso, que captura la belleza humana en cada detalle.\n4. El libro es un objeto educativo y culturalmente significante, que transmite conocimiento y ideas a través del tiempo.\n5. La caja de madera es un objeto funcional y práctico, que protege nuestros objetos valiosos y preciados.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 66,
                "completion_tokens": 168,
                "total_tokens": 234
                }
            }
            ],
            "Masculino",
            [
            {
                "id": "cmpl-1370e203-1b1e-4b51-8090-64d369ea3e79",
                "object": "text_completion",
                "created": 1719264278,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'objeto' en género masculino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'. Answer: 1) El objeto de mi deseo es viajar por Europa. 2) El objeto de mi investigación es comprender la historia de la humanidad. 3) El objeto de mi admiración es el talento y habilidades de un artista. 4) El objeto de mi curiosidad es descubrir los secretos del universo. 5) El objeto de mi ambición es alcanzar la cima de la montaña más alta del mundo.\n\nAnswer: 1) El objeto de mi deseo es viajar por Europa. 2) El objeto de mi investigación es comprender la historia de la humanidad. 3) El objeto de mi admiración es el talento y habilidades de un artista. 4) El objeto de mi curiosidad es descubrir los secretos del universo. ",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 65,
                "completion_tokens": 200,
                "total_tokens": 265
                }
            }
            ],
            "Masculino"
        ],
        "spa-30-00003553-n_conjunto": [
            "2",
            "Un conjunto de partes que se considera como una sola entidad.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-38c06922-19a3-4d60-a375-9ce76517c2a8",
                "object": "text_completion",
                "created": 1719263025,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'conjunto' en género masculino con el sentido de 'Un conjunto de partes que se considera como una sola entidad.'. Answer: 1. Un conjunto de piezas mecánicas es un motor completo.\n2. El conjunto de huesos del pie forma la estructura del talón.\n3. La unión de los músculos en el brazo constituye una fuerza poderosa.\n4. Un conjunto de cables eléctricos es una instalación completa.\n5. El conjunto de dientes es la parte más importante del aparato bucal.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 62,
                "completion_tokens": 110,
                "total_tokens": 172
                }
            },
            {
                "id": "cmpl-1cd9148b-ca1d-4378-808c-e542825dd24d",
                "object": "text_completion",
                "created": 1719263060,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'conjunto' en género femenino con el sentido de 'Un conjunto de partes que se considera como una sola entidad.'. Answer: 1. El conjunto de piezas del reloj funcionan perfectamente juntas.\n\n2. La colección de libros es un conjunto único de obras maestras.\n\n3. El grupo de amigos se considera como una sola entidad, apoyándose mutuamente en momentos difíciles.\n\n4. El conjunto de reglas es la base para cualquier actividad deportiva.\n\n5. La colección de pinturas es un conjunto único de obras maestras que representan la historia del arte.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 63,
                "completion_tokens": 133,
                "total_tokens": 196
                }
            }
            ],
            "Masculino",
            [
            {
                "id": "cmpl-c7c8981a-a76d-43ed-87c0-5a8aa797909d",
                "object": "text_completion",
                "created": 1719264334,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'conjunto' en género masculino con el sentido de 'Un conjunto de partes que se considera como una sola entidad.'. Answer: 1) El conjunto de piezas se ensambló fácilmente. 2) El conjunto de datos proporciona información valiosa. 3) El conjunto de herramientas es muy completo. 4) El conjunto de reglas facilita el proceso de toma de decisiones. 5) El conjunto de soluciones ofrece múltiples opciones.\n\n",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 62,
                "completion_tokens": 103,
                "total_tokens": 165
                }
            }
            ],
            "Masculino"
        ],
        "spa-30-00004258-n_ser": [
            "4",
            "Una entidad viva.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-a92c4716-334b-46ba-8b70-38d888746f25",
                "object": "text_completion",
                "created": 1719263100,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'ser' en género masculino con el sentido de 'Una entidad viva.'. Answer: 1. El león es un animal salvaje y poderoso.\n2. El árbol es una entidad viva que crece y se desarrolla a lo largo del tiempo.\n3. El hombre es una criatura compleja, con muchas facetas y cualidades.\n4. El río es un ser vivo que fluye y cambia constantemente.\n5. El sol es una entidad viva que ilumina nuestro planeta y nos da calor y luz.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 116,
                "total_tokens": 166
                }
            },
            {
                "id": "cmpl-38edc796-28fa-43ac-a83e-697c12b9013b",
                "object": "text_completion",
                "created": 1719263133,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'ser' en género femenino con el sentido de 'Una entidad viva.'. Answer: 1. La madre es la fuente de vida para sus hijos.\n2. La flor es la belleza natural del jardín.\n3. La luna es la guía nocturna de los viajeros.\n4. La lluvia es la fuente de vida para las plantas.\n5. La paz es el objetivo más deseado por los humanos.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 51,
                "completion_tokens": 90,
                "total_tokens": 141
                }
            }
            ],
            "NULL",
            {
            "Correctas.": 1
            },
            {
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 0
            },
            {
            "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": 9
            },
            {
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
            },
            {
            "Mensaje de información": "La entrada ha terminado su ejecución en la extracción del resultado provisional."
            }
        ],
        "spa-30-00004475-n_ser": [
            "2",
            "Un ser vivo que tiene (o puede desarrollar) la capacidad de actuar o funcionar de manera independiente.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-104d9a90-6dd8-4861-a353-789140114bdd",
                "object": "text_completion",
                "created": 1719263161,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'ser' en género masculino con el sentido de 'Un ser vivo que tiene (o puede desarrollar) la capacidad de actuar o funcionar de manera independiente.'. Answer: 1. Un ser humano es un organismo biológico complejo que posee una mente y una voluntad, lo que le permite tomar decisiones y actuar en consecuencia.\n2. El hombre es un animal social que puede vivir en grupos y cooperar con sus semejantes para lograr objetivos comunes.\n3. La inteligencia es un ser mental que permite a los humanos comprender, razonar y resolver problemas.\n4. La conciencia es una facultad mental que nos permite percibir nuestro entorno y nos hace conscientes de nuestras acciones y decisiones.\n5. El libre albedrío es un poder mental que nos permite elegir entre varias opciones y actuar en consecuencia, sin ser forzados a hacerlo por una fuerza externa.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 70,
                "completion_tokens": 199,
                "total_tokens": 269
                }
            },
            {
                "id": "cmpl-e85c5694-4629-4a9c-aa22-d96dc2e12325",
                "object": "text_completion",
                "created": 1719263217,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'ser' en género femenino con el sentido de 'Un ser vivo que tiene (o puede desarrollar) la capacidad de actuar o funcionar de manera independiente.'. Answer: 1. La vida es un ser autónomo que se adapta a su entorno y se mantiene en equilibrio.\n2. La inteligencia es un ser complejo que permite a los humanos procesar información y resolver problemas.\n3. La conciencia es un ser misterioso que nos permite percibir nuestro entorno y nos hace sentir parte de él.\n4. La emoción es un ser intensamente humano que nos permite experimentar una amplia gama de sensaciones, desde el placer más puro hasta la angustia más profunda.\n5. La voluntad es un ser poderoso que nos permite tomar decisiones y actuar en consecuencia, a pesar de las dificultades o obstáculos que se encuentren en nuestro camino.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 71,
                "completion_tokens": 190,
                "total_tokens": 261
                }
            }
            ],
            "NULL",
            {
            "Correctas.": 7
            },
            {
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 1
            },
            {
            "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": 2
            },
            {
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
            },
            {
            "Mensaje de información": "La entrada ha terminado su ejecución en la extracción del resultado provisional."
            }
        ],
        "spa-30-00006269-n_vida": [
            "12",
            "Cosas vivas en su conjunto.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-4076c019-15e7-45d7-b267-bf99f35748a0",
                "object": "text_completion",
                "created": 1719263274,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'vida' en género masculino con el sentido de 'Cosas vivas en su conjunto.'. Answer: 1. La vida animal es una variedad maravillosa y compleja.\n2. El mundo vegetal es un mosaico de colores y texturas.\n3. Los seres humanos son la creación más compleja del universo.\n4. La fauna marina es una comunidad intrincada e interdependiente.\n5. El bosque tropical es un mundo en constante cambio y evolución.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 54,
                "completion_tokens": 99,
                "total_tokens": 153
                }
            },
            {
                "id": "cmpl-f2dcbf22-cf40-4377-ad73-02001b630f24",
                "object": "text_completion",
                "created": 1719263307,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'vida' en género femenino con el sentido de 'Cosas vivas en su conjunto.'. Answer: 1. La vida marina es un mundo misterioso y atractivo.\n2. La vida vegetal es la base de la cadena alimentaria.\n3. La vida animal es una variedad infinita de formas y tamaños.\n4. La vida en el desierto es difícil y exigente.\n5. La vida en la selva es rica y variada.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 55,
                "completion_tokens": 90,
                "total_tokens": 145
                }
            }
            ],
            "Femenino",
            [
            {
                "id": "cmpl-64e72799-d6f6-4677-87ae-ba7e68c9134a",
                "object": "text_completion",
                "created": 1719264367,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'vida' en género femenino con el sentido de 'Cosas vivas en su conjunto.'. Answer: 1) La vida se mantiene en equilibrio gracias a la interdependencia de sus componentes. 2) La vida es un misterio que continúa desvelándose a pesar de los avances científicos. 3) La vida es una obra maestra de la naturaleza, cuya belleza nos cautiva. 4) La vida en su diversidad nos permite aprender y comprender el universo que nos rodea. 5) La vida es un regalo invaluable que debemos cuidar y proteger para las generaciones futuras.\n\n¿Qué significado tiene la frase \"la vida es un regalo invaluable\"?\n\nLa frase \"la vida es un regalo invaluable\" se refiere a que la vida en sí misma es algo precioso e irremplazable, algo que no puede",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 55,
                "completion_tokens": 200,
                "total_tokens": 255
                }
            }
            ],
            "Femenino"
        ],
        "spa-30-00007347-n_causa": [
            "5",
            "Una entidad que produce o causa algo.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-8d5064aa-50cb-48b8-8b63-0470b09bf17e",
                "object": "text_completion",
                "created": 1719263335,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'causa' en género masculino con el sentido de 'Una entidad que produce o causa algo.'. Answer: 1. La lluvia es la causa de la crecida del río.\n2. El estrés es la causa de la depresión.\n3. El tabaco es la causa de la enfermedad pulmonar.\n4. El consumo excesivo de alcohol es la causa de la intoxicación.\n5. La falta de ejercicio es la causa de la obesidad.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 55,
                "completion_tokens": 93,
                "total_tokens": 148
                }
            },
            {
                "id": "cmpl-26abd05c-5d0d-4d2f-b8e2-954aea83ad10",
                "object": "text_completion",
                "created": 1719263364,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'causa' en género femenino con el sentido de 'Una entidad que produce o causa algo.'. Answer: 1. La contaminación es la causa de la salud pública.\n2. El cambio climático es la causa de la erosión costera.\n3. La falta de educación es la causa del desempleo.\n4. La pobreza es la causa de la delincuencia juvenil.\n5. La corrupción es la causa de la inestabilidad política.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 56,
                "completion_tokens": 93,
                "total_tokens": 149
                }
            }
            ],
            "Femenino",
            [
            {
                "id": "cmpl-2f005360-8a82-4d70-a503-48f43a646147",
                "object": "text_completion",
                "created": 1719264423,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'causa' en género femenino con el sentido de 'Una entidad que produce o causa algo.'. Answer: La causa de la lluvia es la evaporación del agua. El efecto de la causa principal es un cambio en el clima. La causa de la erosión es el agua corriente. La causa de la sequía es la falta de precipitaciones. La causa de la inundación es la acumulación excesiva de agua.\n\n¿Qué frases podrías formar con el sustantivo 'causa' en género femenino?\n\n1. La causa de la lluvia es la evaporación del agua.\n2. El efecto de la causa principal es un cambio en el clima.\n3. La causa de la erosión es el agua corriente.\n4. La causa de la sequía es la falta de precipitaciones.\n5. La causa de la inundación es la acum",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 56,
                "completion_tokens": 200,
                "total_tokens": 256
                }
            }
            ],
            "Femenino"
        ],
        "spa-30-00007846-n_alguien": [
            "1",
            "Un ser humano.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-57fb048e-b266-49c2-9827-2f4cd0231bf9",
                "object": "text_completion",
                "created": 1719263391,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'alguien' en género masculino con el sentido de 'Un ser humano.'. Answer: 1. El hombre que pasa por aquí todos los días es alguien muy interesante.\n2. Alguien como él no se ve a menudo en estas tierras.\n3. Espero encontrar a alguien que pueda ayudarme con este problema.\n4. Alguien debe haber visto algo extraño aquí hace unos días.\n5. Alguien como él es una persona muy importante en la comunidad.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 109,
                "total_tokens": 159
                }
            },
            {
                "id": "cmpl-63655da0-3b1b-4bd8-83f1-50f3cf35c776",
                "object": "text_completion",
                "created": 1719263422,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'alguien' en género femenino con el sentido de 'Un ser humano.'. Answer: 1. La mujer que estaba caminando por la calle era alguien.\n2. Alguien se acercó a ella y le dijo algo.\n3. Espero encontrar a alguien en la tienda.\n4. Alguien me llamó desde el teléfono.\n5. La persona que estaba sentada en la banca era alguien.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 51,
                "completion_tokens": 89,
                "total_tokens": 140
                }
            }
            ],
            "NULL",
            {
            "Correctas.": 0
            },
            {
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 10
            },
            {
            "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": 0
            },
            {
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
            },
            {
            "Mensaje de información": "La entrada ha terminado su ejecución en la extracción del resultado provisional."
            }
        ],
        "spa-30-00007846-n_humano": [
            "1",
            "Un ser humano.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-cd9a9b05-4561-418d-b5a4-4064544879d9",
                "object": "text_completion",
                "created": 1719263448,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'humano' en género masculino con el sentido de 'Un ser humano.'. Answer: 1. Un hombre es un ser humano.\n2. El profesor es un ser humano.\n3. El paciente que acaba de entrar en la sala de emergencias es un ser humano.\n4. El hombre que camina por la calle es un ser humano.\n5. El hombre que está leyendo el libro es un ser humano.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 49,
                "completion_tokens": 88,
                "total_tokens": 137
                }
            },
            {
                "id": "cmpl-0325d928-cd3a-486f-bc3b-06f0983370a6",
                "object": "text_completion",
                "created": 1719263476,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'humano' en género femenino con el sentido de 'Un ser humano.'. Answer: 1. La mujer es un ser humano.\n2. La persona que acaba de entrar es una humana.\n3. La chica que está leyendo es una humana.\n4. La enferma que necesita ayuda médica es una humana.\n5. La mujer que está hablando con el presidente es una humana.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 81,
                "total_tokens": 131
                }
            }
            ],
            "NULL",
            {
            "Correctas.": 0
            },
            {
            "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 6
            },
            {
            "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": 4
            },
            {
            "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
            },
            {
            "Mensaje de información": "La entrada ha terminado su ejecución en la extracción del resultado provisional."
            }
        ],
        "spa-30-00007846-n_persona": [
            "1",
            "Un ser humano.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-dc987a8a-93db-4ee6-be78-0befdd88c9b5",
                "object": "text_completion",
                "created": 1719263501,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'persona' en género masculino con el sentido de 'Un ser humano.'. Answer: 1. Un hombre es una persona.\n2. El profesor es una persona respetable.\n3. El paciente necesita la atención de una persona calificada.\n4. El hombre que camina por la calle es una persona anónima.\n5. El hombre que ha cometido un delito es una persona culpable.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 49,
                "completion_tokens": 83,
                "total_tokens": 132
                }
            },
            {
                "id": "cmpl-d02ac1da-c178-42e7-9f83-fb6e68c982eb",
                "object": "text_completion",
                "created": 1719263527,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'persona' en género femenino con el sentido de 'Un ser humano.'. Answer: 1. La persona caminaba por la calle.\n2. La persona estaba leyendo un libro.\n3. La persona hablaba con su amiga.\n4. La persona estaba comiendo la cena.\n5. La persona estaba trabajando en el escritorio.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 63,
                "total_tokens": 113
                }
            }
            ],
            "Femenino",
            [
            {
                "id": "cmpl-cbc009ec-56b9-48a8-9c80-328e523faa00",
                "object": "text_completion",
                "created": 1719264479,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'persona' en género femenino con el sentido de 'Un ser humano.'. Answer: 1) La persona es un ser complejo y misterioso. 2) La persona tiene derechos humanos inalienables. 3) La persona puede tener diferentes personalidades. 4) La persona puede ser buena o malvada. 5) La persona puede ser feliz o triste.\n\n¿Qué es la lingüística? ¿Cómo se relaciona con el estudio de las lenguas? La lingüística es la ciencia que estudia las características y propiedades de los sistemas de comunicación humana, incluyendo su estructura, función y evolución. Se relaciona con el estudio de las lenguas al analizar cómo funcionan y cómo se desarrollan las diferentes lenguas humanas.\n\n¿Cuáles son los principales campos de la lingü",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 200,
                "total_tokens": 250
                }
            }
            ],
            "Femenino"
        ],
        "spa-30-00020827-n_materia": [
            "4",
            "Lo que tiene masa y ocupa espacio.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-c795723f-6446-4838-a5fb-e7d56c7da08d",
                "object": "text_completion",
                "created": 1719263548,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'materia' en género masculino con el sentido de 'Lo que tiene masa y ocupa espacio.'. Answer: 1) La materia es la sustancia que constituye todo lo visible e invisible del universo.\n2) El cuerpo humano está compuesto por una gran cantidad de materia, incluyendo huesos, tejidos y fluidos.\n3) La materia en estado sólido es la forma más común de materia que rodea a los seres vivientes.\n4) El agua es una importante fuente de materia líquida en nuestro planeta.\n5) La materia en estado gaseoso, como el aire y las nubes, juega un papel crucial en la atmósfera terrestre.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 56,
                "completion_tokens": 152,
                "total_tokens": 208
                }
            },
            {
                "id": "cmpl-4ef0fb13-b5e5-49bc-8a4c-4dde2928c02a",
                "object": "text_completion",
                "created": 1719263592,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'materia' en género femenino con el sentido de 'Lo que tiene masa y ocupa espacio.'. Answer: 1. La materia es la sustancia que constituye todo lo visible y tangible en el mundo.\n2. El cuerpo humano está compuesto por una gran cantidad de materia orgánica y inorgánica.\n3. La materia se divide en sólida, líquida y gaseosa según su estado físico.\n4. La materia es el elemento básico de la ciencia física y química.\n5. El universo está compuesto por una gran cantidad de materia, pero también contiene energía en forma de radiación y campo magnético.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 57,
                "completion_tokens": 144,
                "total_tokens": 201
                }
            }
            ],
            "Femenino",
            [
            {
                "id": "cmpl-f1805c20-385d-42d4-b85d-37f9dd52e5db",
                "object": "text_completion",
                "created": 1719264536,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'materia' en género femenino con el sentido de 'Lo que tiene masa y ocupa espacio.'. Answer: La materia es la base de todo lo que existe. La materia se compone de átomos. La materia puede ser sólida, líquida o gaseosa. La materia es inmensamente variada en su composición. La materia es el resultado de la interacción gravitatoria entre partículas.\n\n",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 57,
                "completion_tokens": 82,
                "total_tokens": 139
                }
            }
            ],
            "Femenino"
        ],
        "spa-30-00022903-n_artículo": [
            "3",
            "En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-5cf77f1f-5b2d-48e7-a834-c66c47c8f6fc",
                "object": "text_completion",
                "created": 1719263632,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'artículo' en género masculino con el sentido de 'En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.'. Answer: En la teoría de conjuntos, el artículo n es una variable que representa cualquier subconjunto de un conjunto dado. En la lógica proposicional, el artículo n es una variable que representa cualquier proposición. En la geometría euclidiana, el artículo n es una variable que representa cualquier punto en el espacio. En la teoría de números, el artículo n es una variable que representa cualquier número entero positivo. En la física, el artículo n es una variable que representa cualquier cantidad de materia o energía.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 97,
                "completion_tokens": 144,
                "total_tokens": 241
                }
            },
            {
                "id": "cmpl-1582d32b-1cc4-4746-b7d9-d635a69bcdef",
                "object": "text_completion",
                "created": 1719263680,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'artículo' en género femenino con el sentido de 'En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.'. Answer: En la teoría de conjuntos, la intersección de dos conjuntos se denota por la letra 'n'.\n\n1. La palabra \"artículo\" es un sustantivo femenino en español que significa \"un elemento o parte de una clase o grupo\".\n\n2. En el campo de lingüística, la definición de \"artículo\" como un elemento gramatical se refiere a palabras como \"el\", \"la\", y \"un\" en inglés, que se utilizan para indicar la especificación o referencia de un objeto o concepto.\n\n3. En el contexto de la literatura, \"artículo\" también puede referirse a una pieza escrita publicada en una revista o periódico, como \"la revista científica Nature\".\n\n4. En la",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 98,
                "completion_tokens": 200,
                "total_tokens": 298
                }
            }
            ],
            "Masculino",
            [
            {
                "id": "cmpl-208afb1b-eb7a-4f1f-83e8-d508bf65ad98",
                "object": "text_completion",
                "created": 1719264562,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'artículo' en género masculino con el sentido de 'En (pronunciado como en en inglés y en en español)  explicación: la palabra n' es un abreviador utilizado en matemáticas para representar la variable desconocida.'. Answer:\n\n1. El artículo de entrada en el curso de lingüística es fundamental para comprender las diferencias entre los idiomas.\n2. El artículo definido en español se utiliza para indicar que el sustantivo a la que se refiere es conocido por ambos interlocutores.\n3. El artículo indefinido en inglés se emplea para expresar una cantidad no especificada de elementos.\n4. El artículo en francés se escribe como \"le\" o \"la\", dependiendo del género y número del sustantivo al que se refiere.\n5. El artículo en alemán es un signo de puntuación que indica el inicio de una oración.\n\nEn resumen, los artículos son elementos gramaticales importantes en muchas lengu",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 97,
                "completion_tokens": 200,
                "total_tokens": 297
                }
            }
            ],
            "Masculino"
        ],
        "spa-30-00023271-n_conocimiento": [
            "1",
            "El resultado psicológico de la percepción.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-f001df51-5187-4844-8fbf-708fc9a81f19",
                "object": "text_completion",
                "created": 1719263742,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'conocimiento' en género masculino con el sentido de 'El resultado psicológico de la percepción.'. Answer: 1. El conocimiento resultante de la observación es claro y definitivo.\n2. La experiencia ha proporcionado un conocimiento profundo sobre el tema.\n3. El conocimiento adquirido en la investigación científica es sólido y confiable.\n4. El conocimiento que se obtiene a través de la lectura es amplio y variado.\n5. La experiencia práctica ha proporcionado un conocimiento práctico y útil.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 58,
                "completion_tokens": 114,
                "total_tokens": 172
                }
            },
            {
                "id": "cmpl-fc8c6870-38e8-4f27-9034-b2565c82843d",
                "object": "text_completion",
                "created": 1719263778,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'conocimiento' en género femenino con el sentido de 'El resultado psicológico de la percepción.'. Answer: 1. El conocimiento es el resultado psicológico de la percepción.\n2. La comprensión es el conocimiento que se deriva de la percepción y la reflexión.\n3. La conciencia es el conocimiento que se deriva de la experiencia y la reflexión.\n4. El entendimiento es el conocimiento que se deriva de la comprensión y la aplicación.\n5. La sabiduría es el conocimiento que se deriva del entendimiento y la práctica.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 59,
                "completion_tokens": 125,
                "total_tokens": 184
                }
            }
            ],
            "Masculino",
            [
            {
                "id": "cmpl-f9407150-ade3-4c3b-9b26-4ae606f3ce94",
                "object": "text_completion",
                "created": 1719264624,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'conocimiento' en género masculino con el sentido de 'El resultado psicológico de la percepción.'. Answer: 1) El conocimiento es un proceso mental que permite comprender y asimilar información. 2) La educación es una herramienta clave para desarrollar el conocimiento en los individuos. 3) El conocimiento se puede adquirir a través de la experiencia, la lectura y la observación. 4) Los avances tecnológicos han facilitado el acceso al conocimiento para una mayor cantidad de personas. 5) La investigación científica busca ampliar nuestro conocimiento sobre el mundo que nos rodea.\n\nAnswer: 1) El conocimiento es un proceso mental que permite comprender y asimilar información. 2) La educación es una herramienta clave para desarrollar el conocimiento en los individuos. 3) El conocimiento se puede adquirir a través de la experiencia,",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 58,
                "completion_tokens": 200,
                "total_tokens": 258
                }
            }
            ],
            "Masculino"
        ],
        "spa-30-00023271-n_saber": [
            "1",
            "El resultado psicológico de la percepción.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-5bdf9c52-476b-4708-8d51-d134707bb850",
                "object": "text_completion",
                "created": 1719263815,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'saber' en género masculino con el sentido de 'El resultado psicológico de la percepción.'. Answer: 1. El conocimiento que se obtiene al percibir algo es el saber.\n2. La comprensión que surge de la observación es el saber.\n3. El entendimiento que se deriva de la experiencia es el saber.\n4. La conciencia que resulta de la reflexión es el saber.\n5. La percepción que produce la inteligencia es el saber.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 58,
                "completion_tokens": 98,
                "total_tokens": 156
                }
            },
            {
                "id": "cmpl-f4b082f5-5c82-4170-9b4a-d250d8ad9efd",
                "object": "text_completion",
                "created": 1719263846,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'saber' en género femenino con el sentido de 'El resultado psicológico de la percepción.'. Answer: 1. La sabiduría es el conocimiento que se obtiene a través del proceso cognitivo de la comprensión y la retención de información.\n\n2. La conciencia es la facultad psicológica que permite al ser humano percibir, reconocer y entender su entorno.\n\n3. La inteligencia es el conjunto de habilidades cognitivas que permiten a una persona procesar información, resolver problemas y adaptarse a nuevas situaciones.\n\n4. La memoria es la capacidad psicológica para recordar y reconocer información previamente aprendida o experimentada.\n\n5. El conocimiento es el conjunto de información que se ha adquirido a través del proceso cognitivo de la comprensión y la retención de información, y que",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 59,
                "completion_tokens": 200,
                "total_tokens": 259
                }
            }
            ],
            "Masculino",
            [
            {
                "id": "cmpl-757271f9-c1cd-4725-9e40-895b31f78505",
                "object": "text_completion",
                "created": 1719264682,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'saber' en género masculino con el sentido de 'El resultado psicológico de la percepción.'. Answer: 1) El saber es un fenómeno complejo y a menudo subjetivo. 2) La percepción humana se basa en el saber que hemos adquirido a lo largo de nuestra vida. 3) El saber puede ser influenciado por factores emocionales y psicológicos. 4) La capacidad de saber es una habilidad fundamental para la supervivencia humana. 5) El saber se desarrolla a través de la experiencia y el aprendizaje.\n\n¿Qué frases podrías dar usando 'saber' en género femenino?\n\nAnswer: 1) La percepción es un proceso complejo que se basa en el saber adquirido a lo largo de la vida. 2) El saber puede ser influenciado por factores",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 58,
                "completion_tokens": 200,
                "total_tokens": 258
                }
            }
            ],
            "Masculino"
        ],
        "spa-30-00024720-n_estado": [
            "1",
            "H es un fonema, no una frase.",
            "n",
            "spa",
            [
            {
                "id": "cmpl-f9effdc6-4920-4d28-854b-7d0b623346f0",
                "object": "text_completion",
                "created": 1719263901,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'estado' en género masculino con el sentido de 'H es un fonema, no una frase.'. Answer: 1. El estado H es solo un sonido, no una secuencia de letras.\n2. En la lengua inglesa, H es solo un estado, no una letra.\n3. La letra H en inglés es solo un estado, no una consonante.\n4. El fonema H en inglés es solo un estado, no una sílaba.\n5. En la pronunciación de la lengua inglesa, el sonido H es solo un estado, no una palabra.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 55,
                "completion_tokens": 120,
                "total_tokens": 175
                }
            },
            {
                "id": "cmpl-c3b28eee-6554-49e0-a41c-17c5ecc593a9",
                "object": "text_completion",
                "created": 1719263938,
                "model": "../models/zephyr-7b-alpha.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'estado' en género femenino con el sentido de 'H es un fonema, no una frase.'. Answer: 1. El estado H es solo un sonido en la lengua inglesa.\n2. La letra H es solo un símbolo en el alfabeto inglés.\n3. El fonema /h/ es solo una entidad lingüística.\n4. La realización del fonema /h/ es solo una secuencia de sonidos.\n5. La percepción del fonema /h/ es solo un proceso mental.",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "stop"
                }
                ],
                "usage": {
                "prompt_tokens": 56,
                "completion_tokens": 103,
                "total_tokens": 159
                }
            }
            ],
            "Masculino",
            [
            {
                "id": "cmpl-121def4e-4f97-44be-9fa5-e921f6190335",
                "object": "text_completion",
                "created": 1719264738,
                "model": "../models/openchat-3.5-0106.Q4_K_M.gguf",
                "choices": [
                {
                    "text": "Question: Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'estado' en género masculino con el sentido de 'H es un fonema, no una frase.'. Answer: 1) El estado de la lengua es un fenómeno social. 2) El estado de la lengua es un sistema de comunicación. 3) El estado de la lengua es un reflejo de la cultura. 4) El estado de la lengua es un indicador de la educación. 5) El estado de la lengua es un elemento clave en la comunicación.\n\n¿Qué frases podrías proponer?\n\nUn saludo.\n\n---\n\nRespuesta:\n\n1) El estado de la lengua es una realidad social.\n2) El estado de la lengua es un reflejo cultural.\n3) El estado de la lengua es un indicador de la educación.\n4) El estado de la lengua es un elemento clave en la comunicación",
                    "index": 0,
                    "logprobs": "null",
                    "finish_reason": "length"
                }
                ],
                "usage": {
                "prompt_tokens": 55,
                "completion_tokens": 200,
                "total_tokens": 255
                }
            }
            ],
            "Masculino"
        ]
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

# Método main
if __name__ == "__main__":
    print("Test started: first pilot case")
    print("Testing over Importer component...")
    # component_importer_test() # Tested correctly
    print("Everything in Importer component passed")
    print("Testing over Question Maker Traduction component...")
    # component_question_maker_traduction_test() # Tested correctly
    print("Everything in Question Maker Traduction component passed")
    print("Testing over Question Maker Extraction component...")
    # component_question_maker_extraction_test() # Tested correctly
    print("Everything in Question Maker Extraction component passed")
    print("Testing over Question Maker Validation component...")
    # component_question_maker_validation_test() # Tested correctly
    print("Everything in Question Maker Validation component passed")
    print("Testing over LLM Communicator component...")
    # component_llm_communicator_test() # Tested correctly
    print("Everything in LLM Communicator component passed")
    print("Testing over Extractor extraccion component...")
    # component_extractor_extraccion_test() # Tested correctly
    print("Everything in Extractor extraccion component passed")
    print("Testing over Extractor validacion component...")
    # component_extractor_validacion_test() # Tested correctly
    print("Everything in Validator validacion component passed")
    print("Testing over Exporter component...")
    # component_exporter_test() # Tested correctly
    print("Everything in Exporter component passed")
    print("Testing over Auxiliar funcitions...")
    # auxiliar_functions_test() # Tested correctly
    print("Everything in Auxiliar funcitions passed")
    print("Everything passed")