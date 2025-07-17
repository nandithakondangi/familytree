<template>
	<div v-if="tabs.length" class="w-full flex flex-col h-full">
		<!-- Tab Panels container first -->
		<div class="flex-grow relative">
			<transition
				mode="out-in"
				enter-active-class="transition-all duration-500 ease-[cubic-bezier(0.68,-0.55,0.265,1.55)]"
				leave-active-class="transition-all duration-300 ease-in"
				:enter-from-class="transitionDirection === 'right' ? 'translate-x-10 opacity-0' : '-translate-x-10 opacity-0'"
				enter-to-class="translate-x-0 opacity-100"
				:leave-from-class="'translate-x-0 opacity-100'"
				:leave-to-class="transitionDirection === 'right' ? '-translate-x-10 opacity-0' : 'translate-x-10 opacity-0'"
			>
				<div
					:key="tabs[activeTabIndex].props.title"
					class="h-full"
				>
					<component :is="tabs[activeTabIndex]" />
				</div>
			</transition>
		</div>

		<!-- Tab Switcher -->
		<div class="mt-4">
			<GlassyTabSwitcher
				:tabs="tabs.map(tab => ({ title: tab.props.title }))"
				v-model:activeIndex="activeTabIndex"
				:theme-color="tabs[activeTabIndex]?.props.themeColor || 'indigo'"
			/>
		</div>
	</div>
	<div v-else>
		<p class="text-center text-gray-500">No tabs to display.</p>
	</div>
</template>

<script setup>
import { ref, onMounted, computed, useSlots } from 'vue';
import GlassyTabPanel from '@/components/ui/GlassyTabPanel.vue';
import GlassyTabSwitcher from '@/components/ui/GlassyTabSwitcher.vue';

const slots = useSlots();
const tabs = ref([]);
const activeTabIndex = ref(0);
const prevTabIndex = ref(0);

onMounted(() => {
    if (slots.default) {
        tabs.value = slots.default().filter(child => child.type === GlassyTabPanel);
    }
    console.log(tabs.value);
});

function setActiveTab(index) {
    prevTabIndex.value = activeTabIndex.value;
    activeTabIndex.value = index;
}



const transitionDirection = computed(() => {
    return activeTabIndex.value > prevTabIndex.value ? 'right' : 'left';
});
</script>