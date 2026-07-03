import json
import text_gen
import nws_api
import os

with open("samples.json", "r", encoding="utf-8") as file:
    data = json.load(file)

for alert in data["samples"]:
    file_name = f"{alert["type"].replace("\\", "").replace("/", "").replace(" ", "_")}.txt"
    
    alert_data = alert["alert"]
    name = nws_api.get_alert_name(alert_data)
    text = text_gen.generate_alert_text(name, alert_data)

    with open(os.path.join("AlertText", file_name), "w", encoding="utf-8") as file:
        file.write(text)