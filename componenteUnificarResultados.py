import re

def extract_values(file_path):
    """
    Método para extraer los valores de un archivo que contiene los resultados de una experimentación
        del primer caso piloto.
    
    Parámetros:
        - file_path (str): Path del fichero que contiene los resultados de la experimentación.
        
    Retorna:
        - values (dict): Diccionario con los valores extraídos del archivo.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    values = {
        'entradas_totales': int(re.search(r'Entradas totales: (\d+)', content).group(1)),
        'masculino': int(re.search(r'Cantidad de género \'Masculino\' obtenido: (\d+)', content).group(1)),
        'femenino': int(re.search(r'Cantidad de género \'Femenino\' obtenido: (\d+)', content).group(1)),
        'conocimiento': int(re.search(r'Cantidad de conocimiento obtenido: (\d+)', content).group(1)),
        'null': int(re.search(r"Cantidad de casos sin clasificar \('NULL'\) obtenidos: (\d+)", content).group(1)),
        'null_extraccion': int(re.search(r"Cantidad de casos sin clasificar \('NULL'\) obtenidos en la fase de extracción: (\d+)", content).group(1)),
        'null_validacion': int(re.search(r"Cantidad de casos sin clasificar \('NULL'\) obtenidos en la fase de validación: (\d+)", content).group(1)),
        'total_frases': int(re.search(r"Total de frases analizadas de casos sin clasificar \('NULL'\): (\d+)", content).group(1)),
        'correctas': int(re.search(r'Correctas: (\d+)', content).group(1)),
        'incorrectas_1': int(re.search(r'Incorrectas de tipo 1.*?: (\d+)', content).group(1)),
        'incorrectas_2': int(re.search(r'Incorrectas de tipo 2.*?: (\d+)', content).group(1)),
        'incorrectas_3': int(re.search(r'Incorrectas de tipo 3.*?: (\d+)', content).group(1)),
    }
    return values

def calculate_percentage(part, whole):
    """
    Método para calcular el porcentaje de una parte en relación con el total.
        
    Parámetros:
        - part (int o float): La parte del total.
        - whole (int o float): El total.
        
    Retorna:
        - percentage (float): El porcentaje que representa 'part' del 'whole'. 
          Retorna 0 si 'whole' es 0 para evitar la división por cero.
    """
    return (part / whole) * 100 if whole > 0 else 0

# Paths to the input files
file1_path = './resultados_1.txt'
file2_path = './resultados_2.txt'

# Extract values from the files
values1 = extract_values(file1_path)
values2 = extract_values(file2_path)

# Combine values
combined_values = {key: values1[key] + values2[key] for key in values1}

# Calculate combined percentages
combined_percentages = {
    'entradas_totales': 100.00,
    'masculino': calculate_percentage(combined_values['masculino'], combined_values['entradas_totales']),
    'femenino': calculate_percentage(combined_values['femenino'], combined_values['entradas_totales']),
    'conocimiento': calculate_percentage(combined_values['conocimiento'], combined_values['entradas_totales']),
    'null': calculate_percentage(combined_values['null'], combined_values['entradas_totales']),
    'null_extraccion': calculate_percentage(combined_values['null_extraccion'], combined_values['entradas_totales']),
    'null_validacion': calculate_percentage(combined_values['null_validacion'], combined_values['entradas_totales']),
    'correctas': calculate_percentage(combined_values['correctas'], combined_values['total_frases']),
    'incorrectas_1': calculate_percentage(combined_values['incorrectas_1'], combined_values['total_frases']),
    'incorrectas_2': calculate_percentage(combined_values['incorrectas_2'], combined_values['total_frases']),
    'incorrectas_3': calculate_percentage(combined_values['incorrectas_3'], combined_values['total_frases']),
}

# Write combined results to a new file
output_path = './resultados_unificados.txt'
with open(output_path, 'w', encoding='utf-8') as result_file:
    result_file.write("\n\nINFORMACIÓN DE LOS RESULTADOS DE LA EXPERIMENTACIÓN DEL PRIMER CASO PILOTO\n\n")
    result_file.write(f"Entradas totales: {combined_values['entradas_totales']} ({combined_percentages['entradas_totales']:.2f}%)\n")
    result_file.write(f"Cantidad de género 'Masculino' obtenido: {combined_values['masculino']} ({combined_percentages['masculino']:.2f}%)\n")
    result_file.write(f"Cantidad de género 'Femenino' obtenido: {combined_values['femenino']} ({combined_percentages['femenino']:.2f}%)\n")
    result_file.write(f"Cantidad de conocimiento obtenido: {combined_values['conocimiento']} ({combined_percentages['conocimiento']:.2f}%)\n")
    result_file.write(f"Cantidad de casos sin clasificar ('NULL') obtenidos: {combined_values['null']} ({combined_percentages['null']:.2f}%)\n")
    result_file.write(f"Cantidad de casos sin clasificar ('NULL') obtenidos en la fase de extracción: {combined_values['null_extraccion']} ({combined_percentages['null_extraccion']:.2f}%)\n")
    result_file.write(f"Cantidad de casos sin clasificar ('NULL') obtenidos en la fase de validación: {combined_values['null_validacion']} ({combined_percentages['null_validacion']:.2f}%)\n")
    result_file.write(f"Total de frases analizadas de casos sin clasificar ('NULL'): {combined_values['total_frases']} (100.00%)\n")
    result_file.write(f"Correctas: {combined_values['correctas']} ({combined_percentages['correctas']:.2f}%)\n")
    result_file.write(f"Incorrectas de tipo 1 (Generacion de palabras con otro part of speech. La palabra que buscamos no está como noun en la frase.): {combined_values['incorrectas_1']} ({combined_percentages['incorrectas_1']:.2f}%)\n")
    result_file.write(f"Incorrectas de tipo 2 (La palabra que buscamos no aparece en la frase.): {combined_values['incorrectas_2']} ({combined_percentages['incorrectas_2']:.2f}%)\n")
    result_file.write(f"Incorrectas de tipo 3 (La palabra aparece en la frase, pero no viene precedida de un articulo que indique su género.): {combined_values['incorrectas_3']} ({combined_percentages['incorrectas_3']:.2f}%)\n")
