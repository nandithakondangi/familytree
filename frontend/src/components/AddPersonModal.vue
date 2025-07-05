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
				class="relative backdrop-blur-lg rounded-xl shadow-2xl p-6 max-w-2xl w-full mx-4 flex flex-col h-[65vh]"
				style="background-color: var(--theme-bg-primary)"
			>
				<div
					class="flex justify-between items-center border-b pb-3 mb-4"
					style="border-color: var(--theme-border-color)"
				>
					<h3
						class="text-lg font-semibold"
						style="color: var(--theme-text-on-primary-bg)"
					>
						Add New Family Member
					</h3>
					<button
						@click="closeModal"
						class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
					>
						<svg
							class="h-6 w-6 icon-close"
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

				<form @submit.prevent="saveMember" class="flex-1 flex flex-col min-h-0">
					<div class="flex-1 flex flex-col md:flex-row md:space-x-6 min-h-0">
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
								class="image-upload-area w-36 h-36 rounded-full flex items-center justify-center cursor-pointer border-2 border-dashed transition-colors overflow-hidden"
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
									class="w-16 h-16 image-placeholder-icon"
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
								class="button-danger px-3 py-1 text-xs rounded-md transition-colors"
							>
								Remove Image
							</button>
							<p
								class="text-xs text-center"
								style="color: var(--theme-text-secondary-on-primary-bg)"
							>
								Optional: Click above to upload a profile picture.
							</p>

							<!-- Contextual Information if adding via relationship -->
							<div
								v-if="sourceNodeIdForRelationship"
								class="contextual-info-box mt-4 p-3 rounded-md shadow w-full"
							>
								<h4
									class="text-sm font-semibold mb-2 text-center"
									style="color: var(--theme-text-primary)"
								>
									Adding new member relative to:
								</h4>
								<div class="space-y-1 text-xs">
									<p class="text-center">
										<span
											class="font-medium"
											style="color: var(--theme-text-secondary)"
											>Name:</span
										>
										<span
											class="ml-1"
											style="color: var(--theme-text-primary)"
											>{{ sourceMemberNameForRelationship || "N/A" }}</span
										>
									</p>
									<p class="text-center">
										<span
											class="font-medium"
											style="color: var(--theme-text-secondary)"
											>ID:</span
										>
										<span
											class="ml-1"
											style="color: var(--theme-text-primary)"
											>{{ sourceNodeIdForRelationship }}</span
										>
									</p>
									<p class="text-center">
										<span class="font-medium text-gray-600 dark:text-gray-300"
											>New Member will be their:</span
										>
										<span
											class="ml-1"
											style="color: var(--theme-text-primary)"
											>{{ formattedRelationshipType }}</span
										>
									</p>
								</div>
							</div>
						</div>

						<!-- Right Pane: Form Fields -->
						<div
							class="w-full md:w-2/3 flex-1 space-y-4 overflow-y-auto md:h-full min-h-0 py-4 pr-2"
						>
							<!-- Contextual Information if adding via relationship -->
							<div>
								<label for="name" class="form-label"
									>Name: <span class="text-red-500">*</span></label
								>
								<input
									type="text"
									id="name"
									v-model="form.name"
									required
									class="input-field mt-1 block w-full sm:text-sm"
									placeholder="Full Name"
								/>
							</div>

							<div>
								<label for="nicknames" class="form-label">Nicknames:</label>
								<input
									type="text"
									id="nicknames"
									v-model="form.nicknames"
									class="input-field mt-1 block w-full sm:text-sm"
									placeholder="e.g., Johnny, Beth (comma-separated)"
								/>
							</div>

							<div>
								<label for="gender" class="form-label">Gender:</label>
								<select
									id="gender"
									v-model="form.gender"
									class="input-field mt-1 block w-full sm:text-sm"
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
								<label for="isDobKnown" class="form-label cursor-pointer"
									>Is Date of Birth Known?</label
								>
								<div class="toggle-switch-container">
									<input
										type="checkbox"
										id="isDobKnown"
										v-model="form.isDobKnown"
										class="toggle-checkbox-custom"
									/>
									<label for="isDobKnown" class="toggle-label-custom"></label>
								</div>
							</div>

							<div
								v-if="form.isDobKnown"
								class="space-y-3 p-4 rounded-md shadow-inner"
								style="background-color: var(--theme-bg-tertiary)"
							>
								<!-- DOB Fields (Gregorian, Traditional) -->
								<h4
									class="text-md font-semibold"
									style="color: var(--theme-text-primary)"
								>
									Date of Birth Details:
								</h4>
								<div>
									<label
										class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
										style="color: var(--theme-text-primary)"
										>Gregorian DOB:</label
									>
									<date-picker
										:value="form.gregorianDobString"
										@update:value="
											(value) => handleDateUpdate('gregorianDobString', value)
										"
										type="date"
										format="YYYY-MM-DD"
										value-type="format"
										placeholder="YYYY-MM-DD"
										:editable="true"
										:disabled-date="disableFutureDates"
										input-class="input-field mt-1 block w-full sm:text-sm"
										popup-class="datepicker-popup-theme"
										class="w-full"
										:clearable="true"
									/>
								</div>
								<div v-if="isIndianCulture">
									<!-- Traditional DOB fields -->
									<label
										class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
										style="color: var(--theme-text-primary)"
										>Traditional DOB:</label
									>
									<div class="flex space-x-3">
										<select
											v-model="form.traditionalDob.tamilMonth"
											class="input-field block w-1/2 sm:text-sm"
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
											class="input-field block w-1/2 sm:text-sm"
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
								<label for="isPersonAlive" class="form-label cursor-pointer"
									>This person is alive</label
								>
								<div class="toggle-switch-container">
									<input
										type="checkbox"
										id="isPersonAlive"
										v-model="form.isPersonAlive"
										class="toggle-checkbox-custom"
									/>
									<label
										for="isPersonAlive"
										class="toggle-label-custom"
									></label>
								</div>
							</div>

							<div
								v-if="!form.isPersonAlive"
								class="space-y-3 p-4 rounded-md shadow-inner"
								style="background-color: var(--theme-bg-tertiary)"
							>
								<!-- DOD Fields -->
								<h4
									class="text-md font-semibold"
									style="color: var(--theme-text-primary)"
								>
									Date of Death Details:
								</h4>
								<div class="flex items-center justify-between">
									<label
										for="isDodKnownToggle"
										class="form-label cursor-pointer"
										>Is Date of Death Known?</label
									>
									<div class="toggle-switch-container">
										<input
											type="checkbox"
											id="isDodKnownToggle"
											v-model="form.isDodKnown"
											class="toggle-checkbox-custom"
										/>
										<label
											for="isDodKnownToggle"
											class="toggle-label-custom"
										></label>
									</div>
								</div>
								<div v-if="form.isDodKnown" class="space-y-3">
									<!-- Gregorian and Traditional DOD -->
									<div>
										<label
											class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
											style="color: var(--theme-text-primary)"
											>Gregorian DoD:</label
										>
										<date-picker
											:value="form.gregorianDodString"
											@update:value="
												(value) => handleDateUpdate('gregorianDodString', value)
											"
											type="date"
											format="YYYY-MM-DD"
											value-type="format"
											placeholder="YYYY-MM-DD"
											:editable="true"
											:disabled-date="disableFutureDates"
											input-class="input-field mt-1 block w-full sm:text-sm"
											popup-class="datepicker-popup-theme"
											class="w-full"
											:clearable="true"
										/>
									</div>
									<div v-if="isIndianCulture">
										<!-- Traditional DOD fields -->
										<label
											class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
											style="color: var(--theme-text-primary)"
											>Traditional DoD:</label
										>
										<div class="grid grid-cols-3 gap-3">
											<select
												v-model="form.traditionalDod.tamilMonth"
												class="input-field block w-full sm:text-sm"
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
												class="input-field block w-full sm:text-sm"
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
												class="input-field block w-full sm:text-sm"
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
								<label class="form-label">Additional Information:</label>
								<div
									v-for="(field, index) in form.dynamicFields"
									:key="index"
									class="flex items-center space-x-2"
								>
									<input
										type="text"
										v-model="field.key"
										placeholder="Field Name"
										class="input-field mt-1 block w-2/5 sm:text-sm"
									/>
									<input
										type="text"
										v-model="field.value"
										placeholder="Value"
										class="input-field mt-1 block w-2/5 sm:text-sm"
									/>
									<button
										type="button"
										@click="removeDynamicField(index)"
										title="Remove field"
										class="button-icon-danger p-1.5 rounded-full transition-colors"
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
									class="button-success mt-2 px-3 py-1.5 text-sm font-medium rounded-md transition-colors flex items-center"
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
						class="flex justify-end space-x-4 mt-auto pt-4 border-t border-gray-300/70 dark:border-gray-600/70"
					>
						<button class="button-secondary" type="button" @click="closeModal">
							X Cancel
						</button>
						<button class="button-primary" type="submit">💾 Save Member</button>
					</div>
				</form>
			</div>
		</div>
	</Transition>
