import GlassyFamilyTreeCanvas from './GlassyFamilyTreeCanvas.vue';
import { VNetworkGraph } from 'v-network-graph';
import { useTreeStore } from '@/store/tree';
import { useAppStore } from '@/store/app';
import { provide } from 'vue';

// Mock data for the graph
const mockGraphData = {
  nodes: {
    node1: { name: "Alice" },
    node2: { name: "Bob" },
    node3: { name: "Charlie" },
    node4: { name: "Diana" },
    node5: { name: "Eve" },
  },
  edges: {
    edge1: { source: "node1", target: "node2" },
    edge2: { source: "node2", target: "node3" },
    edge3: { source: "node1", target: "node4" },
    edge4: { source: "node4", target: "node5" },
  },
  layouts: {
    nodes: {
      node1: { x: 0, y: 0 },
      node2: { x: 100, y: 50 },
      node3: { x: 200, y: 0 },
      node4: { x: 100, y: -50 },
      node5: { x: 200, y: -100 },
    },
  },
  configs: {
    // You can override or extend default configs here for the mock
    node: {
      normal: {
        color: "#ffcc99", // A different color for mock nodes
      },
    },
  },
};

// Mock the fetchGraphHtml API call
const mockFetchGraphHtml = async (theme, poiId) => {
  console.log(`Mocking fetchGraphHtml for theme: ${theme}, POI: ${poiId}`);
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(mockGraphData);
    }, 500); // Simulate network delay
  });
};

export default {
  title: 'Graph/GlassyFamilyTreeCanvas',
  component: GlassyFamilyTreeCanvas,
  argTypes: {
    themeColor: {
      control: { type: 'select' },
      options: ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger'],
      description: 'Sets the color theme of the canvas.',
    }
  },
  parameters: {
    backgrounds: {
      default: "dark",
      values: [
        { name: "dark", value: "#1f2937" }, // gray-800
        { name: "light", value: "#f9fafb" }, // gray-50
      ],
    },
  },
  components: { VNetworkGraph },
  decorators: [
    (story) => ({
      components: { story },
      setup() {
        // Initialize Pinia stores for the story
        const treeStore = useTreeStore();
        const appStore = useAppStore();

        // Set initial state for the stores if needed for the story
        treeStore.currentPoi = "node1"; // Example POI
        appStore.currentTheme = "dark"; // Example theme

        // Provide the mock API function
        provide('fetchGraphHtmlApi', mockFetchGraphHtml);

        return { treeStore, appStore };
      },
      template: '<story />',
    }),
  ],
};

const Template = (args) => ({
  components: { GlassyFamilyTreeCanvas },
  setup() {
    return { args };
  },
  template: `
  <div class="absolute inset-0 m-4">
    <GlassyFamilyTreeCanvas v-bind="args" />
  </div>`,
});

export const Default = Template.bind({});
Default.args = {};
