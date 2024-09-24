import cv2
import numpy as np
import onnxruntime

from yolox.data.data_augment import preproc as preprocess
from yolox.data.datasets import COCO_CLASSES
from yolox.utils import multiclass_nms, demo_postprocess, vis

# 画像の読み込み、前処理
input_shape = (640, 640)
origin_img = cv2.imread("infChair.jpg")
img, ratio = preprocess(origin_img, input_shape)

# ONNXセッション
session = onnxruntime.InferenceSession("yolox_s.onnx")

# 推論＋後処理
ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}
output = session.run(None, ort_inputs)
predictions = demo_postprocess(output[0], input_shape, p6=False)[0]

# xyxyへの変換＋NMS
boxes = predictions[:, :4]
scores = predictions[:, 4:5] * predictions[:, 5:]

boxes_xyxy = np.ones_like(boxes)
boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2]/2.
boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3]/2.
boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2]/2.
boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3]/2.
boxes_xyxy /= ratio

# NMSの適用
dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.1)

# 'person' クラスが検出されたかどうかのフラグ
person_detected = False

if dets is not None:
    final_boxes, final_scores, final_cls_inds = dets[:, :4], dets[:, 4], dets[:, 5]
    
    # クラスが 'person' (class_id = 0) かどうか確認
    for cls_ind in final_cls_inds:
        if int(cls_ind) == COCO_CLASSES.index('person'):
            person_detected = True
            break
    
    # BoundingBoxを描画する場合
    inference_img = vis(origin_img, final_boxes, final_scores, final_cls_inds,
                        conf=0.3, class_names=COCO_CLASSES)
    cv2.imwrite("output.jpg", inference_img)

# 'person' が検出されたら1を返す
if person_detected:
    print(1)
else:
    print(0)
