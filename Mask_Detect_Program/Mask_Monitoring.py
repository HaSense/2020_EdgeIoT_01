#import pandas as pd
#from sqlalchemy import create_engine
#from PIL import Image
import base64
from io import BytesIO
import threading
#import pymysql
import cv2
import time

class Mask_Monitoring():
    def __init__(self):
        self.check_time = None
    
    def maskCheck(self, flag, capture):                                   # 출입자 마스크 체크 기능
        if not flag:
            if self.check_time is None:
                self.check_time =  time.time()
                return None
            elif time.time() - self.check_time >= 5: # 테스팅용으로 5초 지정 
                # 카메라 사진 캡처 후 jpg파일로 저장(용량을 줄이기 위해 퀄리티 60으로 지정)
                cv2.imwrite('./testpic/'+str(time.time())+'nomask.jpg',capture, params=[cv2.IMWRITE_JPEG_QUALITY,60])
                #im = Image.open(BytesIO('nomask.jpg')) # 저장된 사진을 경고와 함께 출력(경고는 따로 추가예정)
                self.check_time = None
                return 1
        else:
            self.check_time = None
            return None