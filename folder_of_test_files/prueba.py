
import componenteExtractor
from componenteValidator import ComponenteValidator
import re


array = {'id': 'cmpl-cd76e688-6c34-4cc7-a6d8-67651240e997', 'object': 'text_completion', 'created': 1711043421, 'model': './models/zephyr-7b-alpha.Q4_K_M.gguf', 'choices': [{'text': "Question: Como experto en lingüística, por favor, proporciona cinco frases donde la palabra 'entidad' se utilice en género masculino en todo momento, con el sentido de 'aquello que se percibe o se sabe o se infiere que tiene su existencia propia distinta (viva o no viva)'. Cada frase debe contener la palabra 'entidad' en género masculino, asegurándote de mantener este género en todas las instancias dentro de la frase. Answer:\n1. El roedor es una entidad pequeña y oculta, que a veces causa daño a nuestras cosechas.\n2. La noche es una entidad oscura y misteriosa, que nos inspire a relatar historias y leyendas.\n3. El bosque es una entidad silenciosa y vasto, que nos hace pensar en nuestro propósito y nuestra relación con la naturaleza.\n4. El círculo vicioso es una entidad destructiva y autosostenible, que nos mantiene alejados de nuestros objetivos y nos hace creer que no tenemos otras opciones.\n5. El poema es una entidad artística y emocionante, que nos ayuda a escapar de nuestras preocupaciones y a ver el mundo desde una perspect", 'index': 0, 'logprobs': None, 'finish_reason': 'length'}], 'usage': {'prompt_tokens': 130, 'completion_tokens': 200, 'total_tokens': 330}}
array2 = {'id': 'cmpl-dca4e623-1772-490c-97f9-55e442c5e7ae', 'object': 'text_completion', 'created': 1711043525, 'model': './models/zephyr-7b-alpha.Q4_K_M.gguf', 'choices': [{'text': "Question: Como experto en lingüística, por favor, proporciona cinco frases donde la palabra 'entidad' se utilice en género femenino en todo momento, con el sentido de 'aquello que se percibe o se sabe o se infiere que tiene su existencia propia distinta (viva o no viva)'. Cada frase debe contener la palabra 'entidad' en género femenino, asegurándote de mantener este género en todas las instancias dentro de la frase. Answer: 1. La entidad política es una fuerza poderosa en nuestro mundo. 2. La entidad geográfica del desierto es difícil de cruzar. 3. La entidad económica es un indicador clave de la salud de una nación. 4. La entidad social es crucial para nuestra existencia humana. 5. La entidad legal es una estructura bien definida para resolver conflictos.", 'index': 0, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 132, 'completion_tokens': 102, 'total_tokens': 234}}

# llm_extracted_answer1 = componenteExtractor.extract_llm_answers(array)
# llm_extracted_answer2 = componenteExtractor.extract_llm_answers(array2)

# print('1------------------')
# print(llm_extracted_answer1)

# print('2------------------')
# print(llm_extracted_answer2)

# Eliminar los saltos de linea
# llm_extracted_answer1 = [llm_extracted_answer1.replace('\n',' ').strip()]
# # Dividir el texto en frases utilizando cualquier secuencia de un número seguido de un punto como criterio de separación
# llm_extracted_answer_list1 = re.split(r'\d+\.', llm_extracted_answer1[0])[1:]
# # Quitar los espacios blancos del principio y final de las frases 
# llm_extracted_answer_list1 = [answer.strip() for answer in llm_extracted_answer_list1]
# # Imprimir el resultado 
# # print(llm_extracted_answer_list1)


# # Eliminar los saltos de linea
# llm_extracted_answer2 = [llm_extracted_answer2.replace('\n',' ').strip()]
# # Dividir el texto en frases utilizando cualquier secuencia de un número seguido de un punto como criterio de separación
# llm_extracted_answer_list2 = re.split(r'\d+\.', llm_extracted_answer2[0])[1:]
# # Quitar los espacios blancos del principio y final de las frases 
# llm_extracted_answer_list2 = [answer.strip() for answer in llm_extracted_answer_list2]
# Imprimir el resultado 
# print(llm_extracted_answer_list2)


# Devolver el resultado provisional
# print(componenteExtractor.get_provisional_answer('entidad',[llm_extracted_answer_list1, llm_extracted_answer_list2]))

# a = [
#       [
#         "El conjunto de piezas del juego de ajedrez es un objeto único.",
#         "El conjunto de lecciones aprendidas es esencial para el éxito.",
#         "El conjunto de componentes de la computadora es un sistema completo.",
#         "El conjunto de datos recogidos es la fuente principal de información.",
#         "El conjunto de reglas del club es imprescindible para todos los miembros."
#       ],
#       [
#         "El botánico examinó el conjunto de hojas hervidas como un objeto único para investigar su potencial medicinal.",
#         "La química analizó el conjunto de moléculas orgánicas sintéticas para determinar su reactividad.",
#         "La farmacéutica investigó el conjunto de medicamentos disponibles para mejorar la salud del paciente.",
#         "El arquitecto examinó el conjunto de planos para asegurarse de que todos los detalles de diseño fueran coherentes.",
#         "La matemática estudió el conjunto de ecuaciones matemáticas para comprender su estructura y propiedades."
#       ]
#     ]

# b = [
#       [
#         "El análisis semántico requiere un conjunto femenino de categorías y conceptos para comprender correctamente el significado de las palabras.",
#         "El conjunto femenino de frecuencias y co-ocurrencias ayuda a determinar las relaciones sintácticas entre las palabras de un lenguaje.",
#         "En la gramática, un conjunto femenino de reglas y patrones permite identificar y analizar las estructuras del lenguaje.",
#         "El estudio de la variante regional y social en el uso del lenguaje implica tener un conjunto femenino de características y diferencias entre los dialectos.",
#         "La psicología cognitiva estudia cómo los individuos procesan y organizan la información mediante un conjunto femenino de esqu"
#       ]
#     ]

# print('--------- Pruebas diferentes "get_provisional_answers" ----------------')
# print('')
# print('Get_provisional_answer 1')
# print(componenteExtractor.get_provisional_answer('conjunto',a))
# print('')
# print('Get_provisional_answer 2')
# print(componenteExtractor.get_provisional_answer2('conjunto',a))
# print('')
# print('Get_provisional_answer 3')
# print(componenteExtractor.get_provisional_answer3('conjunto',a))
# print(' ')
# print(' ')
# print('Validación')
# print(componenteValidator.get_final_answer('conjunto', b, 'Masculino'))


# b = [
#       [
#         "El niño es una manifestación del ser humano en su etapa inicial de vida.",
#         "El embrión es una etapa temprana del ser humano cuando se encuentra en el útero.",
#         "El hombre es un ser capaz de actuar y funcionar de manera independiente.",
#         "El bebé es una expresión del ser humano a medida que crece y desarrolla.",
#         "El adulto es un ser capaz de tomar decisiones y actuar independientemente."
#       ]
#     ]

# c =  [
#       [
#         "El tráfico en la carretera es una verdadera causa de accidentes.",
#         "El cambio climático es una causa preocupante de la erosión costera.",
#         "El consumo excesivo de alimentos es una causa principal de obesidad.",
#         "El tabaco es una causa conocida de cáncer pulmonar.",
#         "El alcohol es una causa importante de accidentes automovilísticos."
#       ],
#       [
#         "La causa de su felicidad es la educación.",
#         "El trabajo le ha dado a su hija una causa para seguir adelante.",
#         "La causa de su tristeza es la pérdida de su mascota.",
#         "La causa del crecimiento económico en nuestro país es el aumento de la inversión.",
#         "La causa de su victoria es su estrategia sólida y su entrenamiento físico.  En todas las instancias mencionadas, la palabra causa es utilizada en su forma en género femenino para designar una entidad que produce o causa algo."
#       ]
#     ]

# print('--------- Pruebas diferentes "get_provisional_answers" ----------------')
# print('')
# print('Get_provisional_answer 1')
# print(componenteExtractor.get_provisional_answer('causa',c))
# print('')
# print('Get_provisional_answer 2')
# print(componenteExtractor.get_provisional_answer2('causa',c))
# print('')
# print('Get_provisional_answer 3')
# print(componenteExtractor.get_provisional_answer3('causa',c))

# conponente5 = ComponenteValidator(5)
# print(' ')
# print(' ')
# print('Validación')
# print(conponente5.get_final_answer('ser', b, 'Masculino'))


a = [
      [
        "La abstracción del tamaño es una característica común en los objetos físicos más grandes del mundo.",
        "El concepto abstracto del amor es difícil de definir y es expresado de manera diferente en distintas culturas.",
        "La abstracción del color es un aspecto importante en la creación de una escala de grises.",
        "La abstracción del tiempo es fundamental para medir eficiencia y productividad.",
        "La abstracción del movimiento es utilizada en la fisiología para medir la salud y el rendimiento."
      ],
      [
        "La abstracción del color es un término general que se crea al examinar los ejemplos de azul y rojo y seleccionar las características comunes.",
        "La abstracción del tiempo es una idea abstracta que se desarrolla al considerar los ejemplos de la duración y la frecuencia.",
        "La abstracción del tamaño es un concepto abstracto que surge al analizar las muestras de longitud y anchura y extraer las características comunes.",
        "La abstracción del gusto es una idea abstracta que surge al considerar los ejemplos de preferencia y seleccionar las características comunes.",
        "La abstracción del movimiento es un término general que se desarrolla al examinar los ejemplos de cambio y transición y extraer"
      ]
    ]

element = ["spa-30-00002137-n_abstracción", [
                        "2",
                        "un concepto general que se forma seleccionando características comunes a partir de ejemplos concretos",
                        "n",
                        "spa"
                      ]]



# print('--------- Pruebas diferentes "get_provisional_answers" ----------------')
# print('')
# print('Get_provisional_answer 1')
# print(' ')
# print('Respuesta que se obtiene: ')
# print(componenteExtractor.get_provisional_answer(element,a))
# print('')
# print('Get_provisional_answer 2')
# print(' ')
# print('Respuesta que se obtiene: ')
# print(componenteExtractor.get_provisional_answer2(element,a))
# print('')
# print('Get_provisional_answer 3')
# print(' ')
# print('Respuesta que se obtiene: ')
# print(componenteExtractor.get_provisional_answer3(element,a))

# /////////////////

element2 = ["spa-30-00007347-n_causa", [
        "5",
    "Una entidad que produce o causa algo",
    "n",
    "spa"
                      ]]


p = [
      [
        "El accidente de tráfico fue causado por una falla mecánica.",
        "La caída del precio del dólar es un efecto secundario de una baja demanda.",
        "El aumento de precios es un resultado directo de una inflación sostenida.",
        "El conflicto política está causado por la oposición al nuevo presidente.",
        "La muerte de la joven fue causada por una intoxicación accidental."
      ],
      [
        "La causa de la epidemia fue la falta de higiene personal.",
        "La causa del incendio fue una cortocircución en las instalaciones.",
        "La causa del accidente fue una falla mecánica.",
        "La causa del estrés era la presión laboral excesiva.",
        "La causa del conflicto era la falta de comunicación efectiva.   Note: In these examples, causa is a noun in the feminine gender. In English, cause can also be a noun, but it does not have gender. In Spanish, cause can only be a noun when used as a legal term, and it is also in the feminine gender."
      ]
    ]


print('--------- Pruebas diferentes "get_provisional_answers" ----------------')
print('')
print('Get_provisional_answer 1')
print(' ')
print('Respuesta que se obtiene: ')
print(componenteExtractor.get_provisional_answer(element,a))
print('')
print('Get_provisional_answer 2')
print(' ')
print('Respuesta que se obtiene: ')
print(componenteExtractor.get_provisional_answer2(element,a))
print('')
print('Get_provisional_answer 3')
print(' ')
print('Respuesta que se obtiene: ')
print(componenteExtractor.get_provisional_answer3(element,a))
print('Get_provisional_answer 4')
print(' ')
print('Respuesta que se obtiene: ')
print(componenteExtractor.get_provisional_answer4(element,a))