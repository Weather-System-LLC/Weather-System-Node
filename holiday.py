from datetime import datetime, timezone, date
import json
import os

holiday_dates = []
holiday_alert_text = {}

from datetime import date

def get_easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451

    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1

    return date(year, month, day)

def calculate_dates():
    year = datetime.now(timezone.utc).year
    print(year)
    with open(os.path.join("Resources", "holidays.json"), "r", encoding="utf-8") as file:
        data = json.load(file)
    for holiday in data["holidays"]:
        print(json.dumps(holiday, indent=2))
        holiday_name = holiday["name"]
        holiday_format = holiday["type"]
        if holiday_format == "fixed":
            holiday_date = holiday["date"]
            holiday_dates.append({"name":holiday_name, "start_month":holiday_date[0], "start_day": holiday_date[1], "end_month":holiday_date[0], "end_day": holiday_date[1]})
        elif holiday_format == "range":
            holiday_start_date = holiday["start"]
            holiday_end_date = holiday["end"]
            holiday_dates.append({"name":holiday_name, "start_month":holiday_start_date[0], "start_day": holiday_start_date[1], "end_month":holiday_end_date[0], "end_day": holiday_end_date[1]})

calculate_dates()
print(holiday_dates)