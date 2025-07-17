<template>
	<button :class="buttonClasses" :disabled="disabled">
		<!-- Slot for button text or other content -->
		<span class="relative">
			<slot></slot>
		</span>

		<!-- Permanent shine effect that intensifies on hover to create a bulging look -->
		<div :class="shineEffectClasses"></div>
	</button>
</template>

<script setup>
import { computed } from "vue";
import { useThemeStore } from "@/store/theme";

const props = defineProps({
	themeColor: {
		type: String,
		default: "indigo",
		validator: (value) =>
			["blue", "indigo", "green", "orange", "yellow", "danger"].includes(value),
	},
	disabled: {
		type: Boolean,
		default: false,
	},
});

const themeStore = useThemeStore();

// Base classes are applied regardless of color or state
const baseClasses =
	"group relative px-6 py-3 font-medium rounded-full border border-white/20 shadow-lg backdrop-blur-md transition-all duration-300 ease-out";

// Classes for different states
const enabledStateClasses =
	"hover:scale-105 hover:shadow-xl active:scale-95 active:shadow-md";
const disabledStateClasses = "opacity-50 cursor-not-allowed";

const buttonClasses = computed(() => {
	const color = themeStore.getThemeClasses("GlassyButton", props.themeColor);
	const state = props.disabled ? disabledStateClasses : enabledStateClasses;
	return `${baseClasses} ${color} ${state}`;
});

const shineEffectClasses = computed(() => `
	absolute inset-0 h-full w-full 
	rounded-full 
	bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] 
	from-white/40 to-transparent 
	opacity-60 
	group-hover:opacity-90 
	transition-opacity duration-300
`);
</script>
