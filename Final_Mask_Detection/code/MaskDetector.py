import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)
import pathlib
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
import time
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import cv2
import numpy as np
import time
from centroidtracker import CentroidTracker

class MaskDetector:
    def __init__(self, videopath=0, PATH_TO_SAVED_MODEL="inference_graph/saved_model", PATH_TO_LABELS="mask_label_map.pbtxt", maxDisappeared=100):
        
        gpus = tf.config.experimental.list_physical_devices('GPU')
        print(gpus)
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                print(e)
        
        self.cap = cv2.VideoCapture(videopath, cv2.CAP_DSHOW)
        
        print('Loading model...', end='')
        start_time = time.time()
        
        self.detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('Done! Took {} seconds'.format(elapsed_time))
        
        self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
        
        self.ct = CentroidTracker(maxDisappeared=25)
        
        self.visitorCnt = 0
        
        self.visitorCounter = []
        
        self.checktime = None
        
        self.no_mask = 0
        
        self.nose_mask = 0
        
        self.W = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.H = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
    def detect(self):
        
        flag_detect_mask = False
        flag_detect_pass = False
        
        ret, frame = self.cap.read()
        if not ret:
            print("Video Read Error")
            return None, flag_detect_mask, flag_detect_pass
        input_tensor = tf.convert_to_tensor(frame)
            
        input_tensor = input_tensor[tf.newaxis, ...]
            
        detections = self.detect_fn(input_tensor)
            
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                      for key, value in detections.items()}
        detections['num_detections'] = num_detections
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        image_np_with_detections = frame.copy()
            
        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes'],
            detections['detection_scores'],
            self.category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=.55,
            agnostic_mode=False)
        for i in range(len(detections['detection_scores'])):
            if detections['detection_classes'][i] != 1 and detections['detection_scores'][i] > 0.55:
                if self.checktime == None:
                    self.checktime = time.time()
                else:
                    if time.time() - self.checktime > 1:
                        #insert sound plz
                        cv2.imwrite('../detectedimg/'+str(time.time())+'.jpg',image_np_with_detections, params=[cv2.IMWRITE_JPEG_QUALITY,60])
                        self.checktime = None
                        flag_detect_mask = True
                        for j in range(len(detections['detection_scores']) - i - 1):
                            if detections['detection_classes'][i+j+1] == 2:
                                self.no_mask += 1
                            elif detections['detection_classes'][i+j+1] == 1:
                                self.nose_mask += 1
                break
            else:
                self.checktime = None
        rects = []
        for i in range(len(detections['detection_scores'])):
            if detections['detection_scores'][i] > 0.55:
                box = detections['detection_boxes'][i] * np.array([self.H, self.W, self.H, self.W])
                edit_box = np.array([box[1], box[2], box[3], box[0]])
                rects.append(edit_box.astype("int"))
                    
        objects = self.ct.update(rects)
            
        for (objectID, centroid) in objects.items():
            #text = "ID {}".format(objectID)
            #cv2.putText(image_np_with_detections, text, (centroid[0] - 10, centroid[1] - 10),
            #    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            #cv2.circle(image_np_with_detections, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
                
            if len(self.visitorCounter) <= objectID:
                self.visitorCounter.append(False)
            elif centroid[1] < 150 and self.visitorCounter[objectID] == False:
                self.visitorCnt += 1
                flag_detect_pass = True
                self.visitorCounter[objectID] = True
                    
        cv2.putText(image_np_with_detections, "Visitor: {}".format(self.visitorCnt), (int(20), int(20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        #cv2.imshow('img', image_np_with_detections)
        
        return image_np_with_detections, flag_detect_mask, flag_detect_pass
        
        
    def destroyWindwos(self):
        cv2.destroyAllWindows()
    
    def cap_release(self):
        self.cap.release()