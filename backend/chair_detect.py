import cv2
import numpy as np
import os
import time
import onnxruntime
from yolox.data.data_augment import preproc as preprocess
from yolox.data.datasets import COCO_CLASSES
from yolox.utils import multiclass_nms, demo_postprocess

# グローバル変数
object_data = {
    "bench": {
        "count": 0,
        "positions": []
    },
    "chair": {
        "count": 0,
        "positions": []
    }
}  # 'bench'と'chair'の検出情報を保持

script_dir = os.path.dirname(os.path.abspath(__file__))  # スクリプトのディレクトリパスを取得

# YOLOXモデルのパス（'yolox_s.onnx'というファイルを使用）
onnx_model_path = os.path.join(script_dir, 'yolox_s.onnx')

# グローバルなビデオキャプチャオブジェクト
cap = None  # カメラからの映像を取得するためのVideoCaptureオブジェクト

# 検出対象クラスのリスト
TARGET_CLASSES = ['bench', 'chair']

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
    padded_frame = cv2.copyMakeBorder(resized_frame, pad_h, target_h - new_h - pad_h, pad_w, target_w - new_w - pad_w, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return padded_frame

def detect_objects_once():
    global object_data, cap

    # カメラを開く（0はデフォルトのカメラ）
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
        cap.release()
        return

    print("フレームをリサイズおよびパディングしています...")
    # フレームをリサイズし、640x640にパディング
    frame = resize_with_padding(frame, target_size=(640, 640))

    print("フレームを前処理しています...")
    # 画像の前処理
    input_shape = (640, 640)  # YOLOXの入力サイズ
    img, ratio = preprocess(frame, input_shape)  # 前処理を行い、YOLOXの入力フォーマットに変換

    print("モデルを読み込み、推論を実行しています...")
    # YOLOXモデルをONNXランタイムを使用して読み込む
    session = onnxruntime.InferenceSession(onnx_model_path)

    # YOLOXで推論を行う
    ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}  # 推論の入力を設定
    output = session.run(None, ort_inputs)  # 推論を実行
    predictions = demo_postprocess(output[0], input_shape, p6=False)[0]  # 出力結果を後処理

    print("NMSを適用して最終的な検出結果を取得しています...")
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
    object_data["bench"]["count"] = 0
    object_data["bench"]["positions"] = []
    object_data["chair"]["count"] = 0
    object_data["chair"]["positions"] = []

    print("検出結果を解析しています...")
    # 'bench'と'chair'クラスが検出されたかどうかを確認
    if dets is not None:
        final_cls_inds = dets[:, 5]  # 検出されたクラスID
        final_boxes = dets[:, :4]  # バウンディングボックス
        for cls_ind, box in zip(final_cls_inds, final_boxes):
            class_name = COCO_CLASSES[int(cls_ind)]
            if class_name in TARGET_CLASSES:
                object_data[class_name]["count"] += 1
                # バウンディングボックスの座標をリストとして保存
                object_data[class_name]["positions"].append({
                    "x_min": float(box[0]),
                    "y_min": float(box[1]),
                    "x_max": float(box[2]),
                    "y_max": float(box[3])
                })
                print(f"{class_name.capitalize()} detected at [x_min: {box[0]:.2f}, y_min: {box[1]:.2f}, x_max: {box[2]:.2f}, y_max: {box[3]:.2f}]")
                
                # バウンディングボックスをフレームに描画
                cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (int(box[0]), int(box[1]) - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

    # 検出結果の表示
    print("\nDetection Summary:")
    for obj in TARGET_CLASSES:
        print(f"{obj.capitalize()}: Count = {object_data[obj]['count']}")
        for idx, pos in enumerate(object_data[obj]['positions'], start=1):
            print(f"  {idx}. Position: x_min={pos['x_min']}, y_min={pos['y_min']}, x_max={pos['x_max']}, y_max={pos['y_max']}")

    # フレームを表示
    cv2.imshow('YOLOX Detection', frame)

    print("\nPress 'q' to close the window.")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting...")
            break

    # カメラを解放し、ウィンドウを閉じる
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        detect_objects_once()
    except KeyboardInterrupt:
        print("Shutting down...")
        if cap and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
