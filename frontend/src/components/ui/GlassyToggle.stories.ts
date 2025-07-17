import type { Meta, StoryFn } from "@storybook/vue3";
import { ref } from "vue";
import GlassyToggle from "./GlassyToggle.vue";
import { useThemeStore } from "@/store/theme";

// ----- default export with metadata ----- //
const meta: Meta<typeof GlassyToggle> = {
    title: "UI/GlassyToggle",
    component: GlassyToggle,
    argTypes: {
        modelValue: { control: "boolean", description: "Toggle state (v-model)" },
        themeColor: {
            control: {
                type: "select",
                options: ["blue", "indigo", "green", "orange", "yellow", "danger"],
            },
            description: "Color theme variant",
        },
        size: {
            control: { type: "select", options: ["sm", "md", "lg"] },
            description: "Size variant",
        },
        disabled: { control: "boolean" },
    },
    args: {
        modelValue: false,
        themeColor: "indigo",
        size: "md",
        disabled: false,
    },
    tags: ["autodocs"],
};
export default meta;

// ----- Template definition ----- //
const Template: StoryFn<typeof GlassyToggle> = (args) => ({
    components: { GlassyToggle },
    setup() {
        return { args };
    },
    template: `<GlassyToggle v-bind="args" v-model="args.modelValue" />`,
});

// ----- Stories ----- //
export const Default = Template.bind({});
Default.args = {
    modelValue: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
    disabled: true,
};

export const ColorVariants: StoryFn<typeof GlassyToggle> = () => ({
    components: { GlassyToggle },
    template: `
    <div class="space-y-4">
      <div v-for="color in colors" :key="color" class="flex items-center space-x-4">
        <GlassyToggle v-model="toggles[color]" :themeColor="color" />
        <span class="text-sm">{{ color.charAt(0).toUpperCase() + color.slice(1) }}</span>
      </div>
    </div>
  `,
    setup() {
        const themeStore = useThemeStore();
        const colors = themeStore.availableThemes;
        const toggles = ref(colors.reduce((acc, color) => ({ ...acc, [color]: false }), {}));
        return { colors, toggles };
    },
});

export const Sizes: StoryFn<typeof GlassyToggle> = () => ({
    components: { GlassyToggle },
    template: `
    <div class="flex flex-col space-y-4">
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="sm" size="sm" />
        <span class="text-sm">Small</span>
      </div>
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="md" size="md" />
        <span class="text-sm">Medium (default)</span>
      </div>
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="lg" size="lg" />
        <span class="text-sm">Large</span>
      </div>
    </div>
  `,
    setup() {
        return {
            sm: false,
            md: false,
            lg: false,
        };
    },
}); 