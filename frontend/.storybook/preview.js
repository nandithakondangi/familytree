import "../src/index.css";
import { setup } from "@storybook/vue3";
import { createPinia } from "pinia";
import { withThemeByClassName } from "@storybook/addon-themes";

// Set up Pinia for all stories
setup((app) => {
	app.use(createPinia());
});

export const parameters = {
	backgrounds: {
		disable: true,
	},
	controls: {
		matchers: {
			color: /(background|color)$/i,
			date: /Date$/,
		},
	},
};

export const decorators = [
	withThemeByClassName({
		themes: {
			light: "",
			dark: "dark bg-slate-900",
		},
		defaultTheme: "light",
	}),
];
