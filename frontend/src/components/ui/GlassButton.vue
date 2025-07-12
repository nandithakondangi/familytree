<template>
	<button :class="buttonClasses" :disabled="disabled">
		<!-- Slot for button text or other content -->
		<span class="relative">
			<slot></slot>
		</span>

		<!-- Permanent shine effect that intensifies on hover to create a bulging look -->
		<div
			class="absolute inset-0 h-full w-full rounded-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/40 to-transparent opacity-60 group-hover:opacity-90 transition-opacity duration-300"
		></div>
	</button>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
	color: {
		type: String,
		default: "blue", // e.g., 'blue', 'purple', 'green'
		validator: (value) =>
			["blue", "indigo", "green", "orange", "yellow", "danger"].includes(value),
	},
	disabled: {
		type: Boolean,
		default: false,
	},
});

// Base classes are applied regardless of color or state
const baseClasses =
	"group relative px-6 py-3 font-medium rounded-full border border-white/20 shadow-lg backdrop-blur-md transition-all duration-300 ease-out";

// Color-specific classes
const colorVariantClasses = {
	blue: "text-blue-900 dark:text-blue-100 bg-blue-500/20 dark:bg-blue-400/20 group-hover:bg-blue-500/30 dark:group-hover:bg-blue-400/30",
	indigo:
		"text-indigo-900 dark:text-indigo-100 bg-indigo-500/20 dark:bg-indigo-400/20 group-hover:bg-indigo-500/30 dark:group-hover:bg-indigo-400/30",
	green:
		"text-green-900 dark:text-green-100 bg-green-500/20 dark:bg-green-400/20 group-hover:bg-green-500/30 dark:group-hover:bg-green-400/30",
	orange:
		"text-orange-900 dark:text-orange-100 bg-orange-500/20 dark:bg-orange-400/20 group-hover:bg-orange-500/30 dark:group-hover:bg-orange-400/30",
	yellow:
		"text-yellow-900 dark:text-yellow-100 bg-yellow-500/20 dark:bg-yellow-400/20 group-hover:bg-yellow-500/30 dark:group-hover:bg-yellow-400/30",
	danger:
		"text-red-900 dark:text-red-100 bg-red-500/20 dark:bg-red-400/20 group-hover:bg-red-500/30 dark:group-hover:bg-red-400/30",
};

// Classes for different states
const enabledStateClasses =
	"hover:scale-105 hover:shadow-xl active:scale-95 active:shadow-md";
const disabledStateClasses = "opacity-50 cursor-not-allowed";

const buttonClasses = computed(() => {
	const color = colorVariantClasses[props.color] || colorVariantClasses.blue;
	const state = props.disabled ? disabledStateClasses : enabledStateClasses;
	return `${baseClasses} ${color} ${state}`;
});
</script>
