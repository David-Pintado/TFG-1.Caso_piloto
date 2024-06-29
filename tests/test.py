

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
    frases_piloto_masculino = "\n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras.",
    frases_piloto_femenino = "1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."
    
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
       
    # Tests para obtener el resultado de la fase de extracción answer -----------------------------------
    
    elemento_prueba_tierra_masculino = "\n1. El gran desafío que enfrenta la tierra es combatir la erosión y mantener su fertilidad.\n2. La tierra está siendo devastada por los cambios climáticos y la deforestación.\n3. La tierra necesita que los humanos cambien su manera de pensar y actuar para protegerla.\n4. El hombre ha estado explotando y devastando la tierra durante siglos.\n5. La tierra ha sido la fuente de vida y prosperidad para millones de personas durante milenios.\n6. La tierra es un recurso limitado que necesita ser utilizado y preservado con cuidado.\n7. La tierra es un regalo de la naturaleza que ha sido y seguirá siendo vital para la supervivencia humana.\n8. La tierra es más que un lugar, es un sistema complejo que afecta a todas las formas de vida.\n9. La tierra es la fuente de todos los recursos que necesitamos para sobrevivir y prosperar.\n10. La tierra es un legado que debemos preservar para las generaciones futuras."
    elemento_prueba_tierra_femenino = "1. La tierra es una madre generosa que nos da sustento. 2. La tierra es una hermosa dama que necesita nuestra atención y amor. 3. La tierra es una piel que nos cubre y protege. 4. La tierra es una madre que nos guía y nos da vida. 5. La tierra es una madre que nos da alimentos y agua. 6. La tierra es una madre que nos da un lugar en la que vivir y crecer. 7. La tierra es una madre que nos da un hogar y una casa. 8. La tierra es una madre que nos da un lugar en la que compartir nuestras vidas. 9. La tierra es una madre que nos da un lugar en la que vivir y crecer juntos. 10. La tierra es una madre que nos da una oportunidad de crecer y desarrollarnos."
        
    # --------------------------------------   Prueba 1   -------------------------------------------
        
    element_tierra = ("spa-30-09334396-n_tierra", ["2", "la parte sólida de la superficie de la Tierra", "n","spa"])
    
    llm_answer_list = [elemento_prueba_tierra_masculino, elemento_prueba_tierra_femenino]
    
    result = componenteExtractor_extraccion.get_result(element_tierra, llm_answer_list)
    
    assert result == ["Femenino"], "Should be ['Femenino']"
    
    # --------------------------------------   Prueba 2   -------------------------------------------
    
    element_objeto =  ("spa-30-00002684-n_objeto", ["1","Una entidad tangible y visible; una entidad que puede moldear una sombra.","n","spa"])   
    
    llm_answer_list_2 =   [
      " 1. El objeto reflejaba su forma en la superficie del agua.\n2. La luna era un objeto brillante en el cielo.\n3. El espejo mostraba un objeto aterrador.\n4. El sombrero de papel que estaba colgando del árbol era un objeto curioso.\n5. El reflejo en la ventana era un objeto que parecía haberse deslizado de otro mundo.",
      " 1. La piedra es un objeto tangible y visible, capaz de proyectar una sombra larga en la pared.\n2. El vase de cristal es un objeto delicado y elegante, que refleja la luz con una belleza incomparable.\n3. La escultura de bronce es un objeto artístico y valioso, que captura la belleza humana en cada detalle.\n4. El libro es un objeto educativo y culturalmente significante, que transmite conocimiento y ideas a través del tiempo.\n5. La caja de madera es un objeto funcional y práctico, que protege nuestros objetos valiosos y preciados."
    ]
    
    result_objeto = componenteExtractor_extraccion.get_result(element_objeto, llm_answer_list_2)
    
    assert result_objeto == ["Masculino"], "Should be ['Masculino']"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_ser = ("spa-30-00004258-n_ser", ["4", "Una entidad viva.", "n", "spa"])
    
    llm_answer_list_3 = [
        " 1. El león es un animal salvaje y poderoso.\n2. El árbol es una entidad viva que crece y se desarrolla a lo largo del tiempo.\n3. El hombre es una criatura compleja, con muchas facetas y cualidades.\n4. El río es un ser vivo que fluye y cambia constantemente.\n5. El sol es una entidad viva que ilumina nuestro planeta y nos da calor y luz.",
        " 1. La madre es la fuente de vida para sus hijos.\n2. La flor es la belleza natural del jardín.\n3. La luna es la guía nocturna de los viajeros.\n4. La lluvia es la fuente de vida para las plantas.\n5. La paz es el objetivo más deseado por los humanos."
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
                            "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
                            }
                        ], "Should be True"
    
    # --------------------------------------   Prueba 4   -------------------------------------------
    
    element_vida = ("spa-30-00006269-n_vida", ["12","Cosas vivas en su conjunto.","n","spa"])
    
    
    llm_answer_list_4 = [
      " 1. La vida animal es una variedad maravillosa y compleja.\n2. El mundo vegetal es un mosaico de colores y texturas.\n3. Los seres humanos son la creación más compleja del universo.\n4. La fauna marina es una comunidad intrincada e interdependiente.\n5. El bosque tropical es un mundo en constante cambio y evolución.",
      " 1. La vida marina es un mundo misterioso y atractivo.\n2. La vida vegetal es la base de la cadena alimentaria.\n3. La vida animal es una variedad infinita de formas y tamaños.\n4. La vida en el desierto es difícil y exigente.\n5. La vida en la selva es rica y variada."
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
      " En la teoría de conjuntos, el artículo n es una variable que representa cualquier subconjunto de un conjunto dado. En la lógica proposicional, el artículo n es una variable que representa cualquier proposición. En la geometría euclidiana, el artículo n es una variable que representa cualquier punto en el espacio. En la teoría de números, el artículo n es una variable que representa cualquier número entero positivo. En la física, el artículo n es una variable que representa cualquier cantidad de materia o energía.",
      " En la teoría de conjuntos, la intersección de dos conjuntos se denota por la letra 'n'.\n\n1. La palabra \"artículo\" es un sustantivo femenino en español que significa \"un elemento o parte de una clase o grupo\".\n\n2. En el campo de lingüística, la definición de \"artículo\" como un elemento gramatical se refiere a palabras como \"el\", \"la\", y \"un\" en inglés, que se utilizan para indicar la especificación o referencia de un objeto o concepto.\n\n3. En el contexto de la literatura, \"artículo\" también puede referirse a una pieza escrita publicada en una revista o periódico, como \"la revista científica Nature\".\n\n4. En la"
    ],
    "Masculino"
    ])
    
    llm_answer_list = [
      "\n\n1. El artículo de entrada en el curso de lingüística es fundamental para comprender las diferencias entre los idiomas.\n2. El artículo definido en español se utiliza para indicar que el sustantivo a la que se refiere es conocido por ambos interlocutores.\n3. El artículo indefinido en inglés se emplea para expresar una cantidad no especificada de elementos.\n4. El artículo en francés se escribe como \"le\" o \"la\", dependiendo del género y número del sustantivo al que se refiere.\n5. El artículo en alemán es un signo de puntuación que indica el inicio de una oración.\n\nEn resumen, los artículos son elementos gramaticales importantes en muchas lengu"
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
      " 1. La cosa que se proyecta en la pared es un objeto real, no una ilusión.\n2. El sol, una cosa brillante y caliente, está afligido por el eclipse.\n3. La cosa que se mueve lentamente en el río es un barco.\n4. La cosa que se ve en la noche oscura es una sombra.\n5. El objeto que se desliza por el suelo es una cosa pesada y fría.",
      " 1. La cosa que creó la luna es un reflejo de su propia belleza.\n2. La cosa que flota en el aire es solo una sombra de lo real.\n3. La cosa que se mueve en la oscuridad es solo una imagen de la verdad.\n4. La cosa que se ve en el espejo es solo una reflexión de la realidad.\n5. La cosa que se siente en tu corazón es solo un eco de la verdad."
    ],
    "Femenino"
    ])
    
    llm_answer_list_2 = [
      " 1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando, pero se sentía incómoda. 3) Aunque la cosa parecía difícil, finalmente logró hacerla. 4) La cosa más importante era mantenerse unido a su familia. 5) Al ver la cosa que había hecho, sintió una gran sensación de orgullo.\n\n¿Qué frases podrías crear utilizando el sustantivo 'cosa' en género femenino con el sentido de 'Una entidad tangible y visible; una entidad que puede moldear una sombra.'?\n\n1) La cosa era tan hermosa que no podía creer lo que veía. 2) No sabía qué cosa estaba pasando,"
    ]
    
    result_cosa = componenteExtractor_validacion.get_result(element_cosa, llm_answer_list_2)
    
    assert result_cosa == ['Femenino'], "Should be True"
    
    # --------------------------------------   Prueba 3   -------------------------------------------
    
    element_son = ("spa-30-00546389-n_son", [
    "3",
    "Acto de cantar.",
    "n",
    "spa",
    [
      " 1. El son de la soprano era impresionante.\n2. El son de los niños en la escuela de música era agradable.\n3. El son de la guitarra fue muy bien interpretado.\n4. El son de la canción favorita del compositor es un clásico.\n5. El son de la cantante en el concierto fue magnífico.",
      " 1. La canción es un son hermoso.\n2. El concierto fue un gran son.\n3. La soprano interpretó un son magnífico.\n4. La melodía es un son agradable.\n5. La canción de la noche fue un son encantador."
    ],
    "Masculino"
    ])
    
    llm_answer_list_3 =   [
      " 1) El son es un arte muy antiguo. 2) El son mejilla la voz de los cantantes. 3) El son es una forma de expresión cultural. 4) El son puede ser un medio para comunicarse con Dios. 5) El son es una parte importante de la música tradicional.\n\n"
    ]
    
    result_son = componenteExtractor_validacion.get_result(element_son, llm_answer_list_3)
    
    assert result_son == ["NULL",
    {
      "Correctas.": 0
    },
    {
      "Incorrectas de tipo 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.": 5
    },
    {
      "Incorrectas de tipo 2: La palabra que buscamos no aparece en la frase.": 0
    },
    {
      "Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.": 0
    },
    {
      "Mensaje de información": "La entrada ha terminado su ejecución en la fase de validación."
    }], "Should be True"
    
