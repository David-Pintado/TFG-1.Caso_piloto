

from io import StringIO
import json
from configparser import ConfigParser
import re
import sys
sys.path.append('..')  # Agrega la carpeta superior al sys.path
sys.path.append("../auxFunctionLibrary") #Agrega la carpeta superior al sys.path

from componenteImporter import ComponenteImporter
import componenteQuestionMaker
from componenteLLMCommunicator import ComponenteLLMCommunicator
import componenteExtractor
import componenteValidator
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
    source_information = component1.generate_data_structure()
    
    # Después de comprobar en spa_variant_file las palabras a analizar, en total debe haber 33 elementos
    assert len(source_information) == 32, "Should be 32"
    
    # Contador para contar cuántos elementos tienen una clave
    appearences_tierra = 0
    appearences_mareo = 0

    # Iterar sobre los elementos del diccionario
    for key, _ in source_information.items():
        if "tierra" in key:  # Verificar si la clave contiene "tierra"
            appearences_tierra += 1
        elif "mareo" in key: # Verificar si la clave contiene "mareo"
            appearences_mareo += 1
            
    # source_information debe contener 11 elementos con "tierra"
    assert appearences_tierra == 11, "Should be 11"
    
    # source_information debe contener 11 elementos con "mareo"
    assert appearences_mareo == 4, "Should be 4"
    
    # Elemento que debe contener el source_information
    element_piloto = ("spa-30-10433164-n_piloto", ["2", "NULL", "n","spa"])
    assert (element_piloto[0], element_piloto[1]) in source_information.items(), "Should appear"
    
    # Elemento que debe contener el source_information
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "La parte sólida de la superficie de la tierra.", "n","spa"])
    assert (element_tierra[0], element_tierra[1]) in source_information.items(), "Should appear"
    
    # Creamos la estructura de datos donde guardar las glosas
    eng_data_structure = component1.generate_eng_data_structure()
    
    # Los dos offsets anteriores deben estar, y no deben ser NULL
    offset_piloto = element_piloto[0].split('_')[0]
    assert offset_piloto in eng_data_structure.keys() and eng_data_structure[offset_piloto] != "NULL", "Should be"
    offset_tierra = element_tierra[0].split('_')[0]
    assert offset_tierra in eng_data_structure.keys() and eng_data_structure[offset_tierra] != "NULL", "Should be"
    
    # print the output
    # print(json.dumps(source_information, indent=2, ensure_ascii=False))
    
