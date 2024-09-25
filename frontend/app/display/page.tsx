"use client";

import { useState, useEffect } from "react";
import { BiChair } from "react-icons/bi";

interface Info {
  id: number;
  seat_num: number;
  availability: number;
}

export default function Display() {
  const [infos, setInfos] = useState<Info[]>([]);

  useEffect(() => {
    const fetchFaceStatus = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/get_external_data",
          {
            cache: "no-cache",
          }
        );
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

  // 椅子を3個と5個のグループに分ける
  const firstRow = infos.slice(0, 3);
  const secondRow = infos.slice(3, 8);

  return (
    <div className="h-screen flex flex-col items-center p-20">
      <h1 className="text-7xl mb-5">空き情報</h1>
      <ul className="flex flex-wrap justify-center">
        {infos.map((info) => (
          <li
            key={info.id}
            className="mb-3 p-2 text-3xl flex flex-col items-center"
          >
            <BiChair
              className={`${
                info.availability === 1 ? "text-red-500" : "text-green-500"
              }`}
              size={80}
            />
            <span>{info.seat_num}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
