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
				class="relative backdrop-blur-lg rounded-xl shadow-2xl p-6 max-w-lg w-full mx-4"
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
						Link to Existing Member
					</h3>
					<button
						@click="closeModal"
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

				<form @submit.prevent="handleLink" class="space-y-4">
					<div>
						<label class="form-label">Source Member:</label>
						<input
							type="text"
							:value="sourceMemberName"
							disabled
							class="input-field-disabled mt-1 block w-full sm:text-sm p-2"
						/>
					</div>
					<div>
						<label class="form-label">Relationship Type:</label>
						<input
							type="text"
							:value="relationshipTypeDisplay"
							disabled
							class="input-field-disabled mt-1 block w-full sm:text-sm p-2"
						/>
					</div>
					<div>
						<label for="targetMember" class="form-label">Target Member:</label>
						<select
							id="targetMember"
							v-model="selectedTargetId"
							required
							class="input-field mt-1 block w-full sm:text-sm p-2"
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
						class="flex justify-end space-x-4 pt-4 border-t"
						style="border-color: var(--theme-border-color)"
					>
						<button type="button" @click="closeModal" class="button-secondary">
							Cancel
						</button>
						<button type="submit" class="button-primary">
							🔗 Link Members
						</button>
					</div>
				</form>
			</div>
		</div>
	</Transition>
</template>

<style scoped>
.form-label {
	@apply block text-sm font-medium;
	color: var(--theme-text-on-primary-bg);
}

.input-field-disabled {
	@apply rounded-md shadow-sm cursor-not-allowed;
	background-color: rgba(var(--theme-input-bg-rgb), 0.5);
	color: rgba(var(--theme-input-text-rgb), 0.7);
	border: 1px solid rgba(var(--theme-border-color-rgb), 0.5);
}

.icon-close {
	color: var(--theme-icon-color);
}
.icon-close:hover {
	color: var(--theme-icon-hover-color);
}
/* Assuming .input-field, .button-primary, .button-secondary are defined globally */
/* If not, you would need to add their definitions here or in a global CSS file. */
</style>

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
