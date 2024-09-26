from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import cv2
import numpy as np
import os
import time
import atexit
import onnxruntime
import json
from yolox.data.data_augment import preproc as preprocess
from yolox.data.datasets import COCO_CLASSES
from yolox.utils import multiclass_nms, demo_postprocess

# Flaskアプリケーションのセットアップ
app = Flask(__name__)
CORS(app)  # CORS（Cross-Origin Resource Sharing）を有効にする

# グローバル変数
person_detected = 0  # 'person'クラスが検出されたかどうかを示すフラグ
script_dir = os.path.dirname(os.path.abspath(__file__))  # スクリプトのディレクトリパスを取得

# YOLOXモデルのパス（'yolox_s.onnx'というファイルを使用）
onnx_model_path = os.path.join(script_dir, 'yolox_m.onnx')

# グローバルなビデオキャプチャオブジェクト
cap = None  # カメラからの映像を取得するためのVideoCaptureオブジェクト
running = True  # スレッドを実行中かどうかのフラグ

# 座席データの保存先
seats_file = os.path.join(script_dir, 'seats.json')

# 椅子とベンチの検出対象クラス
TARGET_CLASSES = ['bench', 'chair']

# 重なり具合の閾値（IoU）
IOU_THRESHOLD = 0.6  # 必要に応じて調整

# 関数: バウンディングボックスのカバレッジ率を計算
def compute_coverage_ratio(box1, box2):
    """
    Compute the coverage ratio of box1 and box2 overlapping.
    This returns the ratio of the smaller box's area covered by the intersection.
    """
    xA = max(box1[0], box2[0])
    yA = max(box1[1], box2[1])
    xB = min(box1[2], box2[2])
    yB = min(box1[3], box2[3])

    # Intersection area
    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0

    # Areas of the two boxes
    box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # Calculate the coverage ratio for both boxes and return the larger ratio
    coverage_ratio1 = interArea / box1Area
    coverage_ratio2 = interArea / box2Area

    return max(coverage_ratio1, coverage_ratio2)

def detect_and_save_seats():
    global seats_data, seats_file, onnx_model_path, cap

    if not cap:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video capture.")
            return

    print("カメラを起動しました。3秒間待機します...")
    time.sleep(3)  # カメラ起動後、3秒待機

    print("フレームをキャプチャしています...")
    # 1フレームだけ読み込む
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame from camera.")
        return

    # `resize_with_padding()`の呼び出しを削除
    # frame = resize_with_padding(frame, target_size=(640, 640))

    # 画像の前処理
    input_shape = (640, 640)  # YOLOXの入力サイズ
    img, ratio = preprocess(frame, input_shape)  # 前処理を行い、YOLOXの入力フォーマットに変換

    # YOLOXモデルをONNXランタイムを使用して読み込む
    session = onnxruntime.InferenceSession(onnx_model_path)

    # YOLOXで推論を行う
    ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}  # 推論の入力を設定
    output = session.run(None, ort_inputs)  # 推論を実行
    predictions = demo_postprocess(output[0], input_shape, p6=False)[0]  # 出力結果を後処理

    # 検出されたボックスとスコアを取得
    boxes = predictions[:, :4]  # バウンディングボックスの座標
    scores = predictions[:, 4:5] * predictions[:, 5:]  # スコア

    # xywhからxyxy形式に変換
    boxes_xyxy = np.ones_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.
    boxes_xyxy /= ratio  # 元のサイズにスケーリング

    # NMSを適用して最終的な検出結果を取得
    dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.7)

    # 座席データの初期化
    seats_data = []

    # 'bench'と'chair'クラスが検出されたかどうかを確認
    if dets is not None:
        final_cls_inds = dets[:, 5]  # 検出されたクラスID
        final_boxes = dets[:, :4]  # バウンディングボックス
    
        # 検出された椅子のバウンディングボックスとクラスIDを結合してリストにする
        seats = [
            (box, COCO_CLASSES[int(cls_ind)])
            for cls_ind, box in zip(final_cls_inds, final_boxes)
            if COCO_CLASSES[int(cls_ind)] in TARGET_CLASSES
        ]
    
        # x_min, y_minの座標でソート（左上から右下にかけて順番に）
        seats.sort(key=lambda x: (x[0][0], x[0][1]))

        # 座席データの初期化
        seats_data = []

        # ソートされた椅子に対して番号を振る
        for idx, (box, class_name) in enumerate(seats, start=1):
            seat_info = {
                "id": idx,  # ソート順に番号を付ける
                "box": {
                    "x_min": float(box[0]),
                    "y_min": float(box[1]),
                    "x_max": float(box[2]),
                    "y_max": float(box[3])
                },
                "occupied": False,
                "true_count": 0,
                "false_count": 0
            }
            seats_data.append(seat_info)

    # 座席データをファイルに保存
    with open(seats_file, 'w') as f:
        json.dump(seats_data, f, indent=4)
    print(f"座席データを {seats_file} に保存しました。")

