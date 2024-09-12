
from itertools import product
import spacy
import re
import nltk

# Descargar el recurso necesario
nltk.download('averaged_perceptron_tagger')

# Cargar el modelo de lenguaje en español
nlp = spacy.load("es_core_news_sm")

def pluralize_word(word):
    
    """
    Método para obtener la forma plural de una palabra en castellano. Si word es una palabra compuesta,
    devuelve las permutaciones plurales de esa palabra.
    
        Parámetros:
            - word (str): Palabra en castellano a pluralizar
        Retorna:
            - pluralize_words_list (List[str]): Lista de plurales de la palabra. Incluye la forma singular
    """
    
    # Lista de sufijos comunes para la formación del plural en castellano
    suffixes = {
        'z': 'ces',
        'l': 'les',
        'r': 'res',
        'n': 'nes',
        'y': 'yes',
        'j': 'jes',
        'd': 'des',
        's': 'ses',
        'x': 'xes'
    }

    prepositions = ["a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "durante", "en", "entre", "hacia", "hasta", "mediante", "para", "por", "según", "sin", "so", "sobre", "tras"]

    words = word.split()

    # Función para pluralizar una palabra individual
    def pluralize(word):
        for suffix, plural in suffixes.items():
            if word.endswith(suffix):
                return word[:-1] + plural
        return word + 's'

    plural_permutations = []
    for word in words:
        if word in prepositions:
            plural_permutations.append([word])
        else:
            plural = pluralize(word)
            if plural != word:
                plural_permutations.append([word, plural])
            else:
                plural_permutations.append([word])

    composite_permutations = product(*plural_permutations)
    pluralize_words_list = []
    for permutation in composite_permutations:
        pluralize_words_list.append(" ".join(permutation))

    return pluralize_words_list


def extract_nouns_with_positions(sentence):
        
    """
    Método que extrae los sustantivos de una frase junto con sus posiciones.
    
        Parámetros:
            - sentence (str): Oración sobre la que extraer los sustantivos
        Retorna:
            - nouns_with_positions (List[Tuple[str, int]]): Lista de tuplas que contienen el sustantivo junto a su posición 
                                                            en la frase 'sentence' tokenizada
    """
    
    # Procesar la frase
    doc = nlp(sentence)
    
    # Extraer sustantivos que no sean parte de compuestos y agregar sus posiciones
    nouns_with_positions = [(token.text, token.i, token.dep_, token.head.text) for token in doc if token.pos_ == "NOUN" and token.dep_ != "compound"]
    
    return nouns_with_positions

def destokenize(original_tokens, new_tokens):
    
    """
    Método que reconstruye una oración a partir de una lista de tokens, manejando contracciones y posesivos.
    
        Parámetros:
            - original_tokens (List[str]): Lista de tokens de la oración completa. Necesaria para saber información sobre cada token
            - new_tokens (List[str]): Sublista de tokens de original_tokens.
        Retorna:
            - sentence (str): Oración resultante de la correcta unión de los tokens    
    """
    
    sentence = ''
    for i, token in enumerate(new_tokens):
        # Comprobar si el token actual es un posesivo
        is_current_possessive = is_possessive(original_tokens, i)
        
        # Verificar la unión palabra-palabra (excluyendo puntuación y casos especiales)
        if re.match(r'\w', token) and re.match(r'\w', new_tokens[i - 1]) and token not in ['.', ',', '!', '?', ':', ';'] and new_tokens[i - 1] not in ['¿', '¡']:
            # Manejar las contracciones (termina en "'s")
            if re.match(r'\w', token) and i <= len(new_tokens) - 3 and new_tokens[i + 1] == "'" and not new_tokens[i + 2] == "s":
                # Si el token actual es posesivo, no agregar espacio adicional
                if is_current_possessive:
                    sentence += ' ' + token
                else:
                    sentence += ' ' + token + ' '
            elif token == "'" and not (i <= len(new_tokens) - 2 and new_tokens[i + 1] == 's'): 
                sentence += token
            else:
                sentence += ' ' + token
        else:
            # Manejar espacios después de las puntuaciones al final de la oración
            if token in [')',';',':',',','.', '!','¡','¿','?'] and i < len(new_tokens) - 1:
                sentence += token + ' '
            elif token == "(":
                sentence += ' ' + token
            else:
                if is_possessive(original_tokens, i-2):
                    sentence += ' ' + token
                else:
                    sentence += token
    return sentence.strip()  # Eliminar espacios iniciales/finales

def is_possessive(tokens, index):
    
    """
    Método para determinar si una palabra correspondiente al índice de una lista de tokens es un posesivo.
    
        Parámetros:
            - tokens (List[str]): Lista de tokens
            - index (number): Índice
        Retorna:
            - Valor booleano (True/False)
            
    """
    
    # Etiquetar las partes de la oración
    pos_tags = nltk.pos_tag(tokens)
    
    # Verificar si la palabra en el índice dado es un posesivo
    if index >= 0 and index < len(tokens) - 1:
        # Comprobar si la palabra siguiente es un apóstrofe
        if tokens[index + 1] == "'":
            # Comprobar si la palabra actual es un sustantivo propio (NNP) o plural (NNS)
            if pos_tags[index][1] in ["NNP", "NNS"]:
                return True
    
    return False

def extract_llm_answers_translation(llm_answer):
    
    """
    Método para extraer la respuesta del LLM.
    
        Parámetros:
            - llm_answer (str): Respuesta del LLM sin tratar. Contiene una única frase
        Retorna:
            - llm_extracted_answer (str): Respuesta del LLM extraída. 
            
    """
    
    # Eliminar los saltos de linea
    llm_extracted_answer = llm_answer.replace('\n',' ').replace('\n\n',' ').strip().strip(".")
    # Si es una traducción tratarla
    if type(llm_extracted_answer) is list:
        if len(llm_extracted_answer) > 0:
            llm_extracted_answer = llm_extracted_answer[0]
        elif len(llm_extracted_answer) == 0:
            llm_extracted_answer = ""
    llm_extracted_answer = llm_extracted_answer.split(". ")[0].strip()
    llm_extracted_answer = llm_extracted_answer.strip("'")
    llm_extracted_answer = llm_extracted_answer.strip().replace('"', '').replace("\"", "").replace('\\', '').replace("\\\"", "").replace("?", "").replace("¿", "").capitalize()
    if not llm_extracted_answer.endswith('.'):
        llm_extracted_answer += '.'
    return llm_extracted_answer


def extract_llm_answers_set_of_phrases(llm_answer):
    
    """
    Método para extraer la respuesta del LLM.
    
        Parámetros:
            - llm_answer (str): Respuesta del LLM sin tratar. Contiene separadores de oraciones 
        Retorna:
            - llm_extracted_answer (List[str]): Respuesta del LLM extraída. Se forma una lista con las frases.
            
    """

    # Eliminar los saltos de línea
    llm_extracted_answer = llm_answer.replace('\n', ' ').replace('\n\n', ' ').strip()
    # Comprobar si tiene separadores de frases.
    if re.split(r'\d+\)|\d+\.', llm_extracted_answer)[1:] != [] and len(re.split(r'\d+\)|\d+\.', llm_extracted_answer)) >= 5: 
        # Dividir el texto en frases utilizando cualquier secuencia de un número seguido de un punto o paréntesis como criterio de separación
        llm_extracted_answer = re.split(r'\d+\)|\d+\.', llm_extracted_answer)[1:]
        # Quitar los espacios blancos del principio y final de las frases y asegurarse de que cada frase termine con un punto
        llm_extracted_answer = [answer.strip() + '.' if not answer.strip().endswith('.') else answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("'", "").replace('\\', '') for answer in llm_extracted_answer]
        # Si empieza por '-' eliminarlo
        llm_extracted_answer = [answer[1:].strip() if answer.startswith('-') else answer for answer in llm_extracted_answer]
        return llm_extracted_answer
    # Comprobar si tiene más de una frase separada por un punto seguido de un espacio
    elif len(llm_extracted_answer.split('. ')) >= 5:
        # Dividir el texto en frases utilizando el punto seguido de un espacio como criterio de separación
        llm_extracted_answer = [phrase for phrase in llm_extracted_answer.split('. ')]
        # Quitar los espacios blancos del principio y final de las frases y asegurarse de que cada frase termine con un punto
        llm_extracted_answer = [answer.strip() + '.' if not answer.strip().endswith('.') else answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("'", "").replace('\\', '') for answer in llm_extracted_answer]
        # Si empieza por '-' eliminarlo
        llm_extracted_answer = [answer[1:].strip() if answer.startswith('-') else answer for answer in llm_extracted_answer]
        return llm_extracted_answer
    # Comprobar si tiene más de una frase separada por un punto y coma seguido de un espacio
    elif len(llm_extracted_answer.split('; ')) >= 5:
        # Dividir el texto en frases utilizando el punto y coma seguido de un espacio como criterio de separación
        llm_extracted_answer = [phrase for phrase in llm_extracted_answer.split('; ')]
        # Quitar los espacios blancos del principio y final de las frases y asegurarse de que cada frase termine con un punto
        llm_extracted_answer = [answer.strip() + '.' if not answer.strip().endswith('.') else answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("'", "").replace('\\', '') for answer in llm_extracted_answer]
        # Si empieza por '-' eliminarlo
        llm_extracted_answer = [answer[1:].strip() if answer.startswith('-') else answer for answer in llm_extracted_answer]
        return llm_extracted_answer
    # Comprobar si tiene más de una frase separada por un punto y coma seguido de un espacio
    elif len(llm_extracted_answer.split(', ')) >= 5:
        # Dividir el texto en frases utilizando el punto y coma seguido de un espacio como criterio de separación
        llm_extracted_answer = [phrase for phrase in llm_extracted_answer.split(', ')]
        # Quitar los espacios blancos del principio y final de las frases y asegurarse de que cada frase termine con un punto
        llm_extracted_answer = [answer.strip() + '.' if not answer.strip().endswith('.') else answer.strip() for answer in llm_extracted_answer]
        # Quitar las comillas y barras de las frases
        llm_extracted_answer = [answer.replace('"', '').replace("'", "").replace('\\', '') for answer in llm_extracted_answer]
        # Si empieza por '-' eliminarlo
        llm_extracted_answer = [answer[1:].strip() if answer.startswith('-') else answer for answer in llm_extracted_answer]
        return llm_extracted_answer
    # Si no cumple ninguna de las condiciones anteriores, devolver la respuesta sin tratar
    return llm_extracted_answer


def save_json(file_path, json):
    
    """
    Método para guardar datos JSON en un archivo en la ruta proporcionada.

        Parámetros:
            - file_path (str): Ruta completa donde se guarda el archivo JSON.
            - json_data (str): Datos JSON que se escriben en el archivo.

        Retorna:
            - None
    """
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(json)