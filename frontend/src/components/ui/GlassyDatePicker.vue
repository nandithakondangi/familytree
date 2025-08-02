<template>
  <!-- Wrapper provides padding for bubble effect -->
  <label
    class="relative inline-block select-none group"
    :class="wrapperSizeClasses"
  >
    <!-- Date picker input -->
    <DatePicker
      v-model:value="internalValue"
      :type="type"
      :format="format"
      :value-type="valueType"
      :placeholder="placeholder"
      :editable="editable"
      :disabled-date="disabledDate"
      :clearable="clearable"
      :disabled="disabled"
      :class="datePickerClasses"
      :input-class="inputClasses"
      :popup-class="popupClasses"
    />

    <!-- Glassy backdrop -->
    <div aria-hidden="true" :class="backdropClasses" style="z-index: 1;"></div>
  </label>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import DatePicker from "vue-datepicker-next";
import "vue-datepicker-next/index.css";
import { useThemeStore } from '@/store/theme';

// --------- PROPS & EMITS --------- //
const props = defineProps({
  /**
   * v-model value
   */
  modelValue: {
    type: [String, Date, null],
    default: null,
  },
  /**
   * Date picker type
   */
  type: {
    type: String,
    default: "date",
    validator: (value) => ["date", "datetime", "time", "month", "year"].includes(value),
  },
  /**
   * Date format
   */
  format: {
    type: String,
    default: "YYYY-MM-DD",
  },
  /**
   * Value type
   */
  valueType: {
    type: String,
    default: "format",
    validator: (value) => ["format", "timestamp", "date"].includes(value),
  },
  /**
   * Placeholder text
   */
  placeholder: {
    type: String,
    default: "Select date",
  },
  /**
   * Whether input is editable
   */
  editable: {
    type: Boolean,
    default: true,
  },
  /**
   * Function to disable specific dates
   */
  disabledDate: {
    type: Function,
    default: undefined,
  },
  /**
   * Whether to show clear button
   */
  clearable: {
    type: Boolean,
    default: true,
  },
  /**
   * Color theme – matches other Glassy components
   */
  themeColor: {
    type: String,
    default: "indigo",
    validator: (value) =>
      [
        "blue",
        "indigo",
        "green",
        "orange",
        "yellow",
        "danger",
      ].includes(value),
  },
  /**
   * Size variant
   */
  size: {
    type: String,
    default: "md",
    validator: (value) => ["sm", "md", "lg"].includes(value),
  },
  /**
   * Disable interaction
   */
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue"]);

const internalValue = ref(props.modelValue);

watch(() => props.modelValue, (newValue) => {
  internalValue.value = newValue;
});

watch(internalValue, (newValue) => {
  emit("update:modelValue", newValue);
});


// --------- CLASS COMPOSITION --------- //

// Wrapper padding for hover bubble effect
const wrapperSizeMap = {
  sm: "p-1",
  md: "p-1.5",
  lg: "p-2",
};

const wrapperSizeClasses = computed(
  () => wrapperSizeMap[props.size] || wrapperSizeMap.md
);

// Input height & typography sizing
const inputSizeMap = {
  sm: "h-8 text-sm",
  md: "h-10 text-base",
  lg: "h-12 text-lg",
};

// Get theme definitions from store
const themeStore = useThemeStore();
const datePickerTheme = computed(() =>
  themeStore.getThemeClasses('GlassyDatePicker', props.themeColor)
);

// Backdrop base classes (radial gradient + blur)
const backdropBaseClasses =
  "absolute inset-0 rounded-lg border border-white/20 shadow-inner backdrop-blur-md transition-all duration-300 ease-out bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white/40 to-transparent";

const backdropStateClasses = computed(() =>
  props.disabled
    ? "opacity-50 cursor-not-allowed"
    : "group-hover:scale-105 group-active:scale-105"
);

const backdropClasses = computed(() => {
  const backdropColor = datePickerTheme.value?.backdrop || 'bg-indigo-500/10 dark:bg-indigo-400/10 group-focus-within:bg-indigo-500/20 dark:group-focus-within:bg-indigo-400/20';
  return `${backdropBaseClasses} ${backdropColor} ${backdropStateClasses.value}`;
});

// Date picker container classes
const datePickerClasses = computed(() => {
  const size = inputSizeMap[props.size] || inputSizeMap.md;
  return `relative z-20 w-full ${size}`;
});

// Input classes
const inputBaseClasses =
  "w-full px-3 rounded-lg bg-transparent transition-all duration-300 ease-out focus:placeholder-opacity-40 outline-none border-0";

const inputStateClasses = computed(() =>
  props.disabled ? "cursor-not-allowed opacity-60" : "group-hover:translate-y-0.5 group-active:-translate-y-0.5"
);

const inputClasses = computed(() => {
  const textColors = datePickerTheme.value?.text || 'text-indigo-800 dark:text-indigo-100 placeholder-indigo-600/70 dark:placeholder-indigo-400/60';
  return `${inputBaseClasses} ${inputStateClasses.value} ${textColors}`;
});

// Popup classes
const popupClasses = computed(() => {
  const popupColor = datePickerTheme.value?.popup || '';
  return `rounded-lg shadow-lg backdrop-blur-md ${popupColor}`;
});
</script>

<style scoped>
/* Override default datepicker styles to work with our glassy design */
:deep(.mx-input) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: inherit !important;
  position: relative !important;
  z-index: 20 !important;
}

:deep(.mx-input:focus) {
  box-shadow: none !important;
  border: none !important;
  color: inherit !important;
}

:deep(.mx-datepicker-popup) {
  backdrop-filter: blur(12px);
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

:deep(.mx-calendar) {
  background: transparent !important;
}

:deep(.mx-calendar-header) {
  background: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.mx-calendar-content) {
  background: transparent !important;
}

:deep(.mx-table) {
  background: transparent !important;
}

:deep(.mx-table th) {
  background: transparent !important;
  border: none !important;
  color: inherit !important;
}

:deep(.mx-table td) {
  background: transparent !important;
  border: none !important;
}

:deep(.mx-table .cell) {
  background: transparent !important;
  border-radius: 0.375rem;
  transition: all 0.2s ease-in-out;
}

:deep(.mx-table .cell:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
}

:deep(.mx-table .cell.active) {
  background: rgba(99, 102, 241, 0.2) !important;
  color: inherit !important;
}

:deep(.mx-table .cell.today) {
  background: rgba(99, 102, 241, 0.1) !important;
  color: inherit !important;
}

:deep(.mx-table .cell.disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Theme-specific overrides */
:deep(.mx-table .cell.active) {
  background: var(--theme-active-bg, rgba(99, 102, 241, 0.2)) !important;
}

:deep(.mx-table .cell.today) {
  background: var(--theme-today-bg, rgba(99, 102, 241, 0.1)) !important;
}
</style>