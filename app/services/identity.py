"""
RF7: Verificación de identidad.

El nombre completo por sí solo es una señal débil -- pueden existir muchas
personas con el mismo nombre. Este servicio combina el nombre con señales
adicionales (alias, ciudad, profesión, organización) para decidir con qué
nivel de confianza el documento realmente habla de la persona consultada.

Lógica de decisión:
    - Si aparece el nombre completo Y al menos 1 señal adicional
      coincide -> MISMA_PERSONA (alta confianza)
    - Si aparece el nombre completo pero NINGUNA señal adicional
      coincide -> POSIBLE_COINCIDENCIA (podría ser otra persona con el
      mismo nombre)
    - Si NO aparece el nombre completo, pero sí coinciden 2 o más señales
      adicionales (ej: alias + ciudad) -> POSIBLE_COINCIDENCIA (el
      documento pudo referirse a la persona por su alias)
    - Si NO aparece el nombre completo y solo coincide 1 señal débil
      (ej: solo la ciudad) -> PERSONA_DIFERENTE (es una coincidencia
      demasiado débil, probablemente se trata de alguien más)
    - Si no hay ninguna coincidencia clara -> NO_DETERMINADO
"""


def verificar_identidad(persona, texto):
    """
    Devuelve un string con uno de los 4 estados exigidos por RF7:
    MISMA_PERSONA | POSIBLE_COINCIDENCIA | PERSONA_DIFERENTE | NO_DETERMINADO
    """
    texto_lower = texto.lower()

    tiene_nombre = persona.nombre_completo.lower() in texto_lower

    senales_extra = 0
    if persona.alias and persona.alias.lower() in texto_lower:
        senales_extra += 1
    if persona.ciudad and persona.ciudad.lower() in texto_lower:
        senales_extra += 1
    if persona.profesion_cargo and persona.profesion_cargo.lower() in texto_lower:
        senales_extra += 1
    if persona.empresa_organizacion and persona.empresa_organizacion.lower() in texto_lower:
        senales_extra += 1

    if tiene_nombre and senales_extra >= 1:
        return "MISMA_PERSONA"
    if tiene_nombre and senales_extra == 0:
        return "POSIBLE_COINCIDENCIA"
    if not tiene_nombre and senales_extra >= 2:
        return "POSIBLE_COINCIDENCIA"
    if not tiene_nombre and senales_extra == 1:
        return "PERSONA_DIFERENTE"

    return "NO_DETERMINADO"