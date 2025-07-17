import  { ref } from "vue";
import BaseModal from "./BaseModal.vue";
import GlassyButton from "../ui/GlassyButton.vue";
import { useThemeStore } from "@/store/theme";

export default {
	title: "COMMON/BaseModal",
	component: BaseModal,
	// Add a dark background to all stories for better contrast and to see the glass effect
	parameters: {
		backgrounds: {
			default: "dark",
			values: [
				{ name: "dark", value: "#1f2937" }, // gray-800
				{ name: "light", value: "#f9fafb" }, // gray-50
			],
		},
	},
	argTypes: {
		show: {
			control: "boolean",
			description: "Controls the visibility of the modal.",
			table: { category: "Props", defaultValue: { summary: "false" } },
		},
		width: {
			control: { type: "select" },
			options: ["narrow", "wide"],
			description: "Sets the max-width of the modal.",
			table: { category: "Props", defaultValue: { summary: "narrow" } },
		},
		height: {
			control: { type: "select" },
			options: ["short", "medium", "tall"],
			description: "Sets the max-height of the modal.",
			table: { category: "Props", defaultValue: { summary: "short" } },
		},
		color: {
			control: { type: "select" },
			options: ["default", "blue", "indigo", "green", "orange", "yellow", "danger"],
			description: "Sets the color theme of the modal.",
			table: { category: "Props", defaultValue: { summary: "default" } },
		},
		animationType: {
			control: { type: "select" },
			options: ["expand-from-center", "drop-from-top", "rise-from-bottom", "expand-from-click"],
			description: "Sets the open/close animation.",
			table: { category: "Props", defaultValue: { summary: "expand-from-center" } },
		},
		panelLayout: {
			control: { type: "select" },
			options: ["single", "double"],
			description: "Sets the body layout to single or double panels.",
			table: { category: "Props", defaultValue: { summary: "single" } },
		},
		// Slot content controls
		headerSlot: {
			control: "text",
			description: "Content for the header slot. Leave empty to hide.",
			table: { category: "Slots" },
		},
		defaultSlot: {
			control: "text",
			description: "Content for the default body slot.",
			table: { category: "Slots" },
		},
		leftPanelSlot: {
			control: "text",
			description: "Content for the left panel in 'double' layout.",
			table: { category: "Slots" },
		},
		rightPanelSlot: {
			control: "text",
			description: "Content for the right panel in 'double' layout.",
			table: { category: "Slots" },
		},
		footerSlot: {
			control: "boolean",
			description: "Toggle visibility of the footer slot with buttons.",
			table: { category: "Slots" },
		},
		// Actions
		onClose: {
			action: "close",
			description: "Emitted when the modal is requested to be closed (e.g., backdrop click, Esc key).",
			table: { category: "Events" },
		},
	},
};

const Template = (args) => ({
	components: { BaseModal, GlassyButton },
	setup() {
		return { args };
	},
	template: `
    <!-- The modal is rendered directly. Control visibility with the 'show' prop in the controls panel. -->
    <BaseModal
      :show="args.show"
      :width="args.width"
	  :height="args.height"
      :color="args.color"
	  :animationType="args.animationType"
      :panelLayout="args.panelLayout"
      @close="args.onClose"
    >
      <template #header v-if="args.headerSlot">
        {{ args.headerSlot }}
      </template>
      
      <!-- Default slot for single panel layout -->
      <p>{{ args.defaultSlot }}</p>
      
      <!-- Named slots for double panel layout -->
      <template #left-panel>
        <p>{{ args.leftPanelSlot }}</p>
      </template>
      <template #right-panel>
        <p>{{ args.rightPanelSlot }}</p>
      </template>

      <template #footer v-if="args.footerSlot">
        <GlassyButton themeColor="green" @click="args.onClose">Confirm</GlassyButton>
        <GlassyButton themeColor="danger" @click="args.onClose">Cancel</GlassyButton>
      </template>
    </BaseModal>
  `,
});

export const Default = Template.bind({});
Default.args = {
	show: true,
	width: "narrow",
	height: "medium",
	color: "default",
	animationType: "expand-from-center",
	panelLayout: "single",
	headerSlot: "Default Modal",
	defaultSlot: "This is the body of the modal. You can place any content here, from simple text to complex components.",
	leftPanelSlot: "This is the content for the left panel. It will only be visible when the panel layout is set to 'double'.",
	rightPanelSlot: "This is the content for the right panel. It will only be visible when the panel layout is set to 'double'.",
	footerSlot: true,
};

