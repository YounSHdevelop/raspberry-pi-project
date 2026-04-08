# 라즈베리파이를 이용한 침입자 감지 및 사진 촬영 시스템
# PIR 센서로 움직임을 감지하면 웹캠으로 사진을 촬영하여 저장한다.

from gpiozero import MotionSensor  # PIR 센서 제어를 위한 클래스
import time                        # 대기 시간 설정을 위한 라이브러리
from picamera2 import Picamera2    # 카메라 제어를 위한 라이브러리
import datetime                    # 현재 시각을 파일명으로 사용하기 위한 라이브러리

# GPIO 핀 번호 지정 및 객체 생성
pirPin = MotionSensor(16)  # PIR 센서 Signal 핀 - GPIO 16번 (입력)
picam2 = Picamera2()       # 카메라 객체 생성

# 카메라 설정 및 시작
camera_config = picam2.create_preview_configuration()  # 프리뷰 설정 생성
picam2.configure(camera_config)                        # 카메라에 설정 적용
picam2.start()                                         # 카메라 시작

# 메인 루프: KeyboardInterrupt(Ctrl+C) 입력 전까지 반복 실행
try:
    while True:
        try:
            sensorValue = pirPin.value  # PIR 센서 값 읽기 (1: 감지, 0: 미감지)

            if sensorValue == 1:                        # 움직임 감지 시
                now = datetime.datetime.now()           # 현재 시각 가져오기
                print(now)                              # 터미널에 감지 시각 출력
                fileName = now.strftime('%Y-%m-%d %H:%M:%S')  # 시각을 파일명으로 변환
                picam2.capture_file(fileName + '.jpg')  # 사진 촬영 및 저장
                time.sleep(0.5)                         # 0.5초 대기 후 재감지

        except Exception:
            pass  # 예외 발생 시 무시하고 루프 계속 실행

except KeyboardInterrupt:
    pass  # Ctrl+C 입력 시 루프 종료
