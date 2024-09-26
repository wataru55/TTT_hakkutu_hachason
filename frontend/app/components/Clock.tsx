"use client";
import React, { useState, useEffect } from "react";

interface Time {
  year: number;
  month: number;
  date: number;
  dayNum: number;
  day: string;
  hour: number;
  min: number;
  sec: number;
}

export default function Clock() {
  const weekday = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];

  function getCurrentTime(): Time {
    const d = new Date();
    const dayNum = d.getDay();

    return {
      year: d.getFullYear(),
      month: d.getMonth() + 1,
      date: d.getDate(),
      dayNum: dayNum,
      day: weekday[dayNum],
      hour: d.getHours(),
      min: d.getMinutes(),
      sec: d.getSeconds(),
    };
  }

  const [time, setTime] = useState<Time | null>(null);

  useEffect(() => {
    setTime(getCurrentTime());

    const interval = setInterval(() => {
      setTime(getCurrentTime());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  function padZero(num: number): string {
    return num.toString().padStart(2, "0");
  }

  if (!time) {
    return null;
  }

  return (
    <div className="w-full flex justify-center mb-3">
      <div className="text-[#daf6ff] leading-3 text-center font-share-tech">
        <p className="text-2xs">
          {time.year}.{padZero(time.month)}.{padZero(time.date)} {time.day}
        </p>
        <p className="text-7xl">
          {padZero(time.hour)}:{padZero(time.min)}:{padZero(time.sec)}
        </p>
      </div>
    </div>
  );
}
