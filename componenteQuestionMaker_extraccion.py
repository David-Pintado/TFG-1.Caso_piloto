

def generate_prompts(element):
    
    """
    Método para generar una lista de prompts para la fase de extracción basada en un elemento de 'knowledge_table'.
    
        Parámetros:
            - element (dict): Un elemento de 'knowledge_table'.
                    
        Retorna:
            - prompt_list (List[str]): Lista que contiene los prompts para la fase de extracción.
    """
    
    offset_word = element[0]
    word = offset_word.split('_')[1]
    gloss = element[1][1]
    question1 = f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo '{word}' en género masculino con el sentido de '{gloss}'."
    question2 = f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo '{word}' en género femenino con el sentido de '{gloss}'."
    prompt_list = [question1, question2]
    
    return prompt_list


# ------------------- Otras versiones antiguas --------------------- #

# question1 = f"Como experto en lingüística, proporciona cinco frases donde la palabra '{word}' aparezca solo como sustantivo en género masculino, con el sentido de '{gloss}'. Si no tiene forma masculina, usa el femenino sin modificarla. No utilices formas verbales ni otras variaciones de la palabra."
# question2 = f"Como experto en lingüística, proporciona cinco frases donde la palabra '{word}' aparezca solo como sustantivo en género femenino, con el sentido de '{gloss}'. Si no tiene forma femenina, usa el masculino sin modificarla. No utilices formas verbales ni otras variaciones de la palabra."
# prompt_list = [question1, question2]

# question1 = f"Como experto en lingüística, por favor, proporciona cinco frases donde la palabra '{word}' se utilice exclusivamente en su forma de sustantivo en género masculino, con el sentido de '{gloss}'. Si la palabra no tiene una forma masculina adecuada, utiliza la palabra en su género femenino sin modificarla. Cada frase debe contener la palabra '{word}' en género masculino (o femenino si no tiene masculino), asegurándote de mantener este género en todas las instancias dentro de la frase. No utilices formas verbales ni otras variaciones de la palabra."
# question2 = f"Como experto en lingüística, por favor, proporciona cinco frases donde la palabra '{word}' se utilice exclusivamente en su forma de sustantivo en género femenino, con el sentido de '{gloss}'. Si la palabra no tiene una forma femenina adecuada, utiliza la palabra en su género masculino sin modificarla. Cada frase debe contener la palabra '{word}' en género femenino (o masculino si no tiene femenino), asegurándote de mantener este género en todas las instancias dentro de la frase. No utilices formas verbales ni otras variaciones de la palabra."
# prompt_list = [question1, question2]

# question1 = f"Como experto en lingüística, por favor, proporciona cinco frases donde la palabra '{word}' se utilice exclusivamente en su forma de sustantivo en género masculino, con el sentido de '{gloss}'. Si la palabra no tiene una forma masculina adecuada, utiliza la palabra en su género femenino. Cada frase debe contener la palabra '{word}' en género masculino (o femenino si no tiene masculino), asegurándote de mantener este género en todas las instancias dentro de la frase. No utilices formas verbales ni otras variaciones de la palabra."
# question2 = f"Como experto en lingüística, por favor, proporciona cinco frases donde la palabra '{word}' se utilice exclusivamente en su forma de sustantivo en género femenino, con el sentido de '{gloss}'. Si la palabra no tiene una forma femenina adecuada, utiliza la palabra en su género masculino. Cada frase debe contener la palabra '{word}' en género femenino (o masculino si no tiene femenino), asegurándote de mantener este género en todas las instancias dentro de la frase. No utilices formas verbales ni otras variaciones de la palabra."
# prompt_list = [question1, question2]

# question1 = "Como experto en lingüística, por favor, proporciona cinco frases donde la palabra '" + word + "' se utilice en género masculino en todo momento, con el sentido de '" + gloss + "'. Cada frase debe contener la palabra '" + word + "' en género masculino, asegurándote de mantener este género en todas las instancias dentro de la frase."
# question2 = "Como experto en lingüística, por favor, proporciona cinco frases donde la palabra '" + word + "' se utilice en género femenino en todo momento, con el sentido de '" + gloss + "'. Cada frase debe contener la palabra '" + word + "' en género femenino, asegurándote de mantener este género en todas las instancias dentro de la frase."
# prompt_list = [question1, question2]