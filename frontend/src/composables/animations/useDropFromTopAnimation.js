export function useDropFromTopAnimation() {
	return {
		enterFrom: "opacity-0 -translate-y-full scale-50 rounded-full",
		enterTo: "opacity-100 translate-y-0 scale-100 rounded-2xl",
		leaveFrom: "opacity-100 translate-y-0 scale-100 rounded-2xl",
		leaveTo: "opacity-0 -translate-y-full scale-50 rounded-full",
	};
}