import GlassyTabPanel from './GlassyTabPanel.vue';

export default {
	title: 'UI/GlassyTabPanel',
	component: GlassyTabPanel,
	argTypes: {
		title: {
			control: 'text',
			description: 'The title of the tab panel (used by the parent carousel).',
		},
		themeColor: {
			control: { type: 'select' },
			options: ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger'],
			description: 'Sets the color theme of the panel.',
		},
		default: {
			control: 'text',
			description: 'HTML content for the default slot.',
		},
	},
	parameters: {
		layout: 'centered',
	},
	tags: ["autodocs"],
};

// Base template for stories that use simple text/HTML content
const Template = (args) => ({
	components: { GlassyTabPanel },
	setup() {
		return { args };
	},
	template: `
    <div class="w-80 h-96">
      <GlassyTabPanel v-bind="args">
        <div class="p-4" v-html="args.default"></div>
      </GlassyTabPanel>
    </div>
  `,
});

export const Default = Template.bind({});
Default.args = {
	title: 'Default Panel',
	themeColor: 'indigo',
	default: '<h4>Default Content</h4><p>This is the default content inside the glassy tab panel. It demonstrates the basic look and feel with the indigo theme.</p>',
};

export const DangerTheme = Template.bind({});
DangerTheme.args = {
	title: 'Alerts',
	themeColor: 'danger',
	default: '<h4>Important Alert!</h4><p>This panel uses the "danger" theme to draw attention to critical information.</p>',
};
