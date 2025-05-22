<template>
  <div class="flex flex-col h-full p-1">
    <div class="flex-grow space-y-4">
      <div class="flex items-center">
        <label for="indian-culture-toggle" class="inline-flex items-center cursor-pointer">
          <input 
            id="indian-culture-toggle"
            type="checkbox" 
            v-model="isIndianCultureModel" 
            @change="updateCulture" 
            class="sr-only peer"
          >
          <div class="relative w-9 h-5 bg-white/50 backdrop-blur-sm rounded-full peer peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-inset peer-focus:ring-indigo-500 dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300/70 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-500/90 shadow"></div>
          <span class="ml-3 text-sm font-medium text-gray-700">Culture: Indian</span>
        </label>
        <span class="tooltip-icon ml-2 text-gray-400 text-xs cursor-help" title="Enable to show fields for traditional Indian dates (Tamil Month/Star/Paksham/Thithi).">?</span>
      </div>

      <div class="flex items-center">
        <label for="infer-relationships-toggle" class="inline-flex items-center cursor-pointer">
          <input 
            id="infer-relationships-toggle"
            type="checkbox" 
            v-model="inferRelationshipsEnabledModel" 
            @change="updateInferRelationships" 
            class="sr-only peer"
          >
          <div class="relative w-9 h-5 bg-white/50 backdrop-blur-sm rounded-full peer peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-inset peer-focus:ring-indigo-500 dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300/70 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-500/90 shadow"></div>
          <span class="ml-3 text-sm font-medium text-gray-700">🔗 Infer Relationships</span>
        </label>
         <span class="tooltip-icon ml-2 text-gray-400 text-xs cursor-help" title="If checked, the system will try to automatically infer related spouses, parents, or children. Uncheck for manual control, especially in non-monogamous or complex family structures.">?</span>
      </div>

      <button
        @click="openAddPersonDialog"
        :disabled="isDataLoaded()"
        class="w-full px-4 py-2 bg-purple-600/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-purple-700/90 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
        :title="isDataLoaded() ? 'Add members via right-click on existing nodes once the tree has people.' : 'Create new family tree and add the first person to the family tree.'"
      >
        ➕ NEW FAMILY TREE
      </button>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Load Existing Family Tree:</label>
        <div class="flex items-center space-x-2">
          <input
            type="file"
            ref="fileInput"
            @change="handleFileSelect"
            class="hidden"
            accept=".txtpb"
          />
          <button
            @click="triggerFileInput"
            class="px-4 py-2 bg-blue-500/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-blue-600/90 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
          >
            Choose File
          </button>
          <span class="text-sm text-gray-600 truncate">{{ selectedFileName || 'No file chosen' }}</span>
        </div>
        <button
          @click="loadFile"
          :disabled="!selectedFile"
          class="mt-2 w-full px-4 py-2 bg-teal-500/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-teal-600/90 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
        >
          ↑ LOAD FAMILY TREE
        </button>
      </div>

      <div class="p-3 bg-white/20 backdrop-blur-sm rounded-lg text-sm text-gray-700 shadow-lg">
        ✏️ <b>Edit/Connect:</b> Double-click or Right-click a node in the graph.
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Export:</label>
        <button
          @click="exportData"
          class="w-full px-4 py-2 bg-indigo-500/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-indigo-600/90 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
        >
          💾 EXPORT DATA (.TXTPB)
        </button>
         <button
          @click="exportGraph"
          class="w-full mt-2 px-4 py-2 bg-indigo-500/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-indigo-600/90 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
        >
          📊 EXPORT GRAPH (.HTML)
        </button>
      </div>
    </div>

     <button
      @click="reRenderGraph"
      class="w-full px-4 py-2 bg-gray-400/70 backdrop-blur-sm text-gray-800 text-sm font-medium rounded-lg hover:bg-gray-500/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
    >
      🔄 Re-render Graph
    </button>

  </div>
</template>

