'''
Program for capturing video
history
    - 2020-11-19: Initial Version
'''
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np
import cv2

class Mask_Detection:
    def __init__(self):
       # 얼굴 찾기 모델
        self.facenet = cv2.dnn.readNet('mask_detection-model/models/deploy.prototxt',
                                  'mask_detection-model/models/res10_300x300_ssd_iter_140000.caffemodel')
        # model: 마스크 검출 모델
        self.model = load_model('mask_detection-model/models/mask_detector.model')
    
    
    '''
    method for start capturing. if you stop this, plz key down 'q'.
    history
        - 2020-11-19: Initial Version
    parameter
        - cam: cam or video for capturing
    '''
    def create_Cam(self, cam):
        cap = cv2.VideoCapture(cam)
        return cap
    def start_capture(self, cap):
        # 실시간 웹캠 읽기
        i = 0
        
        if cap.isOpened():
            ret, img = cap.read()
            if not ret:
                return True, None
            ## 필요할 경우 이미지 전처리
            # img = cv2.cvtColor(img, ...)
            
            
            # 이미지의 높이와 너비 추출
            height, width = img.shape[:2]
    
            # 이미지 전처리
            blob = cv2.dnn.blobFromImage(img, scalefactor=1.,
                                 size=(300, 300), mean=(104., 177., 123.))
        
            # facenet의 input으로 blob 설정
            self.facenet.setInput(blob)
            # facenet 결과 추론, 얼굴 추출 결과가 dets에 저장
            dets = self.facenet.forward()

            # 한 프레임 내의 여러 얼굴들 받기
            result_img = img.copy()
            flag = True
            # 마스크 여부 확인
            for i in range(dets.shape[2]):
                # 검출 결과 신뢰도
                confidence = dets[0, 0, i, 2]
                # 신뢰도 0.5를 임계치로 지정
                if confidence < 0.5:
                    continue

                # 바운딩 박스 연산
                x1 = int(dets[0, 0, i, 3] * width)
                y1 = int(dets[0, 0, i, 4] * height)
                x2 = int(dets[0, 0, i, 5] * width)
                y2 = int(dets[0, 0, i, 6] * height)

                # 원본 이미지에서 얼굴 영역 추출
                face = img[y1:y2, x1:x2]

                # 추출한 얼굴 영역 전처리
                try:
                    face_input = cv2.resize(face, dsize=(224, 224))
                    face_input = cv2.cvtColor(face_input, cv2.COLOR_BGR2RGB)
                    face_input = preprocess_input(face_input)
                    face_input = np.expand_dims(face_input, axis=0)
                except Error as e:
                    print(e)
                    return True, result_img

                # 마스크 검출 모델로 결과값 반환
                mask, nomask = self.model.predict(face_input).squeeze()

                # 마스크 착용 여부 라벨링
                if mask > nomask:
                    color = (0, 255, 0)
                    label = 'Mask %d%%' % (mask *100)

                else:
                    color = (0, 0, 255)
                    label = 'No Mask %d%%' % (nomask * 100)
                    flag = False


                # 화면에 얼굴 부분 및 마스크 유무 출력
                cv2.rectangle(result_img, pt1=(x1, y1), pt2=(x2, y2), thickness=2,
                              color=color, lineType=cv2.LINE_AA)
                cv2.putText(result_img, text=label, org=(x1, y1-10),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8,
                            color=color, thickness=2, lineType=cv2.LINE_AA)
            return (flag, result_img)
            #cv2.imshow('img', result_img)

            #if cv2.waitKey(1) & 0xFF == ord('q'):
                #break
        #cap.release()
        #cv2.destroyAllWindows()
    def cap_release(self, cap):
        cap.release()
        

#if __name__ == '__main__':
#    detec = mask_detect()
#    detec.start_capture(0)