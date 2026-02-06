import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Space Grotesk", "sans-serif"],
        serif: ["Instrument Serif", "serif"],
      },
      colors: {
        ink: "#0b0e12",
        mist: "#f2f4f8",
        tide: "#0e8a7a",
        ember: "#f08a4b",
        fog: "#c7cedb",
      },
      boxShadow: {
        glow: "0 0 40px rgba(14, 138, 122, 0.15)",
      },
    },
  },
  plugins: [],
} satisfies Config;
