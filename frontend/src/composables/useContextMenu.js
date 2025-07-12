import { ref, watch } from "vue";

export function useContextMenu() {
	const isVisible = ref(false);
	const position = ref({ x: 0, y: 0 });
	const sourceNodeId = ref(null);

	// This ref will be bound to the <ContextMenu> component instance in App.vue
	// so we can detect clicks outside of it.
	const menuRef = ref(null);

	function open(nodeId, x, y) {
		sourceNodeId.value = nodeId;
		position.value = { x, y };
		isVisible.value = true;
	}

	function close() {
		isVisible.value = false;
		sourceNodeId.value = null;
	}

	const handleClickOutside = (event) => {
		// Close the menu if the click is outside of the menu's DOM element.
		// The menu component itself should use `@click.stop` to prevent internal clicks from closing it.
		if (menuRef.value && !menuRef.value.$el.contains(event.target)) {
			close();
		}
	};

	// Watch for visibility changes to add or remove the global click listener.
	// This is more efficient than having a persistent listener.
	watch(isVisible, (isNowVisible) => {
		if (isNowVisible) {
			document.addEventListener("click", handleClickOutside, true);
		} else {
			document.removeEventListener("click", handleClickOutside, true);
		}
	});

	return {
		isVisible,
		position,
		sourceNodeId,
		menuRef, // Expose the ref to be bound in the template
		open,
		close,
	};
}
