import { useTreeStore } from "@/store/tree";

/**
 * This service centralizes all API calls to the backend.
 */

/**
 * Fetches and processes member information from the API.
 * @param {string} nodeId The ID of the member to fetch.
 * @returns {Promise<object>} A promise that resolves to the member's data.
 * @throws {Error} If the API call fails.
 */
export async function getMemberInfo(nodeId) {
	const response = await fetch(`/api/v1/graph/member_info/${nodeId}`);
	if (!response.ok) {
		const errText = await response.text();
		throw new Error(
			errText || `Failed to fetch member details: ${response.status}`,
		);
	}
	const memberResponse = await response.json();
	const memberData = memberResponse.member_info;

	// The backend sends protobuf JSON, so we clean it up here.
	// This transformation logic belongs with the data-fetching layer.
	if (memberData.nicknamesList) {
		memberData.nicknames = memberData.nicknamesList;
		delete memberData.nicknamesList;
	}
	if (memberData.additionalInfoMap) {
		memberData.additionalInfo = Object.fromEntries(
			memberData.additionalInfoMap,
		);
		delete memberData.additionalInfoMap;
	}

	return memberData;
}

/**
 * Fetches a list of all member summaries (id, name).
 * @returns {Promise<Array<{id: string, name: string}>>} A promise that resolves to an array of member summaries.
 */
export async function getAllMemberSummaries() {
	const response = await fetch("/api/v1/graph/all_member_summaries");
	if (!response.ok) {
		const errText = await response.text();
		throw new Error(
			errText || `Failed to fetch member list: ${response.status}`,
		);
	}
	return await response.json();
}

/**
 * Creates a relationship link between two existing members.
 * @param {object} linkData - The data for linking members.
 * @param {string} linkData.sourceNodeId
 * @param {string} linkData.relationshipType
 * @param {string} linkData.targetMemberId
 * @returns {Promise<object>} The result from the API.
 */
export async function linkMembers(linkData) {
	const response = await fetch("/api/v1/manage/link_members", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(linkData),
	});
	if (!response.ok) {
		const errText = await response.text();
		throw new Error(errText || `Failed to link members: ${response.status}`);
	}
	const result = await response.json();

	// After a successful link, trigger a graph re-render
	const treeStore = useTreeStore();
	treeStore.triggerReRender();

	return result;
}
