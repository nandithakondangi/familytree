<template>
	<Transition
		enter-active-class="transition-all ease-out duration-500"
		enter-from-class="opacity-0 translate-y-full"
		enter-to-class="opacity-100 translate-y-0"
		leave-active-class="transition-all ease-in duration-300"
		leave-from-class="opacity-100 translate-y-0"
		leave-to-class="opacity-0 translate-y-full scale-50"
	>
		<div
			v-if="isVisible"
			class="fixed inset-0 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex justify-center items-center"
		>
			<div
				class="relative bg-indigo-600/50 dark:bg-indigo-400/50 backdrop-blur-lg rounded-xl shadow-2xl p-6 max-w-md w-full mx-4"
			>
				<div
					class="flex justify-between items-center border-b border-gray-300/70 dark:border-gray-600/70 pb-3 mb-4"
				>
					<h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
						Add New Family Member
					</h3>
					<button
						@click="closeModal"
						class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
					>
						<svg
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<form @submit.prevent="saveMember">
					<div class="space-y-4">
						<div>
							<label
								for="name"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>Name: <span class="text-red-500">*</span></label
							>
							<input
								type="text"
								id="name"
								v-model="form.name"
								required
								class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
								placeholder="Name"
							/>
						</div>

						<div>
							<label
								for="nicknames"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>Nicknames:</label
							>
							<input
								type="text"
								id="nicknames"
								v-model="form.nicknames"
								class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
								placeholder="e.g., Johnny, Beth (comma-separated)"
							/>
						</div>

						<div>
							<label
								for="gender"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>Gender:</label
							>
							<select
								id="gender"
								v-model="form.gender"
								class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
							>
								<option
									v-for="option in genderOptions"
									:key="option.value"
									:value="option.value"
								>
									{{ option.text }}
								</option>
							</select>
						</div>

						<div class="flex items-center justify-between">
							<label
								for="isDobKnown"
								class="block text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
								>Is Date of Birth Known?</label
							>
							<div
								class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
							>
								<input
									type="checkbox"
									id="isDobKnown"
									v-model="form.isDobKnown"
									class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white dark:bg-slate-800 border-4 appearance-none cursor-pointer"
								/>
								<label
									for="isDobKnown"
									class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"
								></label>
							</div>
						</div>

						<div
							v-if="form.isDobKnown"
							class="space-y-3 p-4 bg-slate-300/50 dark:bg-slate-200/40 rounded-md shadow-inner"
						>
							<h4
								class="text-md font-semibold text-gray-700 dark:text-gray-300"
							>
								Date of Birth Details:
							</h4>
							<div>
								<label
									class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
									>Gregorian DOB:</label
								>
								<input
									type="date"
									v-model="form.gregorianDobString"
									:max="todayDateString"
									class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
								/>
							</div>

							<div v-if="isIndianCulture">
								<label
									class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
									>Traditional DOB:</label
								>
								<div class="flex space-x-3">
									<select
										v-model="form.traditionalDob.tamilMonth"
										class="block w-1/2 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
									>
										<option
											v-for="option in TamilMonthOptions"
											:key="option.value"
											:value="option.value"
										>
											{{ option.text }}
										</option>
									</select>
									<select
										v-model="form.traditionalDob.tamilStar"
										class="block w-1/2 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
									>
										<option
											v-for="option in TamilStarOptions"
											:key="option.value"
											:value="option.value"
										>
											{{ option.text }}
										</option>
									</select>
								</div>
							</div>
						</div>

						<div class="flex items-center justify-between">
							<label
								for="isPersonAlive"
								class="block text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
								>This person is alive</label
							>
							<div
								class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
							>
								<input
									type="checkbox"
									id="isPersonAlive"
									v-model="form.isPersonAlive"
									class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white dark:bg-slate-800 border-4 appearance-none cursor-pointer"
								/>
								<label
									for="isPersonAlive"
									class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"
								></label>
							</div>
						</div>

						<div
							v-if="!form.isPersonAlive"
							class="space-y-3 p-4 bg-slate-300/50 dark:bg-slate-200/40 rounded-md shadow-inner"
						>
							<h4
								class="text-md font-semibold text-gray-700 dark:text-gray-300"
							>
								Date of Death Details:
							</h4>

							<div class="flex items-center justify-between">
								<label
									for="isDodKnown"
									class="block text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
									>Is Date of Death Known?</label
								>
								<div
									class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
								>
									<input
										type="checkbox"
										id="isDodKnown"
										v-model="form.isDodKnown"
										class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white dark:bg-slate-800 border-4 appearance-none cursor-pointer"
									/>
									<label
										for="isDodKnown"
										class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"
									></label>
								</div>
							</div>

							<div v-if="form.isDodKnown" class="space-y-3">
								<div>
									<label
										class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Gregorian DoD:</label
									>
									<input
										type="date"
										v-model="form.gregorianDodString"
										:max="todayDateString"
										class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
									/>
								</div>

								<div v-if="isIndianCulture">
									<label
										class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Traditional DoD:</label
									>
									<div class="grid grid-cols-3 gap-3">
										<select
											v-model="form.traditionalDod.tamilMonth"
											class="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
										>
											<option
												v-for="option in TamilMonthOptions"
												:key="option.value"
												:value="option.value"
											>
												{{ option.text }}
											</option>
										</select>
										<select
											v-model="form.traditionalDod.paksham"
											class="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
										>
											<option
												v-for="option in PakshamOptions"
												:key="option.value"
												:value="option.value"
											>
												{{ option.text }}
											</option>
										</select>
										<select
											v-model="form.traditionalDod.thithi"
											class="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
										>
											<option
												v-for="options in ThithiOptions"
												:key="options.value"
												:value="options.value"
											>
												{{ options.text }}
											</option>
										</select>
									</div>
								</div>
							</div>
						</div>
					</div>

					<div class="flex justify-end space-x-4 mt-6">
						<button
							type="button"
							@click="closeModal"
							class="px-4 py-2 bg-gray-300/70 dark:bg-gray-600/70 text-gray-800 dark:text-gray-200 font-medium rounded-lg hover:bg-gray-400/80 dark:hover:bg-gray-500/80 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500 focus:ring-opacity-75 transition duration-150 ease-in-out"
						>
							X Cancel
						</button>
						<button
							type="submit"
							class="px-4 py-2 bg-indigo-600 dark:bg-indigo-500 text-white font-medium rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-white/50 dark:focus:ring-offset-slate-800/50 transition duration-150 ease-in-out"
						>
							💾 Save Member
						</button>
					</div>
				</form>
			</div>
		</div>
	</Transition>
