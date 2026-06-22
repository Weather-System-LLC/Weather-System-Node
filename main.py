from datetime import datetime, timezone, date
import ImageCast
import requests
import utilities
import time

HEADERS = {"User-Agent": "WeatherSystemNode (karsonulerick@gmail.com)", "Accept": "application/geo+json"}
counties = utilities.get_config()

#Variables
active_alerts = {}
last_alert_response = {}

def get_tornado_type(damage_threat):
    if(damage_threat):
        match damage_threat[0].lower():
            case "catastrophic":
                return "Tornado Emergency"
            case "considerable":
                return "PDS Tornado Warning"
            case _:
                return "Tornado Warning"
    else:
        return "Tornado Warning"

def get_alerts():
    response = requests.get("https://api.weather.gov/alerts/active", headers=HEADERS)
    if response.status_code == 200:
        last_alert_response = response.json()
    else:
        print("Error Occured")
        utilities.log(f"https://api.weather.gov/alerts/active responded with status {response.status_code} {response.json()}")
    
    return last_alert_response

def alerts_handler():
    alerts = get_alerts()["features"]
    for alert in alerts:
        if not alert["id"] in active_alerts:
            name = alert["properties"]["event"]
            if name == "Tornado Warning":
                name = get_tornado_type(alert["properties"]["parameters"].get("tornadoDamageThreat"))

            print(f"New Alert {datetime.now(timezone.utc).isoformat()}")
            active_alerts[alert["id"]] = {"PostIDs":{}, "PostText":"Placeholder"}

def main():
    while True:
        alerts_handler()
        time.sleep(5)

if __name__ == "__main__":
    main()