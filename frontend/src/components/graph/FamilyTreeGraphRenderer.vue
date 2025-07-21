<template>
  <div class="relative w-full h-full">
    <v-network-graph
      :nodes="nodes"
      :edges="edges"
      :layouts="layouts"
      :configs="configs"
    />
    <div
      v-if="isLoading"
      class="absolute inset-0 flex items-center justify-center rounded-xl"
    >
      <div class="flex flex-col items-center">
        <div class="flex h-12 items-center justify-center space-x-2">
          <div class="h-4 w-4 animate-bounce rounded-full bg-indigo-800/90 dark:bg-indigo-200/90 [animation-delay:-0.3s]"></div>
          <div class="h-4 w-4 animate-bounce rounded-full bg-indigo-800/90 dark:bg-indigo-200/90 [animation-delay:-0.15s]"></div>
          <div class="h-4 w-4 animate-bounce rounded-full bg-indigo-800/90 dark:bg-indigo-200/90"></div>
        </div>
        <p class="mt-4 text-indigo-900 dark:text-indigo-100">Loading graph...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch, ref, onMounted, computed, inject } from "vue";
import { useTreeStore } from "@/store/tree";
import { useAppStore } from "@/store/app";

// Import the original API function for fallback if not mocked
import { fetchGraphHtml as originalFetchGraphHtml } from "@/services/familyTreeApi";

const treeStore = useTreeStore();
const appStore = useAppStore();

const triggerGraphRender = computed(() => treeStore.triggerGraphRender);
const updateStatus = appStore.updateStatus;
const currentTheme = computed(() => appStore.currentTheme);

// Inject the API function, with a fallback to the original if not provided (e.g., in production)
const fetchGraphHtmlFromApi = inject('fetchGraphHtmlApi', originalFetchGraphHtml);

const isLoading = ref(false);
const nodes = ref({});
const edges = ref({});
const layouts = ref({});
const configs = ref({
  view: {
    scale: 1.0,
  },
  node: {
    normal: {
      type: "circle",
      radius: 20,
      color: "#99ccff",
      strokeWidth: 2,
      strokeColor: "#6699ff",
    },
    hover: {
      color: "#6699ff",
      strokeColor: "#3366cc",
    },
    label: {
      visible: true,
      fontFamily: "sans-serif",
      fontSize: 12,
      color: "#333333",
      direction: "south",
      margin: 4,
    },
  },
  edge: {
    normal: {
      width: 2,
      color: "#cccccc",
      dasharray: "0",
      linecap: "butt",
      animate: false,
      animationSpeed: 50,
    },
    hover: {
      color: "#999999",
    },
    marker: {
      source: {
        type: "none",
        width: 4,
        height: 4,
        margin: -1,
        units: "strokeWidth",
        color: null,
      },
      target: {
        type: "arrow",
        width: 4,
        height: 4,
        margin: -1,
        units: "strokeWidth",
        color: null,
      },
    },
  },
});

const currentPoi = computed(() => treeStore.currentPoi);

watch(triggerGraphRender, () => {
  fetchGraphData();
});

watch(currentPoi, (newPoi, oldPoi) => {
  if (newPoi !== oldPoi) {
    fetchGraphData();
  }
});

const fetchGraphData = async () => {
  isLoading.value = true;
  try {
    const response = await fetchGraphHtmlFromApi(currentTheme.value, currentPoi.value);
    // Assuming the API now returns JSON with nodes, edges, layouts, and configs
    const graphData = response;
    nodes.value = graphData.nodes || {};
    edges.value = graphData.edges || {};
    layouts.value = graphData.layouts || {};
    // Merge configs, allowing local overrides
    configs.value = { ...configs.value, ...graphData.configs };
    treeStore.setDataLoaded(true);
  } catch (error) {
    console.error("Error fetching graph data:", error);
    updateStatus(`Error loading graph: ${error.message}`, 7000);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchGraphData();
});
</script>

<style scoped>
/* Basic styling for the graph container */
.v-network-graph {
  width: 100%;
  height: 100%;
  background-color: transparent;
}
</style>
