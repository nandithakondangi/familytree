<template>
  <div class="w-fit" ref="containerRef">
    <Listbox v-model="internalValue" :disabled="disabled">
      <div class="relative">
        <!-- Trigger / Selected pill -->
        <ListboxButton
          class="relative flex items-center justify-between rounded-full border border-white/20 shadow-lg backdrop-blur-md bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white/40 to-transparent px-4 py-2 transition-all duration-300 ease-out overflow-hidden data-focus:ring-2 data-focus:ring-indigo-500/50"
          :class="[containerColorClasses, pillStateClasses]"
          :style="{ minWidth: minWidth }"
        >
          <span
            class="truncate text-sm font-medium transition-colors duration-300"
            :class="textColorClasses"
            >{{ selectedLabel }}</span
          >
          <!-- Chevron icon -->
          <svg
            class="w-5 h-5 ml-3 text-gray-700 dark:text-gray-200 transition-transform duration-300 data-open:rotate-180"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          <!-- Inner shine overlay for glassy effect -->
          <div class="absolute inset-0 rounded-full bg-gradient-to-b from-white/20 to-transparent pointer-events-none"></div>
        </ListboxButton>

        <!-- Options -->
        <transition
          enter-active-class="transition transform ease-out duration-200"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition transform ease-in duration-150"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <ListboxOptions
            class="absolute z-10 mt-2 focus:outline-none"
            :class="optionsContainerClasses"
            :style="{ 
              minWidth: minWidth,
              maxHeight: scrollable ? maxHeight : '15rem',
              height: scrollable ? maxHeight : '15rem',
              overflow: 'hidden'
            }"
          >
            <GlassyScrollContainer
              :theme-color="themeColor"
              class="h-full"
            >
              <ListboxOption
                v-for="(option, idx) in normalizedOptions"
                :key="idx"
                :value="option"
                v-slot="{ active, selected }"
                class="relative cursor-pointer select-none py-2 px-4 text-sm transition-all duration-300"
              >
                <div 
                :class="[
                  active ? activeItemClasses : textColorClasses,
                  selected ? selectedItemClasses : '',
                  'transition-all duration-300'
                ]"> {{ optionLabel(option) }} </div>
              </ListboxOption>
            </GlassyScrollContainer>
          </ListboxOptions>
        </transition>
      </div>
    </Listbox>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue';
import { Listbox, ListboxButton, ListboxOptions, ListboxOption } from '@headlessui/vue';
import { useThemeStore } from '@/store/theme';
import GlassyScrollContainer from './GlassyScrollContainer.vue';

