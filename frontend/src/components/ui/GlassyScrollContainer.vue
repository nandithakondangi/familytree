<template>
	<div
		:class="[
			'glassy-scroll-container',
			'rounded-2xl',
			'shadow-lg',
			'p-2',
			'border',
			'border-white/20',
			'bg-black/5',
			'dark:bg-white/5',
			themeClass,
		]"
		:style="{ '--scrollbar-size': scrollbarSize }"
	>
		<slot></slot>
	</div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
	themeColor: {
		type: String,
		default: "indigo",
		validator: (value) =>
			["blue", "indigo", "green", "orange", "yellow", "danger"].includes(
				value,
			),
	},
	// Allows overriding the default size of the scrollbar
	scrollbarSize: {
		type: String,
		default: "8px",
	},
});

const themeClass = computed(() => `theme-${props.themeColor}`);
</script>

<style>
/* We remove 'scoped' to allow styling of the scrollbar pseudo-elements, which don't work well with Vue's scoped styles. */
/* The .glassy-scroll-container class provides enough specificity to avoid global conflicts. */
.glassy-scroll-container {
	overflow: auto;
	height: 100%;
	width: 100%;
}

/* === Base Scrollbar Styles (Webkit) === */
.glassy-scroll-container::-webkit-scrollbar {
	width: var(--scrollbar-size);
	height: var(--scrollbar-size);
}

.glassy-scroll-container::-webkit-scrollbar-button {
	/* Hide the scrollbar buttons (arrows) on Webkit browsers */
	display: none;
}

.glassy-scroll-container::-webkit-scrollbar-track {
	background: transparent;
}

.glassy-scroll-container::-webkit-scrollbar-thumb {
	border-radius: 10px;
	border: 1px solid rgba(255, 255, 255, 0.2);
	box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.1);
	transition: background-color 0.3s ease-out;
}

.dark .glassy-scroll-container::-webkit-scrollbar-thumb {
	border-color: rgba(0, 0, 0, 0.2);
}

/* === Theme Definitions === */
/* We use Tailwind's color variables (exposed as --tw-color-*) to stay consistent with the theme. */

/* --- Indigo --- */
.glassy-scroll-container.theme-indigo::-webkit-scrollbar-thumb {
	background-color: theme('colors.indigo.400 / 50%');
}
.glassy-scroll-container.theme-indigo::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.indigo.400 / 70%');
}
.dark .glassy-scroll-container.theme-indigo::-webkit-scrollbar-thumb {
	background-color: theme('colors.indigo.300 / 40%');
}
.dark .glassy-scroll-container.theme-indigo::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.indigo.300 / 60%');
}

/* --- Blue --- */
.glassy-scroll-container.theme-blue::-webkit-scrollbar-thumb {
	background-color: theme('colors.blue.400 / 50%');
}
.glassy-scroll-container.theme-blue::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.blue.400 / 70%');
}
.dark .glassy-scroll-container.theme-blue::-webkit-scrollbar-thumb {
	background-color: theme('colors.blue.300 / 40%');
}
.dark .glassy-scroll-container.theme-blue::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.blue.300 / 60%');
}

/* --- Green --- */
.glassy-scroll-container.theme-green::-webkit-scrollbar-thumb {
	background-color: theme('colors.green.400 / 50%');
}
.glassy-scroll-container.theme-green::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.green.400 / 70%');
}
.dark .glassy-scroll-container.theme-green::-webkit-scrollbar-thumb {
	background-color: theme('colors.green.300 / 40%');
}
.dark .glassy-scroll-container.theme-green::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.green.300 / 60%');
}

/* --- Orange --- */
.glassy-scroll-container.theme-orange::-webkit-scrollbar-thumb {
	background-color: theme('colors.orange.400 / 50%');
}
.glassy-scroll-container.theme-orange::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.orange.400 / 70%');
}
.dark .glassy-scroll-container.theme-orange::-webkit-scrollbar-thumb {
	background-color: theme('colors.orange.300 / 40%');
}
.dark .glassy-scroll-container.theme-orange::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.orange.300 / 60%');
}

/* --- Yellow --- */
.glassy-scroll-container.theme-yellow::-webkit-scrollbar-thumb {
	background-color: theme('colors.yellow.400 / 50%');
}
.glassy-scroll-container.theme-yellow::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.yellow.400 / 70%');
}
.dark .glassy-scroll-container.theme-yellow::-webkit-scrollbar-thumb {
	background-color: theme('colors.yellow.300 / 40%');
}
.dark .glassy-scroll-container.theme-yellow::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.yellow.300 / 60%');
}

/* --- Danger (Red) --- */
.glassy-scroll-container.theme-danger::-webkit-scrollbar-thumb {
	background-color: theme('colors.red.400 / 50%');
}
.glassy-scroll-container.theme-danger::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.red.400 / 70%');
}
.dark .glassy-scroll-container.theme-danger::-webkit-scrollbar-thumb {
	background-color: theme('colors.red.300 / 40%');
}
.dark .glassy-scroll-container.theme-danger::-webkit-scrollbar-thumb:hover {
	background-color: theme('colors.red.300 / 60%');
}
</style>