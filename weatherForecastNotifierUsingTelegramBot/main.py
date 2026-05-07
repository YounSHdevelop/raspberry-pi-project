import urllib.request           # OpenWeatherMap API 호출용
import json                     # API 응답(JSON) 파싱용
import datetime                 # 현재 시각 확인용
import asyncio                  # 비동기 처리용
from telegram import Bot        # 텔레그램 봇 메시지 전송용

# 텔레그램 chat_id (메시지를 받을 채팅방 고유 ID)
telegram_id = '8267189918'
# BotFather에서 발급받은 봇 인증 토큰
my_token = '8657951804:AAHTcDj22xS4c2-CN94UC25nJE6IpeofS0Y'
# OpenWeatherMap에서 발급받은 API 키
api_key = '693824b10f2164385b99e66f50ddb7ba'

# 텔레그램 봇 객체 생성
bot = Bot(token=my_token)

# 매일 정각에 알림을 보낼 시각 (24시간제)
ALERT_HOURS = [7, 10, 13, 16, 19, 22]
# 정각 외에 추가로 알림을 보낼 시각
ALERT_TIMES = ["10:25", "15:20"]


# OpenWeatherMap에서 서울의 향후 24시간 예보를 받아와 메시지 문자열로 만드는 함수
def getWeather():
    # 5일/3시간 예보 API URL (cnt=8 → 3시간 간격 8개 = 24시간 분량)
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Seoul&appid={api_key}&units=metric&lang=en&cnt=8"

    # API 호출 후 JSON 응답을 파싱
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())

    # 메시지로 보낼 문자열을 누적할 변수
    text = ""
    for i in range(8):
        item = data['list'][i]
        # UTC 시각(dt_txt의 11~12번째 문자)에 9를 더해 한국 시간(KST)으로 변환
        hour = str((int(item['dt_txt'][11:13]) + 9) % 24).zfill(2)
        temp = item['main']['temp']                # 기온 (℃)
        humi = item['main']['humidity']            # 습도 (%)
        desc = item['weather'][0]['description']   # 날씨 설명
        # 한 시간대 정보를 한 줄로 추가
        text += f"({hour}h {temp}C {humi}% {desc})\n"

    return text


# 1초마다 현재 시각을 확인하여 알림 시각이 되면 메시지를 전송하는 비동기 함수
async def main():
    try:
        while True:
            now = datetime.datetime.now()
            hm = now.strftime('%H:%M')

            # 정각 알림 조건: 현재 시각이 ALERT_HOURS에 포함되고, 분/초가 모두 0일 때
            is_alert_hour = now.hour in ALERT_HOURS and now.minute == 0 and now.second == 0
            # 추가 시각 알림 조건: 현재 시:분이 ALERT_TIMES에 포함되고, 초가 0일 때
            is_alert_time = hm in ALERT_TIMES and now.second == 0

            # 둘 중 하나라도 만족하면 날씨 메시지를 만들어 텔레그램으로 전송
            if is_alert_hour or is_alert_time:
                msg = getWeather()
                print(msg)
                await bot.send_message(chat_id=telegram_id, text=msg)

            # 1초 대기 (다른 비동기 작업에 제어권 양보)
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        # Ctrl+C 입력 시 정상 종료
        pass


# 비동기 메인 함수 실행
asyncio.run(main())
