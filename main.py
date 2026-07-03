from datetime import datetime, timezone, date
import image_cast
import utilities
import requests
import text_gen
import nws_api
import time

counties = utilities.get_config()

#Variables
active_alerts = {}

def alerts_handler():
    alerts = nws_api.get_alerts()["features"]
    for alert in alerts:
        if not alert["id"] in active_alerts:
            name = nws_api.get_alert_name(alert)

            print(f"New Alert {datetime.now(timezone.utc).isoformat()}")
            active_alerts[alert["id"]] = {"PostIDs":{}, "PostText":"Placeholder"}

def main():
    while True:
        alerts_handler()
        time.sleep(5)

if __name__ == "__main__":
    main()