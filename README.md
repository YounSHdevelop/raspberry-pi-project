# Raspberry Pi AIoT Project

한신대학교 AIoT설계입문 수업 프로젝트 — Raspberry Pi GPIO를 활용한 IoT 모듈 모음

## 프로젝트 구조

```
.
├── trafficLightController/   # 신호등 제어 모듈
│   └── main.py
├── gasSmokeDetector/         # 가스/연기 감지 모듈
│   └── main.py
├── pirMotionSensor/          # PIR 침입자 감지 모듈
│   └── main.py
├── ledControlFlaskWebServer/ # Flask 웹서버 LED 제어 모듈
│   ├── main.py
│   └── templates/
│       └── index.html
├── weatherDisplayGuiUseApiKey/ # OpenWeatherMap API 기반 온습도 GUI
│   └── main.py
├── weatherForecastNotifierUsingTelegramBot/ # 텔레그램 봇 날씨 예보 알림
│   └── main.py
├── mqttCommunication/        # MQTT 양방향 LED 제어 모듈
│   └── main.py
├── voiceRecognitionWeatherNotifier/ # 음성 인식 날씨 음성 안내 모듈
│   └── main.py
├── drowsinessPreventionDevice/ # 졸음 방지 장치 (얼굴·눈 검출)
│   └── main.py
└── README.md
```

## 모듈 소개

### 1. 신호등 제어기 (`trafficLightController`)

Raspberry Pi GPIO 핀으로 차량용·보행자용 신호등을 제어하는 프로그램

**사용 부품**
| 부품 | GPIO 핀 |
|------|---------|
| 차량 빨강 LED | GPIO 17 |
| 차량 파랑 LED | GPIO 27 |
| 차량 초록 LED | GPIO 22 |
| 보행자 빨강 LED | GPIO 20 |
| 보행자 초록 LED | GPIO 21 |

**동작 흐름**
```
[차량 초록 / 보행자 빨강] → 7초
         ↓
[차량 파랑 / 보행자 빨강] → 2초
         ↓
[차량 빨강 / 보행자 초록] → 5초
         ↓
        반복
```

---

### 2. 가스/연기 감지기 (`gasSmokeDetector`)

MQ-2 가스 센서로 가스를 감지하면 능동 부저로 경보를 울리는 프로그램

**사용 부품**
| 부품 | GPIO 핀 | 입출력 |
|------|---------|--------|
| 능동 부저 | GPIO 18 | 출력 |
| MQ-2 가스 센서 (DOUT) | GPIO 17 | 입력 (Active Low) |

**동작 방식**
- 센서 DO 핀 LOW → 가스 감지 → 부저 ON
- 센서 DO 핀 HIGH → 정상 → 부저 OFF
- 0.2초 간격으로 센서 값 확인

### 3. PIR 침입자 감지기 (`pirMotionSensor`)

PIR 모션 센서로 움직임을 감지하면 웹캠으로 사진을 촬영하여 저장하는 프로그램

**사용 부품**
| 부품 | GPIO 핀 | 입출력 |
|------|---------|--------|
| PIR 모션 센서 (Signal) | GPIO 16 | 입력 |
| Raspberry Pi 카메라 (picamera2) | CSI 포트 | — |

**동작 방식**
- PIR 센서 값 1 → 움직임 감지 → 현재 시각으로 파일명을 생성하여 사진 촬영·저장
- PIR 센서 값 0 → 대기
- 감지 후 0.5초 간격으로 재감지

---

### 4. Flask 웹서버 LED 제어기 (`ledControlFlaskWebServer`)

Flask 웹서버를 띄우고 브라우저의 ON/OFF 버튼으로 파란 LED와 빨간 LED를 토글하는 프로그램

**사용 부품**
| 부품 | GPIO 핀 | 입출력 |
|------|---------|--------|
| 파란 LED | GPIO 21 | 출력 |
| 빨간 LED | GPIO 20 | 출력 |

**동작 방식**
- 서버 시작 시 기본 페이지(`/`) 접속 → 빨간 LED ON / 파란 LED OFF
- 웹 페이지의 `ON` 버튼 클릭 → `/data`로 POST 전송 → 파란 LED ON / 빨간 LED OFF
- 웹 페이지의 `OFF` 버튼 클릭 → `/data`로 POST 전송 → 파란 LED OFF / 빨간 LED ON
- 페이지 제목이 현재 상태(`LED ON` / `LED OFF`)에 따라 갱신됨

**접속 방법**
- 동일 네트워크에서 `http://<라즈베리파이 IP>/` 로 접속 (포트 80)
- Flask가 자동으로 `templates/index.html`을 렌더링하므로, HTML 파일은 반드시 `templates/` 폴더 안에 위치시켜야 함

---

### 5. 온습도 표시 GUI (`weatherDisplayGuiUseApiKey`)

