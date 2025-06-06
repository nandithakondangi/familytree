<template>
	<div class="flex flex-col h-full p-1">
		<div class="flex-grow space-y-4">
			<div class="flex items-center mt-1">
				<label
					for="indian-culture-toggle"
					class="inline-flex items-center cursor-pointer"
				>
					<input
						id="indian-culture-toggle"
						type="checkbox"
						v-model="isIndianCultureModel"
						@change="updateCulture"
						class="sr-only peer"
					/>
					<div
						class="relative w-9 h-5 bg-white/50 dark:bg-slate-600/70 backdrop-blur-sm rounded-full peer peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-inset peer-focus:ring-indigo-500 dark:peer-focus:ring-indigo-400 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300/70 dark:after:border-gray-500/70 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-500/90 dark:peer-checked:bg-indigo-400/90 shadow"
					></div>
					<span
						class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300"
						>Culture: Indian</span
					>
				</label>
				<span
					class="tooltip-icon ml-2 text-gray-400 text-xs cursor-help"
					title="Enable to show fields for traditional Indian dates (Tamil Month/Star/Paksham/Thithi)."
					>?</span
				>
			</div>

			<div class="flex items-center">
				<label
					for="infer-relationships-toggle"
					class="inline-flex items-center cursor-pointer"
				>
					<input
						id="infer-relationships-toggle"
						type="checkbox"
						v-model="inferRelationshipsEnabledModel"
						@change="updateInferRelationships"
						class="sr-only peer"
					/>
					<div
						class="relative w-9 h-5 bg-white/50 dark:bg-slate-600/70 backdrop-blur-sm rounded-full peer peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-inset peer-focus:ring-indigo-500 dark:peer-focus:ring-indigo-400 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300/70 dark:after:border-gray-500/70 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-500/90 dark:peer-checked:bg-indigo-400/90 shadow"
					></div>
					<span
						class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300"
						>🔗 Infer Relationships</span
					>
				</label>
				<span
					class="tooltip-icon ml-2 text-gray-400 text-xs cursor-help"
					title="If checked, the system will try to automatically infer related spouses, parents, or children. Uncheck for manual control, especially in non-monogamous or complex family structures."
					>?</span
				>
			</div>

			<button
				@click="handleNewFamilyTreeRequest"
				class="w-full px-4 py-2 bg-purple-600/80 dark:bg-purple-700/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-purple-700/90 dark:hover:bg-purple-600/90 focus:outline-none focus:ring-2 focus:ring-purple-600 dark:focus:ring-purple-500 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
				:title="
					isDataLoaded()
						? 'Clear current tree and start a new one. Unsaved changes will be lost.'
						: 'Create new family tree and add the first person to the family tree.'
				"
			>
				➕ NEW FAMILY TREE
			</button>

			<div>
				<label
					class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
					>Load Existing Family Tree:</label
				>
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
						class="px-4 py-2 bg-blue-500/80 dark:bg-blue-600/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-blue-600/90 dark:hover:bg-blue-500/90 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
					>
						Choose File
					</button>
					<span class="text-sm text-gray-600 dark:text-gray-400 truncate">{{
						selectedFileName || "No file chosen"
					}}</span>
				</div>
				<button
					@click="loadFile"
					:disabled="!selectedFile"
					class="mt-2 w-full px-4 py-2 bg-teal-500/80 dark:bg-teal-600/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-teal-600/90 dark:hover:bg-teal-500/90 focus:outline-none focus:ring-2 focus:ring-teal-500 dark:focus:ring-teal-400 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
				>
					↑ LOAD FAMILY TREE
				</button>
			</div>

			<div
				class="p-3 bg-white/20 dark:bg-slate-700/40 backdrop-blur-sm rounded-lg text-sm text-gray-700 dark:text-gray-300 shadow-lg"
			>
				✏️ <b>Edit/Connect:</b> Double-click or Right-click a node in the graph.
			</div>

			<div>
				<label
					class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
					>Export:</label
				>
				<button
					@click="saveData"
					class="w-full px-4 py-2 bg-indigo-500/80 dark:bg-indigo-600/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-indigo-600/90 dark:hover:bg-indigo-500/90 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
					title="Saves the current family tree data to a .txtpb file. If a file was previously loaded or saved using the file picker, it attempts to save to the same file."
				>
					💾 SAVE DATA (.txtpb)
				</button>
				<button
					@click="exportCurrentSnapshot"
					class="w-full mt-2 px-4 py-2 bg-indigo-400/80 dark:bg-indigo-500/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-indigo-500/90 dark:hover:bg-indigo-400/90 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:focus:ring-indigo-300 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
					title="Exports the current state of the family tree data to a new .txtpb file. This always prompts for a new file location."
				>
					📸 EXPORT DATA SNAPSHOT (.txtpb)
				</button>
				<button
					@click="exportGraph"
					class="w-full mt-2 px-4 py-2 bg-green-500/80 dark:bg-green-600/80 backdrop-blur-sm text-white text-sm font-medium rounded-lg hover:bg-green-600/90 dark:hover:bg-green-500/90 focus:outline-none focus:ring-2 focus:ring-green-500 dark:focus:ring-green-400 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
					title="Exports the family tree as an interactive HTML graph file. This always prompts for a new file location."
				>
					📊 EXPORT INTERACTIVE GRAPH (.html)
				</button>
			</div>
		</div>

		<button
			@click="reRenderGraph"
			class="w-full px-4 py-2 bg-gray-400/70 dark:bg-gray-600/70 backdrop-blur-sm text-gray-800 dark:text-gray-200 text-sm font-medium rounded-lg hover:bg-gray-500/80 dark:hover:bg-gray-500/80 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500 focus:ring-opacity-50 transition duration-150 ease-in-out shadow-lg"
		>
			🔄 Re-render Graph
		</button>
	</div>
