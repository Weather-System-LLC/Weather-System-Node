from datetime import datetime, date
from dotenv import load_dotenv
import ImageCast
import requests
import time
import os

load_dotenv()

#Facebook/Instagram 
FacebookToken = os.getenv("FacebookToken")
pageID = os.getenv("PageID")
CountyCode = os.getenv("CountyCode")
ForecastCode = os.getenv("ForecastCode")