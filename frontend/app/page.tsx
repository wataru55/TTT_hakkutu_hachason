import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Display() {

  return (
    <div className='flex justify-evenly h-screen w-full p-10'>
      <Link href="/reserve" className="h-96 w-96 border">
      </Link>
      <Link href="/display" className="h-96 w-96 border">
      </Link>
    </div>
  );
}
