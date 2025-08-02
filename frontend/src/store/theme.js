import { defineStore } from "pinia";

/**
 * A centralized store for managing UI component theme definitions.
 * This provides a single source of truth for all color-related styling,
 * making it easy to add, remove, or update themes across the entire application.
 */
export const useThemeStore = defineStore("theme", {
	state: () => ({
		/**
		 * A nested object defining the class strings for each component and theme.
		 * Structure: themes[themeName][componentName]
		 */
		themes: {
			blue: {
				GlassyButton: "text-blue-900 dark:text-blue-100 bg-blue-500/20 dark:bg-blue-400/20 group-hover:bg-blue-500/30 dark:group-hover:bg-blue-400/30",
				GlassyTabPanel: "text-blue-900 dark:text-blue-100 bg-blue-500/20 dark:bg-blue-400/20",
				GlassyTabSwitcher: {
					container: "bg-blue-500/10 dark:bg-blue-400/10",
					text: "text-blue-900 dark:text-blue-100",
					bubble: "bg-blue-500/5 dark:bg-blue-400/5",
				},
				GlassyToggle: "bg-blue-500/20 dark:bg-blue-400/20 peer-checked:bg-blue-500/60 dark:peer-checked:bg-blue-400/60",
				GlassyScrollContainer: {
					thumb: "rgba(96, 165, 250, 0.5)", // blue-400 / 50%
					thumbHover: "rgba(96, 165, 250, 0.7)", // blue-400 / 70%
					darkThumb: "rgba(147, 197, 253, 0.4)", // blue-300 / 40%
					darkThumbHover: "rgba(147, 197, 253, 0.6)", // blue-300 / 60%
				},
				BaseModal: {
					backdrop: "bg-blue-300/20 dark:bg-blue-950/20",
					panel: "bg-blue-200/50 dark:bg-blue-900/50",
					header: "text-blue-900 dark:text-blue-100",
					body: "text-blue-800 dark:text-blue-200",
				},
				GlassyDropDown: {
					container: "bg-blue-500/10 dark:bg-blue-400/10",
					text: "text-blue-900 dark:text-blue-100",
					focus: "data-focus:bg-blue-500/40 dark:data-focus:bg-blue-400/40 data-focus:text-blue-900 dark:data-focus:text-blue-100 data-focus:ring-2 data-focus:ring-blue-500/60 data-focus:ring-offset-1",
					selected: "data-selected:ring-2 data-selected:ring-blue-500/50",
					active: "text-blue-900 dark:text-blue-100 border-2 border-blue-500/60",
					selectedItem: "ring-2 ring-blue-500/50",
					optionsContainer: "bg-blue-50/90 dark:bg-blue-950/90",
				},
				GlassyTextbox: {
					backdrop: "bg-blue-500/10 dark:bg-blue-400/10 group-focus-within:bg-blue-500/20 dark:group-focus-within:bg-blue-400/20",
					text: "text-blue-800 dark:text-blue-100 placeholder-blue-600/70 dark:placeholder-blue-400/60",
				},
				GlassyDatePicker: {
					backdrop: "bg-blue-500/10 dark:bg-blue-400/10 group-focus-within:bg-blue-500/20 dark:group-focus-within:bg-blue-400/20",
					text: "text-blue-800 dark:text-blue-100 placeholder-blue-600/70 dark:placeholder-blue-400/60",
					popup: "!bg-blue-200/80 dark:!bg-blue-950/95 border border-blue-300/50 dark:border-blue-800/50",
				},
			},
			indigo: {
				GlassyButton: "text-indigo-900 dark:text-indigo-100 bg-indigo-500/20 dark:bg-indigo-400/20 group-hover:bg-indigo-500/30 dark:group-hover:bg-indigo-400/30",
				GlassyTabPanel: "text-indigo-900 dark:text-indigo-100 bg-indigo-500/20 dark:bg-indigo-400/20",
				GlassyTabSwitcher: {
					container: "bg-indigo-500/10 dark:bg-indigo-400/10",
					text: "text-indigo-900 dark:text-indigo-100",
					bubble: "bg-indigo-500/5 dark:bg-indigo-400/5",
				},
				GlassyToggle: "bg-indigo-500/20 dark:bg-indigo-400/20 peer-checked:bg-indigo-500/60 dark:peer-checked:bg-indigo-400/60",
				GlassyScrollContainer: {
					thumb: "rgba(99, 102, 241, 0.5)", // indigo-400 / 50%
					thumbHover: "rgba(99, 102, 241, 0.7)", // indigo-400 / 70%
					darkThumb: "rgba(165, 180, 252, 0.4)", // indigo-300 / 40%
					darkThumbHover: "rgba(165, 180, 252, 0.6)", // indigo-300 / 60%
				},
				BaseModal: {
					backdrop: "bg-indigo-300/20 dark:bg-indigo-950/20",
					panel: "bg-indigo-200/50 dark:bg-indigo-900/50",
					header: "text-indigo-900 dark:text-indigo-100",
					body: "text-indigo-800 dark:text-indigo-200",
				},
				GlassyDropDown: {
					container: "bg-indigo-500/10 dark:bg-indigo-400/10",
					text: "text-indigo-900 dark:text-indigo-100",
					focus: "data-focus:bg-indigo-500/40 dark:data-focus:bg-indigo-400/40 data-focus:text-indigo-900 dark:data-focus:text-indigo-100 data-focus:ring-2 data-focus:ring-indigo-500/60 data-focus:ring-offset-1",
					selected: "data-selected:ring-2 data-selected:ring-indigo-500/50",
					active: "text-indigo-900 dark:text-indigo-100 border-2 border-indigo-500/60",
					selectedItem: "ring-2 ring-indigo-500/50",
					optionsContainer: "bg-indigo-50/90 dark:bg-indigo-950/90",
				},
				GlassyTextbox: {
					backdrop: "bg-indigo-500/10 dark:bg-indigo-400/10 group-focus-within:bg-indigo-500/20 dark:group-focus-within:bg-indigo-400/20",
					text: "text-indigo-800 dark:text-indigo-100 placeholder-indigo-600/70 dark:placeholder-indigo-400/60",
				},
				GlassyDatePicker: {
					backdrop: "bg-indigo-500/10 dark:bg-indigo-400/10 group-focus-within:bg-indigo-500/20 dark:group-focus-within:bg-indigo-400/20",
					text: "text-indigo-800 dark:text-indigo-100 placeholder-indigo-600/70 dark:placeholder-indigo-400/60",
					popup: "!bg-indigo-200/80 dark:!bg-indigo-950/95 border border-indigo-300/50 dark:border-indigo-800/50",
				},
			},
			green: {
				GlassyButton: "text-green-900 dark:text-green-100 bg-green-500/20 dark:bg-green-400/20 group-hover:bg-green-500/30 dark:group-hover:bg-green-400/30",
				GlassyTabPanel: "text-green-900 dark:text-green-100 bg-green-500/20 dark:bg-green-400/20",
				GlassyTabSwitcher: {
					container: "bg-green-500/10 dark:bg-green-400/10",
					text: "text-green-900 dark:text-green-100",
					bubble: "bg-green-500/5 dark:bg-green-400/5",
				},
				GlassyToggle: "bg-green-500/20 dark:bg-green-400/20 peer-checked:bg-green-500/60 dark:peer-checked:bg-green-400/60",
				GlassyScrollContainer: {
					thumb: "rgba(74, 222, 128, 0.5)", // green-400 / 50%
					thumbHover: "rgba(74, 222, 128, 0.7)", // green-400 / 70%
					darkThumb: "rgba(134, 239, 172, 0.4)", // green-300 / 40%
					darkThumbHover: "rgba(134, 239, 172, 0.6)", // green-300 / 60%
				},
				BaseModal: {
					backdrop: "bg-green-300/20 dark:bg-green-950/20",
					panel: "bg-green-200/50 dark:bg-green-900/50",
					header: "text-green-900 dark:text-green-100",
					body: "text-green-800 dark:text-green-200",
				},
				GlassyDropDown: {
					container: "bg-green-500/10 dark:bg-green-400/10",
					text: "text-green-900 dark:text-green-100",
					focus: "data-focus:bg-green-500/40 dark:data-focus:bg-green-400/40 data-focus:text-green-900 dark:data-focus:text-green-100 data-focus:ring-2 data-focus:ring-green-500/60 data-focus:ring-offset-1",
					selected: "data-selected:ring-2 data-selected:ring-green-500/50",
					active: "text-green-900 dark:text-green-100 border-2 border-green-500/60",
					selectedItem: "ring-2 ring-green-500/50",
					optionsContainer: "bg-green-50/90 dark:bg-green-950/90",
				},
				GlassyTextbox: {
					backdrop: "bg-green-500/10 dark:bg-green-400/10 group-focus-within:bg-green-500/20 dark:group-focus-within:bg-green-400/20",
					text: "text-green-800 dark:text-green-100 placeholder-green-600/70 dark:placeholder-green-400/60",
				},
				GlassyDatePicker: {
					backdrop: "bg-green-500/10 dark:bg-green-400/10 group-focus-within:bg-green-500/20 dark:group-focus-within:bg-green-400/20",
					text: "text-green-800 dark:text-green-100 placeholder-green-600/70 dark:placeholder-green-400/60",
					popup: "!bg-green-200/80 dark:!bg-green-900/95 border border-green-300/50 dark:border-green-700/50",
				},
			},
			orange: {
				GlassyButton: "text-orange-900 dark:text-orange-100 bg-orange-500/20 dark:bg-orange-400/20 group-hover:bg-orange-500/30 dark:group-hover:bg-orange-400/30",
				GlassyTabPanel: "text-orange-900 dark:text-orange-100 bg-orange-500/20 dark:bg-orange-400/20",
				GlassyTabSwitcher: {
					container: "bg-orange-500/10 dark:bg-orange-400/10",
					text: "text-orange-900 dark:text-orange-100",
					bubble: "bg-orange-500/5 dark:bg-orange-400/5",
				},
				GlassyToggle: "bg-orange-500/20 dark:bg-orange-400/20 peer-checked:bg-orange-500/60 dark:peer-checked:bg-orange-400/60",
				GlassyScrollContainer: {
					thumb: "rgba(251, 146, 60, 0.5)", // orange-400 / 50%
					thumbHover: "rgba(251, 146, 60, 0.7)", // orange-400 / 70%
					darkThumb: "rgba(253, 186, 116, 0.4)", // orange-300 / 40%
					darkThumbHover: "rgba(253, 186, 116, 0.6)", // orange-300 / 60%
				},
				BaseModal: {
					backdrop: "bg-orange-300/20 dark:bg-orange-950/20",
					panel: "bg-orange-200/50 dark:bg-orange-900/50",
					header: "text-orange-900 dark:text-orange-100",
					body: "text-orange-800 dark:text-orange-200",
				},
				GlassyDropDown: {
					container: "bg-orange-500/10 dark:bg-orange-400/10",
					text: "text-orange-900 dark:text-orange-100",
					focus: "data-focus:bg-orange-500/40 dark:data-focus:bg-orange-400/40 data-focus:text-orange-900 dark:data-focus:text-orange-100 data-focus:ring-2 data-focus:ring-orange-500/60 data-focus:ring-offset-1",
					selected: "data-selected:ring-2 data-selected:ring-orange-500/50",
					active: "text-orange-900 dark:text-orange-100 border-2 border-orange-500/60",
					selectedItem: "ring-2 ring-orange-500/50",
					optionsContainer: "bg-orange-50/90 dark:bg-orange-950/90",
				},
				GlassyTextbox: {
					backdrop: "bg-orange-500/10 dark:bg-orange-400/10 group-focus-within:bg-orange-500/20 dark:group-focus-within:bg-orange-400/20",
					text: "text-orange-800 dark:text-orange-100 placeholder-orange-600/70 dark:placeholder-orange-400/60",
				},
				GlassyDatePicker: {
					backdrop: "bg-orange-500/10 dark:bg-orange-400/10 group-focus-within:bg-orange-500/20 dark:group-focus-within:bg-orange-400/20",
					text: "text-orange-800 dark:text-orange-100 placeholder-orange-600/70 dark:placeholder-orange-400/60",
					popup: "!bg-orange-200/80 dark:!bg-orange-900/95 border border-orange-300/50 dark:border-orange-700/50",
				},
			},
			yellow: {
				GlassyButton: "text-yellow-900 dark:text-yellow-100 bg-yellow-500/20 dark:bg-yellow-400/20 group-hover:bg-yellow-500/30 dark:group-hover:bg-yellow-400/30",
				GlassyTabPanel: "text-yellow-900 dark:text-yellow-100 bg-yellow-500/20 dark:bg-yellow-400/20",
				GlassyTabSwitcher: {
					container: "bg-yellow-500/10 dark:bg-yellow-400/10",
					text: "text-yellow-900 dark:text-yellow-100",
					bubble: "bg-yellow-500/5 dark:bg-yellow-400/5",
				},
				GlassyToggle: "bg-yellow-500/20 dark:bg-yellow-400/20 peer-checked:bg-yellow-500/60 dark:peer-checked:bg-yellow-400/60",
				GlassyScrollContainer: {
					thumb: "rgba(250, 204, 21, 0.5)", // yellow-400 / 50%
					thumbHover: "rgba(250, 204, 21, 0.7)", // yellow-400 / 70%
					darkThumb: "rgba(253, 224, 71, 0.4)", // yellow-300 / 40%
					darkThumbHover: "rgba(253, 224, 71, 0.6)", // yellow-300 / 60%
				},
				BaseModal: {
					backdrop: "bg-yellow-300/20 dark:bg-yellow-950/20",
					panel: "bg-yellow-200/50 dark:bg-yellow-900/50",
					header: "text-yellow-900 dark:text-yellow-100",
					body: "text-yellow-800 dark:text-yellow-200",
				},
				GlassyDropDown: {
					container: "bg-yellow-500/10 dark:bg-yellow-400/10",
					text: "text-yellow-900 dark:text-yellow-100",
					focus: "data-focus:bg-yellow-500/40 dark:data-focus:bg-yellow-400/40 data-focus:text-yellow-900 dark:data-focus:text-yellow-100 data-focus:ring-2 data-focus:ring-yellow-500/60 data-focus:ring-offset-1",
					selected: "data-selected:ring-2 data-selected:ring-yellow-500/50",
					active: "text-yellow-900 dark:text-yellow-100 border-2 border-yellow-500/60",
					selectedItem: "ring-2 ring-yellow-500/50",
					optionsContainer: "bg-yellow-50/90 dark:bg-yellow-950/90",
				},
				GlassyTextbox: {
					backdrop: "bg-yellow-500/10 dark:bg-yellow-400/10 group-focus-within:bg-yellow-500/20 dark:group-focus-within:bg-yellow-400/20",
					text: "text-yellow-800 dark:text-yellow-100 placeholder-yellow-600/70 dark:placeholder-yellow-400/60",
				},
				GlassyDatePicker: {
					backdrop: "bg-yellow-500/10 dark:bg-yellow-400/10 group-focus-within:bg-yellow-500/20 dark:group-focus-within:bg-yellow-400/20",
					text: "text-yellow-800 dark:text-yellow-100 placeholder-yellow-600/70 dark:placeholder-yellow-400/60",
					popup: "!bg-yellow-200/80 dark:!bg-yellow-900/95 border border-yellow-300/50 dark:border-yellow-700/50",
				},
			},
			danger: {
				GlassyButton: "text-red-900 dark:text-red-100 bg-red-500/20 dark:bg-red-400/20 group-hover:bg-red-500/30 dark:group-hover:bg-red-400/30",
				GlassyTabPanel: "text-red-900 dark:text-red-100 bg-red-500/20 dark:bg-red-400/20",
				GlassyTabSwitcher: {
					container: "bg-red-500/10 dark:bg-red-400/10",
					text: "text-red-900 dark:text-red-100",
					bubble: "bg-red-500/5 dark:bg-red-400/5",
				},
				GlassyToggle: "bg-red-500/20 dark:bg-red-400/20 peer-checked:bg-red-500/60 dark:peer-checked:bg-red-400/60",
				GlassyScrollContainer: {
					thumb: "rgba(239, 68, 68, 0.5)", // red-400 / 50%
					thumbHover: "rgba(239, 68, 68, 0.7)", // red-400 / 70%
					darkThumb: "rgba(252, 165, 165, 0.4)", // red-300 / 40%
					darkThumbHover: "rgba(252, 165, 165, 0.6)", // red-300 / 60%
				},
				BaseModal: {
					backdrop: "bg-red-300/20 dark:bg-red-950/20",
					panel: "bg-red-200/50 dark:bg-red-900/50",
					header: "text-red-900 dark:text-red-100",
					body: "text-red-800 dark:text-red-200",
				},
				GlassyDropDown: {
					container: "bg-red-500/10 dark:bg-red-400/10",
					text: "text-red-900 dark:text-red-100",
					focus: "data-focus:bg-red-500/40 dark:data-focus:bg-red-400/40 data-focus:text-red-900 dark:data-focus:text-red-100 data-focus:ring-2 data-focus:ring-red-500/60 data-focus:ring-offset-1",
					selected: "data-selected:ring-2 data-selected:ring-red-500/50",
					active: "text-red-900 dark:text-red-100 border-2 border-red-500/60",
					selectedItem: "ring-2 ring-red-500/50",
					optionsContainer: "bg-red-50/90 dark:bg-red-950/90",
				},
				GlassyTextbox: {
					backdrop: "bg-red-500/10 dark:bg-red-400/10 group-focus-within:bg-red-500/20 dark:group-focus-within:bg-red-400/20",
					text: "text-red-800 dark:text-red-100 placeholder-red-600/70 dark:placeholder-red-400/60",
				},
				GlassyDatePicker: {
					backdrop: "bg-red-500/10 dark:bg-red-400/10 group-focus-within:bg-red-500/20 dark:group-focus-within:bg-red-400/20",
					text: "text-red-800 dark:text-red-100 placeholder-red-600/70 dark:placeholder-red-400/60",
					popup: "!bg-red-200/80 dark:!bg-red-900/95 border border-red-300/50 dark:border-red-700/50",
				},
			},
			"default": {
				BaseModal: {
					backdrop: "bg-gray-500/20 dark:bg-black/20",
					panel: "bg-white/60 dark:bg-gray-900/60",
					header: "text-gray-900 dark:text-gray-50",
					body: "text-gray-800 dark:text-gray-300",
				},
			},
		},
	}),
	getters: {
		/**
		 * Returns an array of available theme names.
		 * @returns {string[]}
		 */
		availableThemes: (state) => Object.keys(state.themes),

		/**
		 * Gets the complete theme definition object for a specific component.
		 * @param {object} state
		 * @returns {(componentName: string, themeColor: string) => object | string}
		 */
		getThemeClasses: (state) => {
			return (componentName, themeColor) => {
				const theme = state.themes[themeColor] || state.themes.indigo;
				return theme[componentName] || {};
			};
		},
	},
});
