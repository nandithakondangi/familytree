<template>
	<div :class="cardClasses">
		<!-- Shine effect from top -->
		<div
			:class="[shineEffectBaseClasses, topShineEffectClasses]"
		></div>
		<!-- Shine effect from bottom -->
		<div
			:class="[shineEffectBaseClasses, bottomShineEffectClasses]"
		></div>

		<!-- Slot for content, positioned above shine effects -->
		<div class="relative h-full">
			<slot></slot>
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { useThemeStore } from "@/store/theme";

const props = defineProps({
	title: {
		type: String,
		required: true,
	},
    themeColor: {
        type: String,
        default: "indigo",
        validator: (value) =>
			["blue", "indigo", "green", "orange", "yellow", "danger"].includes(value),
    },
});

const themeStore = useThemeStore();

const baseClasses =
	"relative overflow-hidden rounded-2xl p-4 backdrop-blur-md border border-white/20 shadow-lg transition-all duration-300 ease-out";

const cardClasses = computed(() => {
	const color = themeStore.getThemeClasses("GlassyTabPanel", props.themeColor);
	return `${baseClasses} ${color}`;
});

const shineEffectBaseClasses = computed(() => {
	return `pointer-events-none absolute inset-0 opacity-50 rounded-2xl`;
});

const topShineEffectClasses = computed(() => {
    return `bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-white/20 to-transparent`;
});
  
const bottomShineEffectClasses = computed(() => {
    return `bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-white/20 to-transparent`;
});
</script>