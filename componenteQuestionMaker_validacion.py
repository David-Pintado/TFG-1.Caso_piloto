

def generate_prompts(element):
    
    offset_word = element[0]
    word = offset_word.split('_')[1]
    gloss = element[1][1]
    extraction_phase_result = element[1][5]
    if extraction_phase_result.lower() == "masculino":
        question = f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo '{word}' en género masculino con el sentido de '{gloss}'."
    elif extraction_phase_result.lower() == "femenino":
        question = f"Como experto en lingüística, proporciona cinco frases utilizando el sustantivo '{word}' en género femenino con el sentido de '{gloss}'."
    prompt_list = [question]
    
    return prompt_list