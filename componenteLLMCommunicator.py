
import json
from llama_cpp import Llama

class ComponenteLLMCommunicator:
    
    def __init__(self, language_model_path):
        self.language_model_path = language_model_path 
        self.llm = None

    # Metodo para cargar el modelo
    def load_model(self):
        # load the model
        print("Loading the model...")
        try:
            self.llm = Llama(model_path= self.language_model_path)
        except ValueError:
            print(f'LLM "{self.language_model_path}" no encontrado. Vuelve a introducir una nueva ruta') 
        print("Model loaded.")
    
    # Metodo para realizar la pregunta al modelo. Devuelve lo obtenido.
    def run_the_model(self, prompt):
        # run the model
        print("Running model...")
        question = f"Question: {prompt} Answer:"
        output = self.llm(
            question, # Prompt
            max_tokens= 200, # Generate up to 200 tokens, set to None to generate up to the end of the context window
            stop = [ "Question: ", "Explanation: "], # Stop generating just before the model would generate a new question
            temperature = 0.1, # Ajusta la aleatoriedad del texto generado (predeterminado: 0,8).  
            echo=True # Echo the prompt back in the output
        )
        
        #print(json.dumps(output, indent=2, ensure_ascii=False))
        
        return output