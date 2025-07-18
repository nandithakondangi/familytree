import "../src/index.css";
import { setup } from "@storybook/vue3";
import { createPinia } from "pinia";
import { withThemeByClassName } from "@storybook/addon-themes";
import vNetworkGraph from "v-network-graph";

// Set up Pinia and v-network-graph for all stories
setup((app) => {
	app.use(createPinia());
	app.use(vNetworkGraph);
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
