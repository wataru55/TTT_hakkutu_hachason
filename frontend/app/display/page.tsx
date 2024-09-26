"use client";

import { useState, useEffect } from "react";
import { BiChair } from "react-icons/bi";
import Image from "next/image"

interface Info {
  id: number;
  availability: number;
  reserver: number;
}

export default function Display() {
  const [infos, setInfos] = useState<Info[]>([]);

  useEffect(() => {
    const fetchFaceStatus = async () => {
      try {
        const response = await fetch("http://localhost:5001/json_data", {
          cache: "no-cache",
        });
        const data: Info[] = await response.json();
        setInfos(data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchFaceStatus();

    const interval = setInterval(fetchFaceStatus, 1000); // 定期的にフェッチ
    return () => clearInterval(interval); // クリーンアップ
  }, []);

  return (
    <div className="flex justify-center items-center h-screen w-full">
      <div className="flex flex-col items-center w-[80%] min-h-[500px] border border-gray-700 rounded-2xl p-5 z-50 justify-center">
        <ul className="flex flex-wrap justify-center">
          {infos.map((info) => (
            <li
              key={info.id}
              className="p-7 text-3xl flex flex-col items-center"
            >
              <span>{info.id}</span>
              {info.availability === 1 || info.availability === 2 ? (
                <Image
                src="/chair_gray.png"
                alt="chair_gray"
                width={120}
                height={120}
                className="opacity-30"
              />
              ) : (
                <Image
                src="/chair_white.png"
                alt="chair_white"
                width={120}
                height={120}
              />
              )}              
              {info.availability === 0 && <p className="text-sm">利用可能</p>}
              {info.availability === 1 && (
                <span className="text-sm">
                  <span className="bg-[#e8bc43] text-black font-bold rounded-md">
                    {info.reserver}
                  </span>
                  が整い中
                </span>
              )}
              {info.availability === 2 && (
                <span className="text-sm">
                  <span className="bg-[#e8bc43] text-black font-bold rounded-md">
                    {info.reserver}
                  </span>
                  が予約中
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
