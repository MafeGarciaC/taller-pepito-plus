def es_contenido_relacionado(persona, texto):
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
