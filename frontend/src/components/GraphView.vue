<template>
	<div class="relative w-full h-full">
		<iframe
			ref="graphIframeRef"
			:key="iframeKey"
			:srcdoc="graphHtml"
			class="w-full h-full border-none"
			@load="onIframeLoad"
		></iframe>
		<div
			v-if="isLoading"
			class="absolute inset-0 bg-white/50 dark:bg-slate-800/60 backdrop-blur-md flex items-center justify-center rounded-xl"
		>
			<div class="flex flex-col items-center">
				<div
					class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500/90 dark:border-indigo-400/90"
				></div>
				<p class="mt-4 text-gray-700 dark:text-gray-300">Loading graph...</p>
			</div>
		</div>
	</div>
</template>

<script>
	import {
		inject,
		watch,
		ref,
		onMounted,
		onBeforeUnmount,
		nextTick,
	} from "vue";

	export default {
		name: "GraphView",
		setup() {
			// Inject the provided state and methods from App.vue
			const triggerGraphRender = inject("triggerGraphRender");
			const setMemberIdToEdit = inject("setMemberIdToEdit");
			const showNodeContextMenu = inject("showNodeContextMenu");
			const handleNodeSingleClickFromApp = inject("handleNodeSingleClick");
			const updateStatus = inject("updateStatus");

			const isLoading = ref(false); // Reactive state for loading indicator
			const graphHtml = ref(""); // Stores HTML from backend (renamed from themedGraphHtml)
			const interactionScriptContent = ref(""); // To store the fetched script
			const graphIframeRef = ref(null); // Ref for the iframe element
			const iframeKey = ref(0); // Key to force iframe re-creation

			// Watch for changes in triggerGraphRender provided by App.vue
			// Removed unused newValue and oldValue parameters
			watch(triggerGraphRender, () => {
				isLoading.value = true; // Show loading indicator
				// When triggered, fetch the latest graph HTML from the backend
				fetchGraphHtml();
			});

			const fetchInteractionScript = async () => {
				try {
					// Path relative to public folder
					const response = await fetch("/scripts/pyvis_interaction_script.js");
					if (!response.ok) {
						throw new Error(
							`Failed to fetch interaction script: ${response.status} ${response.statusText}` // Keep: Error details
						);
					}
					interactionScriptContent.value = await response.text();
				} catch (error) {
					console.error(
						"[GraphView] Error fetching interaction script:",
						error // Keep: Essential error log
					);
					updateStatus("Error loading graph interaction logic.", 7000);
					interactionScriptContent.value =
						"// Failed to load interaction script; console.error('Interaction script load failed');";
				}
			};

			// Function to fetch graph HTML from backend
			const fetchGraphHtml = () => {
				iframeKey.value++;
				fetch("/api/v1/graph/render")
					.then((response) => {
						if (!response.ok) {
							return response
								.json()
								.then((errorData) => {
									throw new Error(
										errorData.detail || `Server error: ${response.status}`
									);
								})
								.catch(() => {
									throw new Error(
										`Server error: ${response.status} ${response.statusText}`
									);
								});
						}
						return response.json();
					})
					.then((data) => {
						graphHtml.value =
							data.graph_html ||
							'<p style="text-align:center; padding-top: 20px;">No graph data received.</p>';
					})
					.catch((error) => {
						console.error("Error fetching graph HTML:", error);
						updateStatus(`Error loading graph: ${error.message}`, 7000); // Keep: User-facing status update
						graphHtml.value = // Directly set graphHtml with error message
							'<p style="color: red; text-align: center; margin-top: 50px;">Failed to load graph.</p>';
						isLoading.value = false;
					});
			};

			const onIframeLoad = () => {
				// Use nextTick to ensure isLoading=false is processed after potential DOM updates from srcdoc change
				nextTick(() => {
					isLoading.value = false;
				});

				const iframe = graphIframeRef.value;
				if (
					iframe &&
					iframe.contentWindow &&
					interactionScriptContent.value &&
					interactionScriptContent.value.startsWith("// Failed to load") ===
						false
				) {
					try {
						const scriptElement =
							iframe.contentWindow.document.createElement("script");
						scriptElement.textContent = interactionScriptContent.value;
						iframe.contentWindow.document.body.appendChild(scriptElement);
					} catch (e) {
						console.error(
							"[GraphView] CRITICAL: Failed to inject script into iframe:",
							e
						);
						updateStatus(
							"CRITICAL: Error injecting script into graph view.",
							10000
						);
					}
				} else {
					if (!iframe || !iframe.contentWindow)
						console.error(
							"[GraphView] Iframe or contentWindow not available for script injection."
						);
					if (
						!interactionScriptContent.value ||
						interactionScriptContent.value.startsWith("// Failed to load")
					)
						console.error(
							"[GraphView] Interaction script content not loaded or failed to load, cannot inject."
						);
				}
			};

			const handleMessageFromIframe = (event) => {
				const data = event.data;
				if (data && data.type) {
					const iframeRect = graphIframeRef.value?.getBoundingClientRect();
					let screenX = data.clientX;
					let screenY = data.clientY;

					if (iframeRect) {
						screenX = iframeRect.left + data.clientX;
						screenY = iframeRect.top + data.clientY;
					}

					switch (data.type) {
						case "nodeSingleClick":
							console.log(
								"[GraphView] Received nodeSingleClick from iframe:",
								data.nodeId,
								`iframeCoords: (${data.clientX}, ${data.clientY})`,
								`screenCoords: (${screenX}, ${screenY})`
							);
							handleNodeSingleClickFromApp(data.nodeId, screenX, screenY);
							break;
						case "nodeDoubleClick":
							console.log(
								"[GraphView] Received nodeDoubleClick from iframe:",
								data.nodeId
							);
							setMemberIdToEdit(data.nodeId);
							break;
						case "nodeRightClick":
							console.log(
								"[GraphView] Received nodeRightClick from iframe:",
								data.nodeId,
								`iframeCoords: (${data.x}, ${data.y})`,
								`screenCoords: (${screenX}, ${screenY})` // Assuming data.x and data.y are also clientX/Y like
							);
							// For context menu, it might also need screen-relative X/Y if the menu is positioned globally.
							showNodeContextMenu(data.nodeId, screenX, screenY);
							break;
						default:
							break;
					}
				}
			};

			onMounted(() => {
				fetchInteractionScript();
				fetchGraphHtml();
				window.addEventListener("message", handleMessageFromIframe);
			});

			onBeforeUnmount(() => {
				window.removeEventListener("message", handleMessageFromIframe);
			});

			return {
				graphHtml, // Expose graphHtml for srcdoc
				isLoading,
				graphIframeRef, // Expose ref for template
				onIframeLoad, // Expose event handler for template
				iframeKey, // Expose key for template binding
			};
		},
	};
</script>

<style scoped>
	/* Scoped styles for the graph view if needed */
</style>
