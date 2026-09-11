import re

PALABRAS_POSITIVAS = [
    "premio", "éxito", "destacad", "reconocimiento", "triunfo", "logro",
    "felicit", "aporte", "contribución", "innovador", "líder", "talento",
    "celebra", "homenaje", "orgullo", "ganó", "gana ",
]

PALABRAS_NEGATIVAS = [
    "arrest", "investigac", "corrupción", "fraude", "delito", "acusad",
    "condena", "escándal", "denuncia", "crimen", "estafa", "asesin",
    "violencia", "abuso", "captur", "juicio", "sanción", "multa",
]


def _dividir_en_oraciones(texto):
    return re.split(r"(?<=[.!?])\s+", texto)


def clasificar_contexto(persona, texto):
    """Devuelve: POSITIVO | NEUTRO | NEGATIVO | NO_DETERMINADO"""
    oraciones = _dividir_en_oraciones(texto)

    nombres_busqueda = [persona.nombre_completo.lower()]
    if persona.alias:
        nombres_busqueda.append(persona.alias.lower())

    # Analizar solo las oraciones donde aparece la persona
    oraciones_relevantes = [
        o for o in oraciones
        if any(n in o.lower() for n in nombres_busqueda)
    ]

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
    return "NEUTRO"
