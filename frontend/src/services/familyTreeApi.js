import { useTreeStore } from "@/store/tree";

/**
 * This service centralizes all API calls to the backend.
 */

/**
 * Generic function to fetch a blob from a given URL.
 * @param {string} url - The URL to fetch from.
 * @param {string} operationName - A descriptive name for the operation, used in error messages.
 * @returns {Promise<Blob>} A promise that resolves to a Blob.
 * @throws {Error} If the fetch operation fails.
 */
export async function fetchBlob(url, operationName = "Data fetch") {
    const response = await fetch(url);
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
            `${operationName} failed: ${response.status} ${errorText || response.statusText}`
        );
    }
    return response.blob();
}

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

/**
 * Adds a new family member to the tree.
 * @param {object} memberData - The data for the new family member.
 * @returns {Promise<object>} A promise that resolves to the API response data.
 * @throws {Error} If the API call fails.
 */
export async function addFamilyMember(memberData) {
    const response = await fetch("/api/v1/manage/add_family_member", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(memberData),
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(
            errorBody.detail || `Server error: ${response.status} ${response.statusText}`
        );
    }
    return response.json();
}

/**
 * Sends a message to the chatbot API.
 * @param {string} message - The user's message.
 * @returns {Promise<object>} A promise that resolves to the chatbot's reply.
 * @throws {Error} If the API call fails.
 */
export async function sendMessageToChatbot(message) {
    const response = await fetch('/api/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    });

    if (!response.ok) {
        throw new Error('Chatbot API failed.');
    }
    return response.json();
}

/**
 * Fetches the HTML content for rendering the family tree graph.
 * @param {string} theme - The current theme (e.g., 'dark', 'light').
 * @param {string} [poiId] - Optional: The ID of the Point of Interest node to center the graph around.
 * @returns {Promise<string>} A promise that resolves to the graph HTML string.
 * @throws {Error} If the API call fails.
 */
export async function fetchGraphHtml(theme, poiId) {
    const params = new URLSearchParams();
    if (theme) {
        params.append('theme', theme);
    }
    if (poiId) {
        params.append('poi', poiId);
    }
    const queryString = params.toString();
    const url = `/api/v1/graph/render${queryString ? `?${queryString}` : ''}`;
    const response = await fetch(url);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            errorData.detail || `Server error: ${response.status} ${response.statusText}`
        );
    }
    const data = await response.json();
    return data;
}

/**
 * Fetches the JavaScript content for graph interaction.
 * @returns {Promise<string>} A promise that resolves to the script content.
 * @throws {Error} If the fetch fails.
 */
export async function fetchGraphInteractionScript() {
    const response = await fetch("/scripts/pyvis_interaction_script.js");
    if (!response.ok) {
        throw new Error(
            `Failed to fetch interaction script: ${response.status} ${response.statusText}`
        );
    }
    return response.text();
}

/**
 * Creates a new empty family tree on the backend.
 * @returns {Promise<object>} A promise that resolves to the API response data.
 * @throws {Error} If the API call fails.
 */
export async function createNewFamilyTree() {
    const response = await fetch("/api/v1/manage/create_family", { method: "POST" });
    if (!response.ok) {
        throw new Error(
            `Server error: ${response.status} ${response.statusText}`
        );
    }
    return response.json();
}

/**
 * Loads a family tree from provided content.
 * @param {string} filename - The name of the file being loaded.
 * @param {string} content - The content of the family tree file.
 * @returns {Promise<object>} A promise that resolves to the API response data.
 * @throws {Error} If the API call fails.
 */
export async function loadFamilyTree(filename, content) {
    const response = await fetch("/api/v1/manage/load_family", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, content }),
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(
            `Server error: ${response.status} ${text || response.statusText}`
        );
    }
    return response.json();
}

/**
 * Saves the current family tree data.
 * @returns {Promise<Blob>} A promise that resolves to a Blob containing the family tree data.
 * @throws {Error} If the API call fails.
 */
export async function saveFamilyTree() {
    return fetchBlob("/api/v1/manage/save_family", "Data export for save");
}

/**
 * Exports a snapshot of the current family tree data.
 * @returns {Promise<Blob>} A promise that resolves to a Blob containing the family tree snapshot.
 * @throws {Error} If the API call fails.
 */
export async function exportFamilyTreeSnapshot() {
    return fetchBlob("/api/v1/manage/export_family_snapshot", "Data snapshot export");
}

/**
 * Exports the interactive graph HTML.
 * @returns {Promise<Blob>} A promise that resolves to a Blob containing the interactive graph HTML.
 * @throws {Error} If the API call fails.
 */
export async function exportInteractiveGraph() {
    return fetchBlob("/api/v1/manage/export_interactive_graph", "Interactive graph export");
}

/**
 * Updates an existing family member's information.
 * @param {string} memberId - The ID of the member to update.
 * @param {object} updatedData - The updated member data.
 * @returns {Promise<object>} A promise that resolves to the API response data.
 * @throws {Error} If the API call fails.
 */
export async function updateMember(memberId, updatedData) {
    const response = await fetch(`/api/v1/manage/update_member/${memberId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedData),
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(
            errorBody.detail || `Server error: ${response.status} ${response.statusText}`
        );
    }
    return response.json();
}