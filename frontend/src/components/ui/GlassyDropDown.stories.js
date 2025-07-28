import { ref } from 'vue';
import GlassyDropDown from './GlassyDropDown.vue';

export default {
    title: 'UI/GlassyDropDown',
    component: GlassyDropDown,
    argTypes: {
        themeColor: {
            control: 'select',
            options: ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger'],
            defaultValue: 'indigo',
        },
        width: {
            control: 'text',
            description: 'Custom width (e.g., "200px", "50%"). Leave empty for auto-sizing.',
        },
    },
    tags: ['autodocs'],
};

const Template = (args) => ({
    components: { GlassyDropDown },
    setup() {
        const selected = ref(null);
        return { args, selected };
    },
    template: `
    <div class="p-4">
      <GlassyDropDown v-model="selected" v-bind="args" />
      <p class="mt-4 text-sm text-gray-500">Selected: {{ selected }}</p>
    </div>
  `,
});

export const Default = Template.bind({});
Default.args = {
    options: ['Option 1', 'Option 2', 'Option 3'],
};

export const WithObjects = Template.bind({});
WithObjects.args = {
    options: [
        { label: 'First', value: 'first' },
        { label: 'Second', value: 'second' },
        { label: 'Third', value: 'third' },
    ],
};

export const Scrollable = Template.bind({});
Scrollable.args = {
    options: [
        'Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5',
        'Option 6', 'Option 7', 'Option 8', 'Option 9', 'Option 10',
        'Option 11', 'Option 12', 'Option 13', 'Option 14', 'Option 15'
    ],
    scrollable: true,
    maxHeight: '12rem',
};

export const ScrollableLarge = Template.bind({});
ScrollableLarge.args = {
    options: [
        'Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5',
        'Item 6', 'Item 7', 'Item 8', 'Item 9', 'Item 10',
        'Item 11', 'Item 12', 'Item 13', 'Item 14', 'Item 15',
        'Item 16', 'Item 17', 'Item 18', 'Item 19', 'Item 20'
    ],
    scrollable: true,
    maxHeight: '20rem',
};

export const ColorVariants = () => ({
    components: { GlassyDropDown },
    setup() {
        const selectedValues = ref({});
        const colors = ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger'];
        const opts = ['One', 'Two', 'Three'];
        colors.forEach((c) => (selectedValues.value[c] = null));
        return { colors, opts, selectedValues };
    },
    template: `
    <div class="space-y-4">
      <GlassyDropDown
        v-for="color in colors"
        :key="color"
        :theme-color="color"
        :options="opts"
        v-model="selectedValues[color]"
      />
    </div>
  `,
});

export const AutoSizing = () => ({
    components: { GlassyDropDown },
    setup() {
        const selected1 = ref(null);
        const selected2 = ref(null);
        const selected3 = ref(null);
        const selected4 = ref(null);
        return { selected1, selected2, selected3, selected4 };
    },
    template: `
    <div class="space-y-4 p-4">
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Short options:</h3>
        <GlassyDropDown
          :options="['A', 'B', 'C']"
          v-model="selected1"
          placeholder="Select..."
        />
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Medium options:</h3>
        <GlassyDropDown
          :options="['Short', 'Medium length option', 'Another option']"
          v-model="selected2"
          placeholder="Choose an option..."
        />
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Long options:</h3>
        <GlassyDropDown
          :options="[
            'Very long option text that should make the dropdown wider',
            'Another very long option with lots of text content',
            'Short'
          ]"
          v-model="selected3"
          placeholder="Select a very long option..."
        />
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Extremely long options:</h3>
        <GlassyDropDown
          :options="[
            'This is an extremely long option text that contains many words and should demonstrate how the dropdown handles very long content that might exceed normal expectations for dropdown option lengths',
            'Another incredibly long option with even more text content that goes on and on to test the maximum width calculation and ensure the component can handle edge cases properly',
            'Short option for contrast'
          ]"
          v-model="selected4"
          placeholder="Select an extremely long option to test auto-sizing limits..."
        />
      </div>
    </div>
  `,
});

export const CustomWidth = () => ({
    components: { GlassyDropDown },
    setup() {
        const selected = ref(null);
        return { selected };
    },
    template: `
    <div class="space-y-4 p-4">
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Auto-sized (default):</h3>
        <GlassyDropDown
          :options="['Short', 'Medium length option', 'Very long option text']"
          v-model="selected"
          placeholder="Auto-sized dropdown"
        />
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Custom width (300px):</h3>
        <GlassyDropDown
          :options="['Short', 'Medium length option', 'Very long option text']"
          v-model="selected"
          placeholder="Custom width dropdown"
          width="300px"
        />
      </div>
    </div>
  `,
});

