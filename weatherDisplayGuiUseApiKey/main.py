# OpenWeatherMap API를 활용한 서울 온습도 실시간 표시 GUI 프로그램

import urllib.request  # HTTP 요청을 보내기 위한 라이브러리
import json            # JSON 데이터 파싱을 위한 라이브러리
import tkinter         # GUI 창 생성을 위한 라이브러리
import tkinter.font    # tkinter 폰트 설정을 위한 라이브러리

API_KEY = "693824b10f2164385b99e66f50ddb7ba"  # OpenWeatherMap에서 발급받은 API 키

def tick1Min():
    # 서울 날씨 데이터를 요청하는 URL (units=metric: 섭씨 단위)
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric"

    with urllib.request.urlopen(url) as r:  # API에 HTTP GET 요청 전송
        data = json.loads(r.read())         # 응답을 JSON 형식으로 파싱하여 딕셔너리로 변환

    temp = data["main"]["temp"]      # JSON 응답에서 온도 값 추출 (°C)
    humi = data["main"]["humidity"]  # JSON 응답에서 습도 값 추출 (%)

    label.config(text=f"{temp:.1f}C   {humi}%")  # 라벨 텍스트를 온습도 값으로 업데이트
    window.after(10000, tick1Min)                 # 10초(10000ms) 후 함수 재실행 (자동 갱신)

# GUI 창 생성 및 설정
window = tkinter.Tk()                # tkinter 메인 창 생성
window.title("TEMP HUMI DISPLAY")   # 창 제목 설정
window.geometry("400x100")          # 창 크기 설정 (가로 400px × 세로 100px)
window.resizable(False, False)       # 창 크기 조절 비활성화 (가로, 세로 모두)

font = tkinter.font.Font(size=30)                    # 폰트 크기 30 설정
label = tkinter.Label(window, text="", font=font)    # 텍스트 라벨 생성
label.pack()                                         # 라벨을 창에 배치

tick1Min()        # 프로그램 시작 시 날씨 데이터 첫 호출
window.mainloop() # 창 유지 및 이벤트 루프 실행 (창이 닫힐 때까지 대기)