<template>
	<Transition
		enter-active-class="transition-all ease-out duration-300"
		:enter-from-class="enterFromClass"
		enter-to-class="opacity-100 scale-100"
		leave-active-class="transition-all ease-in duration-200"
		leave-from-class="opacity-100 scale-100"
		:leave-to-class="leaveToClass"
	>
		<div
			v-if="isVisible && member"
			class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex justify-center items-center"
			@click.self="closeModal"
			:style="transformOriginStyle"
		>
			<div
				class="relative bg-violet-600/90 dark:bg-violet-400/90 backdrop-blur-lg rounded-2xl shadow-2xl p-6 max-w-xl w-full mx-4 flex flex-col h-[55vh]"
				@click.stop
			>
				<div
					class="flex justify-between items-center border-b border-gray-300/70 dark:border-gray-600/70 pb-3 mb-4"
				>
					<h3 class="text-lg font-semibold text-white dark:text-black">
						Member Details
					</h3>
					<button
						@click="closeModal"
						class="text-violet-100 dark:text-violet-800 hover:text-white dark:hover:text-black transition-colors"
						aria-label="Close modal"
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

				<div class="flex-1 flex flex-col md:flex-row md:space-x-6 min-h-0">
					<!-- Left Pane: Image and Basic Info -->
					<div
						class="w-full md:w-1/3 flex flex-col items-center py-4 space-y-3"
						v-if="editableMember.id"
					>
						<div class="relative group">
							<input
								type="file"
								ref="profileImageInputRef"
								@change="handleProfileImageChange"
								class="hidden"
								accept="image/*"
							/>
							<div
								@click="triggerProfileImageUpload"
								class="w-36 h-36 md:w-40 md:h-40 bg-gray-200 dark:bg-slate-700 rounded-md flex items-center justify-center overflow-hidden border border-gray-300 dark:border-gray-600 cursor-pointer"
								title="Click to change profile image"
							>
								<img
									v-if="profilePicture"
									:src="profilePicture"
									alt="Profile"
									class="w-full h-full object-cover"
								/>
								<svg
									v-else
									class="w-20 h-20 text-gray-400 dark:text-gray-500"
									fill="currentColor"
									viewBox="0 0 20 20"
								>
									<path
										fill-rule="evenodd"
										d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
							<button
								@click="triggerProfileImageUpload"
								class="absolute bottom-2 right-2 p-1.5 bg-black/50 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
								title="Edit profile picture"
							>
								<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
									<path
										d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
									/>
								</svg>
							</button>
						</div>
						<h4
							class="w-full text-xl font-bold text-white dark:text-black text-center"
						>
							{{ editableMember.name || "Unnamed" }}
						</h4>
						<!-- Editable Nicknames -->
						<div class="w-full mt-1 min-h-[3rem]">
							<EditableField
								:value="
									editableMember.nicknames
										? editableMember.nicknames.join(', ')
										: ''
								"
								fieldName="nicknames"
								:isEditing="isEditing.nicknames"
								@toggleEdit="toggleEdit"
								@save="saveField"
								@cancel="cancelEdit"
								editTrigger="button"
								:showEditButtonOnHover="true"
								valueClass="text-sm italic text-white dark:text-black text-center"
								inputContainerClass="flex flex-col items-center"
								emptyDisplayValue="''"
								displayArrangement="stacked"
								displayAlignment="center"
							>
								<template #default="{ internalValue, updateInternalValue }">
									<input
										type="text"
										:value="internalValue"
										@input="updateInternalValue($event.target.value)"
										class="form-input w-full text-sm text-center"
										placeholder="e.g., Johnny, Beth (comma-separated)"
									/>
								</template>
							</EditableField>
						</div>
					</div>

					<!-- Right Pane: Detailed Info & Editing -->
					<div
						class="w-full md:w-2/3 flex-1 space-y-3 overflow-y-auto md:h-full min-h-0 py-4 pr-2"
						v-if="editableMember.id"
					>
						<!-- Gender -->
						<div
							class="detail-field-editable flex items-center justify-between"
						>
							<span class="font-medium text-white dark:text-black"
								>Gender:</span
							>
							<div class="ml-2 flex-grow">
								<EditableField
									:value="displayGender"
									fieldName="gender"
									:isEditing="isEditing.gender"
									@toggleEdit="toggleEdit"
									@save="saveField"
									@cancel="cancelEdit"
								>
									<template #default="{ internalValue, updateInternalValue }">
										<select
											:value="internalValue"
											@change="updateInternalValue($event.target.value)"
											class="form-input"
										>
											<option
												v-for="option in genderOptions"
												:key="option.value"
												:value="option.value"
											>
												{{ option.text }}
											</option>
										</select>
									</template>
								</EditableField>
							</div>
						</div>

						<!-- Alive Status -->
						<div
							class="detail-field-editable flex items-center justify-between"
						>
							<span class="font-medium text-white dark:text-black">Alive:</span>
							<div class="ml-2 flex-grow">
								<EditableField
									:value="editableMember.alive"
									fieldName="alive"
									:isEditing="isEditing.alive"
									@toggleEdit="toggleEdit"
									@save="saveField"
									@cancel="cancelEdit"
								>
									<template #default="{ internalValue, updateInternalValue }">
										<div class="flex items-center mt-1">
											<input
												id="aliveToggleDetails"
												type="checkbox"
												:checked="internalValue"
												@change="updateInternalValue($event.target.checked)"
												class="sr-only peer"
											/>
											<label
												for="aliveToggleDetails"
												class="relative w-9 h-5 bg-gray-300/70 dark:bg-slate-600/70 rounded-full peer peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-500 dark:peer-focus:ring-indigo-400 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 dark:after:border-gray-500 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-500 dark:peer-checked:bg-indigo-400"
											></label>
											<label
												for="aliveToggleDetails"
												class="ml-2 text-sm text-white dark:text-black cursor-pointer"
												>{{ internalValue ? "Alive" : "Not Alive" }}</label
											>
										</div>
									</template>
								</EditableField>
							</div>
						</div>

						<!-- Born On -->
						<div
							class="detail-field-editable flex items-center justify-between"
						>
							<span class="font-medium text-white dark:text-black"
								>Born on:</span
							>
							<div class="ml-2 flex-grow">
								<EditableField
									:value="`${
										editableMember.date_of_birth
											? formatDate(editableMember.date_of_birth)
											: 'N/A'
									}${
										editableMember.traditional_date_of_birth &&
										(editableMember.traditional_date_of_birth.month ||
											editableMember.traditional_date_of_birth.star)
											? ' (' +
											  formatTraditionalDate(
													editableMember.traditional_date_of_birth,
													'dob',
											  ) +
											  ')'
											: ''
									}`"
									fieldName="dob"
									:isEditing="isEditing.dob"
									@toggleEdit="toggleEdit"
									@save="saveField"
									@cancel="cancelEdit"
								>
									<template #default>
										<div
											class="space-y-3 p-2 bg-violet-500/20 dark:bg-violet-800/20 rounded-md"
										>
											<div class="flex items-center justify-between">
												<label
													for="isDobKnownToggleField"
													class="block text-sm text-white dark:text-black cursor-pointer"
													>Is Date of Birth Known?</label
												>
												<div
													class="relative inline-block w-10 mr-2 align-middle select-none"
												>
													<input
														type="checkbox"
														id="isDobKnownToggleField"
														:checked="isDobKnown_DobField"
														@change="onIsKnownChange('dobField', $event)"
														class="toggle-checkbox"
													/>
													<label
														for="isDobKnownToggleField"
														class="toggle-label"
													></label>
												</div>
											</div>
											<div v-if="isDobKnown_DobField" class="space-y-2">
												<div>
													<label
														class="block text-xs font-medium text-white dark:text-black mb-0.5"
														>Gregorian DOB:</label
													>
													<date-picker
														:value="gregorianDob_DobField"
														@update:value="
															handleDateUpdate(
																'dobField',
																'gregorianDob_DobField',
																$event,
															)
														"
														type="date"
														format="YYYY-MM-DD"
														value-type="format"
														placeholder="YYYY-MM-DD"
														:editable="true"
														:disabled-date="disableFutureDates"
														input-class="form-input text-sm"
														popup-class="dark:bg-slate-700"
														class="w-full"
														:clearable="true"
													/>
												</div>
												<div v-if="isIndianCulture">
													<label
														class="block text-xs font-medium text-white dark:text-black mb-0.5"
														>Traditional DOB:</label
													>
													<div class="grid grid-cols-2 gap-2">
														<select
															v-model="traditionalDob_DobField.tamilMonth"
															@change="handleTraditionalDateChange('dobField')"
															class="form-input text-sm"
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
															v-model="traditionalDob_DobField.tamilStar"
															@change="handleTraditionalDateChange('dobField')"
															class="form-input text-sm"
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
										</div>
									</template>
								</EditableField>
							</div>
						</div>

						<!-- Died On -->
						<!-- EditableField for DoD, shown if initially not alive -->
						<div
							v-if="
								editableMember.id &&
								!editableMember.alive &&
								!wasAliveWhenModalOpened
							"
							class="detail-field-editable flex items-center justify-between"
						>
							<span class="font-medium text-white dark:text-black"
								>Died on:</span
							>
							<div class="ml-2 flex-grow">
								<EditableField
									:value="`${
										editableMember.date_of_death
											? formatDate(editableMember.date_of_death)
											: 'N/A'
									}${
										editableMember.traditional_date_of_death &&
										(editableMember.traditional_date_of_death.month ||
											editableMember.traditional_date_of_death.paksham ||
											editableMember.traditional_date_of_death.thithi)
											? ' (' +
											  formatTraditionalDate(
													editableMember.traditional_date_of_death,
													'dod',
											  ) +
											  ')'
											: ''
									}`"
									fieldName="dod"
									:isEditing="isEditing.dod"
									@toggleEdit="toggleEdit"
									@save="saveField"
									@cancel="cancelEdit"
								>
									<template #default>
										<div
											class="space-y-3 p-2 bg-violet-500/20 dark:bg-violet-800/20 rounded-md"
										>
											<div class="flex items-center justify-between">
												<label
													for="isDodKnownToggleFieldEditable"
													class="block text-sm text-white dark:text-black cursor-pointer"
													>Is Date of Death Known?</label
												>
												<div
													class="relative inline-block w-10 mr-2 align-middle select-none"
												>
													<input
														type="checkbox"
														id="isDodKnownToggleFieldEditable"
														:checked="isDodKnown_DodFieldEditable"
														@change="
															onIsKnownChange('dodFieldEditable', $event)
														"
														class="toggle-checkbox"
													/>
													<label
														for="isDodKnownToggleFieldEditable"
														class="toggle-label"
													></label>
												</div>
											</div>
											<div v-if="isDodKnown_DodFieldEditable" class="space-y-2">
												<div>
													<label
														class="block text-xs font-medium text-white dark:text-black mb-0.5"
														>Gregorian DoD:</label
													>
													<date-picker
														:value="gregorianDod_DodFieldEditable"
														@update:value="
															handleDateUpdate(
																'dodFieldEditable',
																'gregorianDod_DodFieldEditable',
																$event,
															)
														"
														type="date"
														format="YYYY-MM-DD"
														value-type="format"
														placeholder="YYYY-MM-DD"
														:editable="true"
														:disabled-date="disableFutureDates"
														input-class="form-input text-sm"
														popup-class="dark:bg-slate-700"
														class="w-full"
														:clearable="true"
													/>
												</div>
												<div v-if="isIndianCulture">
													<label
														class="block text-xs font-medium text-white dark:text-black mb-0.5"
														>Traditional DoD:</label
													>
													<div class="grid grid-cols-3 gap-2">
														<select
															v-model="
																traditionalDod_DodFieldEditable.tamilMonth
															"
															@change="
																handleTraditionalDateChange('dodFieldEditable')
															"
															class="form-input text-sm"
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
															v-model="traditionalDod_DodFieldEditable.paksham"
															@change="
																handleTraditionalDateChange('dodFieldEditable')
															"
															class="form-input text-sm"
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
															v-model="traditionalDod_DodFieldEditable.thithi"
															@change="
																handleTraditionalDateChange('dodFieldEditable')
															"
															class="form-input text-sm"
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
									</template>
								</EditableField>
							</div>
						</div>

						<!-- Dedicated DoD Section: Shown if "Alive" is changed from True to False during this edit session -->
						<div
							v-if="
								editableMember.id &&
								!editableMember.alive &&
								wasAliveWhenModalOpened
							"
							class="mt-3 pt-3 border-t border-gray-300/50 dark:border-gray-600/50 space-y-3"
						>
							<h5 class="text-md font-semibold text-white dark:text-black">
								Date of Death Details:
							</h5>
							<div class="flex items-center justify-between">
								<label
									for="isDodKnownToggleDetails"
									class="block text-sm text-white dark:text-black cursor-pointer"
									>Is Date of Death Known?</label
								>
								<div
									class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
								>
									<input
										type="checkbox"
										id="isDodKnownToggleDetails"
										:checked="isDodKnown_Dedicated"
										@change="onIsKnownChange('dodDedicated', $event)"
										class="toggle-checkbox"
									/>
									<label
										for="isDodKnownToggleDetails"
										class="toggle-label"
									></label>
								</div>
							</div>

							<div v-if="isDodKnown_Dedicated" class="space-y-3">
								<div>
									<label
										class="block text-sm font-medium text-white dark:text-black mb-1"
										>Gregorian DoD:</label
									>
									<date-picker
										:value="gregorianDod_Dedicated"
										@update:value="
											handleDateUpdate(
												'dodDedicated',
												'gregorianDod_Dedicated',
												$event,
											)
										"
										type="date"
										format="YYYY-MM-DD"
										value-type="format"
										placeholder="YYYY-MM-DD"
										:editable="true"
										:disabled-date="disableFutureDates"
										input-class="form-input"
										popup-class="dark:bg-slate-700"
										class="w-full"
										:clearable="true"
									/>
								</div>
								<div v-if="isIndianCulture">
									<label
										class="block text-sm font-medium text-white dark:text-black mb-1"
										>Traditional DoD:</label
									>
									<div class="grid grid-cols-3 gap-2">
										<select
											v-model="traditionalDod_Dedicated.tamilMonth"
											@change="handleTraditionalDateChange('dodDedicated')"
											class="form-input text-sm"
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
											v-model="traditionalDod_Dedicated.paksham"
											@change="handleTraditionalDateChange('dodDedicated')"
											class="form-input text-sm"
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
											v-model="traditionalDod_Dedicated.thithi"
											@change="handleTraditionalDateChange('dodDedicated')"
											class="form-input text-sm"
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
						<div
							class="mt-4 pt-3 border-t border-gray-300/50 dark:border-gray-600/50"
						>
							<h5 class="text-md font-semibold text-white dark:text-black mb-2">
								Additional Information
							</h5>
							<div class="space-y-2">
								<!-- Loop for existing fields -->
								<div
									v-for="(value, key) in otherAdditionalFields"
									:key="key"
									class="flex items-start justify-between group bg-violet-500/10 dark:bg-violet-800/10 p-1.5 rounded-md"
								>
									<div class="flex-grow flex items-center">
										<!-- Display Key when NOT editing -->
										<span
											v-if="!isEditing[`additional_info.${key}`]"
											class="font-medium text-white dark:text-black mr-1"
											>{{ formatFieldLabel(key) }}:</span
										>

										<EditableField
											:value="value"
											:fieldName="`additional_info.${key}`"
											:isEditing="isEditing[`additional_info.${key}`]"
											@toggleEdit="toggleEdit"
											@save="saveField"
											@cancel="cancelEdit"
											:valueClass="`text-sm font-semibold text-white dark:text-black`"
											:inputContainerClass="'flex flex-col items-start w-full'"
											:displayArrangement="
												isEditing[`additional_info.${key}`]
													? 'stacked' // When editing, label is above input (slot content)
													: 'inline' // When NOT editing, value and edit button are inline
											"
											displayAlignment="start"
											:editTrigger="'button'"
											:showEditButtonOnHover="
												!isEditing[`additional_info.${key}`]
											"
										>
											<template
												#default="{ internalValue, updateInternalValue }"
											>
												<div class="w-full">
													<span
														class="block text-xs font-medium text-white dark:text-black mb-0.5"
														>{{ formatFieldLabel(key) }}:</span
													>
													<input
														type="text"
														:value="internalValue"
														@input="updateInternalValue($event.target.value)"
														class="form-input text-sm w-full"
													/>
												</div>
											</template>
										</EditableField>
									</div>
									<!-- Delete button for existing field -->
									<button
										v-if="!isEditing[`additional_info.${key}`]"
										@click="confirmDeleteAdditionalField(key)"
										class="ml-2 p-1 text-red-400 hover:text-red-300 dark:text-red-500 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
										title="Delete field"
									>
										<svg
											class="w-4 h-4"
											fill="currentColor"
											viewBox="0 0 20 20"
										>
											<path
												fill-rule="evenodd"
												d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
												clip-rule="evenodd"
											/>
										</svg>
									</button>
								</div>

								<!-- UI for adding a new field -->
								<div
									v-if="isAddingNewAdditionalField"
									class="p-3 bg-slate-500/30 dark:bg-slate-800/30 rounded-lg space-y-2 shadow"
								>
									<input
										type="text"
										v-model="newAdditionalField.key"
										placeholder="New Field Name (e.g., Occupation)"
										class="form-input text-sm w-full"
									/>
									<input
										type="text"
										v-model="newAdditionalField.value"
										placeholder="Value (e.g., Engineer)"
										class="form-input text-sm w-full"
									/>
									<div class="flex justify-end space-x-2 pt-1">
										<button
											@click="cancelAddNewAdditionalField"
											class="px-3 py-1 text-xs rounded-md bg-gray-300/70 dark:bg-gray-600/70 text-gray-800 dark:text-gray-200 hover:bg-gray-400/80 dark:hover:bg-gray-500/80"
										>
											Cancel
										</button>
										<button
											@click="saveNewAdditionalField"
											class="px-3 py-1 text-xs rounded-md bg-green-600 dark:bg-green-500 text-white hover:bg-green-700 dark:hover:bg-green-400"
										>
											Save Field
										</button>
									</div>
								</div>

								<!-- "Add New Field" button -->
								<button
									v-if="!isAddingNewAdditionalField"
									@click="startAddNewAdditionalField"
									class="mt-2 text-sm font-bold text-green-300 hover:text-green-400 dark:text-green-800 dark:hover:text-green-900 flex items-center py-1 px-2 rounded-md hover:bg-indigo-500/20 dark:hover:bg-indigo-700/20 transition-colors"
								>
									<svg
										class="w-4 h-4 mr-1.5"
										fill="currentColor"
										viewBox="0 0 20 20"
									>
										<path
											fill-rule="evenodd"
											d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
											clip-rule="evenodd"
										/>
									</svg>
									Add New Field
								</button>
								<div
									v-if="
										Object.keys(otherAdditionalFields).length === 0 &&
										!isAddingNewAdditionalField
									"
									class="text-xs text-white dark:text-black italic pt-1"
								>
									No custom fields yet. Click "Add New Field" to add one.
								</div>
							</div>
						</div>
					</div>
				</div>

				<div
					class="flex justify-end space-x-4 mt-auto pt-4 border-t border-gray-300/70 dark:border-gray-600/70"
				>
					<button
						v-if="hasChanges"
						type="button"
						@click="handleUpdateMember"
						class="px-4 py-2 bg-green-600 dark:bg-green-500 text-white font-medium rounded-lg hover:bg-green-700 dark:hover:bg-green-400 focus:outline-none focus:ring-2 focus:ring-green-500 dark:focus:ring-green-400 focus:ring-offset-2 focus:ring-offset-white/50 dark:focus:ring-offset-slate-800/50 transition duration-150 ease-in-out"
					>
						💾 Update Member
					</button>
					<button
						type="button"
						@click="closeModal"
						class="px-4 py-2 bg-gray-300/70 dark:bg-gray-600/70 text-gray-800 dark:text-gray-200 font-medium rounded-lg hover:bg-gray-400/80 dark:hover:bg-gray-500/80 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500 focus:ring-opacity-75 transition duration-150 ease-in-out"
					>
						Close
					</button>
				</div>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import {
	ref,
	computed,
	watch,
	defineProps,
	defineEmits,
	reactive,
	inject,
} from "vue";
import DatePicker from "vue-datepicker-next";
import "vue-datepicker-next/index.css";
import EditableField from "./EditableField.vue";
import {
	Gender as ProtoGender,
	TamilMonth as ProtoTamilMonth,
	TamilStar as ProtoTamilStar,
	Paksham as ProtoPaksham,
	Thithi as ProtoThithi,
} from "../proto/utils_pb";

const props = defineProps({
	isVisible: Boolean,
	member: Object,
	clickPosition: {
		// For animation: { x, y }
		type: Object,
		default: () => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 }),
	},
});

const emit = defineEmits(["close", "update-member"]);

const editableMember = ref({});
const isEditing = reactive({}); // Tracks which field is being edited, e.g., { name: true, gender: false }
const editValues = reactive({}); // Stores temporary values for fields being edited
const initialMemberState = ref(null); // To store the state when modal opens
const profileImageInputRef = ref(null);
const updateStatus = inject("updateStatus");
const isIndianCultureCallback = inject("isIndianCulture", () => () => true); // Default to true if not provided
const isIndianCulture = computed(() => isIndianCultureCallback());

const isAddingNewAdditionalField = ref(false);
const newAdditionalField = reactive({ key: "", value: "" });

const wasAliveWhenModalOpened = ref(true);

const hasChanges = computed(() => {
	if (!initialMemberState.value || !editableMember.value) {
		return false;
	}

	// Create deep copies for normalization to avoid mutating reactive state
	const initialCopy = JSON.parse(JSON.stringify(initialMemberState.value));
	const currentCopy = JSON.parse(JSON.stringify(editableMember.value));

	// Normalize additional_info: treat null, undefined, or empty object as null for comparison
	if (
		!initialCopy.additional_info ||
		Object.keys(initialCopy.additional_info).length === 0
	) {
		initialCopy.additional_info = null;
	}
	if (
		!currentCopy.additional_info ||
		Object.keys(currentCopy.additional_info).length === 0
	) {
		currentCopy.additional_info = null;
	}

	// If additional_info is an object, sort its keys for consistent stringification
	if (
		initialCopy.additional_info &&
		typeof initialCopy.additional_info === "object"
	) {
		const sortedInitialAI = {};
		Object.keys(initialCopy.additional_info)
			.sort()
			.forEach((key) => {
				sortedInitialAI[key] = initialCopy.additional_info[key];
			});
		initialCopy.additional_info = sortedInitialAI;
	}
	if (
		currentCopy.additional_info &&
		typeof currentCopy.additional_info === "object"
	) {
		const sortedCurrentAI = {};
		Object.keys(currentCopy.additional_info)
			.sort()
			.forEach((key) => {
				sortedCurrentAI[key] = currentCopy.additional_info[key];
			});
		currentCopy.additional_info = sortedCurrentAI;
	}

	return JSON.stringify(currentCopy) !== JSON.stringify(initialCopy);
});

// --- State for DoB EditableField ---
const isDobKnown_DobField = ref(false);
const gregorianDob_DobField = ref("");
const traditionalDob_DobField = reactive({
	tamilMonth: "TAMIL_MONTH_UNKNOWN",
	tamilStar: "TAMIL_STAR_UNKNOWN",
});

// --- State for DoD EditableField (when initially not alive) ---
const isDodKnown_DodFieldEditable = ref(false);
const gregorianDod_DodFieldEditable = ref("");
const traditionalDod_DodFieldEditable = reactive({
	tamilMonth: "TAMIL_MONTH_UNKNOWN",
	paksham: "PAKSHAM_UNKNOWN",
	thithi: "THITHI_UNKNOWN",
});
// --- State for Dedicated DoD Section (when "Alive" changes T -> F) ---
const isDodKnown_Dedicated = ref(false);
const gregorianDod_Dedicated = ref("");
const traditionalDod_Dedicated = reactive({
	tamilMonth: "TAMIL_MONTH_UNKNOWN",
	paksham: "PAKSHAM_UNKNOWN",
	thithi: "THITHI_UNKNOWN",
});

const genderOptions = computed(() => {
	return Object.keys(ProtoGender).map((key) => {
		const text = key.replace("GENDER_", "").replace("_", " ").toUpperCase();
		return {
			value: ProtoGender[key],
			text: text === "UNKNOWN" ? "GENDER UNKNOWN" : text,
		};
	});
});

const tamilMonthMap = Object.fromEntries(
	Object.entries(ProtoTamilMonth).map(([key, value]) => [
		value,
		key
			.replace("TAMIL_MONTH_", "")
			.replace("_UNKNOWN", "Unknown")
			.replace("_", " "),
	]),
);
const tamilStarMap = Object.fromEntries(
	Object.entries(ProtoTamilStar).map(([key, value]) => [
		value,
		key
			.replace("TAMIL_STAR_", "")
			.replace("_UNKNOWN", "Unknown")
			.replace("_", " "),
	]),
);
const pakshamMap = Object.fromEntries(
	Object.entries(ProtoPaksham).map(([key, value]) => [
		value,
		key
			.replace("PAKSHAM_", "")
			.replace("_UNKNOWN", "Unknown")
			.replace("_", " "),
	]),
);
const thithiMap = Object.fromEntries(
	Object.entries(ProtoThithi).map(([key, value]) => [
		value,
		key.replace("THITHI_", "").replace("_UNKNOWN", "Unknown").replace("_", " "),
	]),
);

const TamilStarOptions = computed(() => {
	return Object.keys(ProtoTamilStar).map((key) => ({
		value: key,
		text: key
			.replace("TAMIL_STAR_", "")
			.replace("_UNKNOWN", "Unknown")
			.replace("_", " "),
	}));
});

const TamilMonthOptions = computed(() => {
	return Object.keys(ProtoTamilMonth).map((key) => ({
		value: key,
		text: key
			.replace("TAMIL_MONTH_", "")
			.replace("_UNKNOWN", "Unknown")
			.replace("_", " "),
	}));
});

const PakshamOptions = computed(() => {
	return Object.keys(ProtoPaksham).map((key) => ({
		value: key,
		text: key
			.replace("PAKSHAM_", "")
			.replace("_UNKNOWN", "Unknown")
			.replace("_", " "),
	}));
});

const ThithiOptions = computed(() => {
	return Object.keys(ProtoThithi).map((key) => ({
		value: key,
		text: key
			.replace("THITHI_", "")
			.replace("_UNKNOWN", "Unknown")
			.replace("_", " "),
	}));
});

const disableFutureDates = (date) => {
	return date > new Date(new Date().setHours(23, 59, 59, 999)); // Allow today
};

watch(
	() => props.member,
	(newMember) => {
		if (newMember) {
			// Deep clone for editing to avoid mutating prop directly
			editableMember.value = JSON.parse(JSON.stringify(newMember));
			initialMemberState.value = JSON.parse(JSON.stringify(newMember)); // Store initial state
			// Reset editing states
			for (const key in isEditing) delete isEditing[key];
			for (const key in editValues) delete editValues[key];
			wasAliveWhenModalOpened.value = newMember ? newMember.alive : true;
			initializeDobFieldState();
			if (newMember && !newMember.alive) {
				initializeDodFieldEditableState();
			}
			initializeDodDedicatedSectionState();
		}
	},
	{ immediate: true, deep: true },
);

watch(isDobKnown_DobField, (isKnown) => {
	if (!isKnown) {
		gregorianDob_DobField.value = "";
		traditionalDob_DobField.tamilMonth = "TAMIL_MONTH_UNKNOWN";
		traditionalDob_DobField.tamilStar = "TAMIL_STAR_UNKNOWN";
	}
});
watch(isDodKnown_DodFieldEditable, (isKnown) => {
	if (!isKnown) {
		gregorianDod_DodFieldEditable.value = "";
		traditionalDod_DodFieldEditable.tamilMonth = "TAMIL_MONTH_UNKNOWN";
		traditionalDod_DodFieldEditable.paksham = "PAKSHAM_UNKNOWN";
		traditionalDod_DodFieldEditable.thithi = "THITHI_UNKNOWN";
	}
});
watch(isDodKnown_Dedicated, (isKnown) => {
	if (!isKnown) {
		gregorianDod_Dedicated.value = "";
		traditionalDod_Dedicated.tamilMonth = "TAMIL_MONTH_UNKNOWN";
		traditionalDod_Dedicated.paksham = "PAKSHAM_UNKNOWN";
		traditionalDod_Dedicated.thithi = "THITHI_UNKNOWN";
	}
});

const initializeDobFieldState = () => {
	if (editableMember.value) {
		const currentDob = editableMember.value.date_of_birth;
		const currentTradDob = editableMember.value.traditional_date_of_birth;
		isDobKnown_DobField.value = !!(currentDob && currentDob.year);
		gregorianDob_DobField.value = isDobKnown_DobField.value
			? formatDate(currentDob)
			: "";
		traditionalDob_DobField.tamilMonth =
			currentTradDob?.month || "TAMIL_MONTH_UNKNOWN";
		traditionalDob_DobField.tamilStar =
			currentTradDob?.star || "TAMIL_STAR_UNKNOWN";
	}
};

const initializeDodFieldEditableState = () => {
	if (editableMember.value) {
		const currentDod = editableMember.value.date_of_death;
		const currentTradDod = editableMember.value.traditional_date_of_death;
		isDodKnown_DodFieldEditable.value = !!(currentDod && currentDod.year);
		gregorianDod_DodFieldEditable.value = isDodKnown_DodFieldEditable.value
			? formatDate(currentDod)
			: "";
		traditionalDod_DodFieldEditable.tamilMonth =
			currentTradDod?.month || "TAMIL_MONTH_UNKNOWN";
		traditionalDod_DodFieldEditable.paksham =
			currentTradDod?.paksham || "PAKSHAM_UNKNOWN";
		traditionalDod_DodFieldEditable.thithi =
			currentTradDod?.thithi || "THITHI_UNKNOWN";
	}
};

const initializeDodDedicatedSectionState = () => {
	if (
		editableMember.value &&
		!editableMember.value.alive &&
		wasAliveWhenModalOpened.value
	) {
		const currentDod = editableMember.value.date_of_death;
		const currentTradDod = editableMember.value.traditional_date_of_death;
		isDodKnown_Dedicated.value = !!(currentDod && currentDod.year);
		gregorianDod_Dedicated.value = isDodKnown_Dedicated.value
			? formatDate(currentDod)
			: "";
		traditionalDod_Dedicated.tamilMonth =
			currentTradDod?.month || "TAMIL_MONTH_UNKNOWN";
		traditionalDod_Dedicated.paksham =
			currentTradDod?.paksham || "PAKSHAM_UNKNOWN";
		traditionalDod_Dedicated.thithi =
			currentTradDod?.thithi || "THITHI_UNKNOWN";
	} else {
		isDodKnown_Dedicated.value = false;
		gregorianDod_Dedicated.value = "";
		traditionalDod_Dedicated.tamilMonth = "TAMIL_MONTH_UNKNOWN";
		traditionalDod_Dedicated.paksham = "PAKSHAM_UNKNOWN";
		traditionalDod_Dedicated.thithi = "THITHI_UNKNOWN";
	}
};

const handleDateUpdate = (context, targetField, value) => {
	if (context === "dobField") gregorianDob_DobField.value = value;
	else if (context === "dodFieldEditable")
		gregorianDod_DodFieldEditable.value = value;
	else if (context === "dodDedicated") gregorianDod_Dedicated.value = value;
};

const handleTraditionalDateChange = () => {
	// context will be 'dobField', 'dodFieldEditable', or 'dodDedicated'
};

const onIsKnownChange = (context, event) => {
	const checked = event.target.checked;
	if (context === "dobField") isDobKnown_DobField.value = checked;
	else if (context === "dodFieldEditable")
		isDodKnown_DodFieldEditable.value = checked;
	else if (context === "dodDedicated") isDodKnown_Dedicated.value = checked;
};

const parseDateString = (dateString) => {
	if (!dateString) return null;
	const parts = dateString.split("-");
	if (parts.length === 3) {
		return {
			year: parseInt(parts[0], 10),
			month: parseInt(parts[1], 10),
			date: parseInt(parts[2], 10),
		};
	}
	return null;
};

const profilePicture = computed(() => {
	return editableMember.value?.additional_info?.profilePictureBase64 || null;
});

const otherAdditionalFields = computed(() => {
	if (!editableMember.value?.additional_info) return {};
	// Create a shallow copy to avoid mutating the original additionalInfo
	const fields = { ...editableMember.value.additional_info };
	delete fields.profilePictureBase64; // Remove the picture from the copied object
	return fields;
});

const displayGender = computed(() => {
	// Ensure editableMember.value and its gender property exist and gender is a string
	if (
		!editableMember.value ||
		typeof editableMember.value.gender !== "string"
	) {
		return "N/A";
	}

	const memberGenderStringKey = editableMember.value.gender.toUpperCase();
	let numericGenderValue = ProtoGender[memberGenderStringKey];
	const genderEntry = genderOptions.value.find(
		(opt) => opt.value === numericGenderValue,
	);
	return genderEntry ? genderEntry.text : "N/A";
});

function formatDate(dateObj) {
	if (!dateObj || !dateObj.year || !dateObj.month || !dateObj.date)
		return "N/A";
	// Ensure month and day are two digits
	const month = String(dateObj.month).padStart(2, "0");
	const date = String(dateObj.date).padStart(2, "0");
	return `${dateObj.year}-${month}-${date}`;
}

function formatTraditionalDate(tradDateObj, type) {
	if (!tradDateObj) return "";
	let parts = [];
	if (
		tradDateObj.month &&
		tamilMonthMap[ProtoTamilMonth[tradDateObj.month]] &&
		tamilMonthMap[ProtoTamilMonth[tradDateObj.month]] !== 0
	)
		parts.push(tamilMonthMap[ProtoTamilMonth[tradDateObj.month]]);

	if (
		type === "dob" &&
		tradDateObj.star &&
		tamilStarMap[ProtoTamilStar[tradDateObj.star]] &&
		tamilStarMap[ProtoTamilStar[tradDateObj.star]] !== 0
	)
		parts.push(tamilStarMap[ProtoTamilStar[tradDateObj.star]]);

	if (type === "dod") {
		if (
			tradDateObj.paksham &&
			pakshamMap[ProtoPaksham[tradDateObj.paksham]] &&
			pakshamMap[ProtoPaksham[tradDateObj.paksham]] !== 0
		)
			parts.push(pakshamMap[ProtoPaksham[tradDateObj.paksham]]);
		if (
			tradDateObj.thithi &&
			thithiMap[ProtoThithi[tradDateObj.thithi]] &&
			thithiMap[ProtoThithi[tradDateObj.thithi]] !== 0
		)
			parts.push(thithiMap[ProtoThithi[tradDateObj.thithi]]);
	}
	return parts.join(", ");
}

function formatFieldLabel(key) {
	return key
		.replace(/([A-Z])/g, " $1")
		.replace(/^./, (str) => str.toUpperCase());
}

const closeModal = () => {
	emit("close");
};

const toggleEdit = (fieldName) => {
	if (isEditing[fieldName]) {
		// Was editing, now cancelling that specific field edit
		cancelEdit(fieldName);
	} else {
		// Start editing
		// Set current value for editing
		if (fieldName.startsWith("additional_info.")) {
			const actualKey = fieldName.substring("additional_info.".length);
			editValues[fieldName] =
				editableMember.value.additional_info?.[actualKey] ?? "";
		} else if (fieldName === "nicknames") {
			editValues.nicknames = editableMember.value.nicknames
				? editableMember.value.nicknames.join(", ")
				: "";
		} else if (fieldName === "alive") {
			editValues.alive =
				typeof editableMember.value.alive === "boolean"
					? editableMember.value.alive
					: true;
		} else if (fieldName === "gender") {
			// editableMember.value.gender is a string like "MALE"
			const stringKey = String(editableMember.value.gender).toUpperCase();
			editValues.gender = ProtoGender[stringKey] ?? ProtoGender.GENDER_UNKNOWN;
		} else {
			editValues[fieldName] = editableMember.value[fieldName];
		}
		// Special handling for gender if it's stored as string key but select needs numeric value
		if (
			fieldName === "gender" &&
			typeof editableMember.value.gender === "string"
		) {
			editValues.gender =
				ProtoGender[editableMember.value.gender.toUpperCase()] ??
				ProtoGender["GENDER_" + editableMember.value.gender.toUpperCase()] ??
				ProtoGender.GENDER_UNKNOWN;
		}
		// The previous complex logic for gender string to numeric conversion was removed here.
		// It's now handled directly in toggleEdit for gender.
		isEditing[fieldName] = true;

		if (fieldName === "dob") initializeDobFieldState();
		else if (fieldName === "dod") initializeDodFieldEditableState();
	}
};

const saveField = (fieldName, newValue) => {
	// For simple fields, update editValues. For complex (DoB/DoD), newValue from EditableField slot might be ignored
	// if the slot directly mutates more complex dedicated state.
	if (fieldName !== "dob" && fieldName !== "dod")
		editValues[fieldName] = newValue;

	if (fieldName.startsWith("additional_info.")) {
		const actualKey = fieldName.substring("additional_info.".length);
		editableMember.value.additional_info[actualKey] = newValue;
	} else if (fieldName === "nicknames") {
		editableMember.value.nicknames = editValues.nicknames
			.split(",")
			.map((n) => n.trim())
			.filter((n) => n);
	} else if (fieldName === "gender") {
		// editValues.gender holds the numeric enum value from the select
		// We need to find the string key (e.g., "MALE") for that numeric value
		const numericGender = parseInt(newValue, 10); // Ensure it's a number
		const stringKey = Object.keys(ProtoGender).find(
			(key) => ProtoGender[key] === numericGender,
		);
		editableMember.value.gender = stringKey || "GENDER_UNKNOWN";
	} else if (fieldName === "alive") {
		editableMember.value.alive = newValue;
		if (!newValue && wasAliveWhenModalOpened.value) {
			// Changed T -> F
			initializeDodDedicatedSectionState(); // Prepare dedicated section
		} else if (newValue) {
			// Changed F -> T or remained T
			initializeDodDedicatedSectionState(); // Reset/clear dedicated section state
		}
	} else if (fieldName === "dob") {
		if (isDobKnown_DobField.value) {
			const dob = parseDateString(gregorianDob_DobField.value);
			editableMember.value.date_of_birth = dob
				? { year: dob.year, month: dob.month, date: dob.date }
				: null;
			if (isIndianCulture.value) {
				const tradDob = {
					month:
						traditionalDob_DobField.tamilMonth !== "TAMIL_MONTH_UNKNOWN"
							? traditionalDob_DobField.tamilMonth
							: null,
					star:
						traditionalDob_DobField.tamilStar !== "TAMIL_STAR_UNKNOWN"
							? traditionalDob_DobField.tamilStar
							: null,
				};
				editableMember.value.traditional_date_of_birth =
					tradDob.month || tradDob.star ? tradDob : null;
			} else editableMember.value.traditional_date_of_birth = null;
		} else {
			editableMember.value.date_of_birth = null;
			editableMember.value.traditional_date_of_birth = null;
		}
	} else if (fieldName === "dod") {
		// Saving from DoD EditableField
		if (isDodKnown_DodFieldEditable.value) {
			const dod = parseDateString(gregorianDod_DodFieldEditable.value);
			editableMember.value.date_of_death = dod
				? { year: dod.year, month: dod.month, date: dod.date }
				: null;
			if (isIndianCulture.value) {
				const tradDod = {
					month:
						traditionalDod_DodFieldEditable.tamilMonth !== "TAMIL_MONTH_UNKNOWN"
							? traditionalDod_DodFieldEditable.tamilMonth
							: null,
					paksham:
						traditionalDod_DodFieldEditable.paksham !== "PAKSHAM_UNKNOWN"
							? traditionalDod_DodFieldEditable.paksham
							: null,
					thithi:
						traditionalDod_DodFieldEditable.thithi !== "THITHI_UNKNOWN"
							? traditionalDod_DodFieldEditable.thithi
							: null,
				};
				editableMember.value.traditional_date_of_death =
					tradDod.month || tradDod.paksham || tradDod.thithi ? tradDod : null;
			} else editableMember.value.traditional_date_of_death = null;
		} else {
			editableMember.value.date_of_death = null;
			editableMember.value.traditional_date_of_death = null;
		}
	}
	isEditing[fieldName] = false;
};

const cancelEdit = (fieldName) => {
	isEditing[fieldName] = false;
	// Revert editValues[fieldName] to original if needed, or simply rely on re-population on next edit toggle
};

const handleUpdateMember = () => {
	// In a real app, you might want to send only changed fields
	const memberToUpdate = JSON.parse(JSON.stringify(editableMember.value));
	if (!memberToUpdate.alive) {
		if (wasAliveWhenModalOpened.value) {
			// "Alive" was changed T -> F, use _Dedicated state
			if (isDodKnown_Dedicated.value) {
				const dod = parseDateString(gregorianDod_Dedicated.value);
				memberToUpdate.date_of_death = dod
					? { year: dod.year, month: dod.month, date: dod.date }
					: null;
				if (isIndianCulture.value) {
					const tradDod = {
						month:
							traditionalDod_Dedicated.tamilMonth !== "TAMIL_MONTH_UNKNOWN"
								? traditionalDod_Dedicated.tamilMonth
								: null,
						paksham:
							traditionalDod_Dedicated.paksham !== "PAKSHAM_UNKNOWN"
								? traditionalDod_Dedicated.paksham
								: null,
						thithi:
							traditionalDod_Dedicated.thithi !== "THITHI_UNKNOWN"
								? traditionalDod_Dedicated.thithi
								: null,
					};
					memberToUpdate.traditional_date_of_death =
						tradDod.month || tradDod.paksham || tradDod.thithi ? tradDod : null;
				} else memberToUpdate.traditional_date_of_death = null;
			} else {
				// Member was initially not alive. DoD was handled by saveField("dod") and is already in memberToUpdate.
			}
		} else {
			// If member is alive, nullify DoD fields
			memberToUpdate.date_of_death = null;
			memberToUpdate.traditional_date_of_death = null;
		}
	} else {
		// If member is alive, nullify DoD fields
		memberToUpdate.date_of_death = null;
		memberToUpdate.traditional_date_of_death = null;
	}
	emit("update-member", memberToUpdate);
	// After successful update, the current state IS the new initial state.
	initialMemberState.value = JSON.parse(JSON.stringify(editableMember.value));
};

const triggerProfileImageUpload = () => {
	profileImageInputRef.value?.click();
};

const handleProfileImageChange = (event) => {
	const file = event.target.files[0];
	if (file && file.type.startsWith("image/")) {
		const reader = new FileReader();
		reader.onload = (e) => {
			const base64Image = e.target.result;
			if (!editableMember.value.additional_info) {
				editableMember.value.additional_info = {};
			}
			editableMember.value.additional_info.profilePictureBase64 = base64Image;
		};
		reader.readAsDataURL(file);
	}
};

const confirmDeleteAdditionalField = async (key) => {
	deleteAdditionalField(key);
};

const deleteAdditionalField = (key) => {
	if (editableMember.value.additional_info) {
		delete editableMember.value.additional_info[key];
	}
};

const startAddNewAdditionalField = () => {
	newAdditionalField.key = "";
	newAdditionalField.value = "";
	isAddingNewAdditionalField.value = true;
};

const cancelAddNewAdditionalField = () => {
	isAddingNewAdditionalField.value = false;
};

const saveNewAdditionalField = () => {
	const key = newAdditionalField.key.trim();
	const value = newAdditionalField.value; // Value can be empty string
	if (!key) {
		return;
	}
	if (!editableMember.value.additional_info) {
		editableMember.value.additional_info = {};
	}
	// Disallow if key already exists
	if (
		Object.prototype.hasOwnProperty.call(
			editableMember.value.additional_info,
			key,
		)
	) {
		updateStatus(
			`Error: Field "${formatFieldLabel(
				key,
			)}" already exists. Please use a unique field name or edit the existing one.`,
			3000,
		);
		return;
	}
	editableMember.value.additional_info[key] = value;
	isAddingNewAdditionalField.value = false;
};

