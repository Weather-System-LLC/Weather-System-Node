import json

def generate_alert_text(name, alert):
    properties = alert.get("properties", {})
    parameters = properties.get("parameters", {})
    lines = []

    heading = [name]

    nws_headline = parameters.get("NWSheadline")
    if nws_headline:
        heading.append(nws_headline[0])

    lines.append("\n".join(heading))

    match name:
        case "Tornado Emergency":
            lines.append("THIS IS THE HIGHEST LEVEL OF TORNADO WARNING. MAJOR DAMAGE IS EXPECTED AND TOTAL DESTRUCTION IS POSSIBLE. TAKE COVER NOW!")
        case "PDS Tornado Warning":
            lines.append("THIS IS A PARTICULARLY DANGEROUS SITUATION. TAKE COVER NOW!")
        case "Confirmed Tornado Warning":
            lines.append("A CONFIRMED TORNADO IS ON THE GROUND. TAKE COVER NOW!")

    headline = properties.get("headline")
    if headline:
        lines.append(headline)

    parameters_text = []

    max_wind_gust = parameters.get("maxWindGust")
    if max_wind_gust:
        parameters_text.append(f"Max Wind Gust: {max_wind_gust[0]}")

    wind_threat = parameters.get("windThreat")
    if wind_threat:
        parameters_text.append(f"Wind Threat: {wind_threat[0]}")

    max_hail_size = parameters.get("maxHailSize")
    if max_hail_size:
        parameters_text.append(f"Max Hail Size: {max_hail_size[0]}")

    hail_threat = parameters.get("hailThreat")
    if hail_threat:
        parameters_text.append(f"Hail Threat: {hail_threat[0]}")

    thunderstorm_damage_threat = parameters.get("thunderstormDamageThreat")
    if thunderstorm_damage_threat:
        parameters_text.append(f"Thunderstorm Damage Threat: {thunderstorm_damage_threat[0]}")

    tornado_detection = parameters.get("tornadoDetection")
    if tornado_detection:
        parameters_text.append(f"Tornado Detection: {tornado_detection[0]}")

    tornado_damage_threat = parameters.get("tornadoDamageThreat")
    if tornado_damage_threat:
        parameters_text.append(f"Tornado Damage Threat: {tornado_damage_threat[0]}")

    waterspout_detection = parameters.get("waterspoutDetection")
    if waterspout_detection:
        parameters_text.append(f"Waterspout Detection: {waterspout_detection[0]}")

    flash_flood_detection = parameters.get("flashFloodDetection")
    if flash_flood_detection:
        parameters_text.append(f"Flash Flood Detection: {flash_flood_detection[0]}")

    flash_flood_damage_threat = parameters.get("flashFloodDamageThreat")
    if flash_flood_damage_threat:
        parameters_text.append(f"Flash Flood Damage Threat: {flash_flood_damage_threat[0]}")

    snow_squall_detection = parameters.get("snowSquallDetection")
    if snow_squall_detection:
        parameters_text.append(f"Snow Squall Detection: {snow_squall_detection[0]}")

    snow_squall_impact = parameters.get("snowSquallImpact")
    if snow_squall_impact:
        parameters_text.append(f"Snow Squall Impact: {snow_squall_impact[0]}")

    if parameters_text:
        lines.append(f"Parameters\n{"\n".join(parameters_text)}")

    severity = properties.get("severity")
    if severity:
        lines.append(f"Severity\n{severity}")

    certainty = properties.get("certainty")
    if certainty:
        lines.append(f"Certainty\n{certainty}")
    
    description = properties.get("description")
    if description:
        lines.append(f"Description\n{description}")

    instructions = properties.get("instruction")
    if instructions:
        lines.append(f"Instructions\n{instructions}")
    
    return "\n\n".join(lines)