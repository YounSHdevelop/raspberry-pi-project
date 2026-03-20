# 라즈베리파이를 이용한 신호등 구현
# GPIO 핀을 제어하여 차량용/보행자용 신호등을 구현한다.

from gpiozero import LED as led  # GPIO 핀을 LED로 제어하기 위한 라이브러리
from time import sleep as time    # 대기 시간 설정을 위한 라이브러리

# GPIO 핀 번호 지정 및 LED 객체 생성
carLedRed   = led(2)    # 차량 신호등 - 빨간 LED (GPIO 2번 핀)
carLedBlue  = led(3)    # 차량 신호등 - 파랑 LED (GPIO 3번 핀)
carLedGreen = led(4)    # 차량 신호등 - 초록 LED (GPIO 4번 핀)

humanLedRed   = led(20) # 보행자 신호등 - 빨간 LED (GPIO 20번 핀)
humanLedGreen = led(21) # 보행자 신호등 - 초록 LED (GPIO 21번 핀)

# 메인 루프: KeyboardInterrupt(Ctrl+C) 입력 전까지 반복 실행
try:
    while 1:

        # [1단계] 차량 초록 / 보행자 빨강 (차량 통행 허용, 7초)
        carLedRed.value   = 0   # 차량 빨강 OFF
        carLedBlue.value  = 0   # 차량 파랑 OFF
        carLedGreen.value = 1   # 차량 초록 ON  → 차량 진행
        humanLedRed.value   = 1 # 보행자 빨강 ON  → 보행자 정지
        humanLedGreen.value = 0 # 보행자 초록 OFF
        time(7.0)              # 7초 대기

        # [2단계] 차량 노랑 / 보행자 빨강 (차량 정지 준비, 2초)
        carLedRed.value   = 0   # 차량 빨강 OFF
        carLedBlue.value  = 1   # 차량 파랑 ON  → 차량 정지 준비
        carLedGreen.value = 0   # 차량 초록 OFF
        humanLedRed.value   = 1 # 보행자 빨강 ON  → 보행자 계속 정지
        humanLedGreen.value = 0 # 보행자 초록 OFF
        time(2.0)              # 2초 대기

        # [3단계] 차량 빨강 / 보행자 초록 (보행자 통행 허용, 5초)
        carLedRed.value   = 1   # 차량 빨강 ON  → 차량 정지
        carLedBlue.value  = 0   # 차량 파랑 OFF
        carLedGreen.value = 0   # 차량 초록 OFF
        humanLedRed.value   = 0 # 보행자 빨강 OFF
        humanLedGreen.value = 1 # 보행자 초록 ON  → 보행자 진행
        time(5.0)              # 5초 대기

except KeyboardInterrupt:
    pass  # Ctrl+C 입력 시 루프 종료 후 아래 정리 코드 실행

# 종료 처리: 프로그램 종료 시 모든 LED를 OFF로 초기화
carLedRed.value     = 0
carLedBlue.value    = 0
carLedGreen.value   = 0
humanLedRed.value   = 0
humanLedGreen.value = 0

### 신호등 동작 흐름 요약

#[차량 초록 / 보행자 빨강] → 7초
#          ↓
#[차량 파랑 / 보행자 빨강] → 2초
#          ↓
#[차량 빨강 / 보행자 초록] → 5초
#          ↓
#         반복
         
