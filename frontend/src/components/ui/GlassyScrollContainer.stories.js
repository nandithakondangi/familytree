import GlassyScrollContainer from "./GlassyScrollContainer.vue";

export default {
	title: "UI/GlassyScrollContainer",
	component: GlassyScrollContainer,
	argTypes: {
		themeColor: {
			control: { type: "select" },
			options: ["blue", "indigo", "green", "orange", "yellow", "danger"],
			description: "The color theme for the scrollbar thumb.",
		},
		scrollbarSize: {
			control: { type: "text" },
			description: "The width/height of the scrollbar (e.g., '12px').",
		},
		default: {
			control: "text",
			description: "The content to be placed inside the scroll container.",
		},
	},
	parameters: {
		backgrounds: {
			default: "dark",
			values: [
				{ name: "dark", value: "#1e293b" }, // slate-800
				{ name: "light", value: "#f1f5f9" }, // slate-100
			],
		},
	},
	tags: ["autodocs"]
};

const Template = (args) => ({
	components: { GlassyScrollContainer },
	setup() {
		return { args };
	},
	// A parent div with a fixed size is necessary to demonstrate the scrolling behavior.
	template: `
    <div style="height: 300px; width: 400px; padding: 1rem;">
      <GlassyScrollContainer v-bind="args">
        <div v-html="args.default" class="text-gray-800 dark:text-gray-200"></div>
      </GlassyScrollContainer>
    </div>
  `,
});

export const WithScrollbar = Template.bind({});
WithScrollbar.args = {
	themeColor: "indigo",
	scrollbarSize: "8px",
	default: Array.from(
		{ length: 50 },
		(_, i) => `<p>Scrollable content line ${i + 1}</p>`,
	).join(""),
};
WithScrollbar.storyName = "With Visible Scrollbar";

export const WithoutScrollbar = Template.bind({});
WithoutScrollbar.args = {
	themeColor: "green",
	scrollbarSize: "8px",
	default: `<p>This content fits perfectly inside the container.</p><p>Therefore, no scrollbar will be visible.</p>`,
};
WithoutScrollbar.storyName = "Without Scrollbar";