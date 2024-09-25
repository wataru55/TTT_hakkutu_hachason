import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function Display() {

  return (
    <div className='relative flex flex-col justify-center items-center h-screen w-full px-10'>
      <div className='h-[30%] w-full border-b border-zinc-600'>

      </div>
       <div className='flex flex-col justify-center p-2 h-[40%]'>
        <div className='text-center mb-10'>
          <h1 className='text-6xl mb-5 font-serif'>最高の整いを</h1>
          <h1 className='text-3xl font-serif'>究極のリラックス体験をあなたに</h1>
        </div>
        <div className='flex justify-center p-2 gap-10'>
          <Link href="/reserve" className='bg-white rounded-md px-5 py-3 text-black hover:bg-slate-200 font-serif font-medium'>
            予約する
          </Link>
          <Link href="/display" className='bg-white rounded-md px-5 py-3 text-black hover:bg-slate-200 font-serif font-medium'>
            画面を見る
          </Link>
        </div>
       </div>
       <div className='h-[30%] w-full border-t border-zinc-600'>
        <div className='absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-10'>
          <p className='steam-01'>
            <img src="/steam2.svg" alt="steam" />
          </p>
        </div>
      </div>
    </div>  
  );
}
