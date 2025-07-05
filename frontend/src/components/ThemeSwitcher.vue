// src/components/ThemeSwitcher.vue (Example)
<template>
	<div
		class="theme-switcher p-4 rounded-md"
		style="background-color: var(--theme-bg-secondary)"
	>
		<label
			for="theme-select"
			class="block mb-2 text-sm font-medium"
			style="color: var(--theme-text-primary)"
			>Select Theme:</label
		>
		<select
			id="theme-select"
			:value="themeStore.currentThemeName"
			@change="themeStore.setThemeName($event.target.value)"
			class="input-field w-full mb-4"
		>
			<option
				v-for="themeKey in themeStore.availableThemes"
				:key="themeKey"
				:value="themeKey"
			>
				{{ formatThemeName(themeKey) }}
			</option>
		</select>

		<button @click="themeStore.toggleMode" class="button-primary w-full">
			Switch to {{ themeStore.currentMode === "light" ? "Dark" : "Light" }} Mode
		</button>
	</div>
</template>

<script setup>
import { useThemeStore } from "@/stores/theme"; // Adjust path as needed

const themeStore = useThemeStore();

const formatThemeName = (themeKey) => {
	// Simple formatter: IndigoViolet -> Indigo Violet
	return themeKey.replace(/([A-Z])/g, " $1").trim();
};
</script>

<style scoped>
/* Add any specific styles for the switcher itself */
</style>
