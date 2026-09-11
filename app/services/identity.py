def verificar_identidad(persona, texto):
    """Devuelve: MISMA_PERSONA | POSIBLE_COINCIDENCIA | PERSONA_DIFERENTE | NO_DETERMINADO"""
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
