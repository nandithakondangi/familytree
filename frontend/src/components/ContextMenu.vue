<template>
	<Transition
		enter-active-class="transition-opacity ease-out duration-150"
		enter-from-class="opacity-0"
		enter-to-class="opacity-100"
		leave-active-class="transition-opacity ease-in duration-100"
		leave-from-class="opacity-100"
		leave-to-class="opacity-0"
	>
		<div
			v-if="isVisible"
			ref="contextMenuEl"
			class="fixed z-[60] bg-indigo-600/80 dark:bg-indigo-700/80 backdrop-blur-md text-white rounded-lg shadow-xl py-2 w-56"
			:style="menuStyle"
			@click.stop
		>
			<!-- Section 1: Add Member -->
			<div class="mb-1">
				<h4
					class="px-3 py-1 text-xs font-semibold text-indigo-200 dark:text-indigo-300 uppercase tracking-wider"
				>
					Add New Member
				</h4>
				<ul>
					<li>
						<button
							@click="emitAction('add-member', 'SPOUSE')"
							class="w-full text-left px-3 py-1.5 text-sm hover:bg-indigo-500/70 dark:hover:bg-indigo-600/70 transition-colors"
						>
							Add Spouse
						</button>
					</li>
					<li>
						<button
							@click="emitAction('add-member', 'CHILD')"
							class="w-full text-left px-3 py-1.5 text-sm hover:bg-indigo-500/70 dark:hover:bg-indigo-600/70 transition-colors"
						>
							Add Child
						</button>
					</li>
					<li>
						<button
							@click="emitAction('add-member', 'PARENT')"
							class="w-full text-left px-3 py-1.5 text-sm hover:bg-indigo-500/70 dark:hover:bg-indigo-600/70 transition-colors"
						>
							Add Parent
						</button>
					</li>
				</ul>
			</div>

			<!-- Separator -->
			<hr class="border-indigo-400/50 dark:border-indigo-500/50 my-1 mx-2" />

			<!-- Section 2: Link Existing -->
			<div>
				<h4
					class="px-3 py-1 text-xs font-semibold text-indigo-200 dark:text-indigo-300 uppercase tracking-wider"
				>
					Link Existing Member
				</h4>
				<ul>
					<li>
						<button
							@click="emitAction('link-member', 'SPOUSE')"
							class="w-full text-left px-3 py-1.5 text-sm hover:bg-indigo-500/70 dark:hover:bg-indigo-600/70 transition-colors"
						>
							Link with Spouse
						</button>
					</li>
					<li>
						<button
							@click="emitAction('link-member', 'PARENT')"
							class="w-full text-left px-3 py-1.5 text-sm hover:bg-indigo-500/70 dark:hover:bg-indigo-600/70 transition-colors"
						>
							Link with Parent
						</button>
					</li>
					<li>
						<button
							@click="emitAction('link-member', 'CHILD')"
							class="w-full text-left px-3 py-1.5 text-sm hover:bg-indigo-500/70 dark:hover:bg-indigo-600/70 transition-colors"
						>
							Link with Child
						</button>
					</li>
				</ul>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { ref, watch, nextTick } from "vue";

const props = defineProps({
	isVisible: Boolean,
	position: Object, // { x: number, y: number } - initial click position
	sourceNodeId: String,
});

const emit = defineEmits(["action"]);

const contextMenuEl = ref(null);
const menuStyle = ref({
	opacity: 0, // Initially hidden to prevent flicker
	top: "0px",
	left: "0px",
});

const CONTEXT_MENU_WIDTH_ESTIMATE = 224; // Corresponds to w-56 (14rem * 16px/rem)
const SCREEN_EDGE_MARGIN = 10; // Minimum margin from window edges

watch(
	() => [props.isVisible, props.position],
	async ([visible, newPosition]) => {
		if (visible && newPosition) {
			await nextTick(); // Wait for DOM update so contextMenuEl is available and has dimensions

			if (contextMenuEl.value) {
				const menuHeight = contextMenuEl.value.offsetHeight;
				const menuWidth =
					contextMenuEl.value.offsetWidth || CONTEXT_MENU_WIDTH_ESTIMATE;

				let targetY = newPosition.y;
				let targetX = newPosition.x;

				// Adjust Y: if not enough space below, try to position above the click point
				if (
					newPosition.y + menuHeight + SCREEN_EDGE_MARGIN >
					window.innerHeight
				) {
					targetY = newPosition.y - menuHeight; // Anchor bottom of menu to click.y
				}

				// Adjust X: if not enough space to the right, try to position to the left of the click point
				if (
					newPosition.x + menuWidth + SCREEN_EDGE_MARGIN >
					window.innerWidth
				) {
					targetX = newPosition.x - menuWidth; // Anchor right of menu to click.x
				}

				// Clamp to window boundaries with margin
				const clampedY = Math.max(
					SCREEN_EDGE_MARGIN,
					Math.min(
						targetY,
						window.innerHeight - menuHeight - SCREEN_EDGE_MARGIN,
					),
				);
				const clampedX = Math.max(
					SCREEN_EDGE_MARGIN,
					Math.min(targetX, window.innerWidth - menuWidth - SCREEN_EDGE_MARGIN),
				);

				menuStyle.value = {
					top: `${clampedY}px`,
					left: `${clampedX}px`,
					opacity: 1, // Make it visible after position calculation
				};
			}
		} else {
			menuStyle.value = { ...menuStyle.value, opacity: 0 }; // Hide if not visible
		}
	},
	{ immediate: true, deep: true },
);

const emitAction = (actionType, relationshipType) => {
	emit("action", { actionType, relationshipType });
};
</script>
