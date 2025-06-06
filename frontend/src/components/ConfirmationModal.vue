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
			class="fixed inset-0 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex justify-center items-center"
			@click.self="handleCancel"
		>
			<div
				class="relative bg-indigo-600/70 dark:bg-indigo-400/70 backdrop-blur-lg rounded-xl shadow-2xl p-6 max-w-md w-full mx-4"
			>
				<div
					class="flex justify-between items-center border-b border-gray-300/70 dark:border-gray-600/70 pb-3 mb-4"
				>
					<h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
						{{ title }}
					</h3>
					<button
						@click="handleCancel"
						class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
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
						class="text-base text-gray-800 dark:text-gray-100 whitespace-pre-line"
					>
						{{ message }}
					</p>
				</div>

				<div class="flex justify-end space-x-4">
					<button
						type="button"
						@click="handleCancel"
						class="px-4 py-2 bg-gray-300/70 dark:bg-gray-600/70 text-gray-800 dark:text-gray-200 font-medium rounded-lg hover:bg-gray-400/80 dark:hover:bg-gray-500/80 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500 focus:ring-opacity-75 transition duration-150 ease-in-out"
					>
						Cancel
					</button>
					<button
						type="button"
						@click="handleConfirm"
						class="px-4 py-2 bg-indigo-600 dark:bg-indigo-500 text-white font-medium rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-white/50 dark:focus:ring-offset-slate-800/50 transition duration-150 ease-in-out"
					>
						Confirm
					</button>
				</div>
			</div>
		</div>
	</Transition>
</template>

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
