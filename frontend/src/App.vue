<template>
	<div
		id="app"
		class="flex flex-col h-screen bg-gray-200 dark:bg-slate-900 font-sans font-light"
	>
		<header
			class="bg-gradient-to-r from-purple-600/80 to-indigo-600/80 dark:from-purple-700/80 dark:to-indigo-700/80 backdrop-blur-md text-white p-4 shadow-lg flex items-center"
		>
			<button
				@click="toggleSidebar"
				class="p-2 rounded-md hover:bg-white/20 dark:hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/50 transition-colors mr-4"
				aria-label="Toggle sidebar"
				:title="isSidebarOpen ? 'Collape Menu' : 'Expand Menu'"
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
						d="M4 6h16M4 12h16M4 18h16"
					/>
				</svg>
			</button>
			<h1
				class="text-2xl font-medium text-center flex-grow ml-[-2.5rem] sm:ml-0"
			>
				Family Tree Viewer
			</h1>
			<button
				@click="toggleTheme"
				class="p-2 rounded-md hover:bg-white/20 dark:hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/50 transition-colors ml-auto"
				aria-label="Toggle theme"
				:title="
					currentTheme === 'dark'
						? 'Switch to light theme'
						: 'Switch to dark theme'
				"
			>
				<svg
					v-if="currentTheme === 'dark'"
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<circle cx="12" cy="12" r="5" />
					<line x1="12" y1="1" x2="12" y2="3" />
					<line x1="12" y1="21" x2="12" y2="23" />
					<line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
					<line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
					<line x1="1" y1="12" x2="3" y2="12" />
					<line x1="21" y1="12" x2="23" y2="12" />
					<line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
					<line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
				</svg>
				<svg
					v-else
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
					/>
				</svg>
			</button>
			<!-- <div class="w-14"></div> Spacer to balance the hamburger button for true title centering -->
		</header>

		<div
			class="flex flex-grow overflow-hidden p-1"
			:class="{
				'blur-sm filter transition-filter duration-300 ease-in-out':
					isAddPersonModalVisible ||
					isConfirmModalVisible ||
					isMemberDetailsModalVisible,
				'filter-none transition-filter duration-300 ease-in-out':
					!isAddPersonModalVisible &&
					!isConfirmModalVisible &&
					!isMemberDetailsModalVisible,
			}"
		>
			<aside
				:class="{
					'w-96 flex-shrink-0 bg-white/30 dark:bg-slate-800/50 backdrop-blur-lg shadow-xl rounded-xl p-4': true,
					'transform transition-transform duration-300 ease-in-out': true, // Animate the slide
					'-translate-x-full': !isSidebarOpen, // Slide out when closed
					'translate-x-0': isSidebarOpen, // Slide in when open
				}"
			>
				<div
					:class="{
						'opacity-0': !isSidebarOpen,
						'opacity-100': isSidebarOpen,
						'transition-opacity duration-300 ease-in-out': true,
						'h-full': true,
					}"
				>
					<Sidebar />
				</div>
			</aside>
			<main
				:class="{
					'flex-grow flex flex-col overflow-hidden p-2': true,
					'transition-all duration-300 ease-in-out': true,
					'ml-0': isSidebarOpen, // No margin needed when sidebar is open and taking its space
					'ml-[-24rem]': !isSidebarOpen, // Pull main content left to cover the space of the hidden sidebar (24rem = w-96)
				}"
			>
				<div
					class="flex-grow bg-white/30 dark:bg-slate-800/50 backdrop-blur-lg shadow-xl rounded-xl overflow-hidden"
				>
					<GraphView @iframe-click="closeContextMenu" />
				</div>
			</main>
		</div>

		<footer
			class="bg-gradient-to-r from-purple-600/60 to-indigo-600/60 dark:from-purple-700/60 dark:to-indigo-700/60 backdrop-blur-md p-2 text-sm text-gray-200 shadow-lg"
		>
			<StatusDisplay />
		</footer>

		<!-- Global Add Person Modal -->
		<AddPersonModal
			:isVisible="isAddPersonModalVisible"
			:isIndianCulture="isIndianCulture"
			:sourceNodeIdForRelationship="addPersonModalSourceNodeId"
			:sourceMemberNameForRelationship="addPersonModalSourceMemberName"
			:relationshipTypeForNewMember="addPersonModalRelationshipType"
			:inferRelationshipsEnabled="inferRelationshipsEnabled"
			@close="closeAddPersonModal"
			@save="handlePersonAdded"
		/>

		<!-- Global Confirmation Modal -->
		<ConfirmationModal
			:isVisible="isConfirmModalVisible"
			:message="confirmModalMessage"
			:title="confirmModalTitle"
			@confirm="handleConfirm"
			@cancel="handleCancelConfirm"
		/>
		<!-- Global Member Details Modal -->
		<MemberDetailsModal
			:isVisible="isMemberDetailsModalVisible"
			:member="currentMemberDetails"
			:clickPosition="clickPositionForModal"
			@close="closeMemberDetailsModal"
			@update-member="handleMemberUpdate"
		/>

		<!-- Global Context Menu -->

		<ContextMenu
			ref="contextMenuComponentRef"
			:isVisible="isContextMenuVisible"
			:position="contextMenuPosition"
			:sourceNodeId="contextMenuSourceNodeId"
			@action="handleContextMenuAction"
		/>

		<!-- Global Link Member Modal -->

		<LinkMemberModal
			:isVisible="isLinkMemberModalVisible"
			:sourceNodeId="linkMemberModalData.sourceNodeId"
			:sourceMemberName="linkMemberModalData.sourceMemberName"
			:relationshipType="linkMemberModalData.relationshipType"
			:potentialTargets="linkMemberModalData.potentialTargets"
			@close="closeLinkMemberModal"
			@link="handleLinkMembers"
		/>
	</div>
