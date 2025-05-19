<template>
  <div class="text-sm text-gray-700">
    Status: <span v-html="statusMessage()"></span>
  </div>
</template>

<script>
import { inject } from 'vue';

export default {
  name: 'StatusDisplay',
  setup() {
    // Inject the status message from App.vue
    const statusMessage = inject('statusMessage');

    return {
      statusMessage,
    };
  },
};
</script>

<style scoped>
/* Scoped styles for the status display if needed */
</style>
