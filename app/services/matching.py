"""
RF5: Identificación de contenido relacionado.

Determina si el texto de una página descargada tiene alguna coincidencia
con los datos registrados de la persona (nombre, alias, ciudad, profesión,
organización, palabras relacionadas). Esta es una versión simple basada
en coincidencia de texto -- se puede sofisticar más adelante.
"""


def es_contenido_relacionado(persona, texto):
    """
    Devuelve (True, None) si hay al menos una coincidencia, o
    (False, motivo) si no se encontró ninguna -- el motivo se guarda
    en el documento para que RF5 pueda mostrar por qué fue descartado.
    """
    texto_lower = texto.lower()

    candidatos = [persona.nombre_completo]
    if persona.alias:
        candidatos.append(persona.alias)
    if persona.ciudad:
        candidatos.append(persona.ciudad)
    if persona.profesion_cargo:
        candidatos.append(persona.profesion_cargo)
    if persona.empresa_organizacion:
        candidatos.append(persona.empresa_organizacion)
    if persona.palabras_relacionadas:
        candidatos.extend([
            p.strip() for p in persona.palabras_relacionadas.split(",") if p.strip()
        ])

    coincidencias = [c for c in candidatos if c and c.lower() in texto_lower]

    if coincidencias:
        return True, None

    return False, (
        "No se encontraron coincidencias con nombre, alias, ciudad, "
        "profesión, organización ni palabras relacionadas."
    )