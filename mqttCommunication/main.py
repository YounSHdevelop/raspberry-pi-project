import paho.mqtt.client as mqtt   # MQTT 통신용 라이브러리
import time                       # 송신 주기 제어용
from gpiozero import LED          # LED 제어용
import threading                  # 송신/수신 동시 처리(멀티태스킹)용

# 색깔별 LED를 각 GPIO 핀에 매핑
greenLed = LED(16)
blueLed = LED(20)
redLed = LED(21)


# 브로커로부터 메시지를 받았을 때 호출되는 콜백 함수
# msg.payload(바이트)를 문자열로 디코딩한 뒤, 명령어에 따라 LED를 제어
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    message = msg.payload.decode()
    print(message)
    if message == "green_on":
        greenLed.on()
    elif message == "green_off":
        greenLed.off()
    elif message == "blue_on":
        blueLed.on()
    elif message == "blue_off":
        blueLed.off()
    elif message == "red_on":
        redLed.on()
    elif message == "red_off":
        redLed.off()


# MQTT 클라이언트 객체 생성 및 콜백 함수 등록
client = mqtt.Client()
client.on_message = on_message

# 라즈베리파이 자체에 설치된 Mosquitto 브로커 주소
broker_address = "192.168.0.67"
client.connect(broker_address)
# "led" 토픽을 QoS 1로 구독 (최소 한 번 전달 보장)
client.subscribe("led", 1)


# "hello" 토픽으로 1초마다 카운트 값을 발행하는 송신 함수
# (수신 루프와 동시에 동작시키기 위해 별도 thread에서 실행)
count = 0
def send_thread():
    global count
    while 1:
        count = count + 1
        client.publish("hello", str(count))
        time.sleep(1.0)


# 송신 함수를 별도의 thread로 분리하여 실행
# → 메인 thread의 수신 루프와 동시에 동작하므로 양방향 통신 가능
task = threading.Thread(target=send_thread)
task.start()

# 브로커로부터 메시지를 계속 감시하는 무한 루프(블로킹)
# 이 줄 이후의 코드는 실행되지 않으므로 발행 작업은 위 thread에서 처리
client.loop_forever()
