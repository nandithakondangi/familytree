import { defineStore } from "pinia";
import { ref, watchEffect } from "vue";
import { themes } from "../assets/themes.js"; // Adjust path if your themes.js is elsewhere

export const useThemeStore = defineStore("theme", () => {
	// Attempt to load saved theme and mode from localStorage, or use defaults
	const currentThemeName = ref(
		localStorage.getItem("themeName") || "indigoViolet",
	); // Default theme
	const currentMode = ref(localStorage.getItem("themeMode") || "light"); // Default mode

	function setThemeName(themeName) {
		if (themes[themeName]) {
			currentThemeName.value = themeName;
			localStorage.setItem("themeName", themeName);
		} else {
			console.warn(`Theme "${themeName}" not found. Falling back to default.`);
			currentThemeName.value = "indigoViolet"; // Fallback
			localStorage.setItem("themeName", "indigoViolet");
		}
	}

	function setMode(mode) {
		currentMode.value = mode;
		localStorage.setItem("themeMode", mode);
	}

	function toggleMode() {
		setMode(currentMode.value === "light" ? "dark" : "light");
	}

	// This is the core logic: apply the selected theme and mode to the document
	watchEffect(() => {
		const themeConfig = themes[currentThemeName.value]?.[currentMode.value];

		if (themeConfig) {
			for (const [key, value] of Object.entries(themeConfig)) {
				document.documentElement.style.setProperty(key, value);
			}

			if (currentMode.value === "dark") {
				document.documentElement.classList.add("dark");
				document.documentElement.classList.remove("light"); // Explicitly remove light
			} else {
				document.documentElement.classList.add("light");
				document.documentElement.classList.remove("dark"); // Explicitly remove dark
			}
		} else {
			console.error(
				`Theme configuration not found for: ${currentThemeName.value} in ${currentMode.value} mode.`,
			);
			// Optionally, apply a very basic fallback theme here
		}
	});

	// Call once on store initialization to apply the initial theme
	// The watchEffect will also run, but this ensures it's applied if localStorage values are valid.

	return {
		currentThemeName,
		currentMode,
		setThemeName,
		setMode,
		toggleMode,
		availableThemes: Object.keys(themes),
	};
});
