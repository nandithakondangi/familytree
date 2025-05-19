<template>
  <div class="prose max-w-none p-2">
    <h2 class="text-xl font-semibold mb-3">About This Software</h2>
    <div v-html="aboutContent" class="text-gray-700">
      </div>
  </div>
</template>

<script>
export default {
  name: 'AboutTab',
  data() {
    return {
      // Initialize aboutContent with a loading message
      aboutContent: '<p>Loading about information...</p>',
    };
  },
  mounted() {
    // Load the about content when the component is mounted
    this.loadAboutContent();
  },
  methods: {
    loadAboutContent() {
      // TODO: Call backend API to get the about information HTML
      // Replace with your actual backend endpoint
      fetch('/api/about-info')
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to load about information.');
          }
          return response.text(); // Assuming backend returns HTML as text
        })
        .then(htmlContent => {
          this.aboutContent = htmlContent;
        })
        .catch(error => {
          console.error('Error loading about info:', error);
          this.aboutContent = `<p class="text-red-500">Error loading information: ${error.message}</p>`;
        });
    },
  },
};
</script>

<style scoped>
/* Scoped styles for the about tab if needed */
/* Using Tailwind's prose class for basic typography styling */
</style>
