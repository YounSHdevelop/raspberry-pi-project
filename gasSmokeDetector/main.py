# 라즈베리파이를 이용한 가스/연기 감지기 구현
# MQ-2 가스 센서로 가스를 감지하면 능동 부저를 울린다.

from gpiozero import DigitalInputDevice  # GPIO 핀을 디지털 입력으로 제어하기 위한 클래스
from gpiozero import OutputDevice        # GPIO 핀을 디지털 출력으로 제어하기 위한 클래스
import time                              # 대기 시간 설정을 위한 라이브러리

# GPIO 핀 번호 지정 및 객체 생성
bz  = OutputDevice(18)       # 능동 부저 - GPIO 18번 핀 (출력)
gas = DigitalInputDevice(17) # MQ-2 가스 감지 모듈 DOUT - GPIO 17번 핀 (입력)

# 메인 루프: KeyboardInterrupt(Ctrl+C) 입력 전까지 반복 실행
try:
    while True:

        if gas.value == 0:       # DO 핀 LOW(0) → 가스 감지됨 (Active Low 방식)
            print("bad") # 터미널에 경고 메시지 출력
            bz.on()              # 부저 ON → 경보음 발생

        else:                    # DO 핀 HIGH(1) → 정상 상태
            print("well")        # 터미널에 정상 메시지 출력
            bz.off()             # 부저 OFF

        time.sleep(0.2)          # 0.2초 간격으로 센서 값 반복 확인

except KeyboardInterrupt:        # Ctrl+C 입력 시 루프 종료
    pass

# 종료 처리: 프로그램 종료 시 부저를 반드시 OFF로 초기화
bz.off()
