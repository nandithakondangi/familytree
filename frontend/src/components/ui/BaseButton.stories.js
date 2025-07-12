import BaseButton from "./BaseButton.vue";

/**
 * More on how to set up stories at: https://storybook.js.org/docs/vue/writing-stories/introduction
 * This is the default export that tells Storybook about our component.
 */
export default {
	title: "UI/BaseButton", // The title in the Storybook sidebar
	component: BaseButton,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/vue/writing-docs/autodocs
	tags: ["autodocs"],
	// `argTypes` configure the controls in the Storybook UI
	argTypes: {
		variant: {
			control: "select",
			options: ["primary", "secondary", "danger"],
		},
		disabled: { control: "boolean" },
		// This defines a control for the default slot
		default: {
			control: "text",
			name: "Content", // This will be the label in the Storybook UI
		},
	},
};

// Each named export is a new story for the component

export const Primary = {
	args: {
		variant: "primary",
		disabled: false,
		default: "Primary Button", // This value populates the default slot
	},
};

export const Secondary = {
	args: {
		variant: "secondary",
		disabled: false,
		default: "Secondary Button",
	},
};

export const Danger = {
	args: {
		variant: "danger",
		disabled: false,
		default: "Danger Button",
	},
};

export const Disabled = {
	args: {
		variant: "primary",
		disabled: true,
		default: "Disabled",
	},
};