OpenWeatherMap API로 서울의 현재 온도·습도를 받아와 tkinter GUI 창에 실시간으로 표시하는 프로그램

**사용 라이브러리**
- `urllib.request` — API HTTP 요청
- `json` — 응답 JSON 파싱
- `tkinter` — GUI 창과 라벨 표시

**동작 방식**
- 프로그램 시작 시 OpenWeatherMap의 서울 날씨 API를 호출 (`units=metric`로 섭씨)
- 응답 JSON에서 `main.temp` (온도), `main.humidity` (습도) 값을 추출
- 400×100 크기의 tkinter 창에 `온도°C   습도%` 형태로 표시
- 10초마다 `window.after()`로 자체 재호출하여 자동 갱신

**API 키 발급**
- [OpenWeatherMap](https://openweathermap.org/api)에서 무료 API 키 발급 후 `main.py`의 `API_KEY` 값에 입력

---

### 6. 텔레그램 봇 날씨 예보 알림 (`weatherForecastNotifierUsingTelegramBot`)

OpenWeatherMap의 5일/3시간 예보 API로 서울의 향후 24시간(3시간 간격 8개 구간) 예보를 받아와 정해진 시간마다 텔레그램 봇으로 발송하는 프로그램

**사용 라이브러리**
- `urllib.request` — API HTTP 요청
- `json` — 응답 JSON 파싱
- `datetime` — 현재 시각 비교
- `asyncio` — 비동기 루프
- `python-telegram-bot` — 텔레그램 봇 메시지 전송

**동작 방식**
- 매초 현재 시각을 확인
- `ALERT_HOURS` (`07, 10, 13, 16, 19, 22`시 정각) 또는 `ALERT_TIMES` (`10:25`, `15:20`)와 일치할 때
  → OpenWeatherMap forecast API 호출 (`cnt=8`로 24시간 분량)
  → 응답 시각(UTC)을 KST(+9)로 변환하여 `(시각h 온도C 습도% 날씨설명)` 형식으로 정리
  → 텔레그램 봇이 지정된 chat_id로 메시지 전송
- `Ctrl + C` 입력 시 정상 종료

**준비물**
- [@BotFather](https://t.me/BotFather)에서 봇 생성 후 토큰 발급 → `my_token`에 입력
- 봇과 1회 이상 대화한 본인 텔레그램 chat_id → `telegram_id`에 입력
- [OpenWeatherMap](https://openweathermap.org/api) API 키 → `api_key`에 입력

---

### 7. MQTT 양방향 LED 제어 (`mqttCommunication`)

라즈베리파이에 설치된 Mosquitto 브로커를 통해 MQTT 메시지를 송·수신하는 프로그램. 외부에서 보낸 명령어로 LED를 제어하는 동시에, 자체적으로 카운트 값을 일정 주기로 발행하여 양방향 통신을 구현

**사용 부품**
| 부품 | GPIO 핀 | 입출력 |
|------|---------|--------|
| 초록 LED | GPIO 16 | 출력 |
| 파란 LED | GPIO 20 | 출력 |
| 빨간 LED | GPIO 21 | 출력 |

**사용 라이브러리**
- `paho-mqtt` — MQTT 클라이언트
- `gpiozero` — LED 제어
- `threading` — 송신과 수신을 동시에 처리하기 위한 멀티스레딩

**동작 방식**
- **수신**: `led` 토픽을 QoS 1로 구독 → 메시지(`green_on`/`green_off`/`blue_on`/`blue_off`/`red_on`/`red_off`)에 따라 해당 LED를 켜고 끔
- **송신**: 별도 thread에서 1초마다 `hello` 토픽으로 카운트 값을 발행
- 메인 thread는 `loop_forever()`로 수신을 지속, 송신은 thread로 분리하여 동시 동작

**준비물**
- 라즈베리파이에 Mosquitto 브로커 설치 (`sudo apt install mosquitto mosquitto-clients`)
- `paho-mqtt` 패키지 설치 (`pip install paho-mqtt`)
- `main.py`의 `broker_address`를 자신의 라즈베리파이 IP로 수정

---

### 8. 음성 인식 날씨 음성 안내 (`voiceRecognitionWeatherNotifier`)

마이크로 음성을 입력받아 Google 음성 인식으로 텍스트화하고, "날씨"라는 단어가 인식되면 OpenWeatherMap API로 서울의 현재 기온·습도를 받아와 espeak로 음성 안내하는 프로그램

**사용 라이브러리**
- `speech_recognition` — 마이크 입력 녹음 및 Google 음성 인식 API 호출
- `requests` — OpenWeatherMap API HTTP 요청
- `os` — `espeak` 시스템 명령 실행
- `espeak` — 텍스트를 음성으로 출력하는 외부 프로그램(시스템 설치 필요)

**사용 부품**
| 부품 | 연결 | 입출력 |
|------|------|--------|
| USB 마이크 | USB 포트 | 입력 |
| 스피커/이어폰 | 오디오 잭·USB | 출력 |

**동작 방식**
- 무한 루프에서 매 반복마다 마이크로 음성을 녹음 (`r.listen()`)
- 녹음된 오디오를 Google 음성 인식 서버로 전송하여 한국어(`ko-KR`) 텍스트로 변환
- 인식된 텍스트에 "날씨" 키워드가 포함되면 OpenWeatherMap의 서울 현재 날씨 API 호출
- 응답 JSON에서 `main.temp` (기온), `main.humidity` (습도)를 추출
- `espeak`로 `기온은 N도 습도는 N퍼센트 입니다` 메시지를 한국어 여성 음성(`ko+f5`)으로 출력
- `Ctrl + C` 입력 시 정상 종료

**준비물**
- USB 마이크와 스피커(또는 이어폰) 연결
- espeak 설치 (`sudo apt install espeak`)
- `speech_recognition`, `requests` 패키지 설치 (`pip install SpeechRecognition requests`)
- [OpenWeatherMap](https://openweathermap.org/api) API 키 → `main.py`의 `API_KEY` 값에 입력

---

### 9. 졸음 방지 장치 (`drowsinessPreventionDevice`)

웹캠으로 운전자의 얼굴과 눈을 실시간 검출하여, 눈이 일정 시간 감겨 있으면(=검출되지 않으면) 능동 부저로 경고를 울리는 프로그램. OpenCV의 Haar Cascade 분류기를 사용

**사용 부품**
| 부품 | GPIO 핀 / 연결 | 입출력 |
|------|----------------|--------|
| USB 웹캠 | USB 포트 | 입력 |
| 능동 부저 | GPIO 16 | 출력 |

**사용 라이브러리**
- `opencv-python` (`cv2`) — 영상 캡처, grayscale 변환, Haar Cascade 기반 얼굴·눈 검출, 화면 표시
- `gpiozero` — 능동 부저 제어
- `time` — 표준 라이브러리

**동작 방식**
- 카메라(640×480)에서 프레임을 읽어 grayscale로 변환 (Haar 특징은 명암 차이로 계산)
- `haarcascade_frontalface_default.xml`로 얼굴 검출 (최소 100×100 크기)
- 검출된 얼굴 ROI 내부에서만 `haarcascade_eye.xml`로 눈 검출 (오탐 감소·속도 향상)
- 검출된 눈 개수가 1개 이하 → 졸음으로 판단하여 부저 ON
- 검출된 눈 개수가 2개 이상 → 정상으로 판단하여 부저 OFF
- 얼굴은 파란색, 눈은 초록색 사각형으로 표시하여 결과 창에 출력
- `q` 키 입력 시 종료 (카메라 창 닫고 부저 OFF)

**준비물**
- USB 웹캠 연결
- OpenCV 설치 (`pip install opencv-python`)
- Haar Cascade XML 파일은 OpenCV 설치 시 `cv2.data.haarcascades` 경로에 기본 포함되어 별도 다운로드 불필요

---

## 실행 환경

- **하드웨어**: Raspberry Pi (GPIO 지원 모델)
- **OS**: Raspberry Pi OS
- **Python**: 3.x
- **라이브러리**: `gpiozero`, `picamera2` (Raspberry Pi OS 기본 포함), `flask`, `tkinter` (Python 기본 포함), `python-telegram-bot`, `paho-mqtt`, `SpeechRecognition`, `requests`, `opencv-python`
- **브로커**: Mosquitto (MQTT 모듈용, 라즈베리파이에 설치)
- **외부 프로그램**: espeak (음성 안내 모듈용, `sudo apt install espeak`)

## 실행 방법

```bash
# 신호등 제어기
python3 trafficLightController/main.py

# 가스/연기 감지기
python3 gasSmokeDetector/main.py

# PIR 침입자 감지기
python3 pirMotionSensor/main.py

# Flask 웹서버 LED 제어기 (sudo 필요: 80번 포트 바인딩)
sudo python3 ledControlFlaskWebServer/main.py

# 온습도 표시 GUI
python3 weatherDisplayGuiUseApiKey/main.py

# 텔레그램 봇 날씨 예보 알림
python3 weatherForecastNotifierUsingTelegramBot/main.py

# MQTT 양방향 LED 제어 (브로커 실행 후 사용)
python3 mqttCommunication/main.py

# 음성 인식 날씨 음성 안내 (마이크·스피커 연결 후 사용)
python3 voiceRecognitionWeatherNotifier/main.py

# 졸음 방지 장치 (웹캠 연결 후 사용)
python3 drowsinessPreventionDevice/main.py
```

> 종료: `Ctrl + C`
