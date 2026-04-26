# 플라스크 웹서버를 이용한 LED 제어 시스템
# 웹 페이지의 ON/OFF 버튼으로 파란 LED와 빨간 LED를 제어한다.

from flask import Flask, request, render_template  # Flask 웹 서버 라이브러리
from gpiozero import LED                           # GPIO 핀을 LED로 제어하기 위한 라이브러리

app = Flask(__name__)  # Flask 앱 생성

blue_led = LED(21)  # 파란 LED - GPIO 21번 핀 (출력)
red_led  = LED(20)  # 빨간 LED - GPIO 20번 핀 (출력)

@app.route('/')          # 기본 주소(/) 접속 시 실행
def home():
    red_led.on()         # 초기 상태: 빨간 LED ON
    blue_led.off()       # 초기 상태: 파란 LED OFF
    return render_template("index.html", status="OFF")  # index.html을 status="OFF"로 렌더링

@app.route('/data', methods=['POST'])  # /data 주소로 POST 요청 왔을 때 실행
def data():
    data = request.form['led']         # HTML 폼에서 'led' 값 가져오기 (on 또는 off)

    if data == 'on':                   # 값이 'on'이면
        blue_led.on()                  # 파란 LED ON
        red_led.off()                  # 빨간 LED OFF
        return render_template("index.html", status="ON")   # 페이지 제목 "LED ON"으로 갱신

    elif data == 'off':                # 값이 'off'이면
        blue_led.off()                 # 파란 LED OFF
        red_led.on()                   # 빨간 LED ON
        return render_template("index.html", status="OFF")  # 페이지 제목 "LED OFF"로 갱신

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # 모든 IP(0.0.0.0)에서 80번 포트로 서버 실행