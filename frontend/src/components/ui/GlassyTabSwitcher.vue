<template>
  <div 
    class="relative w-full px-2 py-1.5 rounded-full border border-white/20 shadow-lg backdrop-blur-md transition-all duration-300 ease-out overflow-hidden"
    :class="containerColorClasses"
  >
    <!-- Inner shadow overlay for beveled effect -->
    <div class="absolute inset-0 rounded-full shadow-[inset_0_2px_4px_0_rgba(0,0,0,0.2)] dark:shadow-[inset_0_2px_8px_0_rgba(0,0,0,0.5)] pointer-events-none"></div>
    
    <!-- Container for tab titles -->
    <div class="relative flex items-center justify-center w-full">
      <button
        v-for="(tab, index) in tabs"
        :key="tab.title"
        :ref="el => { if (el) tabRefs[index] = el }"
        class="relative flex-1 py-2 text-sm font-medium transition-all duration-300 z-10 text-center active:scale-95"
        :class="[
          textColorClasses,
          { 'scale-125': index === activeIndex }
        ]"
        @click="$emit('update:activeIndex', index)"
      >
        {{ tab.title }}
      </button>

      <!-- Sliding bubble indicator -->
      <div
        class="absolute top-0 left-0 h-full rounded-full transition-all duration-300"
        :class="bubbleColorClasses"
        :style="bubbleStyle"
      >
        <!-- Shine effect for the bubble -->
        <div class="absolute inset-0 rounded-full bg-gradient-to-b from-white/30 to-transparent opacity-50"></div>
        <!-- Magnifying glass effect overlay -->
        <div class="absolute inset-0 rounded-full backdrop-blur-[1px] backdrop-brightness-110"></div>
      </div>
    </div>

    <!-- Shine effect for the container -->
    <div 
      class="absolute inset-0 rounded-full bg-gradient-to-b from-white/20 to-transparent opacity-60"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps({
  tabs: {
    type: Array,
    required: true,
    validator: (value) => value.every(tab => 'title' in tab),
  },
  activeIndex: {
    type: Number,
    required: true
  },
  themeColor: {
    type: String,
    default: "indigo",
    validator: (value) =>
      ["blue", "indigo", "green", "orange", "yellow", "danger"].includes(value),
  }
});

const emit = defineEmits(['update:activeIndex']);

const tabRefs = ref([]);
const prevActiveIndex = ref(props.activeIndex);

// Color variants for different theme colors
const colorVariants = {
  blue: {
    container: 'bg-blue-500/10 dark:bg-blue-400/10',
    text: 'text-blue-900 dark:text-blue-100',
    bubble: 'bg-blue-500/5 dark:bg-blue-400/5'
  },
  indigo: {
    container: 'bg-indigo-500/10 dark:bg-indigo-400/10',
    text: 'text-indigo-900 dark:text-indigo-100',
    bubble: 'bg-indigo-500/5 dark:bg-indigo-400/5'
  },
  green: {
    container: 'bg-green-500/10 dark:bg-green-400/10',
    text: 'text-green-900 dark:text-green-100',
    bubble: 'bg-green-500/5 dark:bg-green-400/5'
  },
  orange: {
    container: 'bg-orange-500/10 dark:bg-orange-400/10',
    text: 'text-orange-900 dark:text-orange-100',
    bubble: 'bg-orange-500/5 dark:bg-orange-400/5'
  },
  yellow: {
    container: 'bg-yellow-500/10 dark:bg-yellow-400/10',
    text: 'text-yellow-900 dark:text-yellow-100',
    bubble: 'bg-yellow-500/5 dark:bg-yellow-400/5'
  },
  danger: {
    container: 'bg-red-500/10 dark:bg-red-400/10',
    text: 'text-red-900 dark:text-red-100',
    bubble: 'bg-red-500/5 dark:bg-red-400/5'
  }
};

const containerColorClasses = computed(() => 
  colorVariants[props.themeColor]?.container
);

const textColorClasses = computed(() => 
  colorVariants[props.themeColor]?.text
);

const bubbleColorClasses = computed(() => 
  colorVariants[props.themeColor]?.bubble
);

// Computed style for the sliding bubble
const bubbleStyle = computed(() => {
  if (!tabRefs.value[props.activeIndex]) {
    return { 
      left: '0px', 
      width: '0px', 
      opacity: '0', 
      transform: 'scale(1)',
      transition: 'none' 
    };
  }

  const activeEl = tabRefs.value[props.activeIndex];
  const { offsetLeft, clientWidth } = activeEl;
  const isMovingRight = props.activeIndex > prevActiveIndex.value;

  return {
    left: `${offsetLeft}px`,
    width: `${clientWidth}px`,
    opacity: '1',
    transform: 'scale(1.15)', // More pronounced magnifying effect
    transition: `all 400ms cubic-bezier(0.34, 1.25, 0.64, 1), 
                transform 300ms cubic-bezier(0.4, 0, 0.2, 1) 100ms` // Reduced bounce overshoot
  };
});

// Update prev index for animation direction
watch(() => props.activeIndex, (newVal) => {
  prevActiveIndex.value = props.activeIndex;
});
</script>
