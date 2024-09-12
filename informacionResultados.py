import json
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions 

# Variables globales para contar errores
correct_count = 0
incorrect_1_count = 0
incorrect_2_count = 0
incorrect_3_count = 0
cantidad_masculino = 0
cantidad_femenino = 0
total_frases = 0
null_extraccion = 0
null_validacion = 0

# Leer el archivo JSON
with open('./knowledge_table.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Procesar cada elemento en el archivo JSON
for key, value in data.items():

    if value["Validation gender"] == "Masculino":
        cantidad_masculino += 1
    elif value["Validation gender"] == "Femenino":
        cantidad_femenino += 1

    if value["Extraction gender"] == "NULL" or value["Validation gender"] == "NULL":
        correct_count += value["Correctas"]
        incorrect_1_count += value["Incorrectas de tipo 1: Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase"]
        incorrect_2_count += value["Incorrectas de tipo 2: la palabra a analizar no aparece en la frase"]
        incorrect_3_count += value["Incorrectas de tipo 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género"]
        if value["Extraction gender"] == "NULL":          
            total_frases += len(auxFunctions.extract_llm_answers_set_of_phrases(value["Extraction LLM answers"][0])) + len(auxFunctions.extract_llm_answers_set_of_phrases(value["Extraction LLM answers"][1]))
        elif value["Validation gender"] == "NULL":
            total_frases += len(auxFunctions.extract_llm_answers_set_of_phrases(value["Validation LLM answers"][0]))
        if value["Mensaje de información"] == "La entrada ha terminado su ejecución en la fase de extracción.":
            null_extraccion += 1
        elif value["Mensaje de información"] == "La entrada ha terminado su ejecución en la fase de validación.":
            null_validacion += 1

# Calcular los porcentajes de frases incorrectas
porcentaje_incorrecto_1 = (incorrect_1_count / total_frases) * 100 if total_frases > 0 else 0
porcentaje_incorrecto_2 = (incorrect_2_count / total_frases) * 100 if total_frases > 0 else 0
porcentaje_incorrecto_3 = (incorrect_3_count / total_frases) * 100 if total_frases > 0 else 0
porcentaje_correcto = (correct_count / total_frases) * 100 if total_frases > 0 else 0

# Calcular la suma de las entradas analizadas
suma_total = cantidad_masculino + cantidad_femenino + null_extraccion + null_validacion

# Calcular la suma total de los NULL
suma_total_null = null_extraccion + null_validacion

# Calcular porcentajes de 'Femenino' y 'NULL' respecto al total de 'Masculino', 'Femenino' y 'NULL'
porcentaje_femenino = (cantidad_femenino / suma_total) * 100
porcentaje_null = (suma_total_null / suma_total) * 100
porcentaje_masculino = (cantidad_masculino / suma_total) * 100
porcentaje_null_extraccion = (null_extraccion / suma_total) * 100
porcentaje_null_validacion = (null_validacion / suma_total) * 100

# Guardar los resultados en un archivo de texto
with open('./resultados.txt', 'w', encoding='utf-8') as result_file:
    result_file.write(f"\n\nINFORMACIÓN DE LOS RESULTADOS DE LA EXPERIMENTACIÓN DEL PRIMER CASO PILOTO\n\n")
    result_file.write(f"Entradas totales: {suma_total} (100.00%)\n")
    result_file.write(f"Cantidad de género 'Masculino' obtenido: {cantidad_masculino} ({porcentaje_masculino:.2f}%)\n")
    result_file.write(f"Cantidad de género 'Femenino' obtenido: {cantidad_femenino} ({porcentaje_femenino:.2f}%)\n")
    result_file.write(f"Cantidad de conocimiento obtenido: {cantidad_femenino + cantidad_masculino} ({(porcentaje_femenino + porcentaje_masculino):.2f}%)\n")
    result_file.write(f"Cantidad de casos sin clasificar ('NULL') obtenidos: {suma_total_null} ({porcentaje_null:.2f}%)\n")
    result_file.write(f"Cantidad de casos sin clasificar ('NULL') obtenidos en la fase de extracción: {null_extraccion} ({porcentaje_null_extraccion:.2f}%)\n")
    result_file.write(f"Cantidad de casos sin clasificar ('NULL') obtenidos en la fase de validación: {null_validacion} ({porcentaje_null_validacion:.2f}%)\n")
    result_file.write(f"Total de frases analizadas de casos sin clasificar ('NULL'): {total_frases} (100.00%)\n")
    result_file.write(f"Correctas: {correct_count} ({porcentaje_correcto:.2f}%)\n")
    result_file.write(f"Incorrectas de tipo 1 (Generacion de palabras con otro part of speech. la palabra a analizar no está como sustantivo en la frase.): {incorrect_1_count} ({porcentaje_incorrecto_1:.2f}%)\n")
    result_file.write(f"Incorrectas de tipo 2 (la palabra a analizar no aparece en la frase): {incorrect_2_count} ({porcentaje_incorrecto_2:.2f}%)\n")
    result_file.write(f"Incorrectas de tipo 3 (La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género): {incorrect_3_count} ({porcentaje_incorrecto_3:.2f}%)\n")
