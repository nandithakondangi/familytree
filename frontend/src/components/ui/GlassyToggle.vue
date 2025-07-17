<template>
  <label
    class="relative inline-flex items-center select-none group"
    :class="wrapperSizeClasses"
  >
    <!-- Hidden checkbox to control state -->
    <input
      type="checkbox"
      class="sr-only peer"
      :checked="modelValue"
      :disabled="disabled"
      @change="onToggle"
    />

    <!-- Track -->
    <div :class="trackClasses"></div>

    <!-- Thumb -->
    <span :class="thumbClasses"></span>
  </label>
</template>

<script setup>
import { computed } from "vue";
import { useThemeStore } from "@/store/theme";

const props = defineProps({
  /**
   * v-model value
   */
  modelValue: {
    type: Boolean,
    default: false,
  },
  /**
   * Color theme – matches GlassButton themes
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
const themeStore = useThemeStore();

function onToggle(event) {
  emit("update:modelValue", event.target.checked);
}

// ---------- CLASS COMPOSITION ---------- //

// Base wrapper sizes (padding around the track for bubble hover effect)
const wrapperSizeMap = {
  sm: "p-1",
  md: "p-1.5",
  lg: "p-2",
};

const wrapperSizeClasses = computed(() => wrapperSizeMap[props.size] || wrapperSizeMap.md);

// Track size map (width/height)
const trackSizeMap = {
  sm: "w-9 h-5",
  md: "w-11 h-6",
  lg: "w-14 h-7",
};

// Thumb sizing / positioning map (size, left offset, and translate distance)
const thumbSizeMap = {
  sm: {
    size: "w-4 h-4",
    left: "left-1.5", // increased to 0.375rem to give track outline breathing room
    translate: "peer-checked:translate-x-4", // reduced to 1rem to maintain gap at right edge
  },
  md: {
    size: "w-5 h-5",
    left: "left-2", // increase offset to 0.5rem for extra spacing
    translate: "peer-checked:translate-x-5", // 1.25rem shift to keep symmetric gap
  },
  lg: {
    size: "w-6 h-6",
    left: "left-[10px]", // ~0.625rem offset for balanced spacing
    translate: "peer-checked:translate-x-7", // 1.75rem shift to align with new offset
  },
};

const trackBaseClasses =
  "relative rounded-full border border-white/20 shadow-inner backdrop-blur-md transition-all duration-300 ease-out bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white/40 to-transparent";

const trackStateClasses = props.disabled
  ? "opacity-50 cursor-not-allowed"
  : "group-hover:scale-110 group-active:scale-95";

const trackClasses = computed(() => {
  const size = trackSizeMap[props.size] || trackSizeMap.md;
  const color = themeStore.getThemeClasses("GlassyToggle", props.themeColor);
  return `${trackBaseClasses} ${size} ${color} ${trackStateClasses}`;
});

// Thumb classes
const thumbBaseClasses =
  "absolute top-1/2 -translate-y-1/2 rounded-full bg-white/80 dark:bg-white/60 shadow-lg backdrop-blur-md transition-all duration-300 ease-out";

const thumbClasses = computed(() => {
  const { size, left, translate } = thumbSizeMap[props.size] || thumbSizeMap.md;
  const state = props.disabled ? "opacity-50" : "group-hover:shadow-xl group-active:scale-90";
  return `${thumbBaseClasses} ${size} ${left} ${translate} ${state}`;
});
</script> 