<template>
  <div class="relative w-full h-full">
    <iframe
      ref="graphIframe"
      :srcdoc="graphHtml"
      class="w-full h-full border-none"
      @load="handleIframeLoad"
    ></iframe>
     <div v-if="isLoading" class="absolute inset-0 bg-white/50 backdrop-blur-md flex items-center justify-center rounded-xl"> {/* Matched rounding and glassy style */}
      <div class="flex flex-col items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500/90"></div> {/* Slightly transparent spinner border */}
        <p class="mt-4 text-gray-700">Loading graph...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { inject, watch, ref } from 'vue';

export default {
  name: 'GraphView',
   setup() {
    // Inject the provided state and methods from App.vue
    const triggerGraphRender = inject('triggerGraphRender');
    const setMemberIdToEdit = inject('setMemberIdToEdit'); // For double-click
    const showNodeContextMenu = inject('showNodeContextMenu'); // For right-click
    const updateStatus = inject('updateStatus'); // For status updates

    const isLoading = ref(false); // Reactive state for loading indicator
    const graphHtml = ref(''); // Reactive variable to hold the HTML content

    // Watch for changes in triggerGraphRender provided by App.vue
    // Removed unused newValue and oldValue parameters
    watch(triggerGraphRender, () => {
      console.log('Graph render trigger detected. Loading graph HTML.');
      isLoading.value = true; // Show loading indicator
      // When triggered, fetch the latest graph HTML from the backend
      fetchGraphHtml();
    });

    // Function to fetch graph HTML from backend
    const fetchGraphHtml = () => {
       fetch('/api/get-graph-html') // Replace with your actual backend endpoint
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch graph HTML.');
            }
            return response.text(); // Assuming backend returns HTML as text
        })
        .then(htmlContent => {
            // Update the srcdoc of the iframe
            // Access ref value using .value
            graphHtml.value = htmlContent;
            // Loading indicator will be hidden in handleIframeLoad
        })
        .catch(error => {
            console.error('Error fetching graph HTML:', error);
            updateStatus(`Error loading graph: ${error.message}`, 7000);
            // Access ref value using .value
            graphHtml.value = '<p style="color: red; text-align: center; margin-top: 50px;">Failed to load graph.</p>';
            isLoading.value = false; // Hide loading indicator on error
        });
    };

    // Initial fetch when component is mounted
    fetchGraphHtml();


    return {
      graphHtml, // Return the ref itself
      setMemberIdToEdit,
      showNodeContextMenu,
      isLoading,
    };
  },
  methods: {
    handleIframeLoad() {
      console.log('Iframe loaded.');
      this.isLoading = false; // Hide loading indicator

      // Attempt to inject JavaScript into the iframe to capture events
      const iframe = this.$refs.graphIframe;
      if (iframe && iframe.contentWindow) {
        try {
          const script = iframe.contentWindow.document.createElement('script');
          // Use a simple script to listen for double clicks on nodes
          // This assumes your pyvis HTML structure has elements representing nodes
          // You might need to inspect the generated HTML to target nodes correctly
          // This is a basic example, you might need a more robust approach
          // potentially using QWebChannel like in your PySide6 code,
          // but that requires more complex setup in a web context.
          // A simpler approach is to modify the pyvis template itself
          // to include event listeners and post messages back to the parent window.

          // Example: Listen for double clicks on elements with a specific class/attribute
          // This requires modifying the pyvis template to add data attributes or classes
          // to nodes that include the member ID.
           script.textContent = `
            console.log('Attempting to inject JS into iframe');
            // Wait for the network to be ready (pyvis might load data async)
            // This is a simple polling mechanism, adjust as needed
            let checkNetworkInterval = setInterval(() => {
                if (typeof network !== 'undefined') { // Check if pyvis network object exists
                    clearInterval(checkNetworkInterval);
                    console.log('Pyvis network object found, adding event listeners.');

                    // Add double-click listener
                    network.on("doubleClick", function (params) {
                        if (params.nodes.length > 0) {
                            const nodeId = params.nodes[0];
                            console.log('Node double-clicked:', nodeId);
                            // Post message to parent window with node ID
                            window.parent.postMessage({
                                type: 'nodeDoubleClick',
                                nodeId: nodeId
                            }, '*'); // Replace '*' with your app's origin for security
                        }
                    });

                    // Add right-click listener (contextmenu event)
                    // Note: pyvis might have its own context menu handling,
                    // you might need to disable it or find a way to hook into it.
                    // This is a generic contextmenu listener on the canvas.
                     network.on("oncontext", function (params) {
                         params.event.preventDefault(); // Prevent default browser context menu
                         const nodeId = network.getNodeAt(params.pointer.DOM);
                         if (nodeId !== undefined) {
                              console.log('Node right-clicked:', nodeId);
                              // Post message to parent window with node ID and coordinates
                              window.parent.postMessage({
                                 type: 'nodeRightClick',
                                 nodeId: nodeId,
                                 x: params.event.clientX,
                                 y: params.event.clientY
                             }, '*'); // Replace '*' with your app's origin for security
                         }
                     });

                } else {
                    console.log('Pyvis network object not yet available...');
                }
            }, 500); // Check every 500ms

            // Listen for messages from the parent window if needed
            // window.addEventListener('message', (event) => {
            //     if (event.origin !== 'YOUR_APP_ORIGIN') { // Verify origin
            //         return;
            //     }
            //     // Handle messages from parent
            //     console.log('Message from parent:', event.data);
            // });
          `;
          iframe.contentWindow.document.body.appendChild(script);
           console.log('JS injected successfully.');
        } catch (e) {
          console.error('Failed to inject script into iframe:', e);
          this.updateStatus('Error injecting script into graph view.', 7000);
        }
      }
    },
     // Method to handle messages from the iframe
     handleMessage(event) {
       // if (event.origin !== 'YOUR_APP_ORIGIN') { // Verify origin in production
       //   return;
       // }

       const data = event.data;
       if (data.type === 'nodeDoubleClick') {
         console.log('Received nodeDoubleClick from iframe:', data.nodeId);
         // Call the injected method to trigger edit dialog
         this.setMemberIdToEdit(data.nodeId);
         // In a real app, this would trigger a modal/dialog for editing
       } else if (data.type === 'nodeRightClick') {
          console.log('Received nodeRightClick from iframe:', data.nodeId, data.x, data.y);
          // Call the injected method to show context menu
          this.showNodeContextMenu(data.nodeId, data.x, data.y);
          // In a real app, this would display a context menu at the given coordinates
       }
       // Handle other message types as needed
     }
  },
  mounted() {
    // Listen for messages posted from the iframe
    window.addEventListener('message', this.handleMessage);
  },
   beforeUnmount() {
    // Clean up the event listener when the component is unmounted
    window.removeEventListener('message', this.handleMessage);
  }
};
</script>

<style scoped>
/* Scoped styles for the graph view if needed */
</style>