import componenteExtractor
import componenteValidator
import sys
sys.path.append("./auxFunctionLibrary")
from pythonLib import auxFunctions

a = ("spa-30-00007347-n_causa", [
    "5",
    "Una entidad que produce o causa algo.",
    "n",
    "spa",
    [
      [
        "La lluvia es la causa del crecimiento de las plantas.",
        "El estrés es la causa de la depresión.",
        "El calor es la causa de la evaporación del agua.",
        "El fracaso es la causa de la desmotivación.",
        "La falta de educación es la causa de la pobreza."
      ],
      [
        "La contaminación es la causa de la salud pública.",
        "El cambio climático es la causa de los desastres naturales.",
        "La falta de educación es la causa del desempleo.",
        "La pobreza es la causa de la violencia en las ciudades.",
        "La corrupción es la causa de la inestabilidad política."
      ]
    ],
    "Femenino",
    [
      [
        "La causa de la sequía es la falta de lluvia.",
        "El médico busca determinar la causa de la enfermedad.",
        "La causa principal del desastre natural fue el terremoto.",
        "La causa de la explosión fue un cortocircuito en la electricidad.",
        "La causa de la extinción de las especies es la actividad humana."
      ]
    ],
    "Femenino"
  ]
)

b =      [
      [
        "La lluvia es la causa del crecimiento de las plantas.",
        "El estrés es la causa de la depresión.",
        "El calor es la causa de la evaporación del agua.",
        "El fracaso es la causa de la desmotivación.",
        "La falta de educación es la causa de la pobreza."
      ],
      [
        "La contaminación es la causa de la salud pública.",
        "El cambio climático es la causa de los desastres naturales.",
        "La falta de educación es la causa del desempleo.",
        "La pobreza es la causa de la violencia en las ciudades.",
        "La corrupción es la causa de la inestabilidad política."
      ]
    ]

c =      [
      [
        "El estado de la economía es crítico.",
        "El estado de las relaciones entre los países es tenso.",
        "El estado de la tecnología ha cambiado mucho en los últimos años.",
        "El estado de la educación es preocupante.",
        "El estado de la salud pública es delicado."
      ]
    ]

print(componenteExtractor.get_provisional_result4(a,b))

# print(componenteValidator.get_final_result(a,c,"Masculino"))

# print(auxFunctions.destokenize(['the', 'sports', 'team', "'", 's', 'were', 'great', '.', 'He', 'used', 'to', 'call', 'her', "'", 'supeeer', "'", '.']))

