/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        nest: {
          DEFAULT: "#e05a47",
          dark: "#c44634",
        },
      },
    },
  },
  plugins: [],
};
