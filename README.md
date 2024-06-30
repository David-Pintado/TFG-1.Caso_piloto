1. CASO PILOTO - EXPLOTACIÓN DEL GÉNERO DE LAS PALABRAS

Primer caso piloto del TFG: Arquitectura adaptable para la explotación del conocimiento en modelos de lenguaje (LLMs, Large Language Models).
En este caso piloto, el conocimiento que se extrae es el género de los sustantivos del WordNet en castellano.
Para lograr el objetivo, se hace uso de la arquitectura adaptable definida.

Instrucciones para la configuración del entorno

1. Descargue el proyecto.
2. En el mismo directorio, cree una carpeta llamada `models`.
3. La carpeta `models` debe contener los siguientes archivos:
   - `zephyr-7b-alpha.Q4_K_M.gguf`
   - `openchat-3.5-0106.Q4_K_M.gguf`

Estructura de directorios

your_parent_directory/
│
├── your_project_directory/
│   ├── your_project_files...
│
├── models/
│   ├── zephyr-7b-alpha.Q4_K_M.gguf
│   └── openchat-3.5-0106.Q4_K_M.gguf

Para descargarlos:

1. Instale la herramienta `huggingface-hub`:

   pip3 install huggingface-hub

2. Descargue el modelo `zephyr-7b-alpha.Q4_K_M.gguf`:

   huggingface-cli download TheBloke/zephyr-7B-alpha-GGUF zephyr-7b-alpha.Q4_K_M.gguf --local-dir ./models --local-dir-use-symlinks False

3. Descargue el modelo `openchat-3.5-0106.Q4_K_M.gguf`:

   huggingface-cli download TheBloke/openchat-3.5-0106-GGUF openchat-3.5-0106.Q4_K_M.gguf --local-dir ./models --local-dir-use-symlinks False

---

Además, asegúrese de tener instaladas las siguientes dependencias necesarias para ejecutar el proyecto:

1. Instale `spacy`:

   pip install spacy

2. Instale `nltk`:

   pip install nltk

3. Descargue el modelo de idioma en español para `spacy`:

   python3.10 -m spacy download es_core_news_sm

4. Instale `unidecode`:

   pip install unidecode

5. Instale `llama-cpp-python`:

   pip install --upgrade --quiet llama-cpp-python

---

Ejemplo de ejecución del archivo `componenteManager.py`:

1. Ejecute el script `componenteManager.py`:

   python3.10 componenteManager.py

Si aparece un error indicando que falta un módulo, asegúrese de haber seguido todos los pasos anteriores para instalar las dependencias necesarias.

Con estos pasos, habrás configurado el entorno necesario para ejecutar el caso piloto de explotación del género de las palabras utilizando la arquitectura adaptable definida.
