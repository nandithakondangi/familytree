import { ref, reactive } from "vue";
import { useAppStore } from "@/store/app";
import { getAllMemberSummaries, linkMembers } from "@/services/familyTreeApi";

export function useLinkMemberModal() {
	const isVisible = ref(false);
	const data = reactive({
		sourceNodeId: null,
		sourceMemberName: "",
		relationshipType: null,
		potentialTargets: [],
	});

	const appStore = useAppStore();

	async function open(context) {
		// context: { sourceNodeId, relationshipType }
		appStore.updateStatus("Fetching member list for linking...");
		try {
			const allMembers = await getAllMemberSummaries();

			const sourceMember = allMembers.find(
				(m) => m.id === context.sourceNodeId,
			);
			const sourceMemberName = sourceMember
				? sourceMember.name
				: `ID: ${context.sourceNodeId}`;

			// Filter out the source member from potential targets
			const potentialTargets = allMembers.filter(
				(member) => member.id !== context.sourceNodeId,
			);

			if (potentialTargets.length === 0) {
				appStore.updateStatus("No other members available to link.", 5000);
				return;
			}

			data.sourceNodeId = context.sourceNodeId;
			data.sourceMemberName = sourceMemberName;
			data.relationshipType = context.relationshipType;
			data.potentialTargets = potentialTargets;

			isVisible.value = true;
			appStore.updateStatus("Member list loaded. Select target member.", 3000);
		} catch (error) {
			console.error("Error preparing for link member:", error);
			appStore.updateStatus(`Error: ${error.message}`, 7000);
		}
	}

	function close() {
		isVisible.value = false;
		// Reset data
		Object.assign(data, {
			sourceNodeId: null,
			sourceMemberName: "",
			relationshipType: null,
			potentialTargets: [],
		});
	}

	async function handleLinkMembers(linkData) {
		// linkData: { sourceNodeId, relationshipType, targetMemberId }
		appStore.updateStatus(
			`Linking ${linkData.sourceNodeId} and ${linkData.targetMemberId} as ${linkData.relationshipType}...`,
		);
		try {
			const result = await linkMembers(linkData);
			appStore.updateStatus(
				result.message || "Members linked successfully!",
				5000,
			);
			close(); // Use the composable's close function
			appStore.triggerReRender();
		} catch (error) {
			console.error("Error linking members:", error);
			appStore.updateStatus(`Error linking members: ${error.message}`, 7000);
		}
	}

	return {
		isVisible,
		data,
		open,
		close,
		handleLinkMembers,
	};
}
