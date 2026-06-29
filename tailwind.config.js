/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        talent: { 400: '#38bdf8', 500: '#0ea5e9', 600: '#0284c7' },
        genius: { 400: '#e879f9', 500: '#d946ef', 600: '#c026d3' },
        success: { DEFAULT: '#10b981' },
        warning: { DEFAULT: '#f59e0b' },
        danger: { DEFAULT: '#ef4444' },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}