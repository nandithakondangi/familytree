<template>
	<Transition
		enter-active-class="transition-all ease-out duration-500"
		enter-from-class="opacity-0 translate-y-full"
		enter-to-class="opacity-100 translate-y-0"
		leave-active-class="transition-all ease-in duration-300"
		leave-from-class="opacity-100 translate-y-0"
		leave-to-class="opacity-0 translate-y-full scale-50"
	>
		<div
			v-if="isVisible"
			class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex justify-center items-center"
			@click.self="closeModal"
		>
			<div
				class="relative bg-indigo-600/70 dark:bg-indigo-400/70 backdrop-blur-lg rounded-xl shadow-2xl p-6 max-w-lg w-full mx-4"
			>
				<div
					class="flex justify-between items-center border-b border-gray-300/70 dark:border-gray-600/70 pb-3 mb-4"
				>
					<h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
						Link to Existing Member
					</h3>
					<button
						@click="closeModal"
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

				<form @submit.prevent="handleLink" class="space-y-4">
					<div>
						<label
							class="block text-sm font-medium text-gray-700 dark:text-gray-300"
							>Source Member:</label
						>
						<input
							type="text"
							:value="sourceMemberName"
							disabled
							class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm sm:text-sm bg-gray-100 dark:bg-slate-700 dark:text-gray-400 cursor-not-allowed p-2"
						/>
					</div>
					<div>
						<label
							class="block text-sm font-medium text-gray-700 dark:text-gray-300"
							>Relationship Type:</label
						>
						<input
							type="text"
							:value="relationshipTypeDisplay"
							disabled
							class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm sm:text-sm bg-gray-100 dark:bg-slate-700 dark:text-gray-400 cursor-not-allowed p-2"
						/>
					</div>
					<div>
						<label
							for="targetMember"
							class="block text-sm font-medium text-gray-700 dark:text-gray-300"
							>Target Member:</label
						>
						<select
							id="targetMember"
							v-model="selectedTargetId"
							required
							class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200 p-2"
						>
							<option disabled value="">Please select a member</option>
							<option
								v-for="member in potentialTargets"
								:key="member.id"
								:value="member.id"
							>
								{{ member.name }} (ID: {{ member.id }})
							</option>
						</select>
					</div>

					<div
						class="flex justify-end space-x-4 pt-4 border-t border-gray-300/70 dark:border-gray-600/70"
					>
						<button
							type="button"
							@click="closeModal"
							class="px-4 py-2 bg-gray-300/70 dark:bg-gray-600/70 text-gray-800 dark:text-gray-200 font-medium rounded-lg hover:bg-gray-400/80 dark:hover:bg-gray-500/80 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500 focus:ring-opacity-75 transition duration-150 ease-in-out"
						>
							Cancel
						</button>
						<button
							type="submit"
							class="px-4 py-2 bg-indigo-600 dark:bg-indigo-500 text-white font-medium rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-white/50 dark:focus:ring-offset-slate-800/50 transition duration-150 ease-in-out"
						>
							🔗 Link Members
						</button>
					</div>
				</form>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps({
	isVisible: Boolean,
	sourceNodeId: String,
	sourceMemberName: String,
	relationshipType: String, // e.g., SPOUSE, PARENT, CHILD
	potentialTargets: Array, // [{ id: '...', name: '...' }]
});

const emit = defineEmits(["close", "link"]);

const selectedTargetId = ref("");

const relationshipTypeDisplay = computed(() => {
	if (!props.relationshipType) return "";
	return (
		props.relationshipType.charAt(0).toUpperCase() +
		props.relationshipType.slice(1).toLowerCase()
	);
});

watch(
	() => props.isVisible,
	(newValue) => {
		if (newValue) {
			selectedTargetId.value = ""; // Reset selection when modal becomes visible
		}
	},
);

const closeModal = () => {
	emit("close");
};

const handleLink = () => {
	if (!selectedTargetId.value) {
		// Optionally, show an alert or validation message
		return;
	}
	emit("link", {
		sourceNodeId: props.sourceNodeId,
		relationshipType: props.relationshipType,
		targetMemberId: selectedTargetId.value,
	});
};
</script>