</template>

<script>
import { reactive, watch, computed, inject, ref } from "vue";
import DatePicker from "vue-datepicker-next";
import "vue-datepicker-next/index.css";
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
	components: {
		DatePicker,
	},
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
		sourceNodeIdForRelationship: {
			type: String,
			default: null,
		},
		sourceMemberNameForRelationship: {
			// New prop
			type: String,
			default: null,
		},
		relationshipTypeForNewMember: {
			type: String,
			default: null,
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

		const handleDateUpdate = (field, newValue) => {
			form[field] = newValue;
		};

		const profileImagePreview = ref(null);
		const imageInputRef = ref(null);

		// Function to disable future dates for the date picker
		const disableFutureDates = (date) => {
			return date > new Date(new Date().setHours(23, 59, 59, 999)); // Allow today
		};

		const genderOptions = computed(() => {
			return Object.keys(ProtoGender).map((key) => {
				const text = key.replace("GENDER_", "").replace("_", "").toUpperCase();
				return {
					value: key,
					text: text === "UNKNOWN" ? "GENDER UNKNOWN" : text,
				};
			});
		});

		const relationshipTypeMap = {
			SPOUSE: "SPOUSE",
			PARENT: "CHILD_TO_PARENT",
			CHILD: "PARENT_TO_CHILD",
		};

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

		const formattedRelationshipType = computed(() => {
			if (!props.relationshipTypeForNewMember) return "";
			const type = props.relationshipTypeForNewMember.toLowerCase();
			return type.charAt(0).toUpperCase() + type.slice(1);
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
			},
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
			},
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
			},
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
					.filter((name) => name),
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
							ProtoTamilMonth[form.traditionalDob.tamilMonth],
						);
					}
					if (form.traditionalDob.tamilStar !== "TAMIL_STAR_UNKNOWN") {
						traditionalDobMessage.setStar(
							ProtoTamilStar[form.traditionalDob.tamilStar],
						);
					}
					if (
						traditionalDobMessage.getMonth() !==
							ProtoTamilMonth.TAMIL_MONTH_UNKNOWN ||
						traditionalDobMessage.getStar() !==
							ProtoTamilStar.TAMIL_STAR_UNKNOWN
					) {
						familyMemberMessage.setTraditionalDateOfBirth(
							traditionalDobMessage,
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
							ProtoTamilMonth[form.traditionalDod.tamilMonth],
						);
					}
					if (form.traditionalDod.paksham !== "PAKSHAM_UNKNOWN") {
						traditionalDodMessage.setPaksham(
							ProtoPaksham[form.traditionalDod.paksham],
						);
					}
					if (form.traditionalDod.thithi !== "THITHI_UNKNOWN") {
						traditionalDodMessage.setThithi(
							ProtoThithi[form.traditionalDod.thithi],
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
							traditionalDodMessage,
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

			const additionalInfoProtoMap = familyMemberMessage.getAdditionalInfoMap();
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
					"additionalInfoMap",
				)
			) {
				delete memberProtoJson.additionalInfoMap; // Clean up if toObject() created this
			}

			const request_data = {
				infer_relationships: props.inferRelationshipsEnabled,
				new_member_data: memberProtoJson,
			};

			if (
				props.sourceNodeIdForRelationship &&
				props.relationshipTypeForNewMember
			) {
				request_data.source_node_id = props.sourceNodeIdForRelationship;
				request_data.relationship_type =
					relationshipTypeMap[props.relationshipTypeForNewMember];
			}

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
									errBody.detail || `Server error: ${response.status}`,
								);
							})
							.catch(() => {
								throw new Error(
									`Server error: ${response.status} ${response.statusText}`,
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
						4000,
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
			disableFutureDates,
			closeModal,
			saveMember,
			updateStatus,
			profileImagePreview,
			imageInputRef,
			handleImageUpload,
			triggerImageUpload,
			handleDateUpdate,
			removeImage,
			addDynamicField,
			removeDynamicField,
			formattedRelationshipType,
		};
	},
};
</script>

