import json

# Variables globales para contar errores
error_1_count = 0
error_2_count = 0
error_3_count = 0
cantidad_masculino = 0
cantidad_femenino = 0
total_frases = 0
null_extraccion = 0
null_validacion = 0

# Leer el archivo JSON
with open('./resultados_experimentaciones/experimentacion_1/source_information.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Procesar cada elemento en el archivo JSON
for key, value in data.items():
    # Validar la longitud de la lista value
    if len(value) > 7:
        if value[7] == "Masculino":
            cantidad_masculino += 1
        elif value[7] == "Femenino":
            cantidad_femenino += 1

    if len(value) > 5 and value[5] == "NULL":
        if len(value) > 6:
            error_1_count += value[6].get("Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.", 0)
            error_2_count += value[7].get("Error 2: La palabra que buscamos no aparece en la frase.", 0)
            error_3_count += value[8].get("Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.", 0)
            total_frases += len(value[4][0]) + len(value[4][1])
        if len(value) > 9:
            if value[9].get("Mensaje de información") == "La entrada ha terminado su ejecución en la extracción de la respuesta provisional.":
                null_extraccion += 1
            elif value[9].get("Mensaje de información") == "La entrada ha terminado su ejecución en la validación de la respuesta provisional.":
                null_validacion += 1

    if len(value) > 7 and value[7] == "NULL":
        if len(value) > 8:
            error_1_count += value[8].get("Error 1: Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.", 0)
            error_2_count += value[9].get("Error 2: La palabra que buscamos no aparece en la frase.", 0)
            error_3_count += value[10].get("Error 3: La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.", 0)
            total_frases += len(value[6][0])
        if len(value) > 11:
            if value[11].get("Mensaje de información") == "La entrada ha terminado su ejecución en la extracción de la respuesta provisional.":
                null_extraccion += 1
            elif value[11].get("Mensaje de información") == "La entrada ha terminado su ejecución en la validación de la respuesta provisional.":
                null_validacion += 1

# Calcular los porcentajes de errores
porcentaje_error_1 = (error_1_count / total_frases) * 100 if total_frases > 0 else 0
porcentaje_error_2 = (error_2_count / total_frases) * 100 if total_frases > 0 else 0
porcentaje_error_3 = (error_3_count / total_frases) * 100 if total_frases > 0 else 0

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
with open('./resultados_experimentaciones/experimentacion_1/resultados.txt', 'w', encoding='utf-8') as result_file:
    result_file.write(f"\n\nINFORMACIÓN DE LOS RESULTADOS DE LA EXPERIMENTACIÓN\n\n")
    result_file.write(f"Entradas totales: {suma_total} (100.00%)\n")
    result_file.write(f"Cantidad 'Masculino' obtenidos: {cantidad_masculino} ({porcentaje_masculino:.2f}%)\n")
    result_file.write(f"Cantidad 'Femenino' obtenidos: {cantidad_femenino} ({porcentaje_femenino:.2f}%)\n")
    result_file.write(f"Cantidad de conocimiento obtenido: {cantidad_femenino + cantidad_masculino} ({(porcentaje_femenino + porcentaje_masculino):.2f}%)\n")
    result_file.write(f"Cantidad 'NULL' obtenidos: {suma_total_null} ({porcentaje_null:.2f}%)\n")
    result_file.write(f"'NULL' obtenidos en la fase de extracción de la respuesta provisional: {null_extraccion} ({porcentaje_null_extraccion:.2f}%)\n")
    result_file.write(f"'NULL' obtenidos en la fase de validación de la respuesta provisional: {null_validacion} ({porcentaje_null_validacion:.2f}%)\n")
    result_file.write(f"Total de frases sobre los que se han analizado los errores de 'NULL': {total_frases}\n")
    result_file.write(f"Error 1 (Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.): {error_1_count} ({porcentaje_error_1:.2f}%)\n")
    result_file.write(f"Error 2 (La palabra que buscamos no aparece en la frase.): {error_2_count} ({porcentaje_error_2:.2f}%)\n")
    result_file.write(f"Error 3 (La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.): {error_3_count} ({porcentaje_error_3:.2f}%)\n")
