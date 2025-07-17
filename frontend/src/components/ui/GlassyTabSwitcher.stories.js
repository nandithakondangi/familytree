import { ref } from 'vue';
import GlassyTabSwitcher from './GlassyTabSwitcher.vue';

export default {
  title: 'UI/GlassyTabSwitcher',
  component: GlassyTabSwitcher,
  argTypes: {
    themeColor: {
      control: 'select',
      options: ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger'],
      defaultValue: 'indigo'
    }
  }
};

const Template = (args) => ({
  components: { GlassyTabSwitcher },
  setup() {
    const activeIndex = ref(0);
    return { args, activeIndex };
  },
  template: `
    <GlassyTabSwitcher
      v-model:activeIndex="activeIndex"
      v-bind="args"
    />
  `
});

export const Default = Template.bind({});
Default.args = {
  tabs: [
    { title: 'Profile' },
    { title: 'Settings' },
    { title: 'Messages' },
  ],
};

export const LongTitles = Template.bind({});
LongTitles.args = {
  tabs: [
    { title: 'Personal Information' },
    { title: 'Account Settings' },
    { title: 'Notification Preferences' },
  ],
};

export const ManyTabs = Template.bind({});
ManyTabs.args = {
  tabs: [
    { title: 'Tab 1' },
    { title: 'Tab 2' },
    { title: 'Tab 3' },
    { title: 'Tab 4' },
    { title: 'Tab 5' },
  ],
};

// Show all color variants
export const ColorVariants = () => ({
  components: { GlassyTabSwitcher },
  setup() {
    const activeIndices = ref({
      blue: 0,
      indigo: 0,
      green: 0,
      orange: 0,
      yellow: 0,
      danger: 0
    });
    
    const tabs = [
      { title: 'Profile' },
      { title: 'Settings' },
      { title: 'Messages' },
    ];

    return { activeIndices, tabs };
  },
  template: `
    <div class="space-y-4">
      <GlassyTabSwitcher
        v-for="color in ['blue', 'indigo', 'green', 'orange', 'yellow', 'danger']"
        :key="color"
        :theme-color="color"
        :tabs="tabs"
        v-model:activeIndex="activeIndices[color]"
      />
    </div>
  `
});
