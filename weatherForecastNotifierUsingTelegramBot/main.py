import urllib.request
import json
import datetime
import asyncio
from telegram import Bot

telegram_id = '8267189918'
my_token = '8657951804:AAHTcDj22xS4c2-CN94UC25nJE6IpeofS0Y'  
api_key = '693824b10f2164385b99e66f50ddb7ba'

bot = Bot(token=my_token)

ALERT_HOURS = [7, 10, 13, 16, 19, 22]                                     
ALERT_TIMES = ["10:25", "15:20"]                                         

def getWeather():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Seoul&appid={api_key}&units=metric&lang=en&cnt=8"

    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())

    text = ""
    for i in range(8):
        item = data['list'][i]
        hour = str((int(item['dt_txt'][11:13]) + 9) % 24).zfill(2)
        temp = item['main']['temp']
        humi = item['main']['humidity']
        desc = item['weather'][0]['description']
        text += f"({hour}h {temp}C {humi}% {desc})\n"

    return text

async def main():
    try:
        while True:
            now = datetime.datetime.now()
            hm = now.strftime('%H:%M')            

            is_alert_hour = now.hour in ALERT_HOURS and now.minute == 0 and now.second == 0 
            is_alert_time = hm in ALERT_TIMES and now.second == 0                             

            if is_alert_hour or is_alert_time:
                msg = getWeather()
                print(msg)
                await bot.send_message(chat_id=telegram_id, text=msg)

            await asyncio.sleep(1)

    except KeyboardInterrupt:
        pass

asyncio.run(main())
