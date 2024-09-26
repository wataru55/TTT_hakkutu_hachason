import Link from "next/link";

export default function Display() {
  return (
    <div className="relative flex flex-col justify-center items-center h-[calc(100vh-78px)] w-full px-10">
      <div className="h-[30%] w-full border-b border-zinc-600"></div>
      <div className="flex flex-col justify-center p-2 h-[40%]">
        <div className="text-center mb-10">
          <h1 className="text-7xl mb-5 font-serif font-bold">
            整<span className="font-sans font-thin">know</span>
          </h1>
          <h1 className="text-3xl font-serif">整いスペース事前予約サービス</h1>
        </div>
        <div className="flex justify-center p-2 gap-10">
          <Link
            href="/reserve"
            className="bg-white rounded-md px-5 py-3 text-black hover:bg-slate-200 font-serif font-medium"
          >
            予約する
          </Link>
          <Link
            href="/display"
            className="bg-white rounded-md px-5 py-3 text-black hover:bg-slate-200 font-serif font-medium"
          >
            空き状況を確認
          </Link>
        </div>
      </div>
      <div className="h-[30%] w-full border-t border-zinc-600">
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-10">
          <p className="steam-01">
            <img src="/steam2.svg" alt="steam" />
          </p>
        </div>
      </div>
    </div>
  );
}