</template>

<script>
import Sidebar from "./components/Sidebar.vue";
import GraphView from "./components/GraphView.vue";
import StatusDisplay from "./components/StatusDisplay.vue";
import AddPersonModal from "./components/AddPersonModal.vue"; // Import the modal
import ConfirmationModal from "./components/ConfirmationModal.vue"; // Import the confirmation modal
import MemberDetailsModal from "./components/MemberDetailsModal.vue";
import ContextMenu from "./components/ContextMenu.vue";
import LinkMemberModal from "./components/LinkMemberModal.vue";

export default {
	name: "App",
	components: {
		Sidebar,
		GraphView,
		ConfirmationModal, // Register the confirmation modal
		StatusDisplay,
		AddPersonModal, // Register the modal
		MemberDetailsModal,
		ContextMenu,
		LinkMemberModal,
	},
	// You can add global data or methods here if needed
	data() {
		return {
			// Example: A global status message state
			statusMessage: "Ready.",
			// Example: State for culture setting
			isIndianCulture: true,
			// Example: State for inference setting
			inferRelationshipsEnabled: true,
			// Example: Currently loaded file name
			loadedFileName: null,
			// Example: Flag indicating if data is loaded
			isDataLoaded: false,
			// Example: Member ID for editing
			memberIdToEdit: null,
			// Example: Flag to trigger graph re-render
			triggerGraphRender: false,
			// Controls visibility of AddPersonModal
			isAddPersonModalVisible: false,
			addPersonModalSourceNodeId: null, // For adding via context menu
			addPersonModalSourceMemberName: null, // For adding via context menu
			addPersonModalRelationshipType: null, // For adding via context menu
			// Controls visibility of the main sidebar
			isSidebarOpen: true, // Sidebar starts open by default
			// Theme state
			currentTheme: "light", // 'light' or 'dark'
			// Confirmation Modal State
			isConfirmModalVisible: false,
			confirmModalMessage: "",
			confirmModalTitle: "Confirm Action", // Default title
			confirmModalOnConfirm: null,
			confirmModalOnCancel: null,
			// Member Details Modal State
			isMemberDetailsModalVisible: false,
			currentMemberDetails: null,
			clickPositionForModal: { x: 0, y: 0 },
			// Context Menu State
			isContextMenuVisible: false,
			contextMenuPosition: { x: 0, y: 0 },
			contextMenuSourceNodeId: null,
			// Link Member Modal State
			isLinkMemberModalVisible: false,
			linkMemberModalData: {
				sourceNodeId: null,
				sourceMemberName: "", // Will need to fetch this
				relationshipType: null,
				potentialTargets: [], // [{id: '...', name: '...'}]
			},
		};
	},
	provide() {
		// Provide reactive data and methods to descendant components
		return {
			// State
			statusMessage: () => this.statusMessage,
			isIndianCulture: () => this.isIndianCulture,
			inferRelationshipsEnabled: () => this.inferRelationshipsEnabled,
			loadedFileName: () => this.loadedFileName,
			isDataLoaded: () => this.isDataLoaded,
			memberIdToEdit: () => this.memberIdToEdit,
			triggerGraphRender: () => this.triggerGraphRender,
			currentTheme: () => this.currentTheme, // Add this line

			// Methods to update state (these would often trigger backend calls)
			updateStatus: this.updateStatus,
			updateCultureSetting: this.updateCultureSetting,
			updateInferRelationshipsSetting: this.updateInferRelationshipsSetting,
			setLoadedFileName: this.setLoadedFileName,
			setDataLoaded: this.setDataLoaded,
			setMemberIdToEdit: this.setMemberIdToEdit,
			triggerReRender: this.triggerReRender,
			// Placeholder for opening dialogs (handled by parent App or global state)
			openAddPersonDialog: this.openAddPersonDialog,
			openEditPersonDialog: this.openEditPersonDialog,
			showNodeContextMenu: this.showNodeContextMenu, // For right-click
			handleDeleteMember: this.handleDeleteMember, // For delete action
			handleNodeSingleClick: this.handleNodeSingleClick, // For single-click action
			handleConnectToExisting: this.handleConnectToExisting, // For connect action
			openConfirmModal: this.openConfirmModal, // Provide confirmation modal opener
			handleAddRelationship: this.handleAddRelationship, // Add this line
		};
	},
	created() {
		// Load theme from localStorage or default to 'light'
		const savedTheme = localStorage.getItem("theme");
		if (savedTheme) {
			// TODO: Add listener for clicks outside context menu to close it
			this.currentTheme = savedTheme;
		}
		this.applyTheme();
	},
	watch: {
		currentTheme() {
			this.applyTheme();
		},
		isContextMenuVisible(isVisible) {
			if (isVisible) {
				document.addEventListener(
					"click",
					this.handleClickOutsideContextMenu,
					true,
				);
			} else {
				document.removeEventListener(
					"click",
					this.handleClickOutsideContextMenu,
					true,
				);
			}
		},
	},
	methods: {
		// Method to update the status message
		updateStatus(message, timeout = 5000) {
			this.statusMessage = message;
			if (timeout > 0) {
				setTimeout(() => {
					this.statusMessage = "";
				}, timeout);
			}
		},
		// Method to update the culture setting
		updateCultureSetting(isChecked) {
			this.isIndianCulture = isChecked;
			console.log("Culture setting updated:", this.isIndianCulture);
		},
		// Method to update the inference setting
		updateInferRelationshipsSetting(isChecked) {
			this.inferRelationshipsEnabled = isChecked;
			console.log("Inference setting updated:", this.inferRelationshipsEnabled);
		},
		// Method to set the loaded file name
		setLoadedFileName(fileName) {
			this.loadedFileName = fileName;
		},
		// Method to set the data loaded state
		setDataLoaded(isLoaded) {
			this.isDataLoaded = isLoaded;
		},
		// Method to set the member ID for editing (triggers dialog in a real app)
		setMemberIdToEdit(memberId) {
			this.memberIdToEdit = memberId;
			if (memberId) {
				// In a real app, this would trigger a modal/dialog component
				console.log("Triggering Edit Person dialog for ID:", memberId);
				// TODO: Implement modal/dialog handling here or in a dedicated component
				// For now, just log and clear after a delay
				setTimeout(() => {
					this.memberIdToEdit = null;
				}, 100); // Clear the ID after a short delay
			}
		},
		// Method to trigger graph re-render
		triggerReRender() {
			this.triggerGraphRender = !this.triggerGraphRender; // Toggle to trigger watch in GraphView
			console.log("Re-render triggered");
			// TODO: Call backend API to re-generate graph HTML
		},
		toggleSidebar() {
			this.isSidebarOpen = !this.isSidebarOpen;
		},
		toggleTheme() {
			this.currentTheme = this.currentTheme === "light" ? "dark" : "light";
			localStorage.setItem("theme", this.currentTheme);
		},
		applyTheme() {
			if (this.currentTheme === "dark") {
				document.documentElement.classList.add("dark");
			} else {
				document.documentElement.classList.remove("dark");
			}
		},

		// Placeholder methods for dialogs and context menu actions
		openAddPersonDialog() {
			console.log("Triggering Add New Person dialog");
			this.addPersonModalSourceNodeId = null; // Reset context
			this.addPersonModalSourceMemberName = null; // Reset context
			this.addPersonModalRelationshipType = null; // Reset context
			this.isAddPersonModalVisible = true;
		},
		closeAddPersonModal() {
			this.isAddPersonModalVisible = false;
			this.addPersonModalSourceMemberName = null;
			this.addPersonModalSourceNodeId = null;
			this.addPersonModalRelationshipType = null;
		},
		handlePersonAdded() {
			this.closeAddPersonModal();
			this.triggerReRender();
			this.setDataLoaded(true);
		},
		openEditPersonDialog(memberId) {
			console.log("Triggering Edit Person dialog for ID:", memberId);
			this.closeContextMenu();
			// TODO: Implement modal/dialog for editing a person
		},
		showNodeContextMenu(nodeId, screenX, screenY) {
			console.log(
				`Showing context menu for node ${nodeId} at (${screenX}, ${screenY})`,
			);
			this.contextMenuSourceNodeId = nodeId;
			this.contextMenuPosition = { x: screenX, y: screenY };
			this.isContextMenuVisible = true;
		},
		closeContextMenu() {
			this.isContextMenuVisible = false;
			this.contextMenuSourceNodeId = null;
		},
		handleAddRelationship(originNodeId, relationshipType) {
			console.log(
				`Attempting to add ${relationshipType} for node ${originNodeId}`,
			);
			// TODO: Call backend API to add a new person and establish relationship
			// After successful backend call, trigger re-render
			// this.triggerReRender();
		},
		handleConnectToExisting(originNodeId, connectionType) {
			console.log(
				`Attempting to connect ${originNodeId} via ${connectionType} to an existing member`,
			);
			// TODO: Implement logic to select an existing member (e.g., using a modal with a list)
			// After selecting, call backend API to establish relationship
			// After successful backend call, trigger re-render
			+this.closeContextMenu();
			// this.triggerReRender();
		},
		handleDeleteMember(memberIdToDelete) {
			console.log(`Attempting to delete member with ID: ${memberIdToDelete}`);
			// TODO: Implement confirmation dialog
			// If confirmed, call backend API to delete member
			// After successful backend call, trigger re-render
			// this.triggerReRender();
			+this.closeContextMenu();
		},
		async handleNodeSingleClick(nodeId, clickX, clickY) {
			this.updateStatus(`Fetching details for member ${nodeId}...`);
			this.clickPositionForModal = { x: clickX, y: clickY };
			+this.closeContextMenu();
			try {
				const response = await fetch(`/api/v1/graph/member_info/${nodeId}`);
				if (!response.ok) {
					const errText = await response.text();
					throw new Error(
						errText || `Failed to fetch member details: ${response.status}`,
					);
				}
				const memberResponse = await response.json();
				const memberData = memberResponse.member_info;
				console.log(`Fetched member details for ${nodeId}:`, memberData);

				// The backend sends protobuf JSON, ensure it's in a good state for the modal
				// e.g., nicknamesList to nicknames
				if (memberData.nicknamesList) {
					memberData.nicknames = memberData.nicknamesList;
					delete memberData.nicknamesList;
				}
				// additionalInfoMap to additionalInfo
				if (memberData.additionalInfoMap) {
					memberData.additionalInfo = Object.fromEntries(
						memberData.additionalInfoMap,
					);
					delete memberData.additionalInfoMap;
				}

				this.currentMemberDetails = memberData;
				this.isMemberDetailsModalVisible = true;
				this.updateStatus(
					`Details loaded for ${memberData.name || nodeId}.`,
					3000,
				);
			} catch (error) {
				console.error("Error fetching member details:", error);
				this.updateStatus(`Error fetching details: ${error.message}`, 7000);
				this.currentMemberDetails = null;
			}
		},

		// Confirmation Modal Methods
		openConfirmModal(message, title = "Confirm Action") {
			return new Promise((resolve) => {
				+this.closeContextMenu(); // Close context menu if open
				this.confirmModalMessage = message;
				this.isConfirmModalVisible = true;
				this.confirmModalTitle = title;
				this.confirmModalOnConfirm = () => resolve(true);
				this.confirmModalOnCancel = () => resolve(false);
			});
		},
		handleConfirm() {
			this.isConfirmModalVisible = false;
			if (this.confirmModalOnConfirm) this.confirmModalOnConfirm();
		},
		handleCancelConfirm() {
			this.isConfirmModalVisible = false;
			if (this.confirmModalOnCancel) this.confirmModalOnCancel();
		},

		// Member Details Modal Methods
		closeMemberDetailsModal() {
			this.isMemberDetailsModalVisible = false;
			this.currentMemberDetails = null;
		},
		async handleMemberUpdate(updatedMemberData) {
			this.updateStatus(`Updating ${updatedMemberData.name}...`);
			try {
				// TODO: Implement backend API call to update member
				// Ensure updatedMemberData is in the format your backend expects (protobuf JSON)
				const response = await fetch(`/api/v1/member/${updatedMemberData.id}`, {
					// Assuming ID is present
					method: "PUT", // or PATCH
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(updatedMemberData),
				});

				if (!response.ok) {
					const errText = await response.text();
					throw new Error(
						errText || `Failed to update member: ${response.status}`,
					);
				}
				this.updateStatus(
					`${updatedMemberData.name} updated successfully!`,
					5000,
				);
				this.closeMemberDetailsModal();
				this.triggerReRender(); // Re-render graph if needed
			} catch (error) {
				console.error("Error updating member:", error);
				this.updateStatus(`Error updating member: ${error.message}`, 7000);
				// Optionally, keep modal open or handle error state
			}
		},

		// Context Menu Action Handler
		async handleContextMenuAction(action) {
			const { actionType, relationshipType } = action;
			const sourceNodeId = this.contextMenuSourceNodeId;
			this.closeContextMenu();

			if (!sourceNodeId) {
				console.error("Source node ID not available for context menu action.");
				this.updateStatus("Error: Source node ID missing.", 5000);
				return;
			}

			if (actionType === "add-member") {
				// Fetch source member's name to display in the AddPersonModal
				try {
					const response = await fetch(
						`/api/v1/graph/member_info/${sourceNodeId}`,
					);
					if (!response.ok) {
						const errText = await response.text();
						throw new Error(
							errText ||
								`Failed to fetch source member details: ${response.status}`,
						);
					}
					const memberResponse = await response.json();
					const sourceMemberName =
						memberResponse.member_info?.name || `ID: ${sourceNodeId}`;

					this.addPersonModalSourceNodeId = sourceNodeId;
					this.addPersonModalSourceMemberName = sourceMemberName;
					this.addPersonModalRelationshipType = relationshipType;
					this.isAddPersonModalVisible = true;
				} catch (error) {
					console.error(
						"Error fetching source member name for AddPersonModal:",
						error,
					);
					this.updateStatus(
						`Error: Could not get source member's name. ${error.message}`,
						7000,
					);
					// Optionally, still open the modal but without the name, or prevent opening.
				}
			} else if (actionType === "link-member") {
				this.updateStatus("Fetching member list for linking...");
				try {
					// Fetch all member summaries
					const response = await fetch("/api/v1/graph/all_member_summaries");
					if (!response.ok) {
						const errText = await response.text();
						throw new Error(
							errText || `Failed to fetch member list: ${response.status}`,
						);
					}
					const allMembers = await response.json(); // Expected: [{id: "...", name: "..."}, ...]

					const sourceMember = allMembers.find((m) => m.id === sourceNodeId);
					const sourceMemberName = sourceMember
						? sourceMember.name
						: `ID: ${sourceNodeId}`;

					// Filter out the source member from potential targets
					const potentialTargets = allMembers.filter(
						(member) => member.id !== sourceNodeId,
					);

					if (potentialTargets.length === 0) {
						this.updateStatus("No other members available to link.", 5000);
						return;
					}

					this.linkMemberModalData = {
						sourceNodeId,
						sourceMemberName,
						relationshipType,
						potentialTargets,
					};
					this.isLinkMemberModalVisible = true;
					this.updateStatus("Member list loaded. Select target member.", 3000);
				} catch (error) {
					console.error("Error preparing for link member:", error);
					this.updateStatus(`Error: ${error.message}`, 7000);
				}
			}
		},

		// Link Member Modal Methods
		closeLinkMemberModal() {
			this.isLinkMemberModalVisible = false;
			this.linkMemberModalData = {
				sourceNodeId: null,
				sourceMemberName: "",
				relationshipType: null,
				potentialTargets: [],
			};
		},

		async handleLinkMembers(linkData) {
			// linkData: { sourceNodeId, relationshipType, targetMemberId }
			this.updateStatus(
				`Linking ${linkData.sourceNodeId} and ${linkData.targetMemberId} as ${linkData.relationshipType}...`,
			);
			try {
				const response = await fetch("/api/v1/manage/link_members", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(linkData),
				});
				if (!response.ok) {
					const errText = await response.text();
					throw new Error(
						errText || `Failed to link members: ${response.status}`,
					);
				}
				const result = await response.json();
				this.updateStatus(
					result.message || "Members linked successfully!",
					5000,
				);
				this.closeLinkMemberModal();
				this.triggerReRender();
			} catch (error) {
				console.error("Error linking members:", error);
				this.updateStatus(`Error linking members: ${error.message}`, 7000);
			}
		},
		handleClickOutsideContextMenu(event) {
			// This method is called when `isContextMenuVisible` is true.
			// We need to ensure the click is not on the context menu itself.
			// A simple way is to check if the event path includes an element with a specific class/id of the context menu.
			// The ContextMenu component itself has @click.stop to prevent its own clicks from closing it.
			if (
				this.$refs.contextMenuComponentRef &&
				this.$refs.contextMenuComponentRef.$el &&
				!this.$refs.contextMenuComponentRef.$el.contains(event.target)
			) {
				this.closeContextMenu();
			} else if (
				this.isContextMenuVisible &&
				!this.$refs.contextMenuComponentRef?.$el?.contains(event.target)
			) {
				// Fallback if ref is somehow not resolved but menu is visible
				this.closeContextMenu();
			}
		},
	},
};
</script>

