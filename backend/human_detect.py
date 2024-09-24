from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import cv2
import numpy as np
import os
import time
import atexit
import onnxruntime
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
onnx_model_path = os.path.join(script_dir, 'yolox_s.onnx')

# グローバルなビデオキャプチャオブジェクト
cap = None  # カメラからの映像を取得するためのVideoCaptureオブジェクト
net = None  # YOLOXのモデル
running = True  # スレッドを実行中かどうかのフラグ

# YOLOXを使用してカメラ映像から人物検出を行う関数
def detect_person():
    global person_detected, cap, running

    # カメラを開く（0はデフォルトのカメラ）
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return

    # YOLOXモデルをONNXランタイムを使用して読み込む
    session = onnxruntime.InferenceSession(onnx_model_path)

    # カメラが開いている間、リアルタイムで映像を処理するループ
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

        # 'person'クラスが検出されたかどうかを確認
        person_detected = 0  # 初期化
        if dets is not None:
            final_cls_inds = dets[:, 5]  # 検出されたクラスID
            for cls_ind in final_cls_inds:
                if int(cls_ind) == COCO_CLASSES.index('person'):  # 'person'（クラスID 0）が含まれるか確認
                    person_detected = 1  # 'person'が検出されたらフラグを立てる
                    print("Person detected!")  # コンソールにメッセージを表示
                    break

        time.sleep(1)  # 0.1秒待機して次のフレームを処理

    # カメラを解放
    cap.release()

# 別スレッドでYOLOXによる人物検出を実行
face_thread = threading.Thread(target=detect_person, daemon=True)
face_thread.start()

@app.route('/')
def hello():
    return "Hello from Flask!"

# 人物(椅子)が検出されたかどうかを返すエンドポイント
@app.route('/person_status', methods=['GET'])
def person_status():
    data = [
        {
            "seat_num": "121",
            "availability": person_detected,
            "reserver": None,
            'id': "1"
        },
    ]
    return jsonify(data)

# データを保持するリスト
data_store = []

# # 外部からデータを受け取るエンドポイント
# @app.route('/external_data', methods=['POST'])
# def external_data():
#     posted_data = request.get_json()

#     data_store.append(posted_data)

#     return jsonify({"data": posted_data}), 201

# 外部からデータを受け取るエンドポイント(データを検出結果により変更)
@app.route('/external_data', methods=['POST'])
def external_data():
    posted_data = request.get_json()

    if posted_data.get("availability") == 2:
        if person_detected == 0:
            posted_data["availability"] = 2
        else:
            posted_data["availability"] = 1
    
    if posted_data.get("availability") == 1:
        if person_detected == 0:
            posted_data["availability"] = 0

    data_store.append(posted_data)

    return jsonify({"data": posted_data}), 201

# 外部にデータを返すエンドポイント
@app.route('/get_external_data', methods=['GET'])
def get_external_data():
    return jsonify({"stored_data": data_store}), 201

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
        app.run(debug=True)  # Flaskアプリケーションをデバッグモードで起動
    except KeyboardInterrupt:
        print("Shutting down...")  # キーボード割り込みで終了した場合の処理
