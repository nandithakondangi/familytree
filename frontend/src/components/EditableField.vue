<template>
	<div
		class="editable-field-root w-full"
		:class="{ group: editTrigger === 'button' && showEditButtonOnHover }"
		@click="handleContainerClick"
	>
		<template v-if="!isEditing">
			<div class="flex items-center w-full">
				<!-- Container for display mode: value + edit button -->
				<div :class="displayModeContainerClasses">
					<span :class="displayModeValueClasses">
						{{ displayValue }}
					</span>
					<button
						v-if="editTrigger === 'button'"
						@click.stop="emitToggleEdit"
						:class="
							[
								'p-1 text-sky-600 dark:text-sky-300 hover:text-sky-800 dark:hover:text-sky-100 ml-1 shrink-0',
								{
									'opacity-0 group-hover:opacity-100 focus:opacity-100':
										showEditButtonOnHover,
								},
							].concat(displayModeEditButtonLayoutClasses)
						"
						title="Edit"
					>
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
							<path
								d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
							></path>
						</svg>
					</button>
				</div>
			</div>
		</template>
		<template v-else>
			<div :class="['w-full', inputContainerClassToUse]">
				<div class="w-full">
					<slot
						:internalValue="internalValue"
						:updateInternalValue="updateInternalValue"
					>
						<input
							type="text"
							:value="internalValue"
							@input="updateInternalValue($event.target.value)"
							class="form-input-editable"
							ref="inputRef"
							@keydown.enter.prevent="onSave"
							@keydown.esc.prevent="onCancel"
						/>
					</slot>
				</div>
				<div
					:class="{
						'flex space-x-1 ml-1 shrink-0':
							!inputContainerClassToUse.includes('flex-col'),
						'flex justify-center space-x-2 mt-1 shrink-0':
							inputContainerClassToUse.includes('flex-col'),
					}"
				>
					<button
						@click="onSave"
						class="p-1 text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200"
						title="Save"
					>
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
								clip-rule="evenodd"
							></path>
						</svg>
					</button>
					<button
						@click="onCancel"
						class="p-1 text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-200"
						title="Cancel"
					>
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
								clip-rule="evenodd"
							></path>
						</svg>
					</button>
				</div>
			</div>
		</template>
	</div>
</template>

<script setup>
	import {
		defineProps,
		defineEmits,
		ref,
		watch,
		computed,
		nextTick,
	} from "vue";

	const props = defineProps({
		value: [String, Number, Boolean],
		fieldName: String,
		isEditing: Boolean,
		valueClass: {
			type: String,
			default: "text-white dark:text-black", // Default for right pane
		},
		inputContainerClass: {
			type: String,
			default: "flex items-center", // Default for right pane: input and buttons inline
		},
		editTrigger: {
			type: String,
			default: "button", // 'button' or 'valueClick'
		},
		showEditButtonOnHover: {
			type: Boolean,
			default: false, // If true, parent should be 'group'
		},
		emptyDisplayValue: {
			type: String,
			default: "N/A",
		},
		displayArrangement: {
			type: String,
			default: "inline", // 'inline' or 'stacked'
		},
		displayAlignment: {
			type: String,
			default: "start", // 'start', 'center', 'end'
			// For 'inline': 'start' (default), 'center' (value+btn centered), 'end' (value+btn at end)
			// For 'stacked': 'start' (items align-start), 'center' (items align-center), 'end' (items align-end)
		},
	});

	const emit = defineEmits(["toggleEdit", "save", "cancel"]);

	const internalValue = ref(props.value);
	const inputRef = ref(null);

	const valueClassToUse = computed(() => props.valueClass);
	const inputContainerClassToUse = computed(() => props.inputContainerClass);

	const displayValue = computed(() => {
		if (typeof props.value === "boolean") {
			return props.value ? "Yes" : "No"; // Or make these configurable later
		}
		return (props.value !== null &&
			props.value !== undefined &&
			String(props.value).trim() !== "") ||
			(typeof props.value === "number" && !isNaN(props.value))
			? props.value
			: props.emptyDisplayValue;
	});

	const displayModeContainerClasses = computed(() => {
		const classes = ["w-full"];
		if (props.displayArrangement === "stacked") {
			classes.push("flex", "flex-col");
			if (props.displayAlignment === "center") classes.push("items-center");
			else if (props.displayAlignment === "start") classes.push("items-start");
			else if (props.displayAlignment === "end") classes.push("items-end");
		} else {
			// inline
			classes.push("flex", "items-center");
			if (props.displayAlignment === "center") classes.push("justify-center");
			else if (props.displayAlignment === "end") classes.push("justify-end");
			// 'start' is default for flex
		}
		return classes;
	});

	const displayModeValueClasses = computed(() => {
		const classes = [
			"font-semibold",
			"text-sm",
			"break-all",
			valueClassToUse.value,
		];

		if (props.editTrigger === "valueClick") {
			classes.push("cursor-pointer");
		}
		if (props.displayArrangement === "inline") {
			if (
				props.displayAlignment === "start" ||
				props.displayAlignment === "center" ||
				props.displayAlignment === "end"
			) {
				// If alignment is not start, flex-grow might not be desired,
				// but for simplicity, let's keep it and rely on parent or valueClass for specific text alignment.
				// Or, only add flex-grow if 'start'
				if (props.displayAlignment === "start") {
					classes.push("flex-grow");
				}
			}
		}
		// If stacked and centered, valueClass should handle text-center
		return classes;
	});

	const displayModeEditButtonLayoutClasses = computed(() => {
		if (props.displayArrangement === "stacked") {
			return ["mt-1"]; // Margin top if button is below value
		}
		return ["ml-1"]; // Margin left if button is inline with value
	});

	watch(
		() => props.value,
		(newValue) => {
			if (!props.isEditing) {
				// Only update internalValue if not currently editing this field
				internalValue.value = newValue;
			}
		}
	);
	watch(
		() => props.isEditing,
		(editing) => {
			if (editing) {
				// When starting to edit, ensure internalValue is current
				internalValue.value = props.value;
				nextTick(() => {
					inputRef.value?.focus();
				});
			}
		}
	);

	const updateInternalValue = (val) => {
		internalValue.value = val;
	};

	const emitToggleEdit = () => {
		emit("toggleEdit", props.fieldName);
	};

	const handleContainerClick = () => {
		if (props.editTrigger === "valueClick" && !props.isEditing) {
			emitToggleEdit();
		}
	};

	const onSave = () => {
		// Parent uses `editValues` from its own scope, this component provides the new value
		emit("save", props.fieldName, internalValue.value);
		// Parent will set isEditing to false, which will call the watcher
	};

	const onCancel = () => {
		emit("cancel", props.fieldName);
		// Parent will set isEditing to false
	};
</script>

<style scoped>
	.form-input-editable {
		@apply block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200 text-sm p-1; /* Ensure w-full is effective */
	}
</style>
