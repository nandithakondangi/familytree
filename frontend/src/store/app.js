import { defineStore } from "pinia";
import { ref, watch, onMounted } from "vue";
import { useTreeStore } from "./tree";

export const useAppStore = defineStore("app", () => {
	// --- State ---
	const statusMessage = ref("Ready.");
	const isSidebarOpen = ref(true);
	const currentTheme = ref("light");

	// Settings
	const settings = ref({
		isIndianCulture: true,
		inferRelationships: true,
	});

	// --- Actions ---

	// General UI Actions
	function updateStatus(message, timeout = 5000) {
		statusMessage.value = message;
		if (timeout > 0) {
			setTimeout(() => {
				if (statusMessage.value === message) {
					statusMessage.value = "";
				}
			}, timeout);
		}
	}

	function toggleSidebar() {
		isSidebarOpen.value = !isSidebarOpen.value;
	}

	// Settings Actions
	function updateCultureSetting(isChecked) {
		settings.value.isIndianCulture = isChecked;
	}

	function updateInferRelationshipsSetting(isChecked) {
		settings.value.inferRelationships = isChecked;
	}

	// Theme Management
	function applyTheme() {
		if (currentTheme.value === "dark") {
			document.documentElement.classList.add("dark");
		} else {
			document.documentElement.classList.remove("dark");
		}
	}

	function toggleTheme() {
		currentTheme.value = currentTheme.value === "light" ? "dark" : "light";
		localStorage.setItem("theme", currentTheme.value);
	}

	// --- Watchers and Lifecycle ---
	onMounted(() => {
		const savedTheme = localStorage.getItem("theme");
		if (savedTheme) {
			currentTheme.value = savedTheme;
		}
		applyTheme();
	});

	watch(currentTheme, () => {
		applyTheme();
		const treeStore = useTreeStore();
		if (treeStore.isDataLoaded) {
			treeStore.triggerReRender();
		}
	});

	return {
		// State
		statusMessage,
		isSidebarOpen,
		currentTheme,
		settings,
		// Actions
		updateStatus,
		toggleSidebar,
		updateCultureSetting,
		updateInferRelationshipsSetting,
		toggleTheme,
	};
});
