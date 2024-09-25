import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      fontFamily: {
        sans: ['"Inter"', 'sans-serif'], 
        mono: ['"Roboto Mono"', 'monospace'], 
      },
      keyframes: {
        steam: {
          '0%': { transform: 'translateY(0) scale(1)' },
          '50%': { transform: 'translateY(-10px) scale(1.1)' },
          '100%': { transform: 'translateY(-20px) scale(1)' },
        },
      },
      animation: {
        steam: 'steam 3s ease-in-out infinite', // カスタムアニメーションの定義
      },
    },
  },
  plugins: [],
};
export default config;