<style scoped>
/* Form labels */
.form-label {
	@apply block text-sm font-medium;
	color: var(--theme-text-on-primary-bg);
}

/* Input fields, select */
.input-field {
	@apply rounded-md shadow-sm sm:text-sm p-2;
	background-color: var(--theme-input-bg);
	color: var(--theme-input-text);
	border: 1px solid var(--theme-input-border);
}
.input-field::placeholder {
	color: var(--theme-input-placeholder);
}
.input-field:focus {
	@apply outline-none ring-2 ring-opacity-50;
	border-color: var(--theme-accent);
	ring-color: var(--theme-accent);
}

/* Datepicker popup custom class */
:global(.datepicker-popup-theme) {
	background-color: var(--theme-bg-secondary) !important;
	border: 1px solid var(--theme-border-color) !important;
	color: var(--theme-text-primary) !important;
}
:global(.datepicker-popup-theme .mx-calendar-header-label),
:global(.datepicker-popup-theme .mx-calendar-weekday),
:global(.datepicker-popup-theme .mx-calendar-date),
:global(.datepicker-popup-theme .mx-time-column .mx-time-item),
:global(.datepicker-popup-theme .mx-btn) {
	color: var(--theme-text-primary) !important;
}
:global(.datepicker-popup-theme .mx-calendar-date.today) {
	color: var(--theme-accent) !important;
}
:global(.datepicker-popup-theme .mx-calendar-date:hover),
:global(.datepicker-popup-theme .mx-time-column .mx-time-item:hover) {
	background-color: rgba(var(--theme-accent-rgb), 0.2) !important;
}
:global(.datepicker-popup-theme .mx-calendar-date.active) {
	background-color: var(--theme-accent) !important;
	color: var(--theme-text-on-accent) !important;
}
:global(.datepicker-popup-theme .mx-btn-text:hover) {
	color: var(--theme-accent-hover) !important;
}

