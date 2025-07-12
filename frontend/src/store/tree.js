import { defineStore } from "pinia";

export const useTreeStore = defineStore("tree", {
	state: () => ({
		loadedFileName: null,
		isDataLoaded: false,
		triggerGraphRender: false,
	}),
	actions: {
		setLoadedFileName(fileName) {
			this.loadedFileName = fileName;
		},
		setDataLoaded(isLoaded) {
			this.isDataLoaded = isLoaded;
		},
		triggerReRender() {
			this.triggerGraphRender = !this.triggerGraphRender;
			console.log("Re-render triggered via store");
			// TODO: This action will eventually call the API service
			// to get the new graph HTML.
		},
	},
});
