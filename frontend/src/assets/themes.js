export const themes = {
	indigoViolet: {
		// This can be your current default theme
		displayColor: "#6366f1", //Indigo-500
		light: {
			"--theme-bg-primary-rgb": "99, 102, 241", // indigo-500
			"--theme-bg-primary": "rgba(var(--theme-bg-primary-rgb), 0.7)",
			"--theme-bg-secondary-rgb": "238, 242, 255", // indigo-100
			"--theme-bg-secondary": "rgba(var(--theme-bg-secondary-rgb), 0.8)",
			"--theme-bg-tertiary-rgb": "224, 231, 255", // indigo-200
			"--theme-bg-tertiary": "rgba(var(--theme-bg-tertiary-rgb), 0.6)",
			"--theme-text-on-primary-bg": "#111827", // slate-900 (for high contrast on light primary)
			"--theme-text-secondary-on-primary-bg": "#374151", // slate-700
			"--theme-text-primary": "#1f2937", // slate-800 (general text on secondary/tertiary bg)
			"--theme-text-secondary": "#6b7280", // slate-500
			"--theme-accent-rgb": "79, 70, 229", // indigo-600
			"--theme-accent": "rgb(var(--theme-accent-rgb))",
			"--theme-accent-hover": "#4338ca", // indigo-700
			"--theme-text-on-accent": "#ffffff",
			"--theme-border-color-rgb": "209, 213, 219", // gray-300
			"--theme-border-color": "rgba(var(--theme-border-color-rgb), 0.7)",
			"--theme-input-bg-rgb": "255, 255, 255",
			"--theme-input-bg": "rgba(var(--theme-input-bg-rgb), 0.7)",
			"--theme-input-text": "#111827", // slate-900
			"--theme-input-border": "rgba(var(--theme-border-color-rgb), 0.9)",
			"--theme-input-placeholder": "#9ca3af", // gray-400
			"--theme-button-danger-bg": "#ef4444",
			"--theme-button-danger-hover-bg": "#dc2626",
			"--theme-button-danger-text": "#ffffff",
			"--theme-button-success-bg": "#22c55e",
			"--theme-button-success-hover-bg": "#16a34a",
			"--theme-button-success-text": "#ffffff",
			"--theme-icon-color": "#6b7280", // gray-500
			"--theme-icon-hover-color": "#111827", // gray-900
			"--theme-icon-danger-color": "#f87171", // red-400
			"--theme-icon-danger-hover-color": "#ef4444", // red-500
			"--theme-toggle-bg": "rgba(var(--theme-border-color-rgb), 0.8)",
			"--theme-toggle-thumb-bg": "#ffffff",
			"--theme-toggle-border": "rgba(var(--theme-border-color-rgb), 0.5)",
			"--theme-header-gradient-from": "rgba(147, 51, 234, 0.8)", // purple-600/80
			"--theme-header-gradient-to": "rgba(79, 70, 229, 0.8)", // indigo-600/80
			"--theme-footer-gradient-from": "rgba(147, 51, 234, 0.6)", // purple-600/60
			"--theme-footer-gradient-to": "rgba(79, 70, 229, 0.6)", // indigo-600/60
			"--theme-text-subtle": "rgba(199, 210, 254, 1)", // indigo-200
			"--theme-bg-primary-hover": "rgba(99, 102, 241, 0.7)", // indigo-500/70
			"--theme-bg-overlay": "rgba(255, 255, 255, 0.5)", // white/50
			// ... any other variables you need
		},
		dark: {
			"--theme-bg-primary-rgb": "129, 140, 248", // indigo-400
			"--theme-bg-primary": "rgba(var(--theme-bg-primary-rgb), 0.7)",
			"--theme-bg-secondary-rgb": "67, 56, 202", // indigo-700
			"--theme-bg-secondary": "rgba(var(--theme-bg-secondary-rgb), 0.8)",
			"--theme-bg-tertiary-rgb": "55, 48, 163", // indigo-800
			"--theme-bg-tertiary": "rgba(var(--theme-bg-tertiary-rgb), 0.6)",
			"--theme-text-on-primary-bg": "#f3f4f6", // gray-100 (for high contrast on dark primary)
			"--theme-text-secondary-on-primary-bg": "#d1d5db", // gray-300
			"--theme-text-primary": "#e5e7eb", // gray-200 (general text)
			"--theme-text-secondary": "#9ca3af", // gray-400
			"--theme-accent-rgb": "99, 102, 241", // indigo-500
			"--theme-accent": "rgb(var(--theme-accent-rgb))",
			"--theme-accent-hover": "#818cf8", // indigo-400
			"--theme-text-on-accent": "#ffffff",
			"--theme-border-color-rgb": "75, 85, 99", // gray-600
			"--theme-border-color": "rgba(var(--theme-border-color-rgb), 0.7)",
			"--theme-input-bg-rgb": "55, 65, 81", // slate-700
			"--theme-input-bg": "rgba(var(--theme-input-bg-rgb), 0.7)",
			"--theme-input-text": "#f3f4f6", // gray-100
			"--theme-input-border": "rgba(var(--theme-border-color-rgb), 0.9)",
			"--theme-input-placeholder": "#6b7280", // gray-500
			"--theme-button-danger-bg": "#ef4444",
			"--theme-button-danger-hover-bg": "#dc2626",
			"--theme-button-danger-text": "#ffffff",
			"--theme-button-success-bg": "#22c55e",
			"--theme-button-success-hover-bg": "#16a34a",
			"--theme-button-success-text": "#ffffff",
			"--theme-icon-color": "#9ca3af", // gray-400
			"--theme-icon-hover-color": "#f3f4f6", // gray-100
			"--theme-icon-danger-color": "#ef4444", // red-500
			"--theme-icon-danger-hover-color": "#f87171", // red-400
			"--theme-toggle-bg": "rgba(var(--theme-border-color-rgb), 0.8)",
			"--theme-toggle-thumb-bg": "#1f2937", // slate-800
			"--theme-toggle-border": "rgba(var(--theme-border-color-rgb), 0.5)",
			"--theme-header-gradient-from": "rgba(126, 34, 206, 0.8)", // purple-700/80
			"--theme-header-gradient-to": "rgba(67, 56, 202, 0.8)", // indigo-700/80
			"--theme-footer-gradient-from": "rgba(126, 34, 206, 0.6)", // purple-700/60
			"--theme-footer-gradient-to": "rgba(67, 56, 202, 0.6)", // indigo-700/60
			"--theme-text-subtle": "rgba(165, 180, 252, 1)", // indigo-300
			"--theme-bg-primary-hover": "rgba(79, 70, 229, 0.7)", // indigo-600/70
			"--theme-bg-overlay": "rgba(30, 41, 59, 0.6)", // slate-800/60
			// ...
		},
	},
	oceanBlue: {
		displayColor: "#38bdf8",
		light: {
			"--theme-bg-primary-rgb": "56, 189, 248", // sky-400
			"--theme-bg-primary": "rgba(var(--theme-bg-primary-rgb), 0.7)",
			"--theme-bg-secondary-rgb": "224, 242, 254", // sky-100
			"--theme-bg-secondary": "rgba(var(--theme-bg-secondary-rgb), 0.8)",
			"--theme-bg-tertiary-rgb": "191, 219, 254", // blue-200
			"--theme-bg-tertiary": "rgba(var(--theme-bg-tertiary-rgb), 0.6)",
			"--theme-text-on-primary-bg": "#0c4a6e", // sky-900
			"--theme-text-secondary-on-primary-bg": "#075985", // sky-800
			"--theme-text-primary": "#082f49", // sky-950
			"--theme-text-secondary": "#3f6212", // lime-900
			"--theme-accent-rgb": "14, 165, 233", // sky-500
			"--theme-accent": "rgb(var(--theme-accent-rgb))",
			"--theme-accent-hover": "#0284c7", // sky-600
			"--theme-text-on-accent": "#ffffff",
			"--theme-border-color-rgb": "125, 211, 252", // sky-300
			"--theme-border-color": "rgba(var(--theme-border-color-rgb), 0.7)",
			"--theme-input-bg-rgb": "255, 255, 255",
			"--theme-input-bg": "rgba(var(--theme-input-bg-rgb), 0.7)",
			"--theme-input-text": "#0c4a6e", // sky-900
			"--theme-input-border": "rgba(var(--theme-border-color-rgb), 0.9)",
			"--theme-input-placeholder": "#7dd3fc", // sky-300
			"--theme-button-danger-bg": "#ef4444",
			"--theme-button-danger-hover-bg": "#dc2626",
			"--theme-button-danger-text": "#ffffff",
			"--theme-button-success-bg": "#22c55e",
			"--theme-button-success-hover-bg": "#16a34a",
			"--theme-button-success-text": "#ffffff",
			"--theme-icon-color": "#38bdf8", // sky-400
			"--theme-icon-hover-color": "#0ea5e9", // sky-500
			"--theme-icon-danger-color": "#f87171", // red-400
			"--theme-icon-danger-hover-color": "#ef4444", // red-500
			"--theme-toggle-bg": "rgba(var(--theme-border-color-rgb), 0.8)",
			"--theme-toggle-thumb-bg": "#ffffff",
			"--theme-toggle-border": "rgba(var(--theme-border-color-rgb), 0.5)",
			"--theme-header-gradient-from": "rgba(14, 165, 233, 0.8)", // sky-500/80
			"--theme-header-gradient-to": "rgba(56, 189, 248, 0.8)", // sky-400/80
			"--theme-footer-gradient-from": "rgba(14, 165, 233, 0.6)", // sky-500/60
			"--theme-footer-gradient-to": "rgba(56, 189, 248, 0.6)", // sky-400/60
			"--theme-text-subtle": "rgba(125, 211, 252, 1)", // sky-300
			"--theme-bg-primary-hover": "rgba(56, 189, 248, 0.7)", // sky-400/70
			"--theme-bg-overlay": "rgba(255, 255, 255, 0.5)", // white/50
		},
		dark: {
			"--theme-bg-primary-rgb": "6, 182, 212", // cyan-500
			"--theme-bg-primary": "rgba(var(--theme-bg-primary-rgb), 0.7)",
			"--theme-bg-secondary-rgb": "8, 145, 178", // cyan-700
			"--theme-bg-secondary": "rgba(var(--theme-bg-secondary-rgb), 0.8)",
			"--theme-bg-tertiary-rgb": "21, 94, 117", // cyan-800
			"--theme-bg-tertiary": "rgba(var(--theme-bg-tertiary-rgb), 0.6)",
			"--theme-text-on-primary-bg": "#f0f9ff", // sky-50
			"--theme-text-secondary-on-primary-bg": "#e0f2fe", // sky-100
			"--theme-text-primary": "#e0f2fe", // sky-100
			"--theme-text-secondary": "#a78bfa", // violet-400
			"--theme-accent-rgb": "34, 211, 238", // cyan-400
			"--theme-accent": "rgb(var(--theme-accent-rgb))",
			"--theme-accent-hover": "#06b6d4", // cyan-500
			"--theme-text-on-accent": "#ffffff",
			"--theme-border-color-rgb": "45, 212, 191", // teal-400
			"--theme-border-color": "rgba(var(--theme-border-color-rgb), 0.7)",
			"--theme-input-bg-rgb": "23, 37, 84", // blue-950
			"--theme-input-bg": "rgba(var(--theme-input-bg-rgb), 0.7)",
			"--theme-input-text": "#e0f2fe", // sky-100
			"--theme-input-border": "rgba(var(--theme-border-color-rgb), 0.9)",
			"--theme-input-placeholder": "#67e8f9", // cyan-300
			"--theme-button-danger-bg": "#ef4444",
			"--theme-button-danger-hover-bg": "#dc2626",
			"--theme-button-danger-text": "#ffffff",
			"--theme-button-success-bg": "#22c55e",
			"--theme-button-success-hover-bg": "#16a34a",
			"--theme-button-success-text": "#ffffff",
			"--theme-icon-color": "#67e8f9", // cyan-300
			"--theme-icon-hover-color": "#22d3ee", // cyan-400
			"--theme-icon-danger-color": "#ef4444", // red-500
			"--theme-icon-danger-hover-color": "#f87171", // red-400
			"--theme-toggle-bg": "rgba(var(--theme-border-color-rgb), 0.8)",
			"--theme-toggle-thumb-bg": "#083344", // cyan-950
			"--theme-toggle-border": "rgba(var(--theme-border-color-rgb), 0.5)",
			"--theme-header-gradient-from": "rgba(6, 182, 212, 0.8)", // cyan-500/80
			"--theme-header-gradient-to": "rgba(34, 211, 238, 0.8)", // cyan-400/80
			"--theme-footer-gradient-from": "rgba(6, 182, 212, 0.6)", // cyan-500/60
			"--theme-footer-gradient-to": "rgba(34, 211, 238, 0.6)", // cyan-400/60
			"--theme-text-subtle": "rgba(103, 232, 249, 1)", // cyan-300
			"--theme-bg-primary-hover": "rgba(6, 182, 212, 0.7)", // cyan-500/70
			"--theme-bg-overlay": "rgba(15, 23, 42, 0.6)", // slate-900/60
		},
	},
	forestGreen: {
		displayColor: "#86efac", // Representative color for the picker (Lime-300)
		light: {
			"--theme-bg-primary-rgb": "134, 239, 172", // lime-300
			"--theme-bg-primary": "rgba(var(--theme-bg-primary-rgb), 0.7)",
			"--theme-bg-secondary-rgb": "220, 252, 231", // lime-50
			"--theme-bg-secondary": "rgba(var(--theme-bg-secondary-rgb), 0.8)",
			"--theme-bg-tertiary-rgb": "187, 247, 208", // lime-200
			"--theme-bg-tertiary": "rgba(var(--theme-bg-tertiary-rgb), 0.6)",
			"--theme-text-on-primary-bg": "#134e4a", // emerald-900 (for high contrast on light primary)
			"--theme-text-secondary-on-primary-bg": "#115e59", // emerald-800
			"--theme-text-primary": "#065f46", // green-800 (general text on secondary/tertiary bg)
			"--theme-text-secondary": "#52525b", // slate-800
			"--theme-accent-rgb": "52, 211, 153", // lime-400
			"--theme-accent": "rgb(var(--theme-accent-rgb))",
			"--theme-accent-hover": "#16a34a", // green-600
			"--theme-text-on-accent": "#ffffff",
			"--theme-border-color-rgb": "167, 243, 208", // lime-300
			"--theme-border-color": "rgba(var(--theme-border-color-rgb), 0.7)",
			"--theme-input-bg-rgb": "255, 255, 255",
			"--theme-input-bg": "rgba(var(--theme-input-bg-rgb), 0.7)",
			"--theme-input-text": "#065f46", // green-800
			"--theme-input-border": "rgba(var(--theme-border-color-rgb), 0.9)",
			"--theme-input-placeholder": "#a7f3d0", // lime-200
			"--theme-button-danger-bg": "#ef4444",
			"--theme-button-danger-hover-bg": "#dc2626",
			"--theme-button-danger-text": "#ffffff",
			"--theme-button-success-bg": "#22c55e",
			"--theme-button-success-hover-bg": "#16a34a",
			"--theme-button-success-text": "#ffffff",
			"--theme-icon-color": "#65a30d", // lime-600
			"--theme-icon-hover-color": "#166534", // green-900
			"--theme-icon-danger-color": "#f87171", // red-400
			"--theme-icon-danger-hover-color": "#ef4444", // red-500
			"--theme-toggle-bg": "rgba(var(--theme-border-color-rgb), 0.8)",
			"--theme-toggle-thumb-bg": "#ffffff",
			"--theme-toggle-border": "rgba(var(--theme-border-color-rgb), 0.5)",
			"--theme-header-gradient-from": "rgba(74, 222, 128, 0.8)", // green-400/80
			"--theme-header-gradient-to": "rgba(134, 239, 172, 0.8)", // lime-300/80
			"--theme-footer-gradient-from": "rgba(74, 222, 128, 0.6)", // green-400/60
			"--theme-footer-gradient-to": "rgba(134, 239, 172, 0.6)", // lime-300/60
			"--theme-text-subtle": "rgba(220, 252, 231, 1)", // lime-50 (for context menu headers)
			"--theme-bg-primary-hover": "rgba(134, 239, 172, 0.7)", // lime-300/70 (for context menu item hover)
			"--theme-bg-overlay": "rgba(255, 255, 255, 0.5)", // white/50 (for graph loading overlay)
		},
		dark: {
			// Define dark mode variables for forestGreen here, following the same pattern as other themes
		},
	},
	// ... Define your other themes (ForestGreen, SunsetOrange, GraphiteGray)
	// Make sure to define all the CSS variables for each theme's light and dark mode.
	// For brevity, I've only sketched out oceanBlue.
};
