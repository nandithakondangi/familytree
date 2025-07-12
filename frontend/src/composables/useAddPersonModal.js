import { ref, reactive } from "vue";

export function useAddPersonModal() {
	const isVisible = ref(false);
	const context = reactive({
		sourceNodeId: null,
		sourceMemberName: null,
		relationshipType: null,
	});

	function open(newContext = {}) {
		context.sourceNodeId = newContext.sourceNodeId || null;
		context.sourceMemberName = newContext.sourceMemberName || null;
		context.relationshipType = newContext.relationshipType || null;
		isVisible.value = true;
	}

	function close() {
		isVisible.value = false;
	}

	return { isVisible, context, open, close };
}