</template>

<script>
	import { inject, ref } from "vue";
	export default {
		name: "ManageTreeTab",
		components: {},
		setup() {
			// Inject the provided state and methods from App.vue
			const statusMessage = inject("statusMessage");
			const isIndianCulture = inject("isIndianCulture");
			const inferRelationshipsEnabled = inject("inferRelationshipsEnabled");
			const loadedFileName = inject("loadedFileName");
			const isDataLoaded = inject("isDataLoaded");
			const updateStatus = inject("updateStatus");
			const updateCultureSetting = inject("updateCultureSetting");
			const updateInferRelationshipsSetting = inject(
				"updateInferRelationshipsSetting"
			);
			const setLoadedFileName = inject("setLoadedFileName");
			const setDataLoaded = inject("setDataLoaded");
			const openAddPersonDialog = inject("openAddPersonDialog");
			const triggerReRender = inject("triggerReRender");
			const openConfirmModal = inject("openConfirmModal");
			// Inject other methods needed for actions like export, etc.
			const handleAddRelationship = inject("handleAddRelationship"); // Example usage for context menu actions
			const currentFileHandle = ref(null); // To store the FileSystemFileHandle

			const handleDeleteMember = inject("handleDeleteMember"); // Example usage for context menu actions
			const handleConnectToExisting = inject("handleConnectToExisting"); // Example usage for context menu actions

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
				currentFileHandle,
				openConfirmModal,
				handleAddRelationship, // Expose if needed for child components or direct calls
				handleDeleteMember, // Expose if needed
				handleConnectToExisting, // Expose if needed
			};
		},
		data() {
			return {
				selectedFile: null,
				selectedFileName: this.loadedFileName() || "", // Initialize with globally loaded file name if any
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
			},
			inferRelationshipsEnabled: {
				handler(newValue) {
					this.inferRelationshipsEnabledModel = newValue();
				},
			},
			loadedFileName: {
				handler(newValue) {
					this.selectedFileName = newValue();
				},
			},
		},
		methods: {
			// --- Helper Methods ---
			async _fetchBlobOrThrow(url, operationName = "Data fetch") {
				const response = await fetch(url);
				if (!response.ok) {
					const errorText = await response.text();
					throw new Error(
						`${operationName} failed: ${response.status} ${
							errorText || response.statusText
						}`
					);
				}
				return response.blob();
			},

			async _writeFileToHandle(fileHandle, blob) {
				if (typeof fileHandle.queryPermission === "function") {
					if (
						(await fileHandle.queryPermission({ mode: "readwrite" })) !==
						"granted"
					) {
						if (
							(await fileHandle.requestPermission({ mode: "readwrite" })) !==
							"granted"
						) {
							throw new Error(
								"Permission to write to the file was not granted."
							);
						}
					}
				} else if (typeof fileHandle.requestPermission === "function") {
					// Fallback for browsers that might not have queryPermission but have requestPermission
					if (
						(await fileHandle.requestPermission({ mode: "readwrite" })) !==
						"granted"
					) {
						throw new Error("Permission to write to the file was not granted.");
					}
				}
				// If permissions are fine or not explicitly manageable this way, proceed.
				const writableStream = await fileHandle.createWritable();
				await writableStream.write(blob);
				await writableStream.close();
			},

			async _saveFileWithPickerOrFallback(
				blob,
				{ suggestedName, types, successMessageBase, isGraphExportForFallback }
			) {
				if (window.showSaveFilePicker) {
					try {
						const fileHandle = await window.showSaveFilePicker({
							suggestedName,
							types,
						});
						await this._writeFileToHandle(fileHandle, blob); // Use the helper here too
						this.updateStatus(
							`${successMessageBase} as ${fileHandle.name} successfully!`,
							7000
						);
						return fileHandle;
					} catch (err) {
						if (err.name === "AbortError") {
							this.updateStatus(
								`${successMessageBase} cancelled by user.`,
								3000
							);
						} else if (err.message.includes("Permission to write")) {
							// Specific error from _writeFileToHandle
							this.updateStatus(
								`Save cancelled: ${err.message}. Falling back to download.`,
								7000
							);
							this.fallbackDownload(
								blob,
								suggestedName,
								isGraphExportForFallback
							);
						} else {
							console.error(
								`Error using File System Access API for ${successMessageBase.toLowerCase()}:`,
								err
							);
							this.updateStatus(
								`Error saving ${successMessageBase.toLowerCase()}: ${
									err.message
								}. Falling back to download.`,
								7000
							);
							this.fallbackDownload(
								blob,
								suggestedName,
								isGraphExportForFallback
							);
						}
					}
				} else {
					this.updateStatus(
						`Using standard download method for ${successMessageBase.toLowerCase()}.`,
						3000
					);
					this.fallbackDownload(blob, suggestedName, isGraphExportForFallback);
				}
				return null; // No handle if fallback or error not leading to a handle
			},

			async _callApiToCreateNewFamilyTree() {
				fetch("/api/v1/manage/create_family", { method: "POST" })
					.then((response) => {
						if (!response.ok) {
							throw new Error(
								`Server error: ${response.status} ${response.statusText}`
							);
						}
						return response.json();
					})
					.then((data) => {
						console.log("Family tree created successfully:", data);
					});
				return null;
			},

			// --- Main Functionality Methods ---
			handleNewFamilyTreeRequest() {
				this.$nextTick(async () => {
					// Ensure DOM is updated if called rapidly
					if (this.isDataLoaded()) {
						const confirmed = await this.openConfirmModal(
							"This operation will clear the existing family tree and unsaved changes will be lost. Are you sure you want to proceed?"
						);
						if (confirmed) {
							console.log(
								"User confirmed to clear existing tree and start a new one."
							);
							this._callApiToCreateNewFamilyTree();
							this.currentFileHandle = null;
							this.setLoadedFileName(null);
							this.selectedFile = null;
							this.setDataLoaded(false);
							this.updateStatus(
								"Previous tree cleared. Starting a new family tree.",
								5000
							);
							this.triggerReRender();
							this.openAddPersonDialog();
						} else {
							this.updateStatus("Operation cancelled by user.", 3000);
						}
					} else {
						this._callApiToCreateNewFamilyTree();
						this.updateStatus("Successfully created new family tree", 5000);
						this.openAddPersonDialog();
					}
				});
			},
			async triggerFileInput() {
				if (window.showOpenFilePicker) {
					try {
						const [fileHandle] = await window.showOpenFilePicker({
							types: [
								{
									description: "Family Tree Data",
									accept: { "text/plain": [".txtpb"] },
								},
							],
							multiple: false,
						});
						this.selectedFile = await fileHandle.getFile(); // Get the File object
						this.selectedFileName = this.selectedFile.name;
						this.currentFileHandle = fileHandle; // Store the handle
						this.setLoadedFileName(this.selectedFileName);
						this.updateStatus(`File selected: ${this.selectedFileName}`);
						// Optionally, you could automatically call this.loadFile() here
					} catch (err) {
						if (err.name !== "AbortError") {
							console.error("Error using showOpenFilePicker:", err);
							this.updateStatus("Error selecting file. Using fallback.", 3000);
						} // User cancelled is fine, no message needed or a subtle one.
					}
				} else {
					this.$refs.fileInput.click(); // Fallback to traditional input
				}
			},
			handleFileSelect(event) {
				const file = event.target.files[0];
				if (file) {
					this.selectedFile = file;
					console.log("Selected file:", file);
					this.selectedFileName = file.name;
					this.setLoadedFileName(file.name); // Update global state
					this.currentFileHandle = null; // Clear any previous handle if using input type=file
					this.updateStatus(`File selected: ${file.name}`);
				} else {
					this.selectedFile = null;
					this.selectedFileName = "";
					this.setLoadedFileName(null); // Update global state
					this.updateStatus("No file selected.");
				}
			},
			async loadFile() {
				this.$nextTick(async () => {
					if (!this.selectedFile) {
						this.updateStatus("Please select a file first.", 3000);
						return;
					}

					if (this.isDataLoaded()) {
						// Check if data is already loaded
						const confirmed = await this.openConfirmModal(
							"This operation will clear the existing family tree and unsaved changes will be lost. Are you sure you want to proceed?"
						);
						if (!confirmed) {
							this.updateStatus("Load operation cancelled by user.", 3000);
							return;
						}
						// If confirmed, proceed with loading.
						// No 'else' needed here as the 'return' handles the cancellation.
					}

					this.updateStatus(`Reading file: ${this.selectedFileName}...`);

					try {
						const fileContent = await this.selectedFile.text(); // Modern way to read File as text
						console.log("File content:", fileContent);
						this.updateStatus(`Sending file content to server...`);

						const response = await fetch("/api/v1/manage/load_family", {
							method: "POST",
							headers: { "Content-Type": "application/json" },
							body: JSON.stringify({
								filename: this.selectedFileName,
								content: fileContent,
							}),
						});

						if (!response.ok) {
							const text = await response.text();
							throw new Error(
								`Server error: ${response.status} ${
									text || response.statusText
								}`
							);
						}

						const data = await response.json();
						console.log("File processed successfully by backend:", data);
						this.updateStatus("Data loaded successfully!", 5000);
						this.setDataLoaded(true);
						// If loaded via <input type="file">, currentFileHandle would be null.
						// If loaded via showOpenFilePicker, currentFileHandle is already set.
						this.triggerReRender();
					} catch (error) {
						console.error("Error loading file:", error);
						this.updateStatus(`Error loading file: ${error.message}`, 7000);
						this.setDataLoaded(false);
						if (this.currentFileHandle) this.currentFileHandle = null; // Clear handle on load error
					}
				});
			},
			async saveData() {
				this.updateStatus("Saving data...");
				try {
					const blob = await this._fetchBlobOrThrow(
						"/api/v1/manage/save_family",
						"Data export for save"
					);
					const baseSuggestedName =
						this.loadedFileName() || "family_tree_data.txtpb";
					let suggestedName = this.currentFileHandle?.name || baseSuggestedName;

					if (
						this.currentFileHandle &&
						typeof this.currentFileHandle.createWritable === "function"
					) {
						try {
							await this._writeFileToHandle(this.currentFileHandle, blob);
							this.updateStatus(
								`Data saved to ${this.currentFileHandle.name} successfully!`,
								7000
							);
							this.setLoadedFileName(this.currentFileHandle.name); // Ensure global state is updated
							return; // Save successful
						} catch (err) {
							console.warn(
								`Could not save directly to file handle (name: ${this.currentFileHandle?.name}, error: ${err.name}, message: ${err.message}). Falling back to "Save As".`
							);
							suggestedName = baseSuggestedName; // Reset suggestedName for "Save As"
						}
					}

					// If no handle, or direct save failed, use showSaveFilePicker (Save As behavior)
					const fileHandle = await this._saveFileWithPickerOrFallback(blob, {
						suggestedName,
						types: [
							{
								description: "Family Tree Data",
								accept: { "text/plain": [".txtpb"] },
							},
						],
						successMessageBase: "Data saved",
						isGraphExportForFallback: false,
					});

					if (fileHandle) {
						this.currentFileHandle = fileHandle;
						this.selectedFileName = fileHandle.name;
						this.setLoadedFileName(fileHandle.name);
					}
				} catch (error) {
					console.error("Error preparing data for save:", error);
					this.updateStatus(`Error saving data: ${error.message}`, 10000);
				}
			},

			async exportCurrentSnapshot() {
				// This function will now export the current data state as a .txtpb file, always prompting for a new file.
				const suggestedName = "family_tree_snapshot.txtpb";
				const fileDescription = "Family Tree Data Snapshot";
				const acceptMimeType = "text/plain";
				const acceptExtension = ".txtpb";

				this.updateStatus("Exporting data snapshot...");
				try {
					const blob = await this._fetchBlobOrThrow(
						"/api/v1/manage/export_family_snapshot",
						"Data snapshot export"
					);
					await this._saveFileWithPickerOrFallback(blob, {
						suggestedName,
						types: [
							{
								description: fileDescription,
								accept: { [acceptMimeType]: [acceptExtension] },
							},
						],
						successMessageBase: "Data snapshot exported",
						isGraphExportForFallback: false,
					});
				} catch (error) {
					console.error("Error exporting data snapshot:", error);
					this.updateStatus(
						`Error exporting data snapshot: ${error.message}`,
						10000
					);
				}
			},
			async exportGraph() {
				const suggestedName = "family_tree_graph.html";
				const fileDescription = "HTML Graph File";
				const acceptMimeType = "text/html";
				const acceptExtension = ".html";

				this.updateStatus("Exporting graph...");
				try {
					const blob = await this._fetchBlobOrThrow(
						"/api/v1/manage/export_interactive_graph",
						"Interactive graph export"
					);
					await this._saveFileWithPickerOrFallback(blob, {
						suggestedName,
						types: [
							{
								description: fileDescription,
								accept: { [acceptMimeType]: [acceptExtension] },
							},
						],
						successMessageBase: "Interactive graph exported",
						isGraphExportForFallback: true,
					});
				} catch (error) {
					console.error("Error exporting interactive graph:", error);
					this.updateStatus(
						`Error exporting interactive graph: ${error.message}`,
						10000
					);
				}
			},

			// Helper method for the traditional download
			fallbackDownload(blob, fileName, isGraphExport) {
				const url = window.URL.createObjectURL(blob);
				const a = document.createElement("a");
				a.style.display = "none";
				a.href = url;
				a.download = fileName;
				document.body.appendChild(a);
				a.click();
				window.URL.revokeObjectURL(url);
				document.body.removeChild(a); // Clean up the anchor element
				this.updateStatus(
					`${isGraphExport ? "Graph" : "Data"} downloaded successfully!`,
					isGraphExport ? 5000 : 7000
				);
			},

			reRenderGraph() {
				this.updateStatus("Re-rendering graph...");
				this.triggerReRender();
			},
			updateCulture(event) {
				this.updateCultureSetting(event.target.checked); // Call injected method
			},
			updateInferRelationships(event) {
				this.updateInferRelationshipsSetting(event.target.checked); // Call injected method
			},
		},
	};
</script>

<style scoped>
	/* Add any specific styles for this tab here */
</style>
