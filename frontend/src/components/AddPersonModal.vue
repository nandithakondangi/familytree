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
			class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex justify-center items-center"
		>
			<div
				class="relative bg-indigo-600/50 dark:bg-indigo-400/50 backdrop-blur-lg rounded-xl shadow-2xl p-6 max-w-2xl w-full mx-4"
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
					<div class="flex flex-col md:flex-row md:space-x-6">
						<!-- Left Pane: Image Upload -->
						<div
							class="w-full md:w-1/3 flex flex-col items-center space-y-3 py-4"
						>
							<input
								type="file"
								ref="imageInputRef"
								@change="handleImageUpload"
								class="hidden"
								accept="image/*"
							/>
							<div
								@click="triggerImageUpload"
								class="w-36 h-36 rounded-full bg-gray-200 dark:bg-slate-700 flex items-center justify-center cursor-pointer border-2 border-dashed border-gray-400 dark:border-gray-500 hover:border-indigo-500 dark:hover:border-indigo-400 transition-colors overflow-hidden"
								title="Click to upload profile image"
							>
								<img
									v-if="profileImagePreview"
									:src="profileImagePreview"
									alt="Profile preview"
									class="w-full h-full object-cover"
								/>
								<svg
									v-else
									class="w-16 h-16 text-gray-400 dark:text-gray-500"
									fill="currentColor"
									viewBox="0 0 20 20"
								>
									<path
										fill-rule="evenodd"
										d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
							<button
								v-if="profileImagePreview"
								type="button"
								@click="removeImage"
								class="px-3 py-1 text-xs bg-red-500/80 hover:bg-red-600/80 text-white rounded-md transition-colors"
							>
								Remove Image
							</button>
							<p class="text-xs text-gray-600 dark:text-gray-400 text-center">
								Optional: Click above to upload a profile picture.
							</p>
						</div>

						<!-- Right Pane: Form Fields -->
						<div class="w-full md:w-2/3 space-y-4">
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
									placeholder="Full Name"
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
								<!-- DOB Fields (Gregorian, Traditional) -->
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
									<!-- Traditional DOB fields -->
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
								<!-- DOD Fields -->
								<h4
									class="text-md font-semibold text-gray-700 dark:text-gray-300"
								>
									Date of Death Details:
								</h4>
								<div class="flex items-center justify-between">
									<label
										for="isDodKnownToggle"
										class="block text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
										>Is Date of Death Known?</label
									>
									<div
										class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
									>
										<input
											type="checkbox"
											id="isDodKnownToggle"
											v-model="form.isDodKnown"
											class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white dark:bg-slate-800 border-4 appearance-none cursor-pointer"
										/>
										<label
											for="isDodKnownToggle"
											class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"
										></label>
									</div>
								</div>
								<div v-if="form.isDodKnown" class="space-y-3">
									<!-- Gregorian and Traditional DOD -->
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
										<!-- Traditional DOD fields -->
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
													v-for="option in ThithiOptions"
													:key="option.value"
													:value="option.value"
												>
													{{ option.text }}
												</option>
											</select>
										</div>
									</div>
								</div>
							</div>

							<!-- Additional Information Section -->
							<div class="space-y-2 pt-2">
								<label
									class="block text-sm font-medium text-gray-700 dark:text-gray-300"
									>Additional Information:</label
								>
								<div
									v-for="(field, index) in form.dynamicFields"
									:key="index"
									class="flex items-center space-x-2"
								>
									<input
										type="text"
										v-model="field.key"
										placeholder="Field Name"
										class="mt-1 block w-2/5 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
									/>
									<input
										type="text"
										v-model="field.value"
										placeholder="Value"
										class="mt-1 block w-2/5 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200"
									/>
									<button
										type="button"
										@click="removeDynamicField(index)"
										title="Remove field"
										class="p-1.5 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 rounded-full hover:bg-red-100 dark:hover:bg-red-700/50 transition-colors"
									>
										<svg
											class="w-4 h-4"
											fill="currentColor"
											viewBox="0 0 20 20"
										>
											<path
												fill-rule="evenodd"
												d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z"
												clip-rule="evenodd"
											></path>
										</svg>
									</button>
								</div>
								<button
									type="button"
									@click="addDynamicField"
									class="mt-2 px-3 py-1.5 text-sm bg-green-500/80 hover:bg-green-600/80 text-white font-medium rounded-md hover:bg-green-600 transition-colors flex items-center"
								>
									<svg
										class="w-4 h-4 mr-1"
										fill="currentColor"
										viewBox="0 0 20 20"
									>
										<path
											fill-rule="evenodd"
											d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
											clip-rule="evenodd"
										></path>
									</svg>
									Add Field
								</button>
							</div>
						</div>
					</div>

					<div
						class="flex justify-end space-x-4 mt-8 pt-4 border-t border-gray-300/70 dark:border-gray-600/70"
					>
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
	import { reactive, watch, computed, inject, ref } from "vue";
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
				dynamicFields: [], // For key-value additional info
			});

			const profileImagePreview = ref(null);
			const imageInputRef = ref(null);

			const getTodayDateStringLocal = () => {
				const today = new Date();
				const year = today.getFullYear();
				const month = (today.getMonth() + 1).toString().padStart(2, "0");
				const day = today.getDate().toString().padStart(2, "0");
				return `${year}-${month}-${day}`;
			};
			const todayDateString = getTodayDateStringLocal();

			const genderOptions = computed(() => {
				return Object.keys(ProtoGender).map((key) => {
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
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return { value: key, text: text };
				});
			});

			const TamilStarOptions = computed(() => {
				return Object.keys(ProtoTamilStar).map((key) => {
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return { value: key, text: text };
				});
			});

			const PakshamOptions = computed(() => {
				return Object.keys(ProtoPaksham).map((key) => {
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return { value: key, text: text };
				});
			});

			const ThithiOptions = computed(() => {
				return Object.keys(ProtoThithi).map((key) => {
					const text = key
						.replace("_UNKNOWN", "")
						.replace("_", " ")
						.toUpperCase();
					return { value: key, text: text };
				});
			});

			watch(
				() => form.isPersonAlive,
				(newValue) => {
					if (newValue) {
						form.isDodKnown = false;
						form.gregorianDodString = "";
						form.traditionalDod = {
							tamilMonth: "TAMIL_MONTH_UNKNOWN",
							paksham: "PAKSHAM_UNKNOWN",
							thithi: "THITHI_UNKNOWN",
						};
					}
				}
			);

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
				emit("close");
				resetForm();
			};

			const saveMember = () => {
				if (!form.name.trim()) {
					alert("Name is required.");
					return;
				}

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

				// Prepare additionalInfo map for protobuf
				const finalAdditionalInfoObject = {};
				if (profileImagePreview.value) {
					finalAdditionalInfoObject["profilePictureBase64"] =
						profileImagePreview.value;
				}
				form.dynamicFields.forEach((field) => {
					if (field.key && field.key.trim() !== "") {
						finalAdditionalInfoObject[field.key.trim()] = field.value;
					}
				});

				const additionalInfoProtoMap =
					familyMemberMessage.getAdditionalInfoMap();
				for (const [key, value] of Object.entries(finalAdditionalInfoObject)) {
					additionalInfoProtoMap.set(key, value);
				}

				const memberProtoJson = familyMemberMessage.toObject();

				if (
					Object.prototype.hasOwnProperty.call(memberProtoJson, "nicknamesList")
				) {
					memberProtoJson.nicknames = memberProtoJson.nicknamesList;
					delete memberProtoJson.nicknamesList;
				}

				// Ensure additionalInfo is a direct object for Python backend
				memberProtoJson.additionalInfo = finalAdditionalInfoObject;
				if (
					Object.prototype.hasOwnProperty.call(
						memberProtoJson,
						"additionalInfoMap"
					)
				) {
					memberProtoJson.additionalInfo = memberProtoJson.additionalInfoMap;
					delete memberProtoJson.additionalInfoMap; // Clean up if toObject() created this
				}

				const request_data = {
					infer_relationships: props.inferRelationshipsEnabled,
					new_member_data: memberProtoJson,
				};

				fetch("/api/v1/manage/add_family_member", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(request_data),
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
				form.dynamicFields = [];
				profileImagePreview.value = null;
				if (imageInputRef.value) {
					imageInputRef.value.value = "";
				}
			};

			const addDynamicField = () => {
				form.dynamicFields.push({ key: "", value: "" });
			};

			const removeDynamicField = (index) => {
				form.dynamicFields.splice(index, 1);
			};

			const handleImageUpload = (event) => {
				const file = event.target.files[0];
				if (file && file.type.startsWith("image/")) {
					const reader = new FileReader();
					reader.onload = (e) => {
						profileImagePreview.value = e.target.result; // base64 Data URL
					};
					reader.readAsDataURL(file);
				} else {
					profileImagePreview.value = null;
					if (file) {
						// if a file was selected but not an image
						updateStatus(
							"Please select a valid image file (e.g., JPG, PNG).",
							4000
						);
					}
				}
			};

			const triggerImageUpload = () => {
				imageInputRef.value?.click();
			};

			const removeImage = () => {
				profileImagePreview.value = null;
				if (imageInputRef.value) {
					imageInputRef.value.value = ""; // Reset file input
				}
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
				profileImagePreview,
				imageInputRef,
				handleImageUpload,
				triggerImageUpload,
				removeImage,
				addDynamicField,
				removeDynamicField,
			};
		},
	};
</script>

<style scoped>
	/* Custom styles for the toggle switch (existing) */
	.toggle-checkbox {
		transition: right 0.2s ease-in-out, border-color 0.2s ease-in-out;
	}
	.toggle-checkbox:checked {
		right: 0;
	}
	.toggle-label {
		transition: background-color 0.2s ease-in-out;
	}
	.toggle-checkbox:checked + .toggle-label {
		background-color: #4f46e5; /* indigo-600 */
	}

	/* Ensure enough height for scrollable content if form grows very long */
	/* The parent .fixed inset-0 already has overflow-y-auto */
</style>