def component_exporter_test():
    
    knowledge_table = {
  "spa-30-00002684-n_cosa": [
    "2",
    "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
    "n",
    "spa",
    [
      " 1. La cosa que se proyecta en la pared es un objeto real, no una ilusión.\n2. El reflejo en el agua es solo una cosa, pero parece ser más que eso.\n3. La sombra que sigue a la persona es una cosa tangible y visible, pero no tiene vida propia.\n4. La imagen que se proyecta en la pantalla es una cosa real, pero no es lo mismo que el objeto original.\n5. El eco que se escucha en el túnel es solo una cosa, pero su sonido parece ser más que eso.",
      " 1. La cosa que se proyecta en la pared es un reflejo de lo real.\n2. La cosa que flota en el aire es solo una ilusión.\n3. La cosa que se ve en el espejo es solo una imagen.\n4. La cosa que se mueve en la oscuridad es solo un fantasma.\n5. La cosa que se ve en la noche es solo una sombra."
    ],
    "Femenino",
    [
      " 1) La cosa más importante en la vida es amar. 2) La cosa más difícil de conseguir es la felicidad. 3) La cosa más hermosa del mundo es el amor. 4) La cosa más valiosa que tiene un ser humano es su salud. 5) La cosa más importante para una persona es estar feliz.\n\n"
    ],
    "Femenino"
  ],
  "spa-30-00002684-n_objeto": [
    "1",
    "Una entidad tangible y visible; una entidad que puede moldear una sombra.",
    "n",
    "spa",
    [
      " 1. El objeto reflejaba la luna brillante en su superficie.\n2. La sombra del objeto se proyectó sobre el piso oscuro.\n3. El objeto tenía forma de un cilindro, y su sombra era una recta paralela a la pared.\n4. El objeto estaba tan cerca que su sombra cubría casi toda la superficie del suelo.\n5. La sombra del objeto se deslizó lentamente sobre el piso, dejando un rastro de luz en su camino.",
      " 1. La piedra es un objeto tangible y visible, que puede moldear una sombra.\n2. El cuadro en la pared es un objeto tangible y visible, que puede moldear una sombra.\n3. La escultura de bronce en el parque es un objeto tangible y visible, que puede moldear una sombra.\n4. La estatua de mármol en la plaza es un objeto tangible y visible, que puede moldear una sombra.\n5. El busto de piedra en el jardín es un objeto tangible y visible, que puede moldear una sombra."
    ],
    "Masculino",
    [
      " 1) El objeto de mi deseo es viajar por Europa. 2) El objeto de mi investigación es comprender la historia de la humanidad. 3) El objeto de mi admiración es el talento y habilidades de los atletas olímpicos. 4) El objeto de mi curiosidad es descubrir los secretos del universo. 5) El objeto de mi ambición es alcanzar la cima de la montaña más alta del mundo.\n\n"
    ],
    "Masculino"
  ],
  "spa-30-00003553-n_conjunto": [
    "2",
    "Un conjunto de partes que se considera como una sola entidad.",
    "n",
    "spa",
    [
      " 1. Un conjunto de piezas de ropa es un traje completo.\n2. Un conjunto de herramientas es una caja de herramientas.\n3. Un conjunto de libros es una bibliografía.\n4. Un conjunto de lecciones es un curso.\n5. Un conjunto de piezas de juegos es un set de juegos.",
      " 1. El conjunto de piezas del reloj funcionan perfectamente juntas.\n\n2. La colección de libros es un conjunto único y valioso.\n\n3. El grupo de amigos se considera como una sola entidad, siempre que estén juntos.\n\n4. El conjunto de herramientas es indispensable para cualquier trabajo en la construcción.\n\n5. La colección de pinturas es un conjunto único y valioso, que se exhibe en el museo local."
    ],
    "Masculino",
    [
      " 1) El conjunto de piezas se ensambló fácilmente. 2) El conjunto de datos proporciona información valiosa. 3) El conjunto de herramientas es muy completo. 4) El conjunto de reglas facilita la toma de decisiones. 5) El conjunto de materiales se utiliza para construir el prototipo.\n\n"
    ],
    "Masculino"
  ],
  "spa-30-00004258-n_ser": [
    "4",
    "Una entidad viva.",
    "n",
    "spa",
    [
      " 1. El león es un animal salvaje y poderoso.\n2. El árbol es una planta que crece en la tierra y proporciona sombra y frutas.\n3. El hombre es un ser social y complejo, con emociones y pensamientos.\n4. El río es una corriente de agua que fluye desde las montañas hasta el mar, llevando sedimentos y vida.\n5. El sol es una estrella brillante en el cielo, que proporciona calor y luz a la Tierra.",
      " 1. La madre es la encarnación de amor y sacrificio.\n2. La naturaleza es una fuente inagotable de belleza y misterio.\n3. La cultura es un reflejo del espíritu humano y su evolución histórica.\n4. La ciencia es la herramienta más poderosa para comprender el mundo y sus leyes.\n5. La fe es una fuerza que guía a los hombres en busca de la verdad y la justicia."
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
      "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
    }
  ],
  "spa-30-00004475-n_ser": [
    "2",
    "Un ser vivo que tiene (o puede desarrollar) la capacidad de actuar o funcionar de manera independiente.",
    "n",
    "spa",
    [
      " 1. Un ser humano es un organismo biológico complejo que posee la capacidad de pensar, razonar y tomar decisiones.\n2. El ser humano es una entidad social y cultural que se adapta a su entorno y interactúa con otros seres humanos.\n3. La inteligencia artificial es un sistema informático que simula la capacidad de pensamiento y razonamiento de los seres humanos, pero sin la capacidad de actuar independientemente.\n4. El robot es una máquina programada para realizar tareas específicas y funcionar de manera autónoma en ciertas circunstancias.\n5. La vida extraterrestre es un ser biológico que habita en otros planetas o sistemas estelares, pero cuya existencia aún no ha sido confirmada por la",
      " 1. La planta es un ser vivo capaz de absorber nutrientes y crecer.\n2. La bacteria es un ser vivo microscópico que puede causar enfermedades.\n3. La hormona es un ser químico biológicamente activo que regula procesos vitales en el cuerpo humano.\n4. La computadora es un ser electrónico programable capaz de realizar cálculos y procesar información.\n5. La luna es un ser celestial que ilumina la noche y afecta las mareas."
    ],
    "Masculino",
    [
      " 1. El ser humano es un individuo capaz de tomar decisiones y actuar de forma autónoma. 2. La inteligencia artificial es un ser que simula la capacidad de pensamiento y acción humana. 3. Un robot es un ser mecánico programado para realizar tareas específicas de manera independiente. 4. El embrión es un ser en desarrollo que comienza a funcionar de forma autónoma una vez se implanta en el útero. 5. Un organismo unicelular es un ser vivo que puede actuar y reproducirse de manera independiente.\n\n"
    ],
    "Masculino"
  ],
  "spa-30-00006269-n_vida": [
    "12",
    "Cosas vivas en su conjunto.",
    "n",
    "spa",
    [
      " 1) La vida animal es una variedad maravillosa y compleja que nos rodea.\n2) El planeta está lleno de vida, desde los microbios más pequeños hasta las masas de algas flotantes.\n3) La vida en el océano profundo es aún menos conocida que la vida en la superficie, pero es posiblemente tan abundante y diversa como la vida en la superficie.\n4) El bosque es un mundo lleno de vida, desde los insectos más pequeños hasta los grandes mamíferos.\n5) La vida marina es una variedad increíblemente rica y compleja que nos rodea en nuestras costas y en el fondo del océano.",
      " 1. La vida marina es un mundo misterioso y atractivo.\n2. La vida vegetal es la base de la cadena alimentaria.\n3. La vida animal es una variedad infinita de formas y tamaños.\n4. La vida en el desierto es difícil y exigente.\n5. La vida en la selva tropical es rica y diversa."
    ],
    "Femenino",
    [
      " 1) La vida es un regalo inigualable. 2) La vida nos enseña a aprender. 3) La vida es una gran escuela. 4) La vida es un viaje sin destino. 5) La vida es un misterio que no se puede descifrar.\n\n"
    ],
    "Femenino"
  ],
  "spa-30-00007347-n_causa": [
    "5",
    "Una entidad que produce o causa algo.",
    "n",
    "spa",
    [
      " 1. La lluvia es la causa del crecimiento de las plantas.\n2. El estrés es la causa de la depresión.\n3. El calor es la causa de la evaporación del agua.\n4. El frío es la causa de la congelación del agua.\n5. La contaminación es la causa de la enfermedad.",
      " 1. La contaminación es la causa de la salud pública.\n2. El cambio climático es la causa de los desastres naturales.\n3. La pobreza es la causa de la falta de educación.\n4. La violencia es la causa del tráfico de drogas.\n5. La corrupción es la causa de la injusticia social."
    ],
    "Femenino",
    [
      " 1) La causa de la sequía es la falta de lluvia. 2) El médico busca determinar la causa de la enfermedad. 3) La causa del incendio fue un cortocircuito eléctrico. 4) La causa del aumento de precios es la inflación. 5) La causa de la extinción de especies es la actividad humana.\n\n"
    ],
    "Femenino"
  ],
  "spa-30-00007846-n_alguien": [
    "1",
    "Un ser humano.",
    "n",
    "spa",
    [
      " 1. El hombre que camina por la calle es alguien.\n2. Alguien está hablando en la habitación.\n3. Es alguien que me ha ayudado muchas veces.\n4. Alguien necesita ayuda aquí.\n5. Alguien debe haber dejado esto aquí.",
      " 1. La mujer que estaba caminando por la calle era alguien.\n2. Alguien se acercó a ella y le dijo algo.\n3. Espero encontrar a alguien en este lugar.\n4. Alguien me llamó hoy por teléfono.\n5. La persona que estaba sentada en la esquina era alguien."
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
      "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
    }
  ],
  "spa-30-00007846-n_humano": [
    "1",
    "Un ser humano.",
    "n",
    "spa",
    [
      " 1. Un hombre es un ser humano.\n2. El profesor es un ser humano.\n3. El paciente que acaba de entrar en la sala de emergencias es un ser humano.\n4. El hombre que camina por la calle es un ser humano.\n5. El hombre que está leyendo el libro es un ser humano.",
      " 1. La mujer es un ser humano.\n2. La persona que acaba de entrar es una humana.\n3. Esas dos chicas son humanas.\n4. La enfermera es una humana.\n5. La mujer que está hablando conmigo es una humana."
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
      "Mensaje de información": "La entrada ha terminado su ejecución en la fase de extracción."
    }
  ],
  "spa-30-00007846-n_persona": [
    "1",
    "Un ser humano.",
    "n",
    "spa",
    [
      " 1. Un hombre es una persona.\n2. El profesor es una persona respetable.\n3. El paciente necesita la ayuda de una persona calificada.\n4. El hombre que camina por la calle es una persona desconocida.\n5. El hombre que escribió el libro es una persona famosa.",
      " 1. La persona caminaba por la calle.\n2. La persona estaba leyendo un libro.\n3. La persona hablaba con su amiga.\n4. La persona estaba comiendo la cena.\n5. La persona estaba trabajando en el escritorio."
    ],
    "Femenino",
    [
      " 1) La persona es un ser complejo y misterioso. 2) La persona tiene derechos humanos inalienables. 3) La persona puede ser buena o malvada. 4) La persona puede ser feliz o triste. 5) La persona puede ser inteligente o estúpida.\n\n"
    ],
    "Femenino"
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