/* Toggle Switch */
.toggle-switch-container {
	@apply relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in;
}
.toggle-checkbox-custom {
	@apply absolute block w-5 h-5 rounded-full appearance-none cursor-pointer transition-transform duration-200 ease-in-out;
	background-color: var(--theme-toggle-thumb-bg);
	border: 2px solid var(--theme-toggle-border);
	top: 2px;
	left: 2px;
}
.toggle-checkbox-custom:checked {
	@apply translate-x-full;
	border-color: var(--theme-accent);
}
.toggle-label-custom {
	@apply block overflow-hidden h-6 w-11 rounded-full cursor-pointer transition-colors duration-200 ease-in-out;
	background-color: var(--theme-toggle-bg);
}
.toggle-checkbox-custom:checked + .toggle-label-custom {
	background-color: var(--theme-accent);
}

/* Buttons */
.button-primary {
	@apply px-4 py-2 font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition duration-150 ease-in-out;
	background-color: var(--theme-accent);
	color: var(--theme-text-on-accent);
	ring-offset-color: var(--theme-bg-primary); /* For focus ring */
}
.button-primary:hover {
	background-color: var(--theme-accent-hover);
}
.button-primary:focus {
	ring-color: var(--theme-accent);
}

.button-secondary {
	@apply px-4 py-2 font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-opacity-75 transition duration-150 ease-in-out;
	background-color: var(--theme-bg-secondary);
	color: var(--theme-text-primary);
}
.button-secondary:hover {
	filter: brightness(0.95); /* Or define a specific hover background */
}
.button-secondary:focus {
	ring-color: var(--theme-accent);
}

/* Ensure enough height for scrollable content if form grows very long */
/* The parent .fixed inset-0 already has overflow-y-auto */
</style>

<style>
/* Global or non-scoped for Tailwind overrides if needed, or for datepicker if :deep doesn't work well */
.button-danger {
	background-color: var(--theme-button-danger-bg);
	color: var(--theme-button-danger-text);
}
.button-danger:hover {
	background-color: var(--theme-button-danger-hover-bg);
}
.button-success {
	background-color: var(--theme-button-success-bg);
	color: var(--theme-button-success-text);
}
.button-success:hover {
	background-color: var(--theme-button-success-hover-bg);
}
.button-icon-danger {
	color: var(--theme-icon-danger-color);
}
.button-icon-danger:hover {
	color: var(--theme-icon-danger-hover-color);
	background-color: rgba(var(--theme-accent-rgb), 0.1); /* Subtle hover bg */
}
.icon-close {
	color: var(--theme-icon-color);
}
.icon-close:hover {
	color: var(--theme-icon-hover-color);
}
.image-upload-area {
	background-color: var(--theme-bg-secondary);
	border-color: var(--theme-border-color);
}
.image-upload-area:hover {
	border-color: var(--theme-accent);
}
.image-placeholder-icon {
	color: var(--theme-text-secondary);
}
.contextual-info-box {
	background-color: rgba(var(--theme-accent-rgb), 0.15);
	border: 1px solid rgba(var(--theme-accent-rgb), 0.3);
}
</style>
