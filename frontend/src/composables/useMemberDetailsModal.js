import { ref } from "vue";
import { useAppStore } from "@/store/app";
import { getMemberInfo } from "@/services/familyTreeApi";

export function useMemberDetailsModal() {
	const isVisible = ref(false);
	const member = ref(null);
	const clickPosition = ref({ x: 0, y: 0 });

	// It's okay for UI composables to interact with global stores for things like status updates.
	const appStore = useAppStore();

	async function open(nodeId, clickX, clickY) {
		appStore.updateStatus(`Fetching details for member ${nodeId}...`);
		clickPosition.value = { x: clickX, y: clickY };

		try {
			const memberData = await getMemberInfo(nodeId);

			member.value = memberData;
			isVisible.value = true;
			appStore.updateStatus(
				`Details loaded for ${memberData.name || nodeId}.`,
				3000,
			);
		} catch (error) {
			console.error("Error fetching member details:", error);
			appStore.updateStatus(`Error fetching details: ${error.message}`, 7000);
			member.value = null;
		}
	}

	function close() {
		isVisible.value = false;
		member.value = null;
	}

	return { isVisible, member, clickPosition, open, close };
}
