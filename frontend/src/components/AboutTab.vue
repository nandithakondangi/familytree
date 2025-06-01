<template>
  <div class="prose prose-sm dark:prose-invert max-w-none p-2 text-gray-800 dark:text-gray-300">
    <h2 class="text-xl font-semibold mb-3 text-gray-900 dark:text-gray-100">About This Software</h2>
    <div v-html="aboutContent" class="font-medium text-justify">
      </div>
  </div>
</template>

<script>
export default {
  name: 'AboutTab',
  data() {
    return {
      aboutContent: `
        <p>The Family Tree Visualizer is designed to help users create, visualize, and understand their family connections. It aims to address the challenge of identifying and remembering relatives, especially within large families. A key goal is to be adaptable to different cultural contexts, allowing users to record and view information relevant to their heritage.</p>

        <h3>Goals</h3>
        <ul>
          <li>Provide a user-friendly interface for exploring family connections.</li>
          <li>Enable users to quickly identify relationships between individuals.</li>
          <li>Facilitate the sharing of family tree data with others.</li>
          <li>Preserve and document family history for future generations.</li>
          <li>Support both general family tree information and culture-specific details.</li>
        </ul>

        <h3>Target User</h3>
        <p>This application is for:</p>
        <ul>
          <li>Individuals who want to better understand and visualize their extended family relationships.</li>
          <li>People who struggle to remember the connections between relatives, especially in large families.</li>
          <li>Users interested in documenting and preserving their family history.</li>
          <li>Users from diverse cultural backgrounds with varying needs for family data.</li>
        </ul>
      `,
    };
  },
};
</script>

<style scoped>
/* Scoped styles for the about tab if needed */
/* Using Tailwind's prose class for basic typography styling */
</style>
