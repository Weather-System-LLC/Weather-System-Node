test = [
    ["Today", "Widespread frost this morning. Sunny. Highs in the mid 50s. Northwest winds 5 to 10 mph."],
    ["Tonight", "Clear in the evening, then becoming partly cloudy. Lows in the upper 30s. North winds around 5 mph, becoming southeast after midnight."]
]

from PIL import Image, ImageDraw, ImageFont, ImageCms
import math

def DetermineBackground(ForecastText):
    if("thunderstorm" in ForecastText):
        return "Resources/Photos/Thunderstorm.png"
    elif("snow" in ForecastText or "frost" in ForecastText or "ice" in ForecastText):
        return "Resources/Photos/Snowy.png"
    elif("rain" in ForecastText or "showers" in ForecastText or "sprinkles" in ForecastText):
        return "Resources/Photos/Rainy.png"
    elif("cloud" in ForecastText):
        return "Resources/Photos/Cloudy.png"
    elif("clear" in ForecastText or "sunny" in ForecastText):
        return "Resources/Photos/Sunny.png"
    else:
        return "Resources/Photos/Sunny.png"


# 53
def WrapText(Text):
    if(len(Text)<=57):
        return Text
    
    lines = []
    words = Text.split(" ")

    current_line = []
    for index, word in enumerate(words):
        if (len(" ".join(current_line)) + len(word) > 57):
            lines.append(" ".join(current_line))
            current_line = []
        current_line.append(word)
    
    lines.append(" ".join(current_line))
    final_text = "\n".join(lines)
    return final_text
            


def ForecastImage(Forecast):
    DeterminedBackground = DetermineBackground((Forecast[0][1].lower() + Forecast[1][1]).lower())
    background = Image.open(DeterminedBackground).convert("RGB")
    background = background.resize((2400, 1800))
    overlay = Image.open("Resources/Photos/Credits.png")
    overlay = overlay.resize((1000, 450))

    # Get sizes
    bg_w, bg_h = background.size
    ov_w, ov_h = overlay.size

    # Calculate bottom-right position
    position = (bg_w - ov_w-10, bg_h - ov_h-10)

    # Paste overlay
    background.paste(overlay, position, overlay.convert("RGBA"))

    draw = ImageDraw.Draw(background)

    font_title = ImageFont.truetype("Resources/Montserrat.ttf", 120)
    font_title.set_variation_by_name("Bold")
    body_title = ImageFont.truetype("Resources/Montserrat.ttf", 78)
    body_title.set_variation_by_name("Regular")

    draw.text((30, 30), Forecast[0][0], font=font_title, fill="white")
    Text = WrapText(Forecast[0][1])
    draw.text((30, 200), Text, font=body_title, fill="white")

    AddAmount = 500 + len(Text.split("\n"))*45

    draw.text((30, AddAmount), Forecast[1][0], font=font_title, fill="white")
    Text = WrapText(Forecast[1][1])
    draw.text((30, AddAmount+170), Text, font=body_title, fill="white")

    background.convert("RGB").save("output.jpg", quality=95)