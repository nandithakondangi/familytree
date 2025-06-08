let clickTimeout = null;
let lastClickedNodeId = null;
const doubleClickThreshold = 250;
let networkCheckCount = 0;
const maxNetworkCheckCount = 20;

let checkNetworkInterval = setInterval(() => {
	networkCheckCount++;
	if (typeof network !== "undefined" && network) {
		clearInterval(checkNetworkInterval);

		network.on("click", function (params) {
			if (params.nodes && params.nodes.length > 0) {
				const nodeId = params.nodes[0];
				clearTimeout(clickTimeout);
				lastClickedNodeId = nodeId;
				const clickEvent = params.event.srcEvent;

				clickTimeout = setTimeout(() => {
					window.parent.postMessage(
						{
							type: "nodeSingleClick",
							nodeId: nodeId,
							clientX: clickEvent.clientX,
							clientY: clickEvent.clientY,
						},
						"*"
					);
					clickTimeout = null;
					lastClickedNodeId = null;
				}, doubleClickThreshold);
			} else {
				clearTimeout(clickTimeout);
				clickTimeout = null;
				lastClickedNodeId = null;
			}
		});

		network.on("doubleClick", function (params) {
			if (params.nodes && params.nodes.length > 0) {
				const nodeId = params.nodes[0];
				if (clickTimeout && lastClickedNodeId === nodeId) {
					clearTimeout(clickTimeout);
					clickTimeout = null;
					lastClickedNodeId = null;
				}
				window.parent.postMessage(
					{ type: "nodeDoubleClick", nodeId: nodeId },
					"*"
				);
			}
		});

		network.on("oncontext", function (params) {
			params.event.preventDefault();
			const nodeId = network.getNodeAt(params.pointer.DOM);
			if (nodeId) {
				if (clickTimeout && lastClickedNodeId === nodeId) {
					clearTimeout(clickTimeout);
					clickTimeout = null;
					lastClickedNodeId = null;
				}
				window.parent.postMessage(
					{
						type: "nodeRightClick",
						nodeId: nodeId,
						x: params.event.clientX,
						y: params.event.clientY,
					},
					"*"
				);
			}
		});
	} else {
		if (networkCheckCount >= maxNetworkCheckCount) {
			clearInterval(checkNetworkInterval);
		}
	}
}, 500);
