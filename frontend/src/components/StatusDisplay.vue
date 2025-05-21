<template>
  <div class="text-sm text-gray-200">
    Status: <span v-html="displayedStatusMessage"></span>
  </div>
</template>

<script>
import { inject } from 'vue';

export default {
  name: 'StatusDisplay',
  setup() {
    // Inject the status message from App.vue
    // The 'inject' function's second argument is a default value if 'statusMessage' is not provided.
    // Here, we provide a default function that returns an error message,
    // ensuring getStatusMessageFn is always a function.
    const getStatusMessageFn = inject('statusMessage', () => () => "<span style='color:red;'>Error: Status provider not found.</span>");

    return {
      getStatusMessageFn,
    };
  },
  computed: {
    displayedStatusMessage() {
      // Call the injected function (or its fallback if injection failed)
      const message = this.getStatusMessageFn();
      // If the retrieved message is empty (null, undefined, or empty string), display a default placeholder.
      return message || '<i>No current status.</i>';
    }
  }
};
</script>

<style scoped>
/* Scoped styles for the status display if needed */
</style>
