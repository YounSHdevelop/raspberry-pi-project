import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Wayland 환경에서 OpenCV 창이 열리지 않는 문제 해결

import cv2
from gpiozero import LED, Buzzer
import time
import threading
import asyncio
from datetime import datetime
from telegram import Bot

EMPLOYEES = {
    "EMP001_홍길동": {"name": "홍길동", "level": 1, "role": "일반직원", "en": "Hong (Staff)"},
    "EMP002_김철수": {"name": "김철수", "level": 2, "role": "관리자",   "en": "Kim (Manager)"},
    "EMP003_박사장": {"name": "박사장", "level": 3, "role": "임원",     "en": "Park (Exec)"},
}

TELEGRAM_TOKEN   = "Enter your bot token here"
TELEGRAM_CHAT_ID = "Enter your chat ID here"

green_led = LED(20)
red_led   = LED(21)
buzzer    = Buzzer(18)

camera = cv2.VideoCapture(-1)  # -1: 연결된 웹캠 자동 감지
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not camera.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

qr_detector   = cv2.QRCodeDetector()
is_processing = False  # True인 동안 QR 인식을 건너뜀 (중복 실행 방지)
status_text   = ""

def save_log(name, role, result):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("access_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{now} | {name} | {role} | {result}\n")
    print(f"[로그] {now} | {name} | {role} | {result}")

async def _send_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print(f"[텔레그램 전송 실패] {e}")

async def _send_photo(frame, caption):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        cv2.imwrite("intruder.jpg", frame)
        with open("intruder.jpg", "rb") as photo:
            await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo, caption=caption)
    except Exception as e:
        print(f"[텔레그램 사진 전송 실패] {e}")

def access_level1(name, role, en):
    global is_processing, status_text
    try:
        status_text = f"GRANTED: {en}"
        green_led.on()
        buzzer.on(); time.sleep(0.2); buzzer.off()
        time.sleep(1)
        green_led.off()
        asyncio.run(_send_message(f"[출입 허가] {name} ({role})"))
    finally:
        status_text = ""
        is_processing = False  # 예외 발생 여부와 관계없이 반드시 해제

def access_level2(name, role, en):
    global is_processing, status_text
    try:
        status_text = f"GRANTED: {en}"
        green_led.on()
        for _ in range(2):
            buzzer.on(); time.sleep(0.2); buzzer.off()
            time.sleep(0.1)
        time.sleep(2)
        green_led.off()
        asyncio.run(_send_message(f"[출입 허가] {name} ({role})"))
    finally:
        status_text = ""
        is_processing = False

def access_level3(name, role, en):
    global is_processing, status_text
    try:
        status_text = f"VIP: {en}"
        for _ in range(3):
            green_led.on(); time.sleep(0.15); green_led.off(); time.sleep(0.1)
            buzzer.on(); time.sleep(0.1); buzzer.off()
        green_led.on()
        time.sleep(2)
        green_led.off()
        asyncio.run(_send_message(f"[VIP 출입] {name} ({role})"))
    finally:
        status_text = ""
        is_processing = False

def alarm(frame):
    global is_processing, status_text
    try:
        status_text = "DENIED: Unknown QR"
        red_led.on()
        for _ in range(3):
            buzzer.on(); time.sleep(0.2); buzzer.off()
            time.sleep(0.1)
        asyncio.run(_send_photo(frame, "[경고] 비정상 접근 감지 - 미등록 QR코드 스캔 시도"))
        time.sleep(1)
        red_led.off()
    finally:
        status_text = ""
        is_processing = False

def main():
    global is_processing
    print("QR 출입 통제 시스템 시작 | q 키: 종료")

    while True:
        ret, frame = camera.read()
        if not ret or frame is None:  # 프레임 읽기 실패 시 재시도
            time.sleep(0.1)
            continue

        if not is_processing:
            data, _, _ = qr_detector.detectAndDecode(frame)
            if data:
                print(f"인식된 QR: {data}")
                is_processing = True

                if data in EMPLOYEES:
                    emp  = EMPLOYEES[data]
                    name, role, level, en = emp["name"], emp["role"], emp["level"], emp["en"]
                    save_log(name, role, "출입 허가")
                    targets = {1: access_level1, 2: access_level2, 3: access_level3}
                    # 별도 스레드로 실행해 카메라 루프가 멈추지 않도록 함
                    threading.Thread(target=targets[level], args=(name, role, en), daemon=True).start()
                else:
                    save_log("미등록", "-", "출입 거부")
                    # frame.copy(): 스레드가 실행되는 동안 원본 프레임이 덮어씌워지는 것을 방지
                    threading.Thread(target=alarm, args=(frame.copy(),), daemon=True).start()

        if status_text:
            cv2.putText(frame, status_text, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("QR System", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    green_led.off()
    red_led.off()
    buzzer.off()

if __name__ == '__main__':
    main()
