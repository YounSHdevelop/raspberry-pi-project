import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Qt 플랫폼을 X11로 설정 (Wayland 충돌 방지)

import cv2                              # OpenCV 라이브러리 불러오기
from gpiozero import LED, Buzzer        # GPIO 출력 장치 제어 라이브러리
import time                             # 시간 지연 처리
import threading                        # 메인 루프와 GPIO 제어를 분리하기 위한 스레드
import asyncio                          # 텔레그램 비동기 전송 처리
from datetime import datetime           # 출입 로그 시각 기록
from telegram import Bot                # 텔레그램 봇 라이브러리

# 직원 DB: QR코드 데이터 → 이름, 직급, 레벨, 영문 표시명
EMPLOYEES = {
    "EMP001_홍길동": {"name": "홍길동", "level": 1, "role": "일반직원", "en": "Hong (Staff)"},
    "EMP002_김철수": {"name": "김철수", "level": 2, "role": "관리자",   "en": "Kim (Manager)"},
    "EMP003_박사장": {"name": "박사장", "level": 3, "role": "임원",     "en": "Park (Exec)"},
}

# 텔레그램 설정 (BotFather에서 발급)
TELEGRAM_TOKEN   = "Enter your bot token here"
TELEGRAM_CHAT_ID = "Enter your chat ID here"

green_led = LED(20)     # 초록 LED — GPIO 20번 핀
red_led   = LED(21)     # 빨간 LED — GPIO 21번 핀
buzzer    = Buzzer(18)  # 능동 부저 — GPIO 18번 핀

camera = cv2.VideoCapture(-1)                       # 웹캠 자동 감지 후 열기
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)           # 가로 해상도 640픽셀 설정
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)          # 세로 해상도 480픽셀 설정

if not camera.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

qr_detector   = cv2.QRCodeDetector()   # QR 코드 탐지 객체 생성
is_processing = False                   # QR 처리 중 여부 플래그 (중복 인식 방지)
status_text   = ""                      # 화면에 표시할 상태 메시지 (영문)

# ── 출입 로그 저장 ─────────────────────────────────────────
def save_log(name, role, result):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("access_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{now} | {name} | {role} | {result}\n")
    print(f"[로그] {now} | {name} | {role} | {result}")

# ── 텔레그램 메시지 전송 ───────────────────────────────────
async def _send_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print(f"[텔레그램 전송 실패] {e}")

async def _send_photo(frame, caption):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        cv2.imwrite("intruder.jpg", frame)              # 침입자 프레임 이미지 저장
        with open("intruder.jpg", "rb") as photo:
            await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo, caption=caption)
    except Exception as e:
        print(f"[텔레그램 사진 전송 실패] {e}")

# ── 레벨 1 (일반직원): 초록 LED 1초, 부저 1번 ─────────────
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
        is_processing = False

# ── 레벨 2 (관리자): 초록 LED 2초, 부저 2번 ──────────────
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

# ── 레벨 3 (임원): 초록 LED 깜빡임 3회 (VIP), 부저 3번 ───
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

# ── 미등록 QR: 빨간 LED + 경보음 + 텔레그램 사진 전송 ──────
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

# ── 메인 함수 ──────────────────────────────────────────────
def main():
    global is_processing
    print("QR 출입 통제 시스템 시작 | q 키: 종료")

    while True:
        ret, frame = camera.read()          # 카메라에서 프레임 한 장 읽기
        if not ret or frame is None:        # 프레임 읽기 실패 시 재시도
            time.sleep(0.1)
            continue

        if not is_processing:
            data, _, _ = qr_detector.detectAndDecode(frame)    # QR 코드 탐지 및 디코딩
            if data:
                print(f"인식된 QR: {data}")
                is_processing = True    # 처리 중 플래그 ON (중복 인식 차단)

                if data in EMPLOYEES:
                    emp  = EMPLOYEES[data]
                    name, role, level, en = emp["name"], emp["role"], emp["level"], emp["en"]
                    save_log(name, role, "출입 허가")
                    targets = {1: access_level1, 2: access_level2, 3: access_level3}
                    threading.Thread(target=targets[level], args=(name, role, en), daemon=True).start()
                else:
                    save_log("미등록", "-", "출입 거부")
                    threading.Thread(target=alarm, args=(frame.copy(),), daemon=True).start()

        if status_text:     # 화면에 상태 메시지 출력
            cv2.putText(frame, status_text, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("QR System", frame)
        if cv2.waitKey(1) == ord('q'):  # q 키 입력 시 종료
            break

    camera.release()            # 카메라 자원 해제
    cv2.destroyAllWindows()     # 모든 OpenCV 창 닫기
    green_led.off()
    red_led.off()
    buzzer.off()

if __name__ == '__main__':
    main()
