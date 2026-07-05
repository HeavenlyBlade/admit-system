/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // SACLI brand colors from logo
        sacli: {
          green: '#1a8b6d',      // Main teal/emerald green
          'green-dark': '#146b54', // Darker green
          'green-light': '#2da887', // Lighter green
          gold: '#d4af37',        // Gold accent
          'gold-light': '#e8c960', // Light gold
          'gold-dark': '#b8941f',  // Dark gold
        },
        primary: '#1a8b6d',      // SACLI green
        secondary: '#d4af37',    // SACLI gold
        accent: '#2da887',       // Light green accent
      },
    },
  },
  plugins: [],
}