<style>
/* Basic styling for the app */
body {
	/* Ensure body also gets the base font if #app doesn't cover everything initially */
	font-family: "Quicksand", sans-serif;
}

/* Custom Scrollbar Styles for Webkit-based browsers */
::-webkit-scrollbar {
	width: 8px; /* Width of the vertical scrollbar */
	height: 8px; /* Height of the horizontal scrollbar */
}

::-webkit-scrollbar-track {
	background: transparent; /* Make the track invisible */
}

::-webkit-scrollbar-thumb {
	background-color: rgba(
		100,
		116,
		139,
		0.5
	); /* Neutral semi-transparent color (slate-500 @ 50%) */
	border-radius: 10px; /* Rounded corners for the thumb */
	border: 1px solid rgba(255, 255, 255, 0.1); /* Subtle light border for a glassy edge */
}

::-webkit-scrollbar-thumb:hover {
	background-color: rgba(100, 116, 139, 0.7); /* Darken/intensify on hover */
}

/* Dark mode specific scrollbar thumb for Webkit */
.dark ::-webkit-scrollbar-thumb {
	background-color: rgba(
		148,
		163,
		184,
		0.4
	); /* Lighter semi-transparent color for dark mode (slate-400 @ 40%) */
	border: 1px solid rgba(0, 0, 0, 0.1); /* Subtle dark border */
}

.dark ::-webkit-scrollbar-thumb:hover {
	background-color: rgba(148, 163, 184, 0.6); /* Lighten/intensify on hover */
}

/* Basic Firefox Scrollbar Styling (less customizable for "glassy" but improves consistency) */
* {
	scrollbar-width: thin; /* Makes scrollbar thinner */
	scrollbar-color: rgba(100, 116, 139, 0.5) transparent; /* thumb color, track color (transparent) */
}

.dark * {
	scrollbar-color: rgba(148, 163, 184, 0.4) transparent; /* thumb color for dark mode, track color (transparent) */
}
</style>
