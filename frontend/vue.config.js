const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
	transpileDependencies: true,
	devServer: {
		proxy: {
			"^/api/v1": {
				// Using ^ to match the start of the path
				target: "http://localhost:8000", // Your FastAPI backend address
				changeOrigin: true,
			},
		},
	},
});
