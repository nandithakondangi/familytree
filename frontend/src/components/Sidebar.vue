<template>
  <div class="flex flex-col h-full">
    <div class="relative flex items-center justify-around bg-gray-200 rounded-full p-1 mb-4 shadow-inner">
      <div class="absolute top-1 left-0 bottom-1 bg-indigo-600/25 rounded-full transition-all duration-50 ease-in-out"
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
          'transition-all duration-50 ease-in-out', // Change to transition-all for text
          activeTab === 'manage' ? 'opacity-100 max-w-xs font-bold text-green-800' : 'opacity-75 max-w-xs text-green-600 hover:text-green-600 hover:font-bold'
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
          'transition-all duration-50 ease-in-out', // Change to transition-all for text
          activeTab === 'chat' ? 'opacity-100 max-w-xs font-bold text-gray-700' : 'opacity-75 max-w-xs text-gray-500 hover:text-gray-500 hover:font-bold'
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
          'transition-all duration-50 ease-in-out', // Change to transition-all for text
          activeTab === 'about' ? 'opacity-100 max-w-xs font-bold text-blue-700' : 'opacity-75 max-w-xs text-blue-500 hover:text-blue-500 hover:font-bold'
        ]">About</span>
      </button>
    </div>

    <div class="flex-grow overflow-y-auto pr-2">
      <div v-if="activeTab === 'manage'">
        <ManageTreeTab />
      </div>
      <div v-if="activeTab === 'chat'" class="h-full">
        <FamilyTreeChatbot class="h-full flex flex-col" />
      </div>
      <div v-if="activeTab === 'about'">
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

    // Watch for changes in the active tab and update the indicator style
    watch(activeTab, (newTab) => { // Removed immediate: true, will rely on onMounted for initial
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
