
from itertools import product
import spacy
import re

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

def split_by_position_char(string, position):
    if position < 0 or position >= len(string):
        raise ValueError("La posición está fuera de los límites de la cadena.")
    
    # Obtener el carácter en la posición dada
    char = string[position]
    
    # Dividir la cadena por el carácter encontrado en la posición
    partes = string.split(char)
    
    return partes

def destokenize(tokens):
    # Reconstruir la oración a partir de los tokens
    sentence = ''
    for i, token in enumerate(tokens):
        if i > 0 and re.match(r'\w', token) and re.match(r'\w', tokens[i - 1]):
            sentence += ' '
        sentence += token
    return sentence