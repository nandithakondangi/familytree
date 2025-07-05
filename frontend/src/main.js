import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";

import "./assets/css/tailwind.css"; // Or your main CSS entry
import "./assets/css/global.css"; // Your new global CSS with theme variables

const app = createApp(App);

app.use(createPinia()); // Use Pinia

app.mount("#app");
