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
		]"
		:style="scrollbarStyle"
	>
		<slot></slot>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { useThemeStore } from "@/store/theme";

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

const themeStore = useThemeStore();

const scrollbarStyle = computed(() => {
    const theme = themeStore.getThemeClasses('GlassyScrollContainer', props.themeColor);
    return {
        '--scrollbar-size': props.scrollbarSize,
        '--thumb-color': theme.thumb,
        '--thumb-hover-color': theme.thumbHover,
        '--dark-thumb-color': theme.darkThumb,
        '--dark-thumb-hover-color': theme.darkThumbHover,
    };
});
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
  background-color: var(--thumb-color);
}

.glassy-scroll-container::-webkit-scrollbar-thumb:hover {
  background-color: var(--thumb-hover-color);
}

.dark .glassy-scroll-container::-webkit-scrollbar-thumb {
	border-color: rgba(0, 0, 0, 0.2);
  background-color: var(--dark-thumb-color);
}

.dark .glassy-scroll-container::-webkit-scrollbar-thumb:hover {
  background-color: var(--dark-thumb-hover-color);
}
</style>