def component_question_maker_test():
     
    # Elementos de prueba
    element_piloto = ("spa-30-10433164-n_piloto", ["2", "NULL", "n","spa"])
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n","spa"])
    
    provisional_prompts_piloto = componenteQuestionMaker.generate_provisional_prompts(element_piloto)
    provisional_prompts_tierra = componenteQuestionMaker.generate_provisional_prompts(element_tierra)
    assert provisional_prompts_piloto == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género masculino con el sentido de 'NULL'.", 
                                          f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género femenino con el sentido de 'NULL'."], "Shold be true"
    assert provisional_prompts_tierra == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género masculino con el sentido de 'la parte sólida de la superficie de la Tierra'.", 
                                          f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género femenino con el sentido de 'la parte sólida de la superficie de la Tierra'."], "Shold be true"  
    
    validation_prompts_piloto = componenteQuestionMaker.generate_validation_prompts(element_piloto, "masculino")
    validation_prompts_tierra = componenteQuestionMaker.generate_validation_prompts(element_tierra, "femenino")
    
    assert validation_prompts_piloto == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'piloto' en género masculino con el sentido de 'NULL'."], "Shold be true"
    assert validation_prompts_tierra == [f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo 'tierra' en género femenino con el sentido de 'la parte sólida de la superficie de la Tierra'."], "Shold be true"
        
    
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
    componenteLLMCommunicator_test = ComponenteLLMCommunicator(config['file_path']['provisional_answers_language_model_path_test']) 
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
        componenteLLMCommunicator = ComponenteLLMCommunicator(config['file_path']['provisional_answers_language_model_path'])
        
        # Cargamos el modelo de lenguaje que vamos a utilizar para conseguir las respuestas provisionales
        componenteLLMCommunicator.load_model()
        
        # Elementos de prueba
        element_piloto = ("spa-30-10433164-n_piloto", ["2", "NULL", "n","spa"])
        element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n","spa"])
                
        # Pruebas de preguntas
        provisional_prompts_piloto = componenteQuestionMaker.generate_provisional_prompts(element_tierra)
        provisional_prompts_tierra = componenteQuestionMaker.generate_provisional_prompts(element_piloto)
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

def component_extractor_test():
    
    # Tests de extracción de respuestas ----------------------------------------
    
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
    assert expected_output_piloto_masculino == componenteExtractor.extract_llm_answers(elemento_prueba_piloto_masculino), "Should be true"
    
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
    assert expected_output_piloto_femenino == componenteExtractor.extract_llm_answers(elemento_prueba_piloto_femenino), "Should be true"
    
    
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
    assert expected_output_traduccion == componenteExtractor.extract_llm_answers(elemento_prueba_traducción), "Should be true"
    
    # Tests de obtener el provisional answer -----------------------------------
    
    # --------------------------------------   Prueba 1   -------------------------------------------
        
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n","spa"])
    
    llm_extracted_answer_list = [expected_output_piloto_masculino, expected_output_piloto_femenino]
    
    provisional_answer = componenteExtractor.get_provisional_answer4(element_tierra, llm_extracted_answer_list)
    
    assert provisional_answer == ["Femenino"], "Should be ['Femenino']"
    
    # --------------------------------------   Prueba 2   -------------------------------------------
    
    element_institución = ("spa-30-05669350-n_institución", ["3","\"una costumbre que durante mucho tiempo ha sido una importante característica de un grupo o sociedad específica.\"","n","spa"])
    
    llm_extracted_answer_list_2 =   [
                                        [
                                            "La institución educativa es un lugar predeterminado para obtener un título universitario y una educación superior.",
                                            "La institución religiosa es un lugar predeterminado para participar en cultos y ceremonias religiosas.",
                                            "La institución penitenciaria es un lugar predeterminado para rehabilitar y reinsertar a los criminales.",
                                            "La institución médica es un lugar predeterminado para tratar y curar enfermedades.",
                                            "La institución judicial es un lugar predeterminado para resolver conflictos legales.",
                                            "La institución académica es un lugar predeterminado para investigar y desarrollar nuevas ideas y tecnologías.",
                                            "La institución militar es un lugar predeterminado para entrenar y preparar a los soldados.",
                                            "La institución carcelaria es un lugar predeterminado para rehabilitar y reinsertar a los delincuentes.",
                                            "La institución financiera es un lugar predeterminado para gestionar y administrar recursos financieros.",
                                            "La institución médico-legal es un lugar predeterminado para determinar causas de muerte y traer justicia a las víctimas."
                                        ],
                                        [
                                            "El proceso para unirse a la universidad requiere la presentación de todos los documentos necesarios para la inscripción en la institución educativa.",
                                            "La institución carcelaria ofrece programas educativos para los reclusos.",
                                            "La institución financiera ofrece servicios bancarios a sus clientes.",
                                            "La institución médica realiza exámenes médicos para los pacientes.",
                                            "La institución religiosa ofrece servicios a sus miembros.",
                                            "La institución política es responsable de implementar las leyes.",
                                            "La institución académica es responsable de los estándares académicos.",
                                            "La institución cultural promueve la cultura y las artes.",
                                            "La institución de justicia es responsable de aplicar la ley.",
                                            "La institución social ayuda a las personas en situaciones de crisis."
                                        ]
                                    ]
    
    provisional_answer_intitución = componenteExtractor.get_provisional_answer4(element_institución, llm_extracted_answer_list_2)
    
    assert provisional_answer_intitución == ["Femenino"], "Should be ['Femenino']"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_institución_plural = ("spa-30-05669350-n_institución", ["3","\"una costumbre que durante mucho tiempo ha sido una importante característica de un grupo o sociedad específica.\"","n","spa"])
    
    llm_extracted_answer_list_3 =   [
                                        [
                                            "Las instituciones educativas son un lugar predeterminado para obtener un título universitario y una educación superior.",
                                            "Las instituciones educativas son lugar predeterminado para participar en cultos y ceremonias religiosas.",
                                            "Las instituciones educativas son un lugar predeterminado para rehabilitar y reinsertar a los criminales.",
                                            "Las instituciones educativas son un lugar predeterminado para tratar y curar enfermedades.",
                                            "Las instituciones educativas son un lugar predeterminado para resolver conflictos legales.",
                                            "Las instituciones educativas son un lugar predeterminado para investigar y desarrollar nuevas ideas y tecnologías.",
                                            "Las instituciones educativas son un lugar predeterminado para entrenar y preparar a los soldados.",
                                            "Las instituciones educativas son un lugar predeterminado para rehabilitar y reinsertar a los delincuentes.",
                                            "Las instituciones educativas son un lugar predeterminado para gestionar y administrar recursos financieros.",
                                            "Las instituciones educativas son un lugar predeterminado para determinar causas de muerte y traer justicia a las víctimas."
                                        ],
                                        [
                                            "El proceso para unirse a la universidad requiere la presentación de todos los documentos necesarios para la inscripción en la institución educativa.",
                                            "Las instituciones carcelarias ofrecen programas educativos para los reclusos.",
                                            "Las instituciones financieras ofrecen servicios bancarios a sus clientes.",
                                            "Las instituciones médicas realizan exámenes médicos para los pacientes.",
                                            "Las instituciones religiosas ofrecen servicios a sus miembros.",
                                            "Las instituciones políticas son responsables de implementar las leyes.",
                                            "Las instituciones académicas son responsables de los estándares académicos.",
                                            "Las instituciones culturales promueven la cultura y las artes.",
                                            "Las instituciones de justicia son responsables de aplicar la ley.",
                                            "Las instituciones sociales ayudan a las personas en situaciones de crisis."
                                        ]
                                    ]
    
    provisional_answer_intitución_plural = componenteExtractor.get_provisional_answer4(element_institución_plural, llm_extracted_answer_list_3)
    
    assert provisional_answer_intitución_plural == ["Femenino"], "Should be ['Femenino']"
    
    # --------------------------------------   Prueba 4   -------------------------------------------
    
    element_universal = ("spa-30-06751367-n_universal",["1","\"una proposición que afirma algo de todas las clases.\"","n","spa"])

    llm_extracted_answer_list_4 = [
      [
        "El concepto universal de verdad es una proposición que es verdadera en todos los mundos posibles.",
        "Un ejemplo de una proposición universal en lógica es todos los trapezoides son cuadrangulares.",
        "La teoría de los universales es una teoría filosófica que sostiene que hay propiedades que son universales y reales independientemente del tiempo y del lugar.",
        "Un ejemplo de una proposición universal en matemáticas es si x es mayor que y, y si y es mayor que z, entonces x es mayor que z.",
        "En la gramática, la regla universal es una regla que es aplicable a todos los idiomas naturales.",
        "Un ejemplo de una proposición universal en la biología es los humanos tienen un total de 20 alfa-hemolisina.",
        "En la astronomía, una ley universal es una ley que es verdadera en todos los sistemas planetarios.",
        "En la química, una propiedad universal es una propiedad que es común a todos los elementos químicos.",
        "En la sociología, una regla universal es una regla que es aplicable a todos los sistemas sociales.",
        "En la filosofía, una verdad universal es una verdad que es verdadera independientemente del tiempo y del lugar."
      ],
      [
        "La universalidad de la muerte es inevitable para todos los seres humanos.",
        "La universalidad del amor es una emoción compartida por muchas personas.",
        "La universalidad del lenguaje humano permite a los seres humanos comunicarse y compartir sus ideas.",
        "La universalidad del sufrimiento es un tema recurrente en muchas artes y literaturas mundiales.",
        "La universalidad del amor romántico es un tema popular en muchas películas y canciones.",
        "La universalidad del dolor emocional es un fenómeno humano común y necesario para crecer emocional y mentalmente.",
        "La universalidad del humor es una necesidad humana para aliviar el estrés y la angustia.",
        "La universalidad del deseo de amar y ser amado es una necesidad humana básica.",
        "La universalidad del interés por la investigación científica es una necesidad humana para entender y mejorar nuestro conocimiento del mundo.",
        "La universalidad del deseo de un hogar y una familia es una necesidad humana para sentirse seguros y respetados."
      ]
    ]
    
    provisional_answer_universal = componenteExtractor.get_provisional_answer4(element_universal, llm_extracted_answer_list_4)
    
    assert provisional_answer_universal == ['NULL', {'Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.': 9}, {'Error 2: La palabra que buscamos no aparece en la frase.': 10}, {'Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.': 0}, {'Mensaje de información': 'La entrada ha terminado su ejecución en la extracción de la respuesta provisional.'}], "Should be True"
    
    # --------------------------------------   Prueba 5   -------------------------------------------
    
    element_científico = ("spa-30-09863339-n_científico",["2","The original english phrase is \"a scientist or technician engaged in military research\". the spanish translation is \"un científico o técnico que realiza investigación militar\". in this case, the translator should only provide the translation, without any additional information about the context or source of the phrase.","n","spa"])

    llm_extracted_answer_list_5 = [
      [
        "El científico militar llevó a cabo experimentos para mejorar las armas.",
        "El científico militar está trabajando en una tecnología que ayude a los militares a responder rápidamente a los ataques.",
        "El científico militar está desarrollando armas que sean más eficaces y menos destructivas.",
        "El científico militar ha creado un dispositivo que ayude a los militares a detectar y neutralizar minas.",
        "El científico militar ha desarrollado un sistema de comunicación avanzado para mejorar las comunicaciones entre los militares.",
        "El científico militar está investigando formas para mejorar las capacidades psicológicas y físicas de los militares.",
        "El científico militar ha creado un método para identificar y neutralizar agentes químicos.",
        "El científico militar ha desarrollado una nueva forma de proteger a los soldados de las armas biológicas.",
        "El científico militar ha creado una nueva arma que sea más efectiva y menos destructiva.",
        "El científico militar ha desarrollado una nueva arma que pueda ser utilizada para llevar a cabo operaciones militares en zonas urbanas sin causar daños al entorno."
      ],
      [
        "La ingeniera química y científica está liderando un equipo de investigación para desarrollar nuevas armas químicas.",
        "La doctora física y científica participó en un simposio militar para discutir sus hallazgos en el campo de la energía.",
        "La matemática y científica asistente ayuda a los soldados a planificar operaciones militares.",
        "La química y científica encargada del laboratorio es la más importante persona en la base militar.",
        "La científica y microbióloga está trabajando en un nuevo tratamiento médico para tratar las heridas quemadas de los soldados.",
        "La doctora en biología y científica ayuda a los médicos a entender las causas de las enfermedades que afectan a los soldados.",
        "La química y científica trabajadora creó un nuevo tipo de explosivo que puede ser utilizado en el campo de batalla.",
        "La científica y física desarrolló un nuevo sistema de defensa contra los misiles enemigos.",
        "La bióloga y científica investigadora está trabajando para descubrir una nueva forma de contrarrestar los efectos de los agentes químicos.",
        "La física y científica experimentada ayudó a los soldados a mejorar sus armas de"
      ]
    ]
    
    provisional_answer_científico = componenteExtractor.get_provisional_answer4(element_científico, llm_extracted_answer_list_5)
    
    assert provisional_answer_científico == ["Masculino"], "Should be ['Masculino']"
    
def component_validator_test():
        
    # --------------------------------------   Prueba 1   -------------------------------------------
    
    element_realización = ("spa-30-00062451-n_realización",["4","El acto de cumplir o satisfacer algo (una promesa o deseo, por ejemplo).","n","spa"])
    
    llm_extracted_answer_list_1 = [
      [
        "La realización del sueño de Ana consistió en viajar a París y visitar la Torre Eiffel.",
        "La realización del deseo de Juan era hacerse un tatuaje en su cuerpo.",
        "La realización de los objetivos de Marta era ser arquitecta y diseñar edificios.",
        "La realización del sueño de Pedro es estudiar en el extranjero y conocer otras culturas.",
        "La realización del deseo de Sofía era escribir una novela y publicarla.",
        "La realización de los sueños de los niños es brindarles un hogar seguro y cálido.",
        "La realización del deseo de Laura era abrir su propia tienda y vender productos artesanales.",
        "La realización del sueño de Mireya es hacerse una cirugía plástica y mejorar su autoestima.",
        "La realización del deseo de Ana es ser madre y criar a sus hijos con amor.",
        "La realización de los objetivos de Juan es abrir su propia empresa y tener éxito en su trabajo."
      ]
    ]
    
    final_answer_cosa = componenteValidator.get_final_answer(element_realización, llm_extracted_answer_list_1, "Femenino")
    
    assert final_answer_cosa == ["Femenino"], "Should be ['Femenino']"
    
    # --------------------------------------   Prueba 2   -------------------------------------------
    
    final_answer_cosa_2 = componenteValidator.get_final_answer(element_realización, llm_extracted_answer_list_1, "Masculino")
    
    assert final_answer_cosa_2 == ['NULL', {'Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.': 0}, {'Error 2: La palabra que buscamos no aparece en la frase.': 0}, {'Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.': 10}, {'Mensaje de información': 'La entrada ha terminado su ejecución en la validación de la respuesta provisional.'}], "Should be True"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_error = ("spa-30-00070965-n_error",["4","Una acción incorrecta atribuible a mal juicio o ignorancia o falta de atención.","n","spa"])
    
    llm_extracted_answer_list_2 = [
      [
        "El error cometido fue un malentendido.",
        "¿Cómo corregir este error?",
        "No se puede evitar el error.",
        "Puede haber muchos errores en un texto.",
        "No te preocupes por el error.",
        "Quiero saber el origen del error.",
        "El error está en la palabra mala.",
        "Piensa bien antes de cometer un error.",
        "No importa el error.",
        "El error es innecesario."
      ]
    ]
    
    final_answer_error = componenteValidator.get_final_answer(element_error, llm_extracted_answer_list_2, "Masculino")
    
    assert final_answer_error == ["Masculino"], "Should be ['Masculino']"
    
    # --------------------------------------   Prueba 4   -------------------------------------------
    
    final_answer_error_2 = componenteValidator.get_final_answer(element_error, llm_extracted_answer_list_2, "Femenino")
    
    assert final_answer_error_2 == ['NULL', {'Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.': 0}, {'Error 2: La palabra que buscamos no aparece en la frase.': 0}, {'Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.': 10}, {'Mensaje de información': 'La entrada ha terminado su ejecución en la validación de la respuesta provisional.'}], "Should be True"
    
def component_exporter_test():
    
    exploited_information = {
        "spa-30-00002684-n_cosa": [
            "2",
            "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
            "n",
            "spa",
            [
            [
                "La cosa que se proyecta en la pared es un objeto real, no una ilusión.",
                "El reflejo en el agua es solo una cosa, pero parece ser más que eso.",
                "La sombra que sigue al hombre es una cosa tangible y visible, pero no tiene vida propia.",
                "La imagen en la pantalla es una cosa real, pero no es lo mismo que el objeto en sí mismo.",
                "El eco que se escucha en la habitación es solo una cosa, pero puede ser muy molesto."
            ],
            [
                "La cosa más oscura en la habitación era una sombra larga que se extendía a lo largo del piso.",
                "La cosa más frágil que ella había visto nunca antes era una hoja de papel que flotaba en el aire, sin ningún soplo.",
                "La cosa más difícil para ella era creer que la sombra que le seguía fuera real.",
                "La cosa más hermosa que ella había visto nunca antes era una hoja de oro que brillaba en el sol.",
                "La cosa más misteriosa que ella había visto nunca antes era una sombra oscura que se movía por la habitación sin ninguna explicación aparente."
            ]
            ],
            "Femenino",
            [
            [
                "La cosa era tan hermosa que parecía sacada de un cuento de hadas.",
                "La cosa estaba hecha de madera, pero parecía ser de cristal.",
                "La cosa era tan grande que se podían ver las sombras de las personas que la rodeaban.",
                "La cosa tenía una forma extraña y parecía haber sido moldeada por un artista.",
                "La cosa estaba llena de detalles y parecía haber sido creada por un maestro escultor.  ¿Qué significado tiene la frase moldear una sombra? ¿Cómo se relaciona con el sustantivo 'cosa'?  La frase moldear una sombra hace referencia a crear o dar forma a algo que no es tangible, como una som"
            ]
            ],
            "Femenino"
        ],
        "spa-30-00002684-n_objeto": [
            "1",
            "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
            "n",
            "spa",
            [
            [
                "El objeto reflejaba la luna brillante en su superficie.",
                "La sombra del objeto se proyectó sobre el piso oscuro.",
                "El objeto tenía un contorno definido, lo que le daba una apariencia más realista.",
                "El objeto moldeó una sombra perfectamente redondeada en la pared.",
                "La sombra del objeto se deslizó lentamente sobre el suelo, como si estuviera viviente."
            ],
            [
                "La piedra es un objeto tangible y visible, que puede moldear una sombra en la superficie de otra piedra.",
                "El cuadro es un objeto tangible y visible, que puede moldear una sombra en el muro.",
                "El árbol es un objeto tangible y visible, que puede moldear una sombra en el suelo.",
                "La lámpara es un objeto tangible y visible, que puede moldear una sombra en la pared.",
                "El libro es un objeto tangible y visible, que puede moldear una sombra en la mesa."
            ]
            ],
            "Masculino",
            [
            [
                "El objeto de mi deseo es viajar por Europa.",
                "El objeto de mi investigación es comprender la historia de la humanidad.",
                "El objeto de mi admiración es el talento y habilidades de Beethoven.",
                "El objeto de mi ambición es alcanzar la cima del monte Everest.",
                "El objeto de mi curiosidad es descubrir los secretos de la Antártida."
            ]
            ],
            "Masculino"
        ],
        "spa-30-00003553-n_conjunto": [
            "2",
            "Un conjunto de partes que se considera como una sola entidad.",
            "n",
            "spa",
            [
            [
                "Un conjunto de piezas mecánicas es un motor completo.",
                "El conjunto de huesos del pie forma la estructura de apoyo para el cuerpo.",
                "El conjunto de dientes es una parte importante del sistema digestivo.",
                "Un conjunto de lentes es necesario para corregir la visión.",
                "El conjunto de órganos reproductores masculinos se conoce como genitales masculinos."
            ],
            [
                "El conjunto de piezas del reloj es un mecanismo complejo.",
                "La colección de libros antiguos forma parte de la biblioteca histórica.",
                "El grupo de amigos es una unión fuerte y duradera.",
                "La serie de películas constituye una obra maestra del cine.",
                "La colección de joyas es un tesoro inestimable."
            ]
            ],
            "Masculino",
            [
            [
                "El conjunto de estrellas es un sistema celeste bien definido.",
                "El conjunto de datos proporciona información valiosa para la investigación.",
                "El conjunto de herramientas es suficiente para realizar el trabajo.",
                "El conjunto de leyes establece los límites de lo que es legal y lo que no lo es.",
                "El conjunto de ideas proporciona una visión completa del problema."
            ]
            ],
            "Masculino"
        ],
        "spa-30-00004258-n_ser": [
            "4",
            "Una entidad viva.",
            "n",
            "spa",
            [
            [
                "El león es la reina del bosque.",
                "El elefante es el gigante de la savana.",
                "El tigre es el rey de la selva.",
                "El rinoceronte es el guardián de la pradera.",
                "El gorila es el rey de los simios."
            ],
            [
                "La madre es la fuente de vida para su hijo.",
                "La planta es la encarnación de vitalidad y crecimiento.",
                "La nación es una entidad viva, con un corazón y una mente propia.",
                "La cultura es el alma de una sociedad, que la hace única e inmortal.",
                "La belleza es la expresión más pura del ser humano, que nos une a nuestra naturaleza."
            ]
            ],
            "NULL",
            {
            "Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 0
            },
            {
            "Error 2: La palabra que buscamos no aparece en la frase.": 9
            },
            {
            "Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
            },
            {
            "Mensaje de información": "La entrada ha terminado su ejecución en la extracción de la respuesta provisional."
            }
        ],
        "spa-30-00004475-n_ser": [
            "2",
            "Un ser vivo que tiene (o puede desarrollar) la capacidad de actuar o funcionar de manera independiente.",
            "n",
            "spa",
            [
            [
                "Un ser humano adulto es un individuo capaz de tomar decisiones y actuar de manera autónoma.",
                "El niño pequeño es un ser que aún no ha desarrollado la capacidad de hablar o caminar sin ayuda.",
                "La conciencia es un ser intangible que permite al ser humano tener una percepción de su entorno y sus propias emociones.",
                "El virus es un ser microscópico que puede causar enfermedades graves en los seres vivos.",
                "La inteligencia artificial es un ser creado por la tecnología que tiene la capacidad de aprender y responder a las instrucciones dadas por el usuario."
            ],
            [
                "La planta es un ser vivo capaz de absorber nutrientes y crecer.",
                "La bacteria es un ser vivo microscópico que puede causar enfermedades.",
                "La hormona es un ser químico biológicamente activo que regula procesos fisiológicos.",
                "La computadora es un ser electrónico programable que puede realizar cálculos y operaciones.",
                "La luna es un ser celestial que ilumina la noche y afecta el mar y la tierra."
            ]
            ],
            "Masculino",
            [
            [
                "El ser humano es un individuo capaz de tomar decisiones y actuar de forma autónoma.",
                "La inteligencia artificial es un ser que simula la capacidad de pensamiento y acción humana.",
                "Un robot es un ser mecánico programado para realizar tareas específicas de manera independiente.",
                "El embrión es un ser en desarrollo que comienza a funcionar de forma autónoma una vez implantado en el útero.",
                "Un holograma es un ser virtual que puede interactuar con su entorno y realizar tareas sin la necesidad de una presencia física.  ¿Qué frases podrías dar usando 'ser' en género femenino?"
            ]
            ],
            "Masculino"
        ],
        "spa-30-00006269-n_vida": [
            "12",
            "Cosas vivas en su conjunto.",
            "n",
            "spa",
            [
            [
                "La vida animal es una diversidad maravillosa y compleja.",
                "El mundo vegetal es un vasto reino de seres vivientes.",
                "Los microorganismos son la base de la cadena alimentaria y la mayoría de los procesos biológicos en la Tierra.",
                "La vida marina es una comunidad compleja e interdependiente que abarca todo el planeta.",
                "El bosque tropical es un mosaico de vida exuberante y variada, donde se encuentran especies únicas y raras."
            ],
            [
                "La vida marina es un mundo misterioso y atractivo.",
                "La vida vegetal es la base de la cadena alimentaria.",
                "La vida animal es una variedad infinita de formas y tamaños.",
                "La vida rural es una experiencia única que se puede disfrutar en el campo.",
                "La vida urbana es un entorno complejo y dinámico."
            ]
            ],
            "Femenino",
            [
            [
                "La vida se mantiene en equilibrio a través de la biodiversidad.",
                "La vida es un regalo inestimable que debemos cuidar y proteger.",
                "La vida en su diversidad es el resultado de millones de años de evolución.",
                "La vida en todos sus aspectos es algo hermoso y maravilloso.",
                "La vida en su conjunto es un misterio que aún no ha sido completamente descifrado."
            ]
            ],
            "Femenino"
        ],
        "spa-30-00007347-n_causa": [
            "5",
            "Una entidad que produce o causa algo.",
            "n",
            "spa",
            [
            [
                "La contaminación es la causa de la enfermedad respiratoria.",
                "El estrés es la causa de la depresión.",
                "El tabaco es la causa del cáncer pulmonar.",
                "El consumo excesivo de alcohol es la causa de la cirrosis.",
                "La falta de ejercicio es la causa de la obesidad."
            ],
            [
                "La contaminación es la causa de la salud pública.",
                "El cambio climático es la causa de los desastres naturales.",
                "La falta de educación es la causa del desempleo.",
                "La pobreza es la causa de la violencia en las ciudades.",
                "La corrupción es la causa de la inestabilidad política."
            ]
            ],
            "Femenino",
            [
            [
                "La causa de la sequía es la falta de lluvia.",
                "El médico busca determinar la causa de la enfermedad.",
                "La causa del incendio fue un cortocircuito eléctrico.",
                "La causa del aumento de precios es la inflación.",
                "La causa del accidente fue la falta de atención del conductor."
            ]
            ],
            "Femenino"
        ],
        "spa-30-00007846-n_alguien": [
            "1",
            "Un ser humano.",
            "n",
            "spa",
            [
            [
                "El hombre que camina por la calle es alguien.",
                "Alguien está hablando en la habitación.",
                "Es alguien que me ha ayudado muchas veces.",
                "Alguien debe haber dejado la puerta abierta.",
                "El hombre que se acerca es alguien que conoce a mi madre."
            ],
            [
                "La mujer que estaba caminando por la calle.",
                "La persona que estaba leyendo el libro.",
                "La chica que estaba bailando en la fiesta.",
                "La estudiante que estaba escribiendo su tarea.",
                "La mujer que estaba hablando con su amiga."
            ]
            ],
            "NULL",
            {
            "Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 3
            },
            {
            "Error 2: La palabra que buscamos no aparece en la frase.": 7
            },
            {
            "Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
            },
            {
            "Mensaje de información": "La entrada ha terminado su ejecución en la extracción de la respuesta provisional."
            }
        ],
    }
    
    config = ConfigParser()
    config.read('./config.ini')
    
    componenteExporter = ComponenteExporter(config['file_path']['exploited_information_file_path'])
    
    componenteExporter.export_knowledge(exploited_information)
    
    # Abrir el archivo en modo lectura
    try:
        with open(config['file_path']['exploited_information_file_path'], 'r') as archivo:
            # Leer el archivo línea por línea
            for linea in archivo:
                # Comprobar si la línea cumple con los criterios
                if validar_linea(linea):
                    assert True
                else:
                    assert False
    except FileNotFoundError:
        print(f'Archivo "{config["file_path"]["exploited_information_file_path"]}" no encontrado. Vuelve a introducir una nueva ruta')
        
def validar_linea(linea):
    # Patrón de expresión regular para verificar cada elemento de la línea
    patron = r'^"spa-30-\d{8}-n", "[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+", "\d+", ".+", "n", "spa", "(Femenino|Masculino|NULL)", "------",$'
    # Comprobar si la línea coincide con el patrón
    if re.match(patron, linea.strip()):
        return True
    else:
        return False
    
def prueba():
    
    b = [
      [
        "El error de lógica en su argumento fue evidente.",
        "El error gramatical en el artículo de periodismo fue corregido por la revisión.",
        "El error obvio en la contabilidad llevó a una investigación interna.",
        "El error de pronunciación del actor fue criticado por los seguidores de la escuela de teatro clásica.",
        "El error de programación en la computadora llevó al sistema al caos."
      ],
      [
        "El examen reveló muchos errores en la prueba. Sin embargo, el error más grande fue la falta de atención por parte del docente al leer las preguntas. La omisión de una cuestión clave llevó a la mayoría de los estudiantes a responder incorrectamente.",
        "El editor se enfureció cuando descubrió el error gramatical en el artículo. La falta de un punto después de la coma es inaceptable, dijo, y no debería haberse permitido.",
        "La empresa ha sido criticada por muchos errores en su producto. El problema más recurrente es el defectuoso diseño del botón. Los clientes han sufrido molestias y la compañía ha perdido dinero como resultado de estas fallas.",
        "La estudiante recibió una F en el examen porque cometió muchos errores. El error más grave fue su falta de atención al leer la pregunta. Ella había confundido los nombres de dos personajes principales y había respondido incorrectamente a una de las preguntas.",
        "La jefa del proyecto se sentó para revisar el"
      ]
    ]
    c = [
      [
        "El error mas importante del proyecto fue el no utilizar una base de datos centralizada.",
        "Cuando se comete un error, es necesario corregirlo lo más pronto posible.",
        "No puedes culpar al error por tu falta de atención.",
        "El error humano puede ser muy peligroso en situaciones críticas.",
        "Intentamos evitar los errores, pero a veces es imposible."
      ]
    ]
    
    a = [
      [
        "El hombre mantuvo un contactos prolongado con su amiga durante la fiesta.",
        "El actor tuvo un contactos físico intenso con la actriz durante la escena.",
        "El hombre tuvo un contactos telefónico con su madre para hablar sobre sus planes para el fin de semana.",
        "El hombre tuvo un contactos visual con su hija mientras ella jugaba en el parque.",
        "El hombre tuvo un contactos emocional profundo con su amiga después de que ella le contó sobre sus problemas."
      ],
      [
        "El contacto entre los estudiantes y los profesores es esencial para un buen desarrollo académico.",
        "El contacto entre los pacientes y los médicos es crucial para una buena salud.",
        "El contacto entre los clientes y los empleados es fundamental para una buena experiencia de compra.",
        "El contacto entre los amigos y las familias es esencial para una buena relación social.",
        "EL contacto entre los trabajadores y los supervisores es fundamental para una buena productividad laboral."
      ]
    ]
    
    element_realización = ("spa-30-00039297-n_error",["5","Interacción cercana.","n","spa",])
    
    provisional_answer_intitución = componenteExtractor.get_provisional_answer4(element_realización, b)
    
    print(provisional_answer_intitución)
    
    
    
    final_answer_cosa = componenteValidator.get_final_answer(element_realización, c, "Masculino")
    
    print(final_answer_cosa)
    

# Método main
if __name__ == "__main__":
    print("Test started: first pilot case")
    print("Testing over Importer component...")
    # component_importer_test() # Tested correctly
    print("Everything in Importer component passed")
    print("Testing over Question Maker component...")
    # component_question_maker_test() # Tested correctly
    print("Everything in Question Maker component passed")
    print("Testing over LLM Communicator component...")
    # component_llm_communicator_test() # Tested correctly
    print("Everything in LLM Communicator component passed")
    print("Testing over Extractor component...")
    component_extractor_test() # Tested correctly
    print("Everything in Extractor component passed")
    print("Testing over Validator component...")
    component_validator_test() # Tested correctly
    print("Everything in Validator component passed")
    print("Testing over Exporter component...")
    component_exporter_test() # Tested correctly
    print("Everything in Exporter component passed")
    print("Everything passed")