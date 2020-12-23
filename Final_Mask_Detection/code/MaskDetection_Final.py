from flask import Flask, render_template, Response, request
import cv2
from MaskDetector import MaskDetector
from MyES import ES
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import json
#from MainMaskDetection import Main

app = Flask(__name__)
md = MaskDetector(videopath=0, PATH_TO_SAVED_MODEL='../myimages/inference_graph/saved_model',
                          PATH_TO_LABELS='../myimages/mask_label_map.pbtxt', maxDisappeared=25)
es = ES()
datas = es.datetime_search_fromES()
if len(datas) > 0 and ('visitor' in json.loads(datas[len(datas)-1]).keys()):
    md.visitorCnt = json.loads(datas[len(datas)-1])['visitor']
if len(datas) > 0 and ('nosemask' in json.loads(datas[len(datas)-1]).keys()):
    md.nose_mask = json.loads(datas[len(datas)-1])['nosemask']
if len(datas) > 0 and ('nomask' in json.loads(datas[len(datas)-1]).keys()):
    md.no_mask = json.loads(datas[len(datas)-1])['nomask']

def gen_frames():
    global md, es
    while True:
        frame, flag_mask, flag_pass = md.detect()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        if flag_mask:
            doc = {
                'image_save': frame,
                'visitor': md.visitorCnt,
                'nosemask': md.nose_mask,
                'nomask': md.no_mask
            }
            es.insert_data(doc)
        
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def updateData():
    global es, md
    
    doc = {
            'visitor': md.visitorCnt,
            'nosemask': md.nose_mask,
            'nomask': md.no_mask
    }
    es.insert_data(doc)
    print("update done")

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=updateData, trigger="interval", seconds=5)
scheduler.start()        

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
try:
    if __name__ == "__main__":
        app.run(port=8081, host='0.0.0.0', threaded=True)

finally:
    md.destroyWindwos()
    md.cap_release()

atexit.register(lambda: scheduler.shutdown())