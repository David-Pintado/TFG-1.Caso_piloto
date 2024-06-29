
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions


def get_result(element, llm_answer_list):
    
    """Método para el extraer la traducción de la glosa.
    
       Parámetros:
        - element (dict): Elemento de la estructura de datos knowledge_table, compuesto por key + attributes.
        - llm_answer_list (list): Lista que se compone de respuestas del LLM que necesitan ser extraídas.
       Retorna:
        - result (str): Traducción de la glosa extraída y tratada.
    """
    
    result = auxFunctions.extract_llm_answers_translation(llm_answer_list[0])

    return result