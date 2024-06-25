

def generate_prompts(element):
    
    gloss = element[1][1]
    question = f"Como experto en traducción, necesito una traducción precisa al español de la siguiente frase: '{gloss}'."
    prompt_list = [question]
    
    return prompt_list