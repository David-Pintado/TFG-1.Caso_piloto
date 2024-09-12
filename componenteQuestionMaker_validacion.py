

def generate_prompts(element):
    
    """
    Método para generar una lista de prompts para la fase de validación basada en un elemento de 'knowledge_table'.
    
        Parámetros:
            - element (dict): Un elemento de 'knowledge_table'.
                    
        Retorna:
            - prompt_list (List[str]): Lista que contiene los prompts para la fase de validación.
    """
    
    offset_word = element[0]
    word = offset_word.split('_')[1]
    gloss = element[1]["Gloss"]
    gender = element[1]["Extraction gender"].lower()
    question = f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo '{word}' en género {gender} con el sentido de '{gloss}'."
    prompt_list = [question]
    
    return prompt_list