export const ExtremeLongStrings = () => ({
    components: { GlassyDropDown },
    setup() {
        const selected1 = ref(null);
        const selected2 = ref(null);
        return { selected1, selected2 };
    },
    template: `
    <div class="space-y-4 p-4">
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Super long single option:</h3>
        <GlassyDropDown
          :options="[
            'This is an absolutely massive option text that goes on for what seems like forever with many many words and characters to really push the limits of what the auto-sizing algorithm can handle when calculating the optimal width for the dropdown component'
          ]"
          v-model="selected1"
          placeholder="Select the super long option..."
        />
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg">
        <h3 class="text-sm font-medium mb-2">Multiple extremely long options:</h3>
        <GlassyDropDown
          :options="[
            'First option with incredibly long text that contains many sentences and should demonstrate the maximum width calculation capabilities of the dropdown component',
            'Second option that is even longer than the first one with additional content that goes beyond normal expectations for dropdown option lengths',
            'Third option with maximum length text that includes technical terms, descriptions, and detailed explanations to test edge cases'
          ]"
          v-model="selected2"
          placeholder="Choose from extremely long options..."
        />
      </div>
    </div>
  `,
});

export const ParentWidthConstraint = () => ({
    components: { GlassyDropDown },
    setup() {
        const selected1 = ref(null);
        const selected2 = ref(null);
        const selected3 = ref(null);
        return { selected1, selected2, selected3 };
    },
    template: `
    <div class="space-y-4 p-4">
      <div class="border border-gray-200 p-4 rounded-lg" style="width: 300px;">
        <h3 class="text-sm font-medium mb-2">Auto-detected constraint (300px):</h3>
        <GlassyDropDown
          :options="[
            'This is a very long option that would normally make the dropdown much wider',
            'Another extremely long option with lots of text content that exceeds normal dropdown widths',
            'Short option'
          ]"
          v-model="selected1"
          placeholder="Long options in narrow container..."
        />
        <p class="text-xs text-gray-500 mt-2">Auto-detected parent width constraint</p>
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg" style="width: 200px;">
        <h3 class="text-sm font-medium mb-2">Very narrow parent (200px):</h3>
        <GlassyDropDown
          :options="[
            'Super long option that would normally be much wider than this container',
            'Another option with extensive text content',
            'Short'
          ]"
          v-model="selected2"
          placeholder="In narrow container..."
        />
        <p class="text-xs text-gray-500 mt-2">Auto-detected narrow constraint</p>
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg" style="width: 500px;">
        <h3 class="text-sm font-medium mb-2">Wide parent (500px) with long options:</h3>
        <GlassyDropDown
          :options="[
            'This option has moderate length but the parent container is quite wide',
            'Another option with some length to it',
            'Short option for contrast'
          ]"
          v-model="selected3"
          placeholder="Wide container with options..."
        />
        <p class="text-xs text-gray-500 mt-2">Uses content-based sizing since container is wide enough</p>
      </div>
    </div>
  `,
});

export const AutoDetectParentWidth = () => ({
    components: { GlassyDropDown },
    setup() {
        const selected1 = ref(null);
        const selected2 = ref(null);
        const selected3 = ref(null);
        const selected4 = ref(null);
        return { selected1, selected2, selected3, selected4 };
    },
    template: `
    <div class="space-y-4 p-4">
      <div class="border border-gray-200 p-4 rounded-lg" style="width: 250px;">
        <h3 class="text-sm font-medium mb-2">Auto-detected constraint (250px container):</h3>
        <GlassyDropDown
          :options="[
            'This is a very long option that would normally make the dropdown much wider than 250px',
            'Another extremely long option with lots of text content that exceeds the container width',
            'Short option'
          ]"
          v-model="selected1"
          placeholder="Auto-detected parent width..."
        />
        <p class="text-xs text-gray-500 mt-2">No parentWidth prop needed - auto-detected!</p>
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg" style="max-width: 180px;">
        <h3 class="text-sm font-medium mb-2">Auto-detected max-width (180px):</h3>
        <GlassyDropDown
          :options="[
            'Super long option that would normally be much wider',
            'Another option with extensive text content',
            'Short'
          ]"
          v-model="selected2"
          placeholder="Max-width constraint..."
        />
        <p class="text-xs text-gray-500 mt-2">Detects max-width CSS property</p>
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg" style="width: 400px;">
        <h3 class="text-sm font-medium mb-2">Wide container (400px) with moderate options:</h3>
        <GlassyDropDown
          :options="[
            'This option has moderate length',
            'Another option with some length to it',
            'Short option for contrast'
          ]"
          v-model="selected3"
          placeholder="Wide container..."
        />
        <p class="text-xs text-gray-500 mt-2">Uses content-based sizing since container is wide enough</p>
      </div>
      
      <div class="border border-gray-200 p-4 rounded-lg" style="width: 300px;">
        <h3 class="text-sm font-medium mb-2">Responsive container (300px):</h3>
        <GlassyDropDown
          :options="[
            'Very long option that would exceed the container',
            'Another long option with lots of text',
            'Short'
          ]"
          v-model="selected4"
          placeholder="Responsive container..."
        />
        <p class="text-xs text-gray-500 mt-2">Auto-detects and adapts to container changes</p>
      </div>
    </div>
  `,
}); 