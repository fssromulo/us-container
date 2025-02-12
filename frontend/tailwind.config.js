/** @type {import('tailwindcss').Config} */
const plugin = require("tailwindcss/plugin");

export default {
  corePlugins: {
    preflight: false,
  },
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  darkMode: "media", // or 'class'
  theme: {
    // Extend or customize your theme here
    extend: {
      colors: {
        "cust-dark-navy": "#1F2833",
        "cust-aqua": "#66FCF1",
        "cust-teal": "#45A29E",
        "cust-dark-navy-50%": "#1f28337b",
        "cust-dark-navy-75%": "#1f2833b7",
        "cust-gray": "#999999",
        "cust-silver": "#C0C0C0",
        "cust-gold": "#ffd895",
      },
      primary: "#ffa200", // Custom primary color
      primaryDark: "#d88900", // Darker shade of the primary color
      secondary: "#146ec5", // Custom secondary color
      secondaryDark: "#1438c5", // Darker shade of the secondary color
      // You can continue to define other colors as needed
      contrast: "#171515",
      accentColor: "ced4db",
      white: "#ffffff",
      gray: "#4b5563",
      animation: {
        "spin-slow": "spin 5s linear infinite",
      },
      fontFamily: {
        sans: ["San Francisco Font", "Arial", "sans-serif"],
      },
      backgroundImage: {
        "squares-pattern":
          "url('data:image/svg+xml;utf8,<svg xmlns=%27http://www.w3.org/2000/svg%27 width=%27100%27 height=%27100%27 viewBox=%270 0 100 100%27><defs><pattern id=%27squares-pattern%27 patternUnits=%27userSpaceOnUse%27 width=%27100%27 height=%27100%27><rect x=%270%27 y=%270%27 width=%2750%27 height=%2750%27 fill=%27black%27 /><rect x=%2750%27 y=%270%27 width=%2750%27 height=%2750%27 fill=%27%23ffd895%27 /><rect x=%270%27 y=%2750%27 width=%2750%27 height=%2750%27 fill=%27%23ffd895%27 /><rect x=%2750%27 y=%2750%27 width=%2750%27 height=%2750%27 fill=%27black%27 /></pattern></defs><rect width=%27100%%27 height=%27100%%27 fill=%27url(%23squares-pattern)%27 /></svg>')",
        "squares-pattern-2":
          "url('data:image/svg+xml;utf8,<svg xmlns=%27http://www.w3.org/2000/svg%27 width=%27200%27 height=%27200%27 viewBox=%270 0 200 200%27><defs><pattern id=%27larger-squares%27 patternUnits=%27userSpaceOnUse%27 width=%27200%27 height=%27200%27><rect x=%270%27 y=%270%27 width=%27100%27 height=%27100%27 fill=%27black%27 /><rect x=%27100%27 y=%270%27 width=%27100%27 height=%27100%27 fill=%27%23ffd895%27 /><rect x=%270%27 y=%27100%27 width=%27100%27 height=%27100%27 fill=%27%23ffd895%27 /><rect x=%27100%27 y=%27100%27 width=%27100%27 height=%27100%27 fill=%27black%27 /></pattern></defs><rect width=%27100%%27 height=%27100%%27 fill=%27url(%23larger-squares)%27 /></svg>')",
        "gradient-squares": `url('data:image/svg+xml;utf8,<svg xmlns=%27http://www.w3.org/2000/svg%27 width=%27200%27 height=%27200%27 viewBox=%270 0 200 200%27><defs><linearGradient id=%27gradient1%27 x1=%270%%27 y1=%270%%27 x2=%27100%%27 y2=%27100%%27><stop offset=%270%%27 style=%27stop-color:rgb(0,0,0); stop-opacity:1%27 /><stop offset=%27100%%27 style=%27stop-color:rgb(59,59,59); stop-opacity:0.5%27 /></linearGradient><pattern id=%27gradient-squares%27 patternUnits=%27userSpaceOnUse%27 width=%27200%27 height=%27200%27><rect x=%270%27 y=%270%27 width=%27100%27 height=%27100%27 fill=%27rgba(0, 0, 0, 1)%27 /><rect x=%27100%27 y=%270%27 width=%27100%27 height=%27100%27 fill=%27url(%23gradient1)%27 /><rect x=%270%27 y=%27100%27 width=%27100%27 height=%27100%27 fill=%27url(%23gradient1)%27 /><rect x=%27100%27 y=%27100%27 width=%27100%27 height=%27100%27 fill=%27rgba(0, 0, 0, 0.5)%27 /></pattern></defs><rect width=%27100%%27 height=%27100%%27 fill=%27url(%23gradient-squares)%27 /></svg>')`,
      },
      height: {
        "almost-full": "90%",
      },
    },
  },
  plugins: [
    require("tailwindcss-primeui"),
    plugin(function ({ addUtilities }) {
      const newUtilities = {
        ".mask-gradient-top-to-bottom": {
          maskImage:
            "linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)",
        },
      };
      addUtilities(newUtilities);
    }),
  ],
};

// Issue with bg-gradient not working was bc I was commenting out the @tailwind base; directive in my main.css file
// instead I should do what they did here: https://github.com/tailwindlabs/tailwindcss/issues/11831