</template>

<script>
	import { reactive, watch, computed, inject } from "vue";
	import { FamilyMember } from "../proto/family_tree_pb";
	import {
		GregorianDate as ProtoGregorianDate,
		TraditionalDate as ProtoTraditionalDate,
		Gender as ProtoGender,
		TamilMonth as ProtoTamilMonth,
		TamilStar as ProtoTamilStar,
		Paksham as ProtoPaksham,
		Thithi as ProtoThithi,
	} from "../proto/utils_pb";

	export default {
		name: "AddPersonModal",
		props: {
			isVisible: {
				type: Boolean,
				required: true,
			},
			isIndianCulture: {
				type: Boolean,
				required: true,
			},
			inferRelationshipsEnabled: {
				type: Boolean,
				required: true,
			},
		},
		emits: ["close", "save"],
		setup(props, { emit }) {
			const updateStatus = inject("updateStatus");
			const form = reactive({
				name: "",
				nicknames: "",
				gender: "GENDER_UNKNOWN",
				isDobKnown: false,
				gregorianDobString: "",
				traditionalDob: {
					tamilMonth: "TAMIL_MONTH_UNKNOWN",
					tamilStar: "TAMIL_STAR_UNKNOWN",
				},
				isPersonAlive: true,
				isDodKnown: false,
				gregorianDodString: "",
				traditionalDod: {
					tamilMonth: "TAMIL_MONTH_UNKNOWN",
					paksham: "PAKSHAM_UNKNOWN",
					thithi: "THITHI_UNKNOWN",
				},
			});

			const getTodayDateStringLocal = () => {
				const today = new Date();
				const year = today.getFullYear();
				const month = (today.getMonth() + 1).toString().padStart(2, "0"); // Months are 0-indexed
				const day = today.getDate().toString().padStart(2, "0");
				return `${year}-${month}-${day}`;
			};
			const todayDateString = getTodayDateStringLocal();

			const genderOptions = computed(() => {
				return Object.keys(ProtoGender).map((key) => {
					// Create a more user-friendly text representation for each option
					const text = key
						.replace("GENDER_", "")
						.replace("_", "")
						.toUpperCase();
					return {
						value: key,
						text: text === "UNKNOWN" ? "GENDER UNKNOWN" : text,
					};
				});
			});

			const TamilMonthOptions = computed(() => {
				return Object.keys(ProtoTamilMonth).map((key) => {
					// Create user friendly text representation for each option
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return {
						value: key,
						text: text,
					};
				});
			});

			const TamilStarOptions = computed(() => {
				return Object.keys(ProtoTamilStar).map((key) => {
					// Create user friendly test representation for each option
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return {
						value: key,
						text: text,
					};
				});
			});

			const PakshamOptions = computed(() => {
				return Object.keys(ProtoPaksham).map((key) => {
					// Create user friendly text representation for each option
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return {
						value: key,
						text: text,
					};
				});
			});
			const ThithiOptions = computed(() => {
				return Object.keys(ProtoThithi).map((key) => {
					// Create user friendly text representation for each option
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return {
						value: key,
						text: text,
					};
				});
			});

			// Watch for changes in isPersonAlive to reset isDodKnown if person becomes alive
			watch(
				() => form.isPersonAlive,
				(newValue) => {
					if (newValue) {
						form.isDodKnown = false;
						// Optionally clear death date fields when person is marked alive
						form.gregorianDodString = "";
						form.traditionalDod = {
							tamilMonth: "TAMIL_MONTH_UNKNOWN",
							paksham: "PAKSHAM_UNKNOWN",
							thithi: "THITHI_UNKNOWN",
						};
					}
				}
			);

			// Watch for changes in isDobKnown to clear DOB fields if unknown
			watch(
				() => form.isDobKnown,
				(newValue) => {
					if (!newValue) {
						form.gregorianDobString = "";
						form.traditionalDob = {
							tamilMonth: "TAMIL_MONTH_UNKNOWN",
							tamilStar: "TAMIL_STAR_UNKNOWN",
						};
					}
				}
			);

			// Watch for changes in isDodKnown to clear DOD fields if unknown
			watch(
				() => form.isDodKnown,
				(newValue) => {
					if (!newValue) {
						form.gregorianDodString = "";
						form.traditionalDod = {
							tamilMonth: "TAMIL_MONTH_UNKNOWN",
							paksham: "PAKSHAM_UNKNOWN",
							thithi: "THITHI_UNKNOWN",
						};
					}
				}
			);

			const parseDateString = (dateString) => {
				if (!dateString) return null;
				const parts = dateString.split("-");
				if (parts.length === 3) {
					return {
						day: parseInt(parts[2], 10),
						month: parseInt(parts[1], 10),
						year: parseInt(parts[0], 10),
					};
				}
				return null;
			};

			const closeModal = () => {
				emit("close"); // Emit close event to parent
				resetForm(); // Reset form state when closing
			};

			const saveMember = () => {
				// Basic validation (name is required)
				if (!form.name.trim()) {
					alert("Name is required."); // Replace with a more styled notification later
					return;
				}

				// --- Construct Protobuf Messages ---
				const familyMemberMessage = new FamilyMember();
				familyMemberMessage.setName(form.name.trim());
				familyMemberMessage.setNicknamesList(
					form.nicknames
						.split(",")
						.map((name) => name.trim())
						.filter((name) => name)
				);
				familyMemberMessage.setGender(ProtoGender[form.gender]);
				familyMemberMessage.setAlive(form.isPersonAlive);

				if (form.isDobKnown) {
					const dob = parseDateString(form.gregorianDobString);
					if (dob) {
						const gregorianDobMessage = new ProtoGregorianDate();
						gregorianDobMessage.setYear(dob.year);
						gregorianDobMessage.setMonth(dob.month);
						gregorianDobMessage.setDate(dob.day);
						familyMemberMessage.setDateOfBirth(gregorianDobMessage);
					}

					if (props.isIndianCulture) {
						const traditionalDobMessage = new ProtoTraditionalDate();
						if (form.traditionalDob.tamilMonth !== "TAMIL_MONTH_UNKNOWN") {
							traditionalDobMessage.setMonth(
								ProtoTamilMonth[form.traditionalDob.tamilMonth]
							);
						}
						if (form.traditionalDob.tamilStar !== "TAMIL_STAR_UNKNOWN") {
							traditionalDobMessage.setStar(
								ProtoTamilStar[form.traditionalDob.tamilStar]
							);
						}
						// Only set if at least one field is not UNKNOWN
						if (
							traditionalDobMessage.getMonth() !==
								ProtoTamilMonth.TAMIL_MONTH_UNKNOWN ||
							traditionalDobMessage.getStar() !==
								ProtoTamilStar.TAMIL_STAR_UNKNOWN
						) {
							familyMemberMessage.setTraditionalDateOfBirth(
								traditionalDobMessage
							);
						}
					}
				}

				if (!form.isPersonAlive && form.isDodKnown) {
					const dod = parseDateString(form.gregorianDodString);
					if (dod) {
						const gregorianDodMessage = new ProtoGregorianDate();
						gregorianDodMessage.setYear(dod.year);
						gregorianDodMessage.setMonth(dod.month);
						gregorianDodMessage.setDate(dod.day);
						familyMemberMessage.setDateOfDeath(gregorianDodMessage);
					}

					if (props.isIndianCulture) {
						const traditionalDodMessage = new ProtoTraditionalDate();
						if (form.traditionalDod.tamilMonth !== "TAMIL_MONTH_UNKNOWN") {
							traditionalDodMessage.setMonth(
								ProtoTamilMonth[form.traditionalDod.tamilMonth]
							);
						}
						if (form.traditionalDod.paksham !== "PAKSHAM_UNKNOWN") {
							traditionalDodMessage.setPaksham(
								ProtoPaksham[form.traditionalDod.paksham]
							);
						}
						if (form.traditionalDod.thithi !== "THITHI_UNKNOWN") {
							traditionalDodMessage.setThithi(
								ProtoThithi[form.traditionalDod.thithi]
							);
						}
						// Only set if at least one field is not UNKNOWN
						if (
							traditionalDodMessage.getMonth() !==
								ProtoTamilMonth.TAMIL_MONTH_UNKNOWN ||
							traditionalDodMessage.getPaksham() !==
								ProtoPaksham.PAKSHAM_UNKNOWN ||
							traditionalDodMessage.getThithi() !== ProtoThithi.THITHI_UNKNOWN
						) {
							familyMemberMessage.setTraditionalDateOfDeath(
								traditionalDodMessage
							);
						}
					}
				}

				const memberProtoJson = familyMemberMessage.toObject();
				console.log("Saving member (Protobuf JSON):", memberProtoJson);

				fetch("/api/v1/manage/add_family_member", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(memberProtoJson),
				})
					.then((response) => {
						if (!response.ok) {
							return response
								.json()
								.then((errBody) => {
									throw new Error(
										errBody.detail || `Server error: ${response.status}`
									);
								})
								.catch(() => {
									throw new Error(
										`Server error: ${response.status} ${response.statusText}`
									);
								});
						}
						return response.json();
					})
					.then((data) => {
						console.log("Person added successfully:", data.message);
						updateStatus(data.message || "Person added successfully!", 5000);

						emit("save", data);
						closeModal();
					})
					.catch((error) => {
						console.error("Error adding person:", error);
						updateStatus(`Error adding person: ${error.message}`, 7000);
					});
			};

			const resetForm = () => {
				form.name = "";
				form.nicknames = "";
				form.gender = "GENDER_UNKNOWN";
				form.isDobKnown = false;
				form.gregorianDobString = "";
				form.traditionalDob = {
					tamilMonth: "TAMIL_MONTH_UNKNOWN",
					tamilStar: "TAMIL_STAR_UNKNOWN",
				};
				form.isPersonAlive = true;
				form.isDodKnown = false;
				form.gregorianDodString = "";
				form.traditionalDod = {
					tamilMonth: "TAMIL_MONTH_UNKNOWN",
					paksham: "PAKSHAM_UNKNOWN",
					thithi: "THITHI_UNKNOWN",
				};
			};

			return {
				form,
				genderOptions,
				TamilMonthOptions,
				TamilStarOptions,
				PakshamOptions,
				ThithiOptions,
				todayDateString,
				closeModal,
				saveMember,
				updateStatus,
			};
		},
	};
</script>

<style scoped>
	/* Custom styles for the toggle switch */
	.toggle-checkbox {
		transition: right 0.2s ease-in-out, border-color 0.2s ease-in-out;
	}

	.toggle-checkbox:checked {
		right: 0; /* This might need adjustment if the knob is not visually centered */
		/* border-color: #6366f1; /* indigo-500 */ /* Color is handled by peer-checked on the label now */
	}

	.toggle-label {
		transition: background-color 0.2s ease-in-out;
	}
	.toggle-checkbox:checked + .toggle-label {
		background-color: #4f46e5; /* indigo-600 */
		/* In dark mode, this will be overridden by dark:peer-checked:bg-indigo-500 on the toggle div itself */
	}
</style>
