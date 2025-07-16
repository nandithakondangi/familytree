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

const baseClasses =
	"relative overflow-hidden rounded-2xl p-4 backdrop-blur-md border border-white/20 shadow-lg transition-all duration-300 ease-out";

// Color-specific classes
const colorVariantClasses = {
    blue: "text-blue-900 dark:text-blue-100 bg-blue-500/20 dark:bg-blue-400/20",
    indigo:
        "text-indigo-900 dark:text-indigo-100 bg-indigo-500/20 dark:bg-indigo-400/20",
    green:
        "text-green-900 dark:text-green-100 bg-green-500/20 dark:bg-green-400/20",
    orange:
        "text-orange-900 dark:text-orange-100 bg-orange-500/20 dark:bg-orange-400/20",
    yellow:
        "text-yellow-900 dark:text-yellow-100 bg-yellow-500/20 dark:bg-yellow-400/20",
    danger:
        "text-red-900 dark:text-red-100 bg-red-500/20 dark:bg-red-400/20",
};

const cardClasses = computed(() => {
	const color = colorVariantClasses[props.themeColor] || colorVariantClasses.indigo;
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