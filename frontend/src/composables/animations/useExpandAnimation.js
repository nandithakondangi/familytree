export function useExpandAnimation() {
	return {
        enterFrom: 'opacity-0 scale-0 rounded-full',
        enterTo: 'opacity-100 scale-100 rounded-2xl',
        leaveFrom: 'opacity-100 scale-100 rounded-2xl',
        leaveTo: 'opacity-0 scale-0 rounded-full',
    };
}
