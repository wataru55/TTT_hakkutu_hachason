"use client";

import { useState, useEffect } from "react";
import { BiChair } from "react-icons/bi";

interface Info {
  id: number;
  availability: number;
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
        console.log("data", data);
        setInfos(data);
        console.log(data);
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
      <div className="flex flex-col items-center w-[80%] h-[500px] border border-gray-700 rounded-2xl p-5 z-50 justify-center">
        <ul className="flex flex-wrap justify-center">
          {infos.map((info) => (
            <li
              key={info.id}
              className="p-7 text-3xl flex flex-col items-center"
            >
              <BiChair
                className={`${
                  info.availability === 1 || info.availability === 2
                    ? "text-gray-400 opacity-30"
                    : "text-[#ab653d]"
                }`}
                size={120}
              />
              <span>{info.id}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
