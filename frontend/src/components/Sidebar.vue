<template>
  <div class="flex flex-col h-full">
    <div class="relative flex items-center justify-around bg-white/40 dark:bg-slate-700/60 backdrop-blur-md shadow-lg rounded-full p-1 mb-4">
      <div class="absolute top-1 left-0 bottom-1 bg-indigo-500/70 dark:bg-indigo-300/60 rounded-full transition-all duration-50 ease-in-out"
        :style="indicatorStyle"></div>

      <button ref="manageTabButton" @click="activeTab = 'manage'" :class="[
        'relative z-10 flex-1 py-2 px-4 text-center text-sm font-medium rounded-full transition-colors duration-300 ease-in-out flex items-center justify-center'
      ]">
        <span :class="[
          'ml-1',
          'overflow-hidden',
          'transition-all duration-50 ease-in-out',
          activeTab === 'manage' ? 'opacity-100 max-w-[1.5rem]' : 'opacity-0 max-w-0' // Use a fixed max-width for icon
        ]">🌳</span> <span :class="[
          'ml-1',
          'overflow-hidden', // Add for text
          'transition-all duration-50 ease-in-out', // text-gray-700 dark:text-gray-300
          activeTab === 'manage' ? 'opacity-100 max-w-xs font-bold text-indigo-700 dark:text-indigo-700' : 'opacity-80 max-w-xs text-gray-600 dark:text-gray-300 hover:text-indigo-400 dark:hover:text-indigo-300 hover:font-bold'
        ]">Manage</span>
      </button>
      <button ref="chatTabButton" @click="activeTab = 'chat'" :class="[
        'relative z-10 flex-1 py-2 px-4 text-center text-sm font-medium rounded-full transition-colors duration-300 ease-in-out flex items-center justify-center'
      ]">
        <span :class="[
          'ml-1',
          'overflow-hidden',
          'transition-all duration-50 ease-in-out',
          activeTab === 'chat' ? 'opacity-100 max-w-[1.5rem]' : 'opacity-0 max-w-0' // Use a fixed max-width for icon
        ]">💬</span> <span :class="[
          'ml-1',
          'overflow-hidden', // Add for text
          'transition-all duration-50 ease-in-out', // text-gray-700 dark:text-gray-300
          activeTab === 'chat' ? 'opacity-100 max-w-xs font-bold text-indigo-700 dark:text-indigo-700' : 'opacity-80 max-w-xs text-gray-600 hover:text-indigo-400 dark:text-gray-400 dark:hover:text-indigo-300 hover:font-bold'
        ]">Chat</span>
      </button>
      <button ref="aboutTabButton" @click="activeTab = 'about'" :class="[
        'relative z-10 flex-1 py-2 px-4 text-center text-sm font-medium rounded-full transition-colors duration-300 ease-in-out flex items-center justify-center'
      ]">
        <span :class="[
          'ml-1',
          'overflow-hidden',
          'transition-all duration-50 ease-in-out', // Standardize duration
          activeTab === 'about' ? 'opacity-100 max-w-[1.5rem]' : 'opacity-0 max-w-0' // Use a fixed max-width for icon
        ]">ℹ️</span> <span :class="[
          'ml-1',
          'overflow-hidden', // Add for text
          'transition-all duration-50 ease-in-out', // text-gray-700 dark:text-gray-300
          activeTab === 'about' ? 'opacity-100 max-w-xs font-bold text-indigo-700 dark:text-indigo-700' : 'opacity-80 max-w-xs text-gray-600 hover:text-indigo-400 dark:text-gray-400 dark:hover:text-indigo-300 hover:font-bold'
        ]">About</span>
      </button>
    </div>

    <div class="flex-1 pr-2 relative min-h-0 overflow-y-auto">
      <div v-if="activeTab === 'manage'" class="w-full h-full">
        <ManageTreeTab />
      </div>
      <div v-else-if="activeTab === 'chat'" class="w-full h-full">
        <FamilyTreeChatbot />
      </div>
      <div v-else-if="activeTab === 'about'" class="w-full h-full">
        <AboutTab />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import ManageTreeTab from './ManageTreeTab.vue';