const props = defineProps({
  modelValue: {
    type: [String, Number, Object, null],
    default: null,
  },
  options: {
    type: Array,
    required: true,
  },
  placeholder: {
    type: String,
    default: 'Select an option',
  },
  themeColor: {
    type: String,
    default: 'indigo',
    validator: (value) => [
      'blue',
      'indigo',
      'green',
      'orange',
      'yellow',
      'danger',
    ].includes(value),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  scrollable: {
    type: Boolean,
    default: false,
  },
  maxHeight: {
    type: String,
    default: '15rem', // 240px
  },
  width: {
    type: String,
    default: null, // null means auto-fit, otherwise use specified width
  },
});

const emit = defineEmits(['update:modelValue']);

// Container ref for auto-detecting parent width
const containerRef = ref(null);
const detectedParentWidth = ref(null);
let resizeObserver = null;

// Local reactive copy for headlessui v-model
const internalValue = ref(props.modelValue);

watch(
  () => props.modelValue,
  (val) => {
    internalValue.value = val;
  }
);

watch(internalValue, (val) => {
  emit('update:modelValue', val);
});

// Normalize options so we can accept string or object { label, value }
const normalizedOptions = computed(() =>
  props.options.map((o) =>
    typeof o === 'object' ? o : { label: o, value: o }
  )
);

function optionLabel(option) {
  return option.label ?? option.value;
}

const selectedLabel = computed(() => {
  if (!internalValue.value) return props.placeholder;
  
  // Handle both object and primitive values
  const found = normalizedOptions.value.find((opt) => {
    // If internalValue is an object, compare with the option object
    if (typeof internalValue.value === 'object' && internalValue.value !== null) {
      return opt.value === internalValue.value.value;
    }
    // If internalValue is a primitive, compare with option.value
    return opt.value === internalValue.value;
  });
  
  return found ? optionLabel(found) : String(internalValue.value);
});

const themeStore = useThemeStore();
// Get GlassyDropDown theme definitions
const dropdownTheme = computed(() =>
  themeStore.getThemeClasses('GlassyDropDown', props.themeColor)
);

const containerColorClasses = computed(() =>
  dropdownTheme.value?.container || 'bg-indigo-500/10 dark:bg-indigo-400/10'
);
const textColorClasses = computed(() =>
  dropdownTheme.value?.text || 'text-indigo-900 dark:text-indigo-100'
);
const pillStateClasses = computed(() =>
  props.disabled
    ? 'opacity-50 cursor-not-allowed'
    : ''
);
const dataFocusClasses = computed(() => {
  const focusClasses = dropdownTheme.value?.focus || 'data-focus:bg-indigo-500/40 dark:data-focus:bg-indigo-400/40 data-focus:text-indigo-900 dark:data-focus:text-indigo-100 data-focus:ring-2 data-focus:ring-indigo-500/60 data-focus:ring-offset-1';
  return `${focusClasses} data-focus:scale-105 data-focus:font-bold data-focus:shadow-lg data-focus:backdrop-blur-md data-focus:border data-focus:border-white/50 data-focus:bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] data-focus:from-white/40 data-focus:to-transparent`;
});

const dataSelectedClasses = computed(() => {
  return dropdownTheme.value?.selected || 'data-selected:ring-2 data-selected:ring-indigo-500/50';
});

const activeItemClasses = computed(() => {
  const activeClasses = dropdownTheme.value?.active || 'text-indigo-900 dark:text-indigo-100 border-2 border-indigo-500/60';
  return `${activeClasses} scale-105 font-bold shadow-lg backdrop-blur-md bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white/40 to-transparent border border-white/20 rounded-full px-3 py-1 mx-1 ${containerColorClasses.value}`;
});

const selectedItemClasses = computed(() => {
  return dropdownTheme.value?.selectedItem || 'ring-2 ring-indigo-500/50';
});

const optionsContainerClasses = computed(() => {
  return dropdownTheme.value?.optionsContainer || 'bg-white dark:bg-gray-900';
});


// Auto-detect parent container width using ResizeObserver
const setupResizeObserver = () => {
  if (!containerRef.value) return;
  
  // Find the parent element that constrains the width
  let parentElement = containerRef.value.parentElement;
  let maxWidth = null;
  
  // Traverse up the DOM tree to find a parent with a defined width
  while (parentElement && parentElement !== document.body) {
    const computedStyle = window.getComputedStyle(parentElement);
    const width = computedStyle.width;
    const maxWidthStyle = computedStyle.maxWidth;
    
    // Check if parent has a defined width (not auto)
    if (width !== 'auto' && width !== '0px') {
      const widthValue = parseFloat(width);
      if (widthValue > 0) {
        maxWidth = widthValue;
        break;
      }
    }
    
    // Check if parent has a max-width constraint
    if (maxWidthStyle !== 'none' && maxWidthStyle !== '0px') {
      const maxWidthValue = parseFloat(maxWidthStyle);
      if (maxWidthValue > 0) {
        maxWidth = maxWidthValue;
        break;
      }
    }
    
    parentElement = parentElement.parentElement;
  }
  
  if (maxWidth) {
    detectedParentWidth.value = maxWidth;
  }
};

// Setup ResizeObserver to watch for container size changes
onMounted(() => {
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      setupResizeObserver();
    });
    
    if (containerRef.value) {
      resizeObserver.observe(containerRef.value);
      // Also observe the parent element
      if (containerRef.value.parentElement) {
        resizeObserver.observe(containerRef.value.parentElement);
      }
    }
  }
  
  // Initial setup
  setupResizeObserver();
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
});

const minWidth = computed(() => {
  // If custom width is provided, use it
  if (props.width) {
    return props.width;
  }
  
  // Calculate minimum width based on the longest option text
  const allLabels = [
    props.placeholder,
    ...normalizedOptions.value.map(option => optionLabel(option))
  ];
  
  // Estimate width based on character count (rough approximation)
  // Each character is roughly 8-10px, plus padding and icon space
  const maxLength = Math.max(...allLabels.map(label => label.length));
  const estimatedWidth = Math.max(maxLength * 10 + 80, 120); // 80px for padding/icon, minimum 120px
  
  // Use auto-detected parent width if available, otherwise fall back to estimated width
  let maxAllowedWidth = null;
  
  if (detectedParentWidth.value) {
    maxAllowedWidth = detectedParentWidth.value * 0.9;
  }
  
  if (maxAllowedWidth) {
    const finalWidth = Math.min(estimatedWidth, maxAllowedWidth);
    return `${finalWidth}px`;
  }
  
  return `${estimatedWidth}px`;
});
  
</script> 