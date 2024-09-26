import React from "react";
import Image from "next/image";
import Link from "next/link";

const Header = () => {
  return (
    <div
      style={{
        borderRadius: "50%",
        overflow: "hidden",
        width: 50,
        height: 50,
      }}
      className="mt-2 mr-2"
    >
      <Link href="/">
        <Image
          src="/logo.png"
          alt="logo"
          width={50}
          height={50}
          className="opacity-80"
        />
      </Link>
    </div>
  );
};

export default Header;