import AboutTab from './AboutTab.vue';
import FamilyTreeChatbot from './FamilyTreeChatbot.vue';

export default {
  // eslint-disable-next-line
  name: 'Sidebar',
  components: {
    ManageTreeTab,
    AboutTab,
    FamilyTreeChatbot,
  },
  setup() {
    const activeTab = ref('manage'); // 'manage', 'chat', or 'about'
    const indicatorStyle = ref({}); // Reactive style object for the indicator

    // Refs to the tab buttons to measure their positions
    const manageTabButton = ref(null);
    const chatTabButton = ref(null);
    const aboutTabButton = ref(null);

    // Function to update the indicator style based on the target button
    const updateIndicatorStyle = (targetButton) => {
      if (targetButton && targetButton.parentElement) {
        // Use targetButton.offsetLeft to get the button's true starting position
        // relative to its parent's padding edge. This automatically accounts for
        // any spacing applied by flexbox properties like justify-around.
        const left = targetButton.offsetLeft;
        // targetButton.offsetWidth gives the full rendered width of the button.
        const width = targetButton.offsetWidth;

        indicatorStyle.value = {
          transform: `translateX(${left}px)`,
          width: `${width}px`,
        };
      }
    };

    // Watch for changes in the active tab to update indicator and set transition direction
    watch(activeTab, (newTab) => {
      nextTick(() => { // Ensure DOM updates with new classes before scheduling timeout
        let targetButton = null;
        if (newTab === 'manage' && manageTabButton.value) {
          targetButton = manageTabButton.value;
        } else if (newTab === 'chat' && chatTabButton.value) {
          targetButton = chatTabButton.value;
        } else if (newTab === 'about' && aboutTabButton.value) {
          targetButton = aboutTabButton.value;
        }

        if (targetButton) {
          // Delay the style update to allow CSS transitions (e.g., max-width on icon, font-weight on text)
          // to complete. These transitions affect the button's offsetWidth.
          // The transition duration is 300ms.
          setTimeout(() => {
            // Re-check current activeTab and button ref in case of rapid changes during timeout
            let currentButtonRef = null;
            if (activeTab.value === 'manage') currentButtonRef = manageTabButton.value;
            else if (activeTab.value === 'chat') currentButtonRef = chatTabButton.value;
            else if (activeTab.value === 'about') currentButtonRef = aboutTabButton.value;

            // Only update if the tab is still the one we initiated for and the button ref is valid
            if (currentButtonRef && activeTab.value === newTab) {
              updateIndicatorStyle(currentButtonRef);
            }
          }, 60); // 50ms transition duration + 10ms buffer
        }
      });
    });

    // Also update the indicator style if the window is resized, as positions might change
    // This is important for responsiveness
    const handleResize = () => {
      nextTick(() => {
        let targetButton = null;
        if (activeTab.value === 'manage' && manageTabButton.value) {
          targetButton = manageTabButton.value;
        } else if (activeTab.value === 'chat' && chatTabButton.value) {
          targetButton = chatTabButton.value;
        } else if (activeTab.value === 'about' && aboutTabButton.value) {
          targetButton = aboutTabButton.value;
        }
        updateIndicatorStyle(targetButton);
      });
    };

    // Add event listener on mount
    onMounted(() => {
      window.addEventListener('resize', handleResize);
      // Call updateIndicatorStyle initially after mount to ensure correct position
      nextTick(() => {
        let targetButton = null;
        if (activeTab.value === 'manage' && manageTabButton.value) {
          targetButton = manageTabButton.value;
        } else if (activeTab.value === 'chat' && chatTabButton.value) {
          targetButton = chatTabButton.value;
        } else if (activeTab.value === 'about' && aboutTabButton.value) {
          targetButton = aboutTabButton.value;
        }
        updateIndicatorStyle(targetButton);
      });
    });

    // Clean up event listener on unmount
    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
    });

    return {
      activeTab,
      indicatorStyle,
      manageTabButton,
      chatTabButton,
      aboutTabButton,
    };
  },
};
</script>

<style scoped>
/* Scoped styles for the sidebar if needed */
</style>
