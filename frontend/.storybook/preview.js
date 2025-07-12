import "../src/index.css";
import { withThemeByClassName } from "@storybook/addon-themes";

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
