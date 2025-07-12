/** @type { import('@storybook/vue3-vite').StorybookConfig } */
const config = {
	stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|ts|tsx)"],
	addons: [
		"@storybook/addon-docs",
		"@storybook/addon-a11y",
		"@storybook/addon-themes",
	],
	framework: {
		name: "@storybook/vue3-vite",
		options: {},
	},
	docs: {
		autodocs: "tag",
	},
};
export default config;
