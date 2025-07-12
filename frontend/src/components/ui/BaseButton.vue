<template>
	<button :class="buttonClasses" :disabled="disabled">
		<slot></slot>
	</button>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
	variant: {
		type: String,
		default: "primary", // e.g., 'primary', 'secondary', 'danger'
	},
	disabled: {
		type: Boolean,
		default: false,
	},
});

const baseClasses =
	"px-4 py-2 rounded-md font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-slate-900 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed";

const variantClasses = {
	primary: "bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-500",
	secondary:
		"bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600",
	danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
};

const buttonClasses = computed(() => {
	return `${baseClasses} ${
		variantClasses[props.variant] || variantClasses.primary
	}`;
});
</script>
