
from llama_cpp import Llama

class ComponenteLLMCommunicator:
    
    def __init__(self, language_model_path):
        self.language_model_path = language_model_path 
        self.llm = None

    def load_model(self):
        
        """
        Método para cargar el modelo de lenguaje.

            Parámetros:
                - self: instancia de la clase que contiene este método.

            Retorna:
                - None: Este método no retorna ningún valor, pero carga el modelo en el atributo `llm` de la instancia.
        """
        
        print("Loading the model...")
        try:
            self.llm = Llama(model_path= self.language_model_path)
        except ValueError:
            print(f'LLM "{self.language_model_path}" no encontrado. Vuelve a introducir una nueva ruta') 
        print("Model loaded.")
    

    def run_the_model(self, prompt):
        
        """
        Método para ejecutar el modelo de lenguaje con un prompt dado y retornar la respuesta generada.

            Parámetros:
                - self: instancia de la clase que contiene este método.
                - prompt (str): El prompt o pregunta que se envía al modelo.

            Retorna:
                - llm_answer (str): La respuesta generada por el modelo después de procesar el prompt.
        """

        print("Running model...")
        question = f"Question: {prompt} Answer:"
        output = self.llm(
            question, # Prompt
            max_tokens= 200,  # Genera hasta 200 tokens, (None para generar hasta el final de la ventana de contexto)
            stop = [ "Question: ", "Explanation: ", "Q: ", "Explicación: ", "\n\n# ¿", "\n\n¿", "\n\nPregunta: ¿"], # Para el proceso cuando encuentra una nueva pregunta o una explicación
            temperature = 0.1, # Ajusta la aleatoriedad del texto generado (predeterminado: 0,8).  
            echo=True # Repite el mensaje nuevamente en la salida.
        )
        
        # Imprimir la respuesta del LLM por consola
        # print(json.dumps(output, indent=2, ensure_ascii=False))
        
        # Extraer el texto devuelto
        llm_answer = output['choices'][0]['text']
        # Dividirlo en dos partes (la parte de la pregunta, la parte de la respuesta). Obtener la respuesta
        llm_answer = llm_answer.split('Answer:')[1]
        
        return llm_answer