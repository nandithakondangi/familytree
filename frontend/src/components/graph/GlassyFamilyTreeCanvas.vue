<template>
  <div :class="containerClasses">
    <div :class="[shineEffectBaseClasses, topShineEffectClasses]"></div>
    <div :class="[shineEffectBaseClasses, bottomShineEffectClasses]"></div>
  <FamilyTreeGraphRenderer />
  </div>
</template>

<script setup>
import FamilyTreeGraphRenderer from './FamilyTreeGraphRenderer.vue';
import { computed } from 'vue';
import { useThemeStore } from '@/store/theme';

const props = defineProps({
  themeColor: {
    type: String,
    default: 'indigo',
    validator: (value) => ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger'].includes(value),
  }
});

const themeStore = useThemeStore();

const baseClasses = 
  "relative w-full h-full overflow-hidden rounded-2xl p-4 backdrop-blur-md border border-white/20 shadow-lg transition-all duration-300 ease-out";

const containerClasses = computed(() => {
  const color = themeStore.getThemeClasses('GlassyFamilyTreeCanvas', props.themeColor);
  return `${baseClasses} ${color}`;
});

const shineEffectBaseClasses = computed(() => {
  return `pointer-events-none absolute inset-0 opacity-50 rounded-2xl`;
});

const topShineEffectClasses = computed(() => {
  return `bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white/40 to-transparent`;
});

const bottomShineEffectClasses = computed(() => {
  return `bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-white/40 to-transparent`;
});


</script>