export const DangerTheme = Template.bind({});
DangerTheme.args = {
	...Default.args,
	panelLayout: "single",
	color: "danger",
	animationType: "drop-from-top",
	headerSlot: "Confirm Deletion",
	defaultSlot: "Are you sure you want to proceed? This action cannot be undone and all associated data will be permanently lost.",
};

export const DoublePanel = Template.bind({});
DoublePanel.args = {
	...Default.args,
	width: "wide",
	height: "tall",
	color: "indigo",
	panelLayout: "double",
	headerSlot: "Compare Information",
	// defaultSlot is ignored in double panel layout, but we can leave it for arg control consistency
	leftPanelSlot: "This panel could contain information about the 'source' member. For example, details about John Doe, born 1980. He is the father in this relationship.",
	rightPanelSlot: "This panel could contain details about the 'target' member or new information to be added. For example, details about Jane Smith, born 1982. She will be linked as the spouse.",
};

export const WithLongContent = Template.bind({});
WithLongContent.args = {
	...Default.args,
	panelLayout: "single",
	width: "narrow",
	height: "tall",
	color: "blue",
	animationType: "drop-from-top",
	defaultSlot: `
    <p>${"This is some long content. ".repeat(100)}</p>
    <p>${"More content to ensure scrolling. ".repeat(50)}</p>
  `,
};
WithLongContent.storyName = "With Scrollable Content";

export const WithoutFooter = Template.bind({});
WithoutFooter.args = {
	...Default.args,
	panelLayout: "single",
	height: "short",
	color: "blue",
	headerSlot: "Informational Message",
	defaultSlot: "This is a simple notification modal without any action buttons in the footer.",
	footerSlot: false,
};

export const DropFromTop = Template.bind({});
DropFromTop.args = {
	...Default.args,
	animationType: "drop-from-top",
	height: "medium",
	color: "green",
	headerSlot: "Drop From Top Animation",
	defaultSlot: "This modal demonstrates the 'drop-from-top' animation with the splash effect.",
};

export const RiseFromBotton = Template.bind({});
RiseFromBotton.args = {
	...Default.args,
	animationType: "rise-from-bottom",
	color: "green",
	headerSlot: "Rise From Bottom Animation",
	defaultSlot: "This modal demonstrates the 'rise-from-bottom' animation with the splash effect.",
};

export const ExpandFromClick = (args) => ({
	components: { BaseModal, GlassyButton },
	setup() {
		const isModalOpen = ref(false);
		const clickPos = ref({ x: 0, y: 0 });

		const openModal = (event) => {
			clickPos.value = { x: event.clientX, y: event.clientY };
			isModalOpen.value = true;
		};

		const closeModal = () => {
			isModalOpen.value = false;
		};

		return { args, isModalOpen, clickPos, openModal, closeModal };
	},
	template: `
    <div @click="openModal" class="h-screen w-full flex items-center justify-center bg-gray-200 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-400 dark:border-gray-600 cursor-pointer">
      <div class="text-center p-8 pointer-events-none">
        <h2 class="text-2xl font-bold text-gray-700 dark:text-gray-300">Click Anywhere</h2>
        <p class="text-gray-500 dark:text-gray-400">Click anywhere in this box to open the modal from that position.</p>
      </div>
      <BaseModal
        :show="isModalOpen"
        :width="args.width"
		:height="args.height"
        :color="args.color"
        animationType="expand-from-click"
        :clickPosition="clickPos"
        :panelLayout="args.panelLayout"
        @close="closeModal"
      >
        <template #header v-if="args.headerSlot">
        	{{ args.headerSlot }}
      	</template>
      
      	<!-- Default slot for single panel layout -->
      	<p>{{ args.defaultSlot }}</p>
      
      	<!-- Named slots for double panel layout -->
      	<template #left-panel>
       		<p>{{ args.leftPanelSlot }}</p>
      	</template>
      	<template #right-panel>
        	<p>{{ args.rightPanelSlot }}</p>
      	</template>

      	<template #footer v-if="args.footerSlot">
        	<GlassyButton themeColor="blue" @click="closeModal">Got it!</GlassyButton>
      	</template>
      </BaseModal>
    </div>
  `,
});

ExpandFromClick.args = {
	...Default.args,
	show: false, // Start with modal hidden for this interactive story
	headerSlot: "Expanding From Your Click",
	defaultSlot: "This modal animates out directly from the point where you clicked.",
};

ExpandFromClick.parameters = {
	controls: {
		// We control these via the interactive wrapper, so hide them from the controls panel
		exclude: ['show', 'onClose', 'clickPosition', 'animationType'],
	},
};

