"use client";

import { useState, useEffect } from "react";
import { BiChair } from "react-icons/bi";
import Clock from "../components/Clock";

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
    <div className="flex flex-col justify-center items-center h-[calc(100vh-20px)] w-full">
      <Clock />
      <div className="flex flex-col items-center w-[80%] min-h-[500px] border border-gray-700 rounded-2xl p-5 z-50 justify-center">
        <ul className="flex flex-wrap justify-center">
          {infos.map((info) => (
            <li
              key={info.id}
              className="p-7 text-3xl flex flex-col items-center"
            >
              <span>{info.id}</span>
              <BiChair
                className={`${
                  info.availability === 1 || info.availability === 2
                    ? "text-gray-400 opacity-30"
                    : "text-[#ab653d]"
                }`}
                size={120}
              />
              {info.availability === 0 && <p className="text-sm">利用可能</p>}
              {info.availability === 1 && (
                <span className="text-sm">
                  <span className="bg-[#e8bc43] text-black font-bold rounded-md p-0.5">
                    {info.reserver}
                  </span>
                  &nbsp;整い中
                </span>
              )}
              {info.availability === 2 && (
                <span className="text-sm">
                  <span className="bg-[#e8bc43] text-black font-bold rounded-md p-0.5">
                    {info.reserver}
                  </span>
                  &nbsp;予約中
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
