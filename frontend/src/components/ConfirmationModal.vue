<template>
	<Transition
		enter-active-class="transition-all ease-out duration-300"
		enter-from-class="opacity-0 -translate-y-full transform scale-95"
		enter-to-class="opacity-100 translate-y-0 transform scale-100"
		leave-active-class="transition-all ease-in duration-200"
		leave-from-class="opacity-100 translate-y-0 transform scale-100"
		leave-to-class="opacity-0 -translate-y-full transform scale-95"
	>
		<div
			v-if="isVisible"
			class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex justify-center items-center"
			@click.self="handleCancel"
		>
			<div
				class="relative backdrop-blur-lg rounded-xl shadow-2xl p-6 max-w-md w-full mx-4"
				style="background-color: var(--theme-bg-primary)"
			>
				<div
					class="flex justify-between items-center border-b pb-3 mb-4"
					style="border-color: var(--theme-border-color)"
				>
					<h3
						class="text-lg font-semibold"
						style="color: var(--theme-text-on-primary-bg)"
					>
						{{ title }}
					</h3>
					<button
						@click="handleCancel"
						class="icon-close transition-colors"
						aria-label="Close modal"
					>
						<svg
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<div class="mb-6">
					<p
						class="text-base whitespace-pre-line"
						style="color: var(--theme-text-on-primary-bg)"
					>
						{{ message }}
					</p>
				</div>

				<div class="flex justify-end space-x-4">
					<button type="button" @click="handleCancel" class="button-secondary">
						Cancel
					</button>
					<button type="button" @click="handleConfirm" class="button-primary">
						Confirm
					</button>
				</div>
			</div>
		</div>
	</Transition>
</template>

<style scoped>
.icon-close {
	color: var(--theme-icon-color);
}
.icon-close:hover {
	color: var(--theme-icon-hover-color);
}
</style>

<script setup>
import { defineProps, defineEmits } from "vue";

defineProps({
	isVisible: Boolean,
	title: {
		type: String,
		default: "Confirm Action",
	},
	message: {
		type: String,
		required: true,
	},
});

const emit = defineEmits(["confirm", "cancel"]);

const handleConfirm = () => {
	emit("confirm");
};

const handleCancel = () => {
	emit("cancel");
};
</script>
