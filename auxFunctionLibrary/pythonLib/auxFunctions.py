
from itertools import product
import spacy
import re
import nltk

# Descargar el recurso necesario
nltk.download('averaged_perceptron_tagger')

# Cargar el modelo de lenguaje en español
nlp = spacy.load("es_core_news_sm")

def pluralize_word(word):
    """Función para obtener la forma plural de una palabra (En el caso de que esta sea plural, devolverá su plural)
       En el caso de que la palabra sea compuesta, devolverá las permutaciones plurales de esa palabra en español
       
       Parámetros:
        - word (string)= Palabra a pluralizar (Puede ser simple o compuesta)
        
       Retorna:
        - pluralize_words_list (Array<string>)
                - Si la palabra es simple la lista contendrá solo un elemento
                - Si la palabra es compuesta la lista contendrá las permutaciones plurales de la palabra
                    () 
    """
    # Lista de sufijos comunes para la formación del plural en español
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
    Extrae los sustantivos de una frase junto con sus posiciones, excluyendo los que son parte de compuestos.

    Args:
    sentence (str): La frase de la que se extraerán los sustantivos.

    Returns:
    List[Tuple[str, int, str, str]]: Una lista de tuplas que contiene el sustantivo, su posición,
                                     su dependencia y la palabra cabeza.
    """
    
    # Procesar la frase
    doc = nlp(sentence)
    
    # Extraer sustantivos que no sean parte de compuestos y agregar sus posiciones
    nouns_with_positions = [(token.text, token.i, token.dep_, token.head.text) for token in doc if token.pos_ == "NOUN" and token.dep_ != "compound"]
    
    return nouns_with_positions

def destokenize(original_tokens, new_tokens):
    """Reconstruye una oración a partir de una lista de tokens, manejando contracciones y posesivos."""
    sentence = ''
    for i, token in enumerate(new_tokens):
        # Check if the current token is a possessive
        is_current_possessive = is_possessive(original_tokens, i)
        
        # Check for word-word junction (excluding punctuation and special cases)
        if re.match(r'\w', token) and re.match(r'\w', new_tokens[i - 1]) and token not in ['.', ',', '!', '?', ':', ';'] and new_tokens[i - 1] not in ['¿', '¡']:
            # Handle contractions (ends with "'s")
            if re.match(r'\w', token) and i <= len(new_tokens) - 3 and new_tokens[i + 1] == "'" and not new_tokens[i + 2] == "s":
                # If the current token is a possessive, don't add extra space
                if is_current_possessive:
                    sentence += ' ' + token
                else:
                    sentence += ' ' + token + ' '
            elif token == "'" and not (i <= len(new_tokens) - 2 and new_tokens[i + 1] == 's'): 
                sentence += token
            else:
                sentence += ' ' + token
        else:
            # Handle spaces after sentence-ending punctuations
            if token in [')',';',':',',','.', '!','¡','¿','?'] and i < len(new_tokens) - 1:
                sentence += token + ' '
            elif token == "(":
                sentence += ' ' + token
            else:
                if is_possessive(original_tokens, i-2):
                    sentence += ' ' + token
                else:
                    sentence += token
    return sentence.strip()  # Remove leading/trailing spaces

def is_possessive(tokens, index):
    """Determina si la palabra en el índice dado es un posesivo."""
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
