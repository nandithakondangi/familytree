<template>
  <!-- Wrapper provides padding for bubble effect -->
  <label
    class="relative inline-block select-none group"
    :class="wrapperSizeClasses"
  >
    <!-- Actual text input -->
    <input
      type="text"
      class="relative z-10 w-full bg-transparent outline-none placeholder-white/50 dark:placeholder-white/40 peer"
      :class="inputClasses"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="onInput"
    />

    <!-- Glassy backdrop -->
    <div aria-hidden="true" :class="backdropClasses"></div>
  </label>
</template>

<script setup>
import { computed } from "vue";
import { useThemeStore } from '@/store/theme';

// --------- PROPS & EMITS --------- //
const props = defineProps({
  /**
   * v-model value
   */
  modelValue: {
    type: String,
    default: "",
  },
  /**
   * Placeholder text for the input
   */
  placeholder: {
    type: String,
    default: "",
  },
  /**
   * Color theme – matches GlassyToggle themes
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

function onInput(event) {
  emit("update:modelValue", event.target.value);
}

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
const textboxTheme = computed(() =>
  themeStore.getThemeClasses('GlassyTextbox', props.themeColor)
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
  const backdropColor = textboxTheme.value?.backdrop || 'bg-indigo-500/10 dark:bg-indigo-400/10 group-focus-within:bg-indigo-500/20 dark:group-focus-within:bg-indigo-400/20';
  return `${backdropBaseClasses} ${backdropColor} ${backdropStateClasses.value}`;
});

// Input classes
const inputBaseClasses =
  "w-full px-3 rounded-lg bg-transparent transition-all duration-300 ease-out focus:placeholder-opacity-40 outline-none";

const inputStateClasses = computed(() =>
  props.disabled ? "cursor-not-allowed opacity-60" : "group-hover:translate-y-0.5 group-active:-translate-y-0.5"
);

const inputClasses = computed(() => {
  const size = inputSizeMap[props.size] || inputSizeMap.md;
  const textColors = textboxTheme.value?.text || 'text-indigo-800 dark:text-indigo-100 placeholder-indigo-600/70 dark:placeholder-indigo-400/60';
  return `${inputBaseClasses} ${size} ${inputStateClasses.value} ${textColors}`;
});
</script> 