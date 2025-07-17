<template>
	<TransitionRoot appear :show="show" as="template">
		<Dialog as="div" @close="closeModal" class="relative z-50">
			<TransitionChild
				as="div"
				:class="['fixed inset-0 backdrop-blur-md', colorClasses.backdrop]"
				enter="duration-300 ease-out"
				enter-from="opacity-0"
				enter-to="opacity-100"
				leave="duration-200 ease-in"
				leave-from="opacity-100"
				leave-to="opacity-0"
			/>

			<!-- Full-screen container to center the panel -->
			<div class="fixed inset-0 overflow-hidden">
				<TransitionChild
					as="div"
					:style="panelStyle"
					class="flex h-full w-full items-center justify-center p-4 text-center overflow-y-auto"
					enter="transition-modal-enter"
					:enter-from="animationClasses.enterFrom"
					:enter-to="animationClasses.enterTo"
					leave="transition-modal-leave"
					:leave-from="animationClasses.leaveFrom"
					:leave-to="animationClasses.leaveTo"
				>
					<DialogPanel
							:class="[
								'relative flex w-full flex-col overflow-hidden rounded-2xl p-4 text-left align-middle shadow-2xl transition-all',
								'border border-white/20 backdrop-blur-xl',
								widthClass,
								heightClass,
								colorClasses.panel,
							]"
						>
						<!-- Permanent shine effect for a glassy look -->
						<div
							class="pointer-events-none absolute inset-0 h-full w-full rounded-2xl bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-white/30 to-transparent opacity-40"
						></div>

						<div class="relative flex flex-grow flex-col min-h-0">
							<!-- The header of the modal -->
							<DialogTitle
								v-if="$slots.header"
								as="h3"
								:class="['flex-shrink-0 text-xl font-semibold leading-6', colorClasses.header]"
							>
								<slot name="header"></slot>
							</DialogTitle>

							<!-- The main content area, which will grow and scroll -->
							<div :class="['mt-4 flex-grow flex flex-col text-sm min-h-0', colorClasses.body]">
								<!-- Single Panel Layout -->
								<GlassyScrollContainer v-if="panelLayout === 'single'">
									<slot></slot>
								</GlassyScrollContainer>
								<!-- Double Panel Layout -->
								<div v-else-if="panelLayout === 'double'" class="grid grid-cols-1 gap-1 md:grid-cols-5 flex-grow flex-col min-h-0">
									<GlassyScrollContainer class="md:col-span-2">
										<slot name="left-panel"></slot>
									</GlassyScrollContainer>
									<GlassyScrollContainer class="md:col-span-3">
										<slot name="right-panel"></slot>
									</GlassyScrollContainer>
								</div>
							</div>

							<div v-if="$slots.footer" class="mt-4 flex flex-shrink-0 justify-end space-x-4">
								<slot name="footer"></slot>
							</div>
						</div>
					</DialogPanel>
				</TransitionChild>
			</div>
		</Dialog>
	</TransitionRoot>
</template>

<script setup>
import { computed } from "vue";
import {
	TransitionRoot,
	TransitionChild,
	Dialog,
	DialogPanel,
	DialogTitle,
} from "@headlessui/vue";
import GlassyScrollContainer from "@/components/ui/GlassyScrollContainer.vue";
import { useExpandAnimation } from "@/composables/animations/useExpandAnimation";
import { useDropFromTopAnimation } from "@/composables/animations/useDropFromTopAnimation";
import { useRiseFromBottomAnimation } from "@/composables/animations/useRiseFromBottomAnimation";
import { useThemeStore } from "@/store/theme";

const props = defineProps({
	show: {
		type: Boolean,
		default: false,
	},
	width: {
		type: String,
		default: "narrow",
		validator: (value) => ["narrow", "wide"].includes(value),
	},
	height: {
		type: String,
		default: "short",
		validator: (value) => ["short", "medium", "tall"].includes(value),
	},
	color: {
		type: String,
		default: "default",
		validator: (value) =>
			["default", "blue", "indigo", "green", "orange", "yellow", "danger"].includes(value),
	},
	panelLayout: {
		type: String,
		default: "single",
		validator: (value) => ["single", "double"].includes(value),
	},
	animationType: {
		type: String,
		default: "expand-from-center",
		validator: (value) => ["expand-from-center", "drop-from-top", "rise-from-bottom", "expand-from-click"].includes(value),
	},
	clickPosition: {
		type: Object,
		default: null, // Expected: { x: number, y: number }
	},
});

const emit = defineEmits(["close"]);

const themeStore = useThemeStore();

function closeModal() {
	emit("close");
}

const widthClass = computed(() => {
	return {
		narrow: "max-w-md", wide: "max-w-2xl",
	}[props.width];
});

const heightClass = computed(() => {
	return {
		short: "h-[30vh]",
		medium: "h-[45vh]",
		tall: "h-[75vh]",
	}[props.height];
});

const animationClasses = computed(() => {
	switch (props.animationType) {
		case "drop-from-top":
			return useDropFromTopAnimation();
		case "rise-from-bottom":
			return useRiseFromBottomAnimation();
		case "expand-from-click": // This animation uses the same classes as expand-from-center, but a different transform-origin
			// falls through
		case "expand-from-center":
		default:
			return useExpandAnimation();
	}
});

const panelStyle = computed(() => {
	if (props.animationType === 'expand-from-click' && props.clickPosition) {
		// The click position is relative to the viewport. We need to apply it as the transform origin.
		return {
			transformOrigin: `${props.clickPosition.x}px ${props.clickPosition.y}px`,
		};
	}
	return {};
});

const colorClasses = computed(() => {
	return themeStore.getThemeClasses("BaseModal", props.color);
});
</script>