import globals from "globals";
import pluginJs from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import pluginStorybook from "eslint-plugin-storybook";
import eslintConfigPrettier from "eslint-config-prettier";
import vueParser from "vue-eslint-parser";
import babelParser from "@babel/eslint-parser";


export default [
  // Ignore Storybook configuration files from general linting, but allow plugin-storybook to lint them.
  {
    ignores: ["!.storybook"],
  },
  // Global settings for all files
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
  // ESLint's recommended rules
  pluginJs.configs.recommended,

  

  // Vue.js configuration
  ...pluginVue.configs["flat/recommended"], // Use 'flat/recommended' for Vue 3
  {
    files: ["**/*.vue"],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: babelParser, // Specify @babel/eslint-parser for Vue files
        requireConfigFile: false,
      },
    },
    rules: {
      // Add or override Vue-specific rules here
      // Example: 'vue/multi-word-component-names': 'off',
    },
  },

  // Storybook configuration
  ...pluginStorybook.configs["flat/recommended"],
  {
    files: ["**/*.stories.{js,jsx,ts,tsx,mjs,cjs}"],
    languageOptions: {
      parser: babelParser, // Use babelParser for JS Storybook files
      parserOptions: {
        requireConfigFile: false, // Allow @babel/eslint-parser to work without a babel.config.js
      },
    },
    rules: {
      // Add or override Storybook-specific rules here
      // Example: 'storybook/hierarchy-separator': 'error',
    },
  },

  // Prettier integration (must be last to override other formatting rules)
  eslintConfigPrettier,
];
