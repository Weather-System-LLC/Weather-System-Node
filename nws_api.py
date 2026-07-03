import utilities
import requests

HEADERS = {"User-Agent": "WeatherSystemNode (karsonulerick@gmail.com)", "Accept": "application/geo+json"}
last_alert_response = {}

def get_tornado_type(detection, damage_threat):
    if detection:
        observed = detection[0].lower() == "observed"
    else:
        observed = False

    if(damage_threat):
        match damage_threat[0].lower():
            case "catastrophic":
                return "Tornado Emergency"
            case "considerable":
                return "PDS Tornado Warning"
            case _:
                if observed:
                    return "Confirmed Tornado Warning"
                else:
                    return "Tornado Warning"
    else:
        if observed:
            return "Confirmed Tornado Warning"
        else:
            return "Tornado Warning"
    
def get_flash_flood_type(damage_threat):
    if(damage_threat):
        match damage_threat[0].lower():
            case "catastrophic":
                return "Flash Flood Emergency"
            case "considerable":
                return "Considerable Flash Flood Warning"
            case _:
                return "Flash Flood Warning"
    else:
        return "Flash Flood Warning"
    
def get_severe_thunderstorm_type(damage_threat):
    if(damage_threat):
        match damage_threat[0].lower():
            case "destructive":
                return "Destructive Severe Thunderstorm Warning"
            case "considerable":
                return "Considerable Severe Thunderstorm Warning"
            case _:
                return "Severe Thunderstorm Warning"
    else:
        return "Severe Thunderstorm Warning"
    
def get_snow_squall_type(damage_threat):
    if(damage_threat):
        match damage_threat[0].lower():
            case "significant":
                return "Significant Snow Squall Warning"
            case _:
                return "Snow Squall Warning"
    else:
        return "Snow Squall Warning"
    
def get_alert_name(alert):
    properties = alert.get("properties", {})
    parameters = properties.get("parameters", {})
    name = properties.get("event", "Unknown Event")
    match name:
        case "Tornado Warning":
            name = get_tornado_type(parameters.get("tornadoDetection"), parameters.get("tornadoDamageThreat"))
        case "Flash Flood Warning":
            name = get_flash_flood_type(parameters.get("flashFloodDamageThreat"))
        case "Severe Thunderstorm Warning":
            name = get_severe_thunderstorm_type(parameters.get("thunderstormDamageThreat"))
        case "Snow Squall Warning":
            name = get_snow_squall_type(parameters.get("snowSquallImpact"))

    return name

def get_alerts():
    try:
        global last_alert_response
        response = requests.get("https://api.weather.gov/alerts/active", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            last_alert_response = response.json()
        else:
            print("Error Occurred")
            utilities.log(f"https://api.weather.gov/alerts/active responded with status {response.status_code} {response.text}")
    except requests.RequestException as error:
        print("Error Occurred")
        utilities.log(f"Exception occurred in get_alerts function. Error: {error}")
    return last_alert_response