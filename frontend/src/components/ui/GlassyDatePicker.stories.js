import GlassyDatePicker from './GlassyDatePicker.vue';

export default {
    title: 'UI/GlassyDatePicker',
    component: GlassyDatePicker,
    parameters: {
        docs: {
            description: {
                component: 'A glassy-styled date picker component that wraps vue-datepicker-next with consistent theming and animations.',
            },
        },
    },
    argTypes: {
        modelValue: {
            control: 'text',
            description: 'The selected date value (v-model)',
        },
        type: {
            control: { type: 'select' },
            options: ['date', 'datetime', 'time', 'month', 'year'],
            description: 'The type of date picker',
        },
        format: {
            control: 'text',
            description: 'The date format string',
        },
        valueType: {
            control: { type: 'select' },
            options: ['format', 'timestamp', 'date'],
            description: 'The type of value to return',
        },
        placeholder: {
            control: 'text',
            description: 'Placeholder text for the input',
        },
        editable: {
            control: 'boolean',
            description: 'Whether the input is editable',
        },
        clearable: {
            control: 'boolean',
            description: 'Whether to show a clear button',
        },
        themeColor: {
            control: { type: 'select' },
            options: ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger'],
            description: 'Color theme for the component',
        },
        size: {
            control: { type: 'select' },
            options: ['sm', 'md', 'lg'],
            description: 'Size variant of the component',
        },
        disabled: {
            control: 'boolean',
            description: 'Whether the component is disabled',
        },
    },
};

// Base story
export const Default = {
    args: {
        modelValue: '',
        placeholder: 'Select a date',
        themeColor: 'indigo',
        size: 'md',
        disabledDate: undefined,
    },
};

// Different themes
export const Themes = {
    render: (args) => ({
        components: { GlassyDatePicker },
        setup() {
            return { args };
        },
        template: `
      <div class="space-y-4 p-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <h3 class="text-sm font-medium mb-2">Blue Theme</h3>
            <GlassyDatePicker v-bind="args" theme-color="blue" />
          </div>
          <div>
            <h3 class="text-sm font-medium mb-2">Indigo Theme</h3>
            <GlassyDatePicker v-bind="args" theme-color="indigo" />
          </div>
          <div>
            <h3 class="text-sm font-medium mb-2">Green Theme</h3>
            <GlassyDatePicker v-bind="args" theme-color="green" />
          </div>
          <div>
            <h3 class="text-sm font-medium mb-2">Orange Theme</h3>
            <GlassyDatePicker v-bind="args" theme-color="orange" />
          </div>
          <div>
            <h3 class="text-sm font-medium mb-2">Yellow Theme</h3>
            <GlassyDatePicker v-bind="args" theme-color="yellow" />
          </div>
          <div>
            <h3 class="text-sm font-medium mb-2">Danger Theme</h3>
            <GlassyDatePicker v-bind="args" theme-color="danger" />
          </div>
        </div>
      </div>
    `,
    }),
    args: {
        modelValue: '',
        placeholder: 'Select a date',
        size: 'md',
        disabledDate: undefined,
    },
};

// Different sizes
export const Sizes = {
    render: (args) => ({
        components: { GlassyDatePicker },
        setup() {
            return { args };
        },
        template: `
      <div class="space-y-4 p-4">
        <div>
          <h3 class="text-sm font-medium mb-2">Small</h3>
          <GlassyDatePicker v-bind="args" size="sm" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Medium</h3>
          <GlassyDatePicker v-bind="args" size="md" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Large</h3>
          <GlassyDatePicker v-bind="args" size="lg" />
        </div>
      </div>
    `,
    }),
    args: {
        modelValue: '',
        placeholder: 'Select a date',
        themeColor: 'indigo',
        disabledDate: undefined,
    },
};

// Different types
export const Types = {
    render: (args) => ({
        components: { GlassyDatePicker },
        setup() {
            return { args };
        },
        template: `
      <div class="space-y-4 p-4">
        <div>
          <h3 class="text-sm font-medium mb-2">Date</h3>
          <GlassyDatePicker v-bind="args" type="date" format="YYYY-MM-DD" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Date Time</h3>
          <GlassyDatePicker v-bind="args" type="datetime" format="YYYY-MM-DD HH:mm" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Time</h3>
          <GlassyDatePicker v-bind="args" type="time" format="HH:mm" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Month</h3>
          <GlassyDatePicker v-bind="args" type="month" format="YYYY-MM" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Year</h3>
          <GlassyDatePicker v-bind="args" type="year" format="YYYY" />
        </div>
      </div>
    `,
    }),
    args: {
        modelValue: '',
        placeholder: 'Select a date',
        themeColor: 'indigo',
        size: 'md',
        disabledDate: undefined,
    },
};

// States
export const States = {
    render: (args) => ({
        components: { GlassyDatePicker },
        setup() {
            return { args };
        },
        template: `
      <div class="space-y-4 p-4">
        <div>
          <h3 class="text-sm font-medium mb-2">Default</h3>
          <GlassyDatePicker v-bind="args" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">With Value</h3>
          <GlassyDatePicker v-bind="args" :model-value="'2024-01-15'" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Disabled</h3>
          <GlassyDatePicker v-bind="args" :disabled="true" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Not Editable</h3>
          <GlassyDatePicker v-bind="args" :editable="false" />
        </div>
        <div>
          <h3 class="text-sm font-medium mb-2">Not Clearable</h3>
          <GlassyDatePicker v-bind="args" :clearable="false" />
        </div>
      </div>
    `,
    }),
    args: {
        modelValue: '',
        placeholder: 'Select a date',
        themeColor: 'indigo',
        size: 'md',
        disabledDate: undefined,
    },
};

// Interactive example
export const Interactive = {
    render: (args) => ({
        components: { GlassyDatePicker },
        setup() {
            return { args };
        },
        template: `
      <div class="space-y-4 p-4">
        <div>
          <h3 class="text-sm font-medium mb-2">Interactive Date Picker</h3>
          <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
            Try clicking on the date picker to see the glassy popup in action
          </p>
          <GlassyDatePicker v-bind="args" />
          <p class="text-xs text-gray-500 mt-2">Selected value: {{ args.modelValue || 'None' }}</p>
        </div>
      </div>
    `,
    }),
    args: {
        modelValue: '',
        placeholder: 'Click to select a date',
        themeColor: 'indigo',
        size: 'md',
        disabledDate: undefined,
    },
};

// Debug story
export const Debug = {
    render: (args) => ({
        components: { GlassyDatePicker },
        setup() {
            return { args };
        },
        template: `
      <div class="space-y-4 p-4">
        <div>
          <h3 class="text-sm font-medium mb-2">Debug Date Picker</h3>
          <GlassyDatePicker v-bind="args" />
          <div class="mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs">
            <p>Value: {{ args.modelValue || 'None' }}</p>
            <p>Type: {{ typeof args.modelValue }}</p>
            <p>Length: {{ args.modelValue ? args.modelValue.length : 0 }}</p>
          </div>
        </div>
      </div>
    `,
    }),
    args: {
        modelValue: '',
        placeholder: 'Debug date picker',
        themeColor: 'indigo',
        size: 'md',
        disabledDate: undefined,
    },
}; 