"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation'; // 正しいインポート
import Link from 'next/link';

interface Info {
    id: number;
    seat_num: number;
    availability: number;
    reserver: number;
}

export default function Reserve() {      
    const [infos, setInfo] = useState<Info[]>([]);
    const [selectedSeat, setSelectedSeat] = useState<number | null>(null); // 選択された座席番号
    const [reserver, setReserver] = useState<string>(''); // 入力された名前
    const [state, setState] = useState<number | null>(null); // 予約状態
    const [ID, setID] = useState<number | null>(null); // id
    const router = useRouter(); // useRouter フックを使用

    useEffect(() => {
        const fetchFaceStatus = async () => {
            try {
              const response = await fetch("http://localhost:5000/person_status", {
                cache: "no-cache",
              });
              const data: Info[] = await response.json();
              setInfo(data);
            } catch (err) {
              console.error(err);
            }
          };

        fetchFaceStatus();

        const interval = setInterval(fetchFaceStatus, 1000); // 定期的にフェッチ
        return () => clearInterval(interval); // クリーンアップ
    }, []);

    // 予約ボタンのハンドラー
    const handleReserve = async () => {
        if (selectedSeat === null) {
            alert('座席番号を選択してください。');
            return;
        }
        if (reserver.trim() === '') {
            alert('名前を入力してください。');
            return;
        }

        try {
            // 予約処理をバックエンドに送信
            const response = await fetch('http://localhost:5000/external_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    seat_num: selectedSeat,
                    reserver: reserver,
                    availability: state,
                    id: ID,
                }),
            });
            

            alert("予約が完了しました。")
            setSelectedSeat(null);
            setReserver('');
            setState(null);
            setID(null);

            if (!response.ok) {
                throw new Error('予約に失敗しました。');
            }
             
        } catch (error) {
            console.error(error);
            alert('予約に失敗しました。再度お試しください。');
        }
    };

    return(
        <div className="flex justify-center items-center h-screen w-full">
            <div className="flex flex-col items-center w-[80%] border border-gray-700 rounded-2xl p-5 z-50">
                <div className="mb-5">
                    <h1 className="text-5xl text-center font-bold">~ Reserve ~</h1>
                </div>
                <div className="flex w-full justify-evenly items-center mb-10">
                    <div className='p-5 border shadow-inner shadow-white rounded-2xl'>
                        <h1 className='text-center text-3xl font-bold mb-5 text-emerald-300'>利用可能</h1>
                        <ul>
                            {infos.map((info) => (
                                info.availability === 0 ? (
                                    <li key={info.id} className='mb-3'>
                                        <button 
                                            className={`p-2 rounded-lg bg-slate-800 hover:bg-gray-900 ${
                                                selectedSeat === info.seat_num ? 'bg-emerald-500' : ''
                                            }`}
                                            onClick={() => {
                                                setSelectedSeat(info.seat_num);
                                                setState(2);
                                                setID(info.id)                             
                                            }}                                            
                                        >
                                            Seat Number: {info.seat_num}
                                        </button>                                
                                    </li>
                                ) : null
                            ))}
                        </ul>
                    </div>
                    <div className='p-5 border shadow-inner shadow-white rounded-2xl'>
                        <h1 className='text-center text-3xl font-bold text-red-600 mb-5'>利用不可</h1>
                        <ul>
                            {infos.map((info) => (
                                info.availability === 1 ? (
                                    <li key={info.id} className='mb-4'>
                                        <button 
                                            className='p-2 rounded-lg bg-gray-800 hover:bg-gray-900 cursor-not-allowed' 
                                            disabled
                                        >
                                            Seat Number: {info.seat_num}
                                        </button> 
                                    </li>
                                ) : null
                            ))}
                        </ul>
                    </div>
                </div>  

                {/* 選択された座席番号の表示 */}
                {selectedSeat !== null && (
                    <div className='mb-5'>
                        <p className='text-xl'>選択された座席番号: <span className='font-bold'>{selectedSeat}</span></p>
                    </div>
                )}

                {/* 名前入力フィールド */}
                <div className='mb-5 w-full flex justify-center'>
                    <input 
                        type="text" 
                        className='text-black text-center p-2 w-1/2 rounded-lg'
                        placeholder='ロッカー番号を入力してください'
                        value={reserver}
                        onChange={(e) => setReserver(e.target.value)}
                    />
                </div>
                <div>
                    <button 
                        className='w-32 p-2 rounded-lg bg-gray-800 hover:bg-gray-900 text-white font-semibold'
                        onClick={handleReserve} // 予約ボタンのクリックハンドラー
                    >
                        予約
                    </button>
                </div>            
            </div>
        </div>
    );
}
