import GlassyButton from "./GlassyButton.vue";
import { useThemeStore } from "@/store/theme";

// More on how to set up stories at: https://storybook.js.org/docs/vue/writing-stories/introduction
export default {
	title: "UI/GlassyButton",
	component: GlassyButton,
	tags: ["autodocs"],
	argTypes: {
		// Slot content control
		default: {
			control: "text",
			description: "The content to display inside the button slot.",
			name: "slotContent", // Rename for clarity in controls panel
		},
		// Prop controls
		themeColor: {
			control: { type: "select" },
			options: ["blue", "indigo", "green", "orange", "yellow", "danger"],
			description: "The color theme of the button.",
		},
		disabled: {
			control: "boolean",
			description: "Whether the button is disabled.",
		},
	},
	// Use a render function to pass props and slot content via args
	render: (args) => ({
		components: { GlassyButton },
		setup() {
			return { args };
		},
		template:
			'<GlassyButton :themeColor="args.themeColor" :disabled="args.disabled">{{ args.slotContent }}</GlassyButton>',
	}),
};

// Story that allows playing with all controls
export const Primary = {
	args: {
		slotContent: "Interactive Button",
		themeColor: "blue",
		disabled: false,
	},
};

// Story to display all color variants
export const AllColors = {
	render: () => ({
		components: { GlassyButton },
		setup() {
			const themeStore = useThemeStore();
			const colors = themeStore.availableThemes;
			return { colors };
		},
		template: `
      <div class="flex flex-wrap items-center gap-4">
        <GlassyButton v-for="color in colors" :key="color" :themeColor="color">
          {{ color.charAt(0).toUpperCase() + color.slice(1) }}
        </GlassyButton>
      </div>
    `,
	}),
	// We don't need args from the controls panel for this story
	argTypes: {
		slotContent: { table: { disable: true } },
		default: { table: { disable: true } },
		themeColor: { table: { disable: true } },
		disabled: { table: { disable: true } },
	},
};

// Story for the disabled state
export const Disabled = {
	args: {
		slotContent: "Disabled Button",
		disabled: true,
		themeColor: "blue",
	},
};

// Story with complex content (icon)
export const WithIcon = {
	args: {
		slotContent: "Save Changes",
		themeColor: "green",
		disabled: false,
	},
	render: (args) => ({
		components: { GlassyButton },
		setup() {
			return { args };
		},
		template: `
      <GlassyButton :themeColor="args.themeColor" :disabled="args.disabled">
        <span class="flex items-center justify-center">
          💾
          <span class="ml-2">{{ args.slotContent }}</span>
        </span>
      </GlassyButton>
    `,
	}),
};
