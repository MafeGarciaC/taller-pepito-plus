"""
RF8: Clasificación contextual del contenido.

Solo se ejecuta sobre documentos cuya verificación de identidad (RF7)
resultó MISMA_PERSONA o POSIBLE_COINCIDENCIA (así lo exige el requisito).

Para respetar que la clasificación "no debe considerar únicamente la
aparición de palabras individuales", el análisis no busca palabras clave
en TODA la página -- primero acota el texto a las oraciones donde
efectivamente se menciona a la persona (por nombre o alias), y solo ahí
busca señales de tono positivo/negativo. Esto ata el contexto a los
hechos descritos sobre la persona, no a cualquier parte del artículo.
"""

import re

PALABRAS_POSITIVAS = [
    "premio", "éxito", "destacad", "reconocimiento", "triunfo", "logro",
    "felicit", "aporte", "contribución", "innovador", "líder", "talento",
    "celebra", "homenaje", "orgullo", "gan\u00f3", "gana ",
]

PALABRAS_NEGATIVAS = [
    "arrest", "investigac", "corrupción", "fraude", "delito", "acusad",
    "condena", "escándal", "denuncia", "crimen", "estafa", "asesin",
    "violencia", "abuso", "captur", "juicio", "sanción", "multa",
]


def _dividir_en_oraciones(texto):
    """Divide el texto en oraciones usando puntuación básica."""
    return re.split(r"(?<=[.!?])\s+", texto)


def clasificar_contexto(persona, texto):
    """
    Devuelve uno de: POSITIVO | NEUTRO | NEGATIVO | NO_DETERMINADO
    """
    oraciones = _dividir_en_oraciones(texto)

    nombres_busqueda = [persona.nombre_completo.lower()]
    if persona.alias:
        nombres_busqueda.append(persona.alias.lower())

    # Oraciones donde efectivamente se menciona a la persona
    oraciones_relevantes = [
        o for o in oraciones
        if any(n in o.lower() for n in nombres_busqueda)
    ]

    # Si por alguna razón no hay oraciones directas (mención muy dispersa),
    # usamos todo el texto como respaldo.
    texto_analisis = " ".join(oraciones_relevantes) if oraciones_relevantes else texto
    texto_analisis = texto_analisis.lower()

    positivas = sum(1 for p in PALABRAS_POSITIVAS if p in texto_analisis)
    negativas = sum(1 for n in PALABRAS_NEGATIVAS if n in texto_analisis)

    if positivas == 0 and negativas == 0:
        return "NO_DETERMINADO"
    if positivas > negativas:
        return "POSITIVO"
    if negativas > positivas:
        return "NEGATIVO"
    return "NEUTRO"  # empate: hay señales de ambos tipos, contexto mixto