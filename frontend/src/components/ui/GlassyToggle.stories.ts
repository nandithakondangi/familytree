import type { Meta, StoryFn } from "@storybook/vue3";
import GlassyToggle from "./GlassyToggle.vue";

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
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="blue" themeColor="blue" />
        <span class="text-sm">Blue</span>
      </div>
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="indigo" themeColor="indigo" />
        <span class="text-sm">Indigo (default)</span>
      </div>
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="green" themeColor="green" />
        <span class="text-sm">Green</span>
      </div>
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="orange" themeColor="orange" />
        <span class="text-sm">Orange</span>
      </div>
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="yellow" themeColor="yellow" />
        <span class="text-sm">Yellow</span>
      </div>
      <div class="flex items-center space-x-4">
        <GlassyToggle v-model="danger" themeColor="danger" />
        <span class="text-sm">Danger (red)</span>
      </div>
    </div>
  `,
    setup() {
        return {
            blue: false,
            indigo: false,
            green: false,
            orange: false,
            yellow: false,
            danger: false,
        };
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