// Animation related
const transformOriginStyle = computed(() => {
	if (
		props.clickPosition &&
		props.clickPosition.x !== undefined &&
		props.clickPosition.y !== undefined
	) {
		return {
			transformOrigin: `${props.clickPosition.x}px ${props.clickPosition.y}px`,
		};
	}
	return { transformOrigin: "center center" }; // Fallback
});

const enterFromClass = computed(() => {
	return "opacity-0 scale-50";
});

const leaveToClass = computed(() => {
	return "opacity-0 scale-50";
});
</script>

<style scoped>
.form-input {
	@apply mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-500 dark:focus:ring-indigo-400 sm:text-sm bg-white/70 dark:bg-slate-700/70 dark:text-gray-200;
}
.detail-field,
.detail-field-editable {
	/* This class is now for the wrapper in MemberDetailsModal */
	/* Ensure consistent spacing for all fields */
	@apply py-1 min-h-[36px]; /* From EditableField.vue for consistency */
}
/* Ensure the direct child (EditableField's root) of .ml-2.flex-grow takes up space */
.ml-2.flex-grow > .editable-field-root {
	width: 100%;
}
.toggle-checkbox {
	@apply absolute block w-5 h-5 rounded-full bg-white dark:bg-slate-800 border-2 dark:border-gray-500 appearance-none cursor-pointer transition-transform duration-200 ease-in-out;
}
.toggle-checkbox:checked {
	@apply translate-x-full bg-indigo-500 dark:bg-indigo-400 border-indigo-500 dark:border-indigo-400;
}
.toggle-label {
	@apply block overflow-hidden h-5 w-10 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer transition-colors duration-200 ease-in-out;
}
.toggle-checkbox:checked + .toggle-label {
	@apply bg-indigo-500/70 dark:bg-indigo-400/70;
}

/* DatePicker styling */
:deep(.mx-datepicker-popup) {
	@apply dark:bg-slate-700 dark:text-gray-200;
}
:deep(.mx-calendar-header-label),
:deep(.mx-calendar-weekday),
:deep(.mx-calendar-date),
:deep(.mx-time-column .mx-time-item),
:deep(.mx-btn) {
	@apply dark:text-gray-200;
}
:deep(.mx-calendar-date.today) {
	@apply dark:text-indigo-400;
}
:deep(.mx-calendar-date:hover),
:deep(.mx-time-column .mx-time-item:hover) {
	@apply dark:bg-slate-600;
}
:deep(.mx-calendar-date.active) {
	@apply dark:bg-indigo-500 dark:text-white;
}
:deep(.mx-btn-text) {
	@apply dark:hover:text-indigo-300;
}
</style>
