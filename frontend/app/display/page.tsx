"use client";

import { useState, useEffect } from 'react';

export default function Display() {
  const [faceDetected, setFaceDetected] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFaceStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000/face_status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setFaceDetected(data.face_detected);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    //ページロード時に一度実行
    fetchFaceStatus();

    //定期的に顔検出状態をチェックする
    const interval = setInterval(fetchFaceStatus, 1000);

    //クリーンアップ
    return () => clearInterval(interval);
  }, []);

  return (
    <div className='text-center mt-10'>
      <h1>Next.js + Flask 顔検出ステータス</h1>
      {error && <p className='text-red-500'>エラー: {error}</p>}
      {faceDetected === null ? (
        <p>データを取得中...</p>
      ) : faceDetected === 1 ? (
        <p className='text-green-500'>顔が検出されました！ (1)</p>
      ) : (
        <p className='text-red-500'>顔は検出されていません。 (0)</p>
      )}
    </div>
  );
}