<script>
import { inject } from 'vue';
export default {
  name: 'ManageTreeTab',
  components: {
  },
  setup() {
    // Inject the provided state and methods from App.vue
    const statusMessage = inject('statusMessage');
    const isIndianCulture = inject('isIndianCulture');
    const inferRelationshipsEnabled = inject('inferRelationshipsEnabled');
    const loadedFileName = inject('loadedFileName');
    const isDataLoaded = inject('isDataLoaded');
    const updateStatus = inject('updateStatus');
    const updateCultureSetting = inject('updateCultureSetting');
    const updateInferRelationshipsSetting = inject('updateInferRelationshipsSetting');
    const setLoadedFileName = inject('setLoadedFileName');
    const setDataLoaded = inject('setDataLoaded');
    const openAddPersonDialog = inject('openAddPersonDialog');
    const triggerReRender = inject('triggerReRender');
    // Inject other methods needed for actions like export, etc.
    const handleAddRelationship = inject('handleAddRelationship'); // Example usage for context menu actions
    const handleDeleteMember = inject('handleDeleteMember'); // Example usage for context menu actions
    const handleConnectToExisting = inject('handleConnectToExisting'); // Example usage for context menu actions

    return {
      statusMessage,
      isIndianCulture,
      inferRelationshipsEnabled,
      loadedFileName,
      isDataLoaded,
      updateStatus,
      updateCultureSetting,
      updateInferRelationshipsSetting,
      setLoadedFileName,
      setDataLoaded,
      openAddPersonDialog,
      triggerReRender,
      handleAddRelationship, // Expose if needed for child components or direct calls
      handleDeleteMember, // Expose if needed
      handleConnectToExisting, // Expose if needed
    };
  },
  data() {
    return {
      selectedFile: null,
      selectedFileName: '',
      // Use internal models for checkboxes bound to injected values
      isIndianCultureModel: this.isIndianCulture(),
      inferRelationshipsEnabledModel: this.inferRelationshipsEnabled(),
    };
  },
  watch: {
    // Watch for changes in injected values and update internal models
    isIndianCulture: {
      handler(newValue) {
        this.isIndianCultureModel = newValue();
      },
      deep: true
    },
     inferRelationshipsEnabled: {
      handler(newValue) {
        this.inferRelationshipsEnabledModel = newValue();
      },
      deep: true
    },
     loadedFileName: {
      handler(newValue) {
        this.selectedFileName = newValue();
      },
      deep: true
    },
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.selectedFileName = file.name;
        this.setLoadedFileName(file.name); // Update global state
        this.updateStatus(`File selected: ${file.name}`);
      } else {
        this.selectedFile = null;
        this.selectedFileName = '';
        this.setLoadedFileName(null); // Update global state
        this.updateStatus('No file selected.');
      }
    },
    loadFile() {
      if (!this.selectedFile) {
        this.updateStatus('Please select a file first.', 3000);
        return;
      }
      this.updateStatus(`Loading file: ${this.selectedFileName}...`);
      // TODO: Implement file upload and load logic
      // You will need to send this.selectedFile to your FastAPI backend
      // Example: using fetch or axios
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      fetch('/api/load-file', { // Replace with your actual backend endpoint
        method: 'POST',
        body: formData,
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('File upload failed.');
        }
        return response.json(); // Or response.text() depending on backend response
      })
      .then(data => {
        console.log('File loaded successfully:', data);
        this.updateStatus('Data loaded successfully!', 5000);
        this.setDataLoaded(true); // Update global state
        this.triggerReRender(); // Re-render graph after loading
      })
      .catch(error => {
        console.error('Error loading file:', error);
        this.updateStatus(`Error loading file: ${error.message}`, 7000);
        this.setDataLoaded(false); // Update global state
      });
    },
    exportData() {
      this.updateStatus('Exporting data...');
      // TODO: Call backend API to export data (.txtpb)
      // The backend should return the file or a link to download it
       fetch('/api/export-data') // Replace with your actual backend endpoint
        .then(response => {
            if (!response.ok) {
                throw new Error('Data export failed.');
            }
            return response.blob(); // Get the response as a Blob
        })
        .then(blob => {
            // Create a temporary link to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'family_tree_data.txtpb'; // Suggested download file name
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url); // Clean up the URL object
            this.updateStatus('Data exported successfully!', 5000);
        })
        .catch(error => {
            console.error('Error exporting data:', error);
            this.updateStatus(`Error exporting data: ${error.message}`, 7000);
        });
    },
     exportGraph() {
      this.updateStatus('Exporting graph...');
      // TODO: Call backend API to export graph (.html)
      // The backend should return the file or a link to download it
       fetch('/api/export-graph') // Replace with your actual backend endpoint
        .then(response => {
            if (!response.ok) {
                throw new Error('Graph export failed.');
            }
            return response.blob(); // Get the response as a Blob
        })
        .then(blob => {
            // Create a temporary link to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'family_tree_graph.html'; // Suggested download file name
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url); // Clean up the URL object
            this.updateStatus('Graph exported successfully!', 5000);
        })
        .catch(error => {
            console.error('Error exporting graph:', error);
            this.updateStatus(`Error exporting graph: ${error.message}`, 7000);
        });
    },
    reRenderGraph() {
      this.updateStatus('Re-rendering graph...');
      // This will trigger the watch in GraphView.vue
      this.triggerReRender();
      // The actual re-rendering logic (calling backend to generate HTML)
      // is handled by the triggerReRender method provided by App.vue,
      // which is watched by GraphView.vue
    },
    updateCulture(event) {
        this.updateCultureSetting(event.target.checked); // Call injected method
    },
    updateInferRelationships(event) {
        this.updateInferRelationshipsSetting(event.target.checked); // Call injected method
    }
  },
};
</script>

<style scoped>
/* Add any specific styles for this tab here */
</style>
