/** @type {import('tailwindcss').Config} */
const defaultTheme = require("tailwindcss/defaultTheme");
const plugin = require('tailwindcss/plugin');

module.exports = {
	darkMode: "class",
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./.storybook/preview.js",
	],
	theme: {
		extend: {
			fontFamily: {
				sans: ["Quicksand", ...defaultTheme.fontFamily.sans],
			},
			transitionTimingFunction: {
				'splash': 'cubic-bezier(0.6, 1.3, 0.85, 1)',
			}
		},
	},
	plugins: [
		require("@tailwindcss/typography"),
		plugin(function({ addUtilities, theme }) {
			const newUtilities = {
				'.transition-modal-enter': {
				transition: `transform 500ms ${theme('transitionTimingFunction.splash')}, opacity 500ms ${theme('transitionTimingFunction.splash')}, border-radius 100ms ease-in-out 400ms`,
				},
				'.transition-modal-leave': {
				transition: `transform 300ms ease-in, opacity 200ms ease-in, border-radius 300ms ease-in`,
				}
			}
      		addUtilities(newUtilities)
    	})
	],
};
