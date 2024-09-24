import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function Display() {

  return (
    <div className='flex flex-col h-screen w-full'>
      <div className='flex items-end h-[15%]'>
        <h1 className='text-7xl ml-5'>最高の整いを</h1>
      </div>
      <div className='flex h-[70%]'>
        <div className='flex flex-col justify-end h-full w-1/2'>
          <div className='relative flex flex-col justify-center items-center h-[80%]'>
            <Link href="/reserve">
              <Image
                src="/reserve.jpeg"
                alt='reserve'
                width={600}
                height={400}
              />
            </Link>
            <p className='text-3xl mb-2'>Reserve</p>         
          </div>
        </div>
        <div className='flex flex-col justify-start h-full w-1/2'>
          <div className='relative flex flex-col justify-center items-center h-[80%]'>
            <Link href="/display">
              <Image
                src="/display.jpg"
                alt='reserve'
                width={600}
                height={400}
                className=''
              />
            </Link>           
            <p className='text-3xl mt-2'>Display</p>
          </div>
        </div>
      </div>
      <div className='h-[15%]'>
        <h1 className='text-right text-7xl mr-5'>体験しませんか</h1>
      </div>
    </div>  
  );
}
