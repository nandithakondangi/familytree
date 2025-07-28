import type { Meta, StoryFn } from "@storybook/vue3";
import GlassyTextbox from "./GlassyTextbox.vue";

// ----- default export with metadata ----- //
const meta: Meta<typeof GlassyTextbox> = {
    title: "UI/GlassyTextbox",
    component: GlassyTextbox,
    argTypes: {
        modelValue: {
            control: "text",
            description: "Textbox value (v-model)",
            table: { category: "Props" },
        },
        placeholder: {
            control: "text",
            description: "Placeholder text",
            table: { category: "Props" },
        },
        themeColor: {
            control: {
                type: "select",
                options: ["blue", "indigo", "green", "orange", "yellow", "danger"],
            },
            description: "Color theme variant",
            table: { category: "Props" },
        },
        size: {
            control: { type: "select", options: ["sm", "md", "lg"] },
            description: "Size variant",
            table: { category: "Props" },
        },
        disabled: {
            control: "boolean",
            description: "Disable interaction",
            table: { category: "Props" },
        },
    },
    args: {
        modelValue: "",
        placeholder: "Type something...",
        themeColor: "indigo",
        size: "md",
        disabled: false,
    },
    tags: ["autodocs"],
};
export default meta;

// ----- Template definition ----- //
const Template: StoryFn<typeof GlassyTextbox> = (args) => ({
    components: { GlassyTextbox },
    setup() {
        return { args };
    },
    template: `<GlassyTextbox v-bind="args" v-model="args.modelValue" />`,
});

// ----- Stories ----- //
export const Default = Template.bind({});
Default.args = {
    placeholder: "Enter text...",
};

export const Disabled = Template.bind({});
Disabled.args = {
    disabled: true,
    modelValue: "Can't edit...",
};

export const ColorVariants: StoryFn<typeof GlassyTextbox> = () => ({
    components: { GlassyTextbox },
    template: `
    <div class="space-y-4">
      <GlassyTextbox v-model="blue" themeColor="blue" placeholder="Blue" />
      <GlassyTextbox v-model="indigo" themeColor="indigo" placeholder="Indigo (default)" />
      <GlassyTextbox v-model="green" themeColor="green" placeholder="Green" />
      <GlassyTextbox v-model="orange" themeColor="orange" placeholder="Orange" />
      <GlassyTextbox v-model="yellow" themeColor="yellow" placeholder="Yellow" />
      <GlassyTextbox v-model="danger" themeColor="danger" placeholder="Danger" />
    </div>
  `,
    setup() {
        return {
            blue: "",
            indigo: "",
            green: "",
            orange: "",
            yellow: "",
            danger: "",
        };
    },
});

export const Sizes: StoryFn<typeof GlassyTextbox> = () => ({
    components: { GlassyTextbox },
    template: `
    <div class="space-y-4">
      <GlassyTextbox v-model="sm" size="sm" placeholder="Small" />
      <GlassyTextbox v-model="md" size="md" placeholder="Medium (default)" />
      <GlassyTextbox v-model="lg" size="lg" placeholder="Large" />
    </div>
  `,
    setup() {
        return {
            sm: "",
            md: "",
            lg: "",
        };
    },
}); 