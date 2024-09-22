from flask import Flask, jsonify
from flask_cors import CORS
import threading
import cv2
import numpy as np
import os
import time
import atexit

app = Flask(__name__)
CORS(app)  # CORS設定を追加

face_detected = 0
script_dir = os.path.dirname(os.path.abspath(__file__))
prototxt = os.path.join(script_dir, 'deploy.prototxt') #モデル構造
model = os.path.join(script_dir, 'res10_300x300_ssd_iter_140000.caffemodel') #重み

# グローバルなビデオキャプチャオブジェクト
cap = None
net = None
running = True  # スレッド実行フラグ

def detect_faces():
    global face_detected, cap, net, running

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return

    if not os.path.exists(prototxt):
        print(f"Error: Prototxt file not found at {prototxt}")
        return
    if not os.path.exists(model):
        print(f"Error: Model file not found at {model}")
        return
    
    #顔検出モデルの読み込み
    net = cv2.dnn.readNetFromCaffe(prototxt, model)

    while running:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from camera.")
            break

        img = cv2.resize(frame, (400, int(frame.shape[0] * 400 / frame.shape[1]))) #フレームを400にリサイズ
        (h, w) = img.shape[:2] #リサイズ後の高さと幅を取得
        blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0)) #画像をdnnモデルに入力できる形に変換

        net.setInput(blob) #blobをdnnモデルの入力に設定
        detections = net.forward() #結果を取得

        face_detected = 0
        for i in range(0, detections.shape[2]): #detections.shape[2]は検出された顔の数
            confidence = detections[0, 0, i, 2] #信頼度を計測
            if confidence > 0.5:
                face_detected = 1
                break

        time.sleep(0.1)

    cap.release()

face_thread = threading.Thread(target=detect_faces, daemon=True)
face_thread.start()

@app.route('/')
def hello():
    return "Hello from Flask!"

@app.route('/face_status')
def face_status():
    return jsonify({'face_detected': face_detected})

def shutdown(): #クリーンアップ関数
    global running
    print("Shutting down...")
    running = False
    if cap and cap.isOpened():
        cap.release()

atexit.register(shutdown)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        print("Shutting down...")
