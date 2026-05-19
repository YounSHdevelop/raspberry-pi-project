import speech_recognition as sr   # 음성 인식 라이브러리 (Google API 호출)
import requests                   # OpenWeatherMap API 호출용 HTTP 라이브러리
import os                         # 시스템 명령(espeak) 실행용
import time                       # 시간 처리용

# OpenWeatherMap에서 발급받은 API 키
API_KEY = "693824b10f2164385b99e66f50ddb7ba"
# 서울의 현재 날씨를 섭씨(metric) 단위로 요청하는 API URL
url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric"


# espeak 명령으로 문자열을 음성으로 출력하는 함수
# option에는 속도/음높이/음량/음성 설정이 들어감
def speak(option, msg):
    os.system("espeak {} '{}'".format(option, msg))


try:
    while True:
        # 매 반복마다 음성 인식기 객체 생성
        r = sr.Recognizer()

        # 마이크를 입력 소스로 지정하여 음성을 녹음
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)   # 마이크에서 음성을 듣고 audio에 저장

        try:
            # 녹음된 오디오를 Google 음성 인식 서버로 보내 한국어 텍스트로 변환
            text = r.recognize_google(audio, language='ko-KR')
            print("You said: " + text)

            # 인식된 텍스트에 '날씨' 키워드가 포함되었는지 확인
            if text in "날씨":
                print("날씨 음성을 인식하였습니다.")

                # OpenWeatherMap API 호출 및 JSON 응답 파싱
                response = requests.get(url)
                data = response.json()
                temp = data["main"]["temp"]        # 현재 기온(℃)
                humi = data["main"]["humidity"]    # 현재 습도(%)

                # 음성으로 출력할 메시지 생성 (정수 기온 + 습도)
                msg = '    기온은 ' + str(int(temp)) + '도 습도는 ' + str(humi) + '퍼센트 입니다'

                # espeak 옵션: 속도 180, 음높이 50, 음량 200, 한국어 여성 음성(ko+f5)
                option = '-s 180 -p 50 -a 200 -v ko+f5'
                speak(option, msg)   # 음성 출력 실행

        except sr.UnknownValueError:
            # 음성을 알아듣지 못한 경우
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            # Google 서버에 요청을 보내지 못한 경우(네트워크 오류 등)
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

except KeyboardInterrupt:
    # Ctrl+C 입력 시 정상 종료
    pass