def resize_with_padding(frame, target_size=(640, 640)):
    original_h, original_w = frame.shape[:2]
    target_w, target_h = target_size

    # フレームをアスペクト比を保ちながらリサイズ
    scale = min(target_w / original_w, target_h / original_h)
    new_w = int(original_w * scale)
    new_h = int(original_h * scale)
    resized_frame = cv2.resize(frame, (new_w, new_h))

    # パディングを追加して640x640にする
    pad_w = (target_w - new_w) // 2
    pad_h = (target_h - new_h) // 2

    # 黒い背景で新しいフレームを作成
    padded_frame = cv2.copyMakeBorder(resized_frame, pad_h, target_h - new_h - pad_h, pad_w, target_w - new_w - pad_w, 
                                      cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return padded_frame

# 関数: 人物検出と座席の占有状況更新
def detect_person_and_update():
    global person_detected, cap, running, seats_data

    # YOLOXモデルをONNXランタイムを使用して読み込む
    session = onnxruntime.InferenceSession(onnx_model_path)

    # カメラが開かれていない場合はカメラを開く
    if not cap:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video capture.")
            return

    while running:
        ret, frame = cap.read()  # カメラから1フレームを読み込む
        if not ret:
            print("Error: Failed to read frame from camera.")
            break

        # 画像の前処理
        input_shape = (640, 640)  # YOLOXの入力サイズ
        img, ratio = preprocess(frame, input_shape)  # 前処理を行い、YOLOXの入力フォーマットに変換

        # YOLOXで推論を行う
        ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}  # 推論の入力を設定
        output = session.run(None, ort_inputs)  # 推論を実行
        predictions = demo_postprocess(output[0], input_shape, p6=False)[0]  # 出力結果を後処理

        # 検出されたボックスとスコアを取得し、NMS（Non-Maximum Suppression）を適用
        boxes = predictions[:, :4]  # バウンディングボックスの座標
        scores = predictions[:, 4:5] * predictions[:, 5:]  # スコア
        boxes_xyxy = np.ones_like(boxes)  # xywhからxyxy形式に変換
        boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.
        boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.
        boxes_xyxy /= ratio  # 元のサイズにスケーリング

        # NMSを適用して最終的な検出結果を取得
        dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.7)

        # 検出結果の初期化
        person_detected = 0  # 初期化

        # 座席の占有状態を初期化
        for seat in seats_data:
            seat["occupied"] = False  # 各フレーム処理の最初にリセット

        # 人物検出と座席との重なり判定
        if dets is not None:
            final_cls_inds = dets[:, 5]  # 検出されたクラスID
            final_boxes = dets[:, :4]    # バウンディングボックス
            for cls_ind, box in zip(final_cls_inds, final_boxes):
                class_name = COCO_CLASSES[int(cls_ind)]
                if class_name == 'person':
                    print('Person detected!')
                    person_detected = 1  # 'person'が検出されたらフラグを立てる 
                    # 各座席と重なり具合をチェック
                    for seat in seats_data:
                        seat_box = [
                            seat["box"]["x_min"], seat["box"]["y_min"],
                            seat["box"]["x_max"], seat["box"]["y_max"]
                        ]
                        ratio = compute_coverage_ratio(box, seat_box)
                        if ratio > IOU_THRESHOLD:
                            seat["true_count"] += 1
                            seat["false_count"] = 0
                            if seat["true_count"] >= 3:
                                seat["occupied"] = True  # 重なっていればTrueに設定
                                seat["true_count"] = 0
   
        for seat in seats_data:
            print(f"Seat {seat['id']} true_count: {seat['true_count']}, false_count: {seat['false_count']}, {seat['occupied']}")

        print('-----------------------------')

        # データの更新（必要に応じてここで座席データを保存や他の処理を行う）
        time.sleep(5)  # フレーム処理間の待機時間

    # カメラを解放
    cap.release()

# 別スレッドで人物検出と座席占有状況の更新を実行
def start_detection_thread():
    detection_thread = threading.Thread(target=detect_person_and_update, daemon=True)
    detection_thread.start()

# 初期化処理
detect_and_save_seats()

# 別スレッドで人物検出を開始
start_detection_thread()

data = []
data_reserve = []

for seat_data in seats_data:
        data_info = {
            "id": seat_data["id"],
            "availability": 1 if seat_data["occupied"] else 0,
            "reserver": None
        }

        data.append(data_info)

for seat_data in seats_data:
        data_info = {
            "id": seat_data["id"],
            "availability": 1 if seat_data["occupied"] else 0,
            "reserver": None
        }

        data_reserve.append(data_info)

@app.route('/external_data', methods=['POST'])
def external_data():
    posted_data = request.get_json()

    seat_id = posted_data.get("id")  # "id" キーが存在しない場合は None になる   
    if seat_id is None:
        return jsonify({"error": "Invalid data, 'id' field is missing"}), 400  # idがない場合はエラーレスポンスを返す
    
    data_reserve[int(seat_id) - 1]["availability"] = posted_data.get("availability")
    data_reserve[int(seat_id) - 1]["reserver"] = posted_data.get("reserver")

    return jsonify({"data": posted_data}), 201


# 外部にデータを返すエンドポイント
@app.route('/get_external_data', methods=['GET'])
def get_external_data():
    for i, seat in enumerate(seats_data):

        data[i]["availability"] = 1 if seat["occupied"] else 0
    
    for i, seat in enumerate(data_reserve):
        # data_reserve の seat に対して処理を行う
        if seat["availability"] == 2:
            # 対応する data の availability を確認
            if data[i]["availability"] == 0:
                seat["availability"] = 2
            elif data[i]["availability"] == 1:
                seat["availability"] = 1

        if seat["availability"] == 1:
            if data[i]["availability"] == 0:
                seat["availability"] = 0

    return jsonify(data_reserve)

# クリーンアップ関数（Flaskサーバーが終了する際に呼び出される）
def shutdown():
    global running
    print("Shutting down...")
    running = False  # スレッドループを終了
    if cap and cap.isOpened():
        cap.release()  # カメラを解放

# プログラム終了時にクリーンアップ関数を呼び出す
atexit.register(shutdown)

# Flaskアプリケーションを実行
if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False)  # Flaskアプリケーションをデバッグモードで起動
    except KeyboardInterrupt:
        print("Shutting down...")
