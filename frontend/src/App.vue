<template>
  <div id="app" class="flex flex-col h-screen bg-gray-200 font-sans font-light">
    <header class="bg-gradient-to-r from-purple-600/80 to-indigo-600/80 backdrop-blur-md text-white p-4 shadow-lg flex items-center">
      <button
        @click="toggleSidebar"
        class="p-2 rounded-md hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/50 transition-colors mr-4"
        aria-label="Toggle sidebar"
      >
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <h1 class="text-2xl font-medium text-center flex-grow">Family Tree Viewer</h1>
      <div class="w-14"></div> <!-- Spacer to balance the hamburger button for true title centering -->
    </header>

    <div class="flex flex-grow overflow-hidden p-1">
      <aside
        :class="{
          'w-96 flex-shrink-0 bg-white/30 backdrop-blur-lg shadow-xl rounded-xl p-4 overflow-y-auto': true, // Always has its width and padding
          'transform transition-transform duration-300 ease-in-out': true, // Animate the slide
          '-translate-x-full': !isSidebarOpen, // Slide out when closed
          'translate-x-0': isSidebarOpen,      // Slide in when open
        }"
      >
        <div :class="{'opacity-0': !isSidebarOpen, 'opacity-100': isSidebarOpen, 'transition-opacity duration-300 ease-in-out': true }">
          <Sidebar />
        </div>
      </aside>
      <main
        :class="{
          'flex-grow flex flex-col overflow-hidden p-2': true,
          'transition-all duration-300 ease-in-out': true,
          'ml-0': isSidebarOpen,      // No margin needed when sidebar is open and taking its space
          'ml-[-24rem]': !isSidebarOpen, // Pull main content left to cover the space of the hidden sidebar (24rem = w-96)
        }"
      >
        <div class="flex-grow bg-white/30 backdrop-blur-lg shadow-xl rounded-xl overflow-hidden">
          <GraphView />
        </div>

      </main>
    </div>

    <footer class="bg-gradient-to-r from-purple-600/60 to-indigo-600/60 backdrop-blur-md p-2 text-sm text-gray-200 shadow-lg">
      <StatusDisplay />
    </footer>

    <!-- Global Add Person Modal -->
    <AddPersonModal
      :isVisible="isAddPersonModalVisible"
      @close="closeAddPersonModal"
      @save="handlePersonAdded"
    />
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue';
import GraphView from './components/GraphView.vue';
import StatusDisplay from './components/StatusDisplay.vue';
import AddPersonModal from './components/AddPersonModal.vue'; // Import the modal

export default {
  name: 'App',
  components: {
    Sidebar,
    GraphView,
    StatusDisplay,
    AddPersonModal, // Register the modal
  },
  // You can add global data or methods here if needed
  data() {
    return {
      // Example: A global status message state
      statusMessage: 'Ready.',
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
      // Controls visibility of the main sidebar
      isSidebarOpen: true, // Sidebar starts open by default
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
      handleConnectToExisting: this.handleConnectToExisting, // For connect action
    };
  },
  methods: {
    // Method to update the status message
    updateStatus(message, timeout = 5000) {
      this.statusMessage = message;
      if (timeout > 0) {
        setTimeout(() => {
          this.statusMessage = '';
        }, timeout);
      }
    },
    // Method to update the culture setting (would likely call backend)
    updateCultureSetting(isChecked) {
      this.isIndianCulture = isChecked;
      console.log('Culture setting updated:', this.isIndianCulture);
      // TODO: Call backend API to update culture setting
    },
    // Method to update the inference setting (would likely call backend)
    updateInferRelationshipsSetting(isChecked) {
      this.inferRelationshipsEnabled = isChecked;
      console.log('Inference setting updated:', this.inferRelationshipsEnabled);
      // TODO: Call backend API to update inference setting
    },
    // Method to set the loaded file name
    setLoadedFileName(fileName) {
      this.loadedFileName = fileName;
    },
    // Method to set the data loaded state
    setDataLoaded(isLoaded) {
      this.isDataLoaded = isLoaded;
      // Update button states based on data loaded state if needed
    },
    // Method to set the member ID for editing (triggers dialog in a real app)
    setMemberIdToEdit(memberId) {
      this.memberIdToEdit = memberId;
      if (memberId) {
        // In a real app, this would trigger a modal/dialog component
        console.log('Triggering Edit Person dialog for ID:', memberId);
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
      console.log('Re-render triggered');
      // TODO: Call backend API to re-generate graph HTML
    },
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },

    // Placeholder methods for dialogs and context menu actions
    openAddPersonDialog() {
      console.log('Triggering Add New Person dialog');
      this.isAddPersonModalVisible = true;
    },
    closeAddPersonModal() {
      this.isAddPersonModalVisible = false;
    },
    handlePersonAdded(newPersonData) {
      console.log('[App.vue] Person added from modal:', newPersonData);
      this.closeAddPersonModal();
      this.updateStatus('Person added successfully!', 5000);
      this.triggerReRender();
    },
    openEditPersonDialog(memberId) {
      console.log('Triggering Edit Person dialog for ID:', memberId);
      // TODO: Implement modal/dialog for editing a person
    },
    showNodeContextMenu(nodeId, x, y) {
      console.log(`Showing context menu for node ${nodeId} at (${x}, ${y})`);
      // TODO: Implement context menu display (e.g., using a custom component or library)
      // The menu options would then call handleAddRelationship or handleDeleteMember
    },
    handleAddRelationship(originNodeId, relationshipType) {
      console.log(`Attempting to add ${relationshipType} for node ${originNodeId}`);
      // TODO: Call backend API to add a new person and establish relationship
      // After successful backend call, trigger re-render
      // this.triggerReRender();
    },
    handleConnectToExisting(originNodeId, connectionType) {
      console.log(`Attempting to connect ${originNodeId} via ${connectionType} to an existing member`);
      // TODO: Implement logic to select an existing member (e.g., using a modal with a list)
      // After selecting, call backend API to establish relationship
      // After successful backend call, trigger re-render
      // this.triggerReRender();
    },
    handleDeleteMember(memberIdToDelete) {
      console.log(`Attempting to delete member with ID: ${memberIdToDelete}`);
      // TODO: Implement confirmation dialog
      // If confirmed, call backend API to delete member
      // After successful backend call, trigger re-render
      // this.triggerReRender();
    },
  },
};
</script>

<style>
/* Basic styling for the app */
body { /* Ensure body also gets the base font if #app doesn't cover everything initially */
  font-family: 'Quicksand', sans-serif;
}
</style>
