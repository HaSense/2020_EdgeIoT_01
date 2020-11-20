import winsound

class Mask_Announce:                # 클래스명 :  주의 안내 
    def __init__(self):
        pass
    def passenger(self):             # 함수 : 출입구 탑승자 안내사항 송출
        #print("마스크 미 착용자입니다. 마스크 미 착용시 탑승할 수 없으며, 마스크 착용 후 탑승 진행해 주세요.")
        print("마스크 미 착용자입니다. 마스크 미 착용시 탑승할 수 없으며, 마스크 착용 후 탑승 진행해 주세요.")
        frequency = 2500
        duration = 1000
        winsound.Beep(frequency, duration)

    def in_passenger(self):          # 함수 : 내부 탑승자 안내사항 송출
        print("내부에 마스크 착용 불량자가 있습니다. 마스크를 착용해 주세요.")
        frequency = 2500
        duration = 1000
        winsound.Beep(frequency, duration)
        

    def attentionButton(self):       # 함수 : 운전자 안내 방송 송출 버튼
        print("""2020년 11월 13일부터 마스크 미착용시 10만원 이하의 과태료가 부가 됩니다. 
                마스크를 착용하였으나 입과 코를 완전히 가리지 않은 경우는 미착용으로 간주되므로 올바른 마스크 착용을 해주세요.
                착용 불가능한 마스크는 망사형, 밸브형, 스카프 등으로 얼굴을 가리는 것은 인정하지 않습니다.
                자세한 마스크 착용 안내 기준은 식품의약품안전처의 마스크 착용 기준을 참고하세요.""")
        frequency = 2500
        duration = 1000
        winsound.Beep(frequency, duration)

