from datetime import datetime, timezone
import os

def log(text):
    with open("logs.txt", "a", encoding="utf-8") as log:
        log.write(f"{datetime.now(timezone.utc).isoformat()} {text}\n")

def get_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return file.read()