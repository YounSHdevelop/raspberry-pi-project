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

## 실행 환경

- **하드웨어**: Raspberry Pi (GPIO 지원 모델)
- **OS**: Raspberry Pi OS
- **Python**: 3.x
- **라이브러리**: `gpiozero`, `picamera2` (Raspberry Pi OS 기본 포함)

## 실행 방법

```bash
# 신호등 제어기
python3 trafficLightController/main.py

# 가스/연기 감지기
python3 gasSmokeDetector/main.py
```

# PIR 침입자 감지기
python3 pirMotionSensor/main.py
```

> 종료: `Ctrl + C`
