import GlassyTabCarousel from './GlassyTabCarousel.vue';
import GlassyTabPanel from '../ui/GlassyTabPanel.vue';

// A simple placeholder component to simulate content inside the panels
const PlaceholderContent = {
	props: ['title', 'body'],
	template: `
        <div class="p-4 h-64 flex flex-col items-center justify-center text-center">
            <h3 class="text-xl font-bold mb-2">{{ title }}</h3>
            <p>{{ body }}</p>
        </div>
    `,
};

export default {
	title: 'Common/GlassyTabCarousel',
	component: GlassyTabCarousel,
	parameters: {
		layout: 'centered',
		backgrounds: {
			default: 'light',
			values: [
				{ name: "dark", value: "#1f2937" }, // gray-800
				{ name: "light", value: "#f9fafb" }, // gray-50
			],
		},
	},
};

// --- STORIES ---

export const Default = (args) => ({
	components: { GlassyTabCarousel, GlassyTabPanel, PlaceholderContent },
	setup() {
		return { args };
	},
	template: `
    <div class="w-[450px]">
      <GlassyTabCarousel>
        <GlassyTabPanel title="Dashboard" themecolor="green">
            <PlaceholderContent title="Dashboard Panel" body="Content for the dashboard goes here." />
        </GlassyTabPanel>
        <GlassyTabPanel title="Profile" themeColor="blue">
            <PlaceholderContent title="Profile Panel" body="User profile information and settings." />
        </GlassyTabPanel>
        <GlassyTabPanel title="Manage" themeColor="indigo">
            <PlaceholderContent title="Manage Tree Panel" body="This could contain the ManageTreeTab component." />
        </GlassyTabPanel>
        <GlassyTabPanel title="Alerts" themeColor="danger">
            <PlaceholderContent title="Alerts Panel" body="Critical alerts and notifications." />
        </GlassyTabPanel>
      </GlassyTabCarousel>
    </div>
  `,
});
Default.storyName = "Default";

export const SingleTab = (args) => ({
	components: { GlassyTabCarousel, GlassyTabPanel, PlaceholderContent },
	setup() {
		return { args };
	},
	template: `
    <div class="w-[450px]">
      <GlassyTabCarousel>
        <GlassyTabPanel title="Dashboard" themeColor="green">
            <PlaceholderContent title="Dashboard Panel" body="Content for a single dashboard tab." />
        </GlassyTabPanel>
      </GlassyTabCarousel>
    </div>
  `,
});
SingleTab.storyName = 'With a Single Tab';

export const NoTabs = (args) => ({
	components: { GlassyTabCarousel },
	setup() {
		return { args };
	},
	template: `
    <div class="w-[450px]">
        <GlassyTabCarousel v-bind="args" />
    </div>
  `,
});
NoTabs.storyName = 'Empty (No Tabs)';