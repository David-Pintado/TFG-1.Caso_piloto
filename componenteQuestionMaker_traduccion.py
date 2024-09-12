

def generate_prompts(element):
    
    """
    Método para generar una lista de prompts para la traducción de una glosa de un elemento de 'knowledge_table'.
    
        Parámetros:
            - element (dict): Un elemento de 'knowledge_table'.
                    
        Retorna:
            - prompt_list (List[str]): Lista que contiene los prompts para la traducción de una glosa en inglés al castellano.
    """
    
    gloss = element[1]["Gloss"]
    question = f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: '{gloss}'."
    prompt_list = [question]
    
    return prompt_list