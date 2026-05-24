import cv2                          # OpenCV 라이브러리 (영상 처리, 객체 검출)
from gpiozero import Buzzer         # GPIO 핀에 연결된 능동부저 제어
import time

# GPIO 16번 핀에 능동부저 연결
buzzerPin = Buzzer(16)

def main():
    # 카메라 장치 열기 (-1: 첫 번째로 연결된 카메라 자동 선택)
    camera = cv2.VideoCapture(-1)
    camera.set(3, 640)              # 가로 해상도 640
    camera.set(4, 480)              # 세로 해상도 480
    
    # Haar Cascade XML 파일 경로 (OpenCV 기본 제공)
    face_xml = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    eye_xml = cv2.data.haarcascades + 'haarcascade_eye.xml'
    
    # 얼굴 분류기와 눈 분류기 생성
    face_cascade = cv2.CascadeClassifier(face_xml)
    eye_cascade = cv2.CascadeClassifier(eye_xml)
    
    # 카메라가 열려 있는 동안 반복
    while( camera.isOpened() ):
        # 한 프레임을 읽어 grayscale로 변환 (Haar 특징은 명암 차이로 계산되므로)
        _, image = camera.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 얼굴 검출 (크기 100x100 이상만 검출 대상)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100,100), flags=cv2.CASCADE_SCALE_IMAGE)
        print("faces detected Number: " + str(len(faces)))

        # 얼굴이 하나 이상 검출되었을 때만 처리
        if len(faces):
            for (x,y,w,h) in faces:
                # 얼굴 영역에 파란색 사각형 그리기
                cv2.rectangle(image, (x,y), (x+w,y+h), (255,0,0), 2)
                
                # 얼굴 영역(ROI)만 잘라내어 눈 검출에 사용 (오탐 감소, 속도 향상)
                face_gray = gray[y:y+h, x:x+w]
                face_color = image[y:y+h, x:x+w]
                
                # 얼굴 영역 내부에서만 눈 검출
                eyes = eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=5)
                
                # 눈이 1개 이하면 졸음으로 판단하여 부저 ON, 2개 이상이면 정상으로 판단하여 부저 OFF
                if len(eyes) <= 1:
                    buzzerPin.on()
                else:
                    buzzerPin.off()
                
                # 검출된 각 눈에 초록색 사각형 그리기
                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(face_color, (ex, ey), (ex+ew, ey+eh), (0,255,0), 2)
        
        # 처리 결과 화면 출력
        cv2.imshow('result', image)
        
        # q 키 입력 시 반복문 탈출
        if cv2.waitKey(1) == ord('q'):
            break
    
    # 카메라 창 닫고 부저 끄기
    cv2.destroyAllWindows()
    buzzerPin.off()

if __name__ == '__main__':
    main()
