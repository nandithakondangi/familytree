import { ref, reactive } from "vue";

export function useConfirmModal() {
	const isVisible = ref(false);
	const state = reactive({
		message: "",
		title: "Confirm Action",
		resolve: null,
	});

	function open(message, title = "Confirm Action") {
		return new Promise((resolvePromise) => {
			state.message = message;
			state.title = title;
			state.resolve = resolvePromise; // Store the resolver
			isVisible.value = true;
		});
	}

	function confirm() {
		isVisible.value = false;
		if (state.resolve) state.resolve(true);
	}

	function cancel() {
		isVisible.value = false;
		if (state.resolve) state.resolve(false);
	}

	return { isVisible, state, open, confirm, cancel };
}
