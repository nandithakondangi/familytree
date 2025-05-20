<template>
  <div v-if="isVisible" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
    <div class="relative bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">

      <div class="flex justify-between items-center border-b pb-3 mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Add New Family Member</h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="saveMember">
        <div class="space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700">Name: <span class="text-red-500">*</span></label>
            <input
              type="text"
              id="name"
              v-model="form.name"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Name"
            />
          </div>

          <div>
            <label for="nicknames" class="block text-sm font-medium text-gray-700">Nicknames:</label>
            <input
              type="text"
              id="nicknames"
              v-model="form.nicknames"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="e.g., Johnny, Beth (comma-separated)"
            />
          </div>

          <div>
            <label for="gender" class="block text-sm font-medium text-gray-700">Gender:</label>
            <select
              id="gender"
              v-model="form.gender"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="UNKNOWN">GENDER UNKNOWN</option>
              <option value="MALE">MALE</option>
              <option value="FEMALE">FEMALE</option>
            </select>
          </div>

          <div class="flex items-center justify-between">
            <label for="isDobKnown" class="block text-sm text-gray-900 cursor-pointer">Is Date of Birth Known?</label>
            <div class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
              <input
                type="checkbox"
                id="isDobKnown"
                v-model="form.isDobKnown"
                class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
              />
              <label for="isDobKnown" class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
            </div>
          </div>

          <div v-if="form.isDobKnown" class="space-y-3 p-4 bg-gray-100 rounded-md shadow-inner">
            <h4 class="text-md font-semibold text-gray-700">Date of Birth Details:</h4>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Gregorian DOB:</label>
              <div class="flex space-x-3">
                 <input
                  type="number"
                  v-model.number="form.gregorianDob.day"
                  placeholder="DD"
                  min="1"
                  max="31"
                  class="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                 <input
                  type="number"
                  v-model.number="form.gregorianDob.month"
                  placeholder="MM"
                  min="1"
                  max="12"
                  class="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                 <input
                  type="number"
                  v-model.number="form.gregorianDob.year"
                  placeholder="YYYY"
                   min="0"
                  :max="new Date().getFullYear()"
                  class="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Traditional DOB:</label>
               <div class="flex space-x-3">
                 <select
                   v-model="form.traditionalDob.tamilMonth"
                   class="block w-1/2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                 >
                   <option value="">TAMIL MONTH</option>
                   <option value="chithirai">Chithirai</option>
                   <option value="vaikasi">Vaikasi</option>
                   </select>
                 <select
                   v-model="form.traditionalDob.tamilStar"
                   class="block w-1/2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                 >
                   <option value="">TAMIL STAR</option>
                   <option value="ashwini">Ashwini</option>
                   <option value="bharani">Bharani</option>
                    </select>
               </div>
             </div>
          </div>

           <div class="flex items-center justify-between">
            <label for="isPersonAlive" class="block text-sm text-gray-900 cursor-pointer">This person is alive</label>
             <div class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
              <input
                type="checkbox"
                id="isPersonAlive"
                v-model="form.isPersonAlive"
                class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
              />
              <label for="isPersonAlive" class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
            </div>
          </div>

          <div v-if="!form.isPersonAlive" class="space-y-3 p-4 bg-gray-100 rounded-md shadow-inner">
             <h4 class="text-md font-semibold text-gray-700">Date of Death Details:</h4>

             <div class="flex items-center justify-between">
               <label for="isDodKnown" class="block text-sm text-gray-900 cursor-pointer">Is Date of Death Known?</label>
                <div class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                 <input
                   type="checkbox"
                   id="isDodKnown"
                   v-model="form.isDodKnown"
                   class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
                 />
                 <label for="isDodKnown" class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
               </div>
             </div>

             <div v-if="form.isDodKnown" class="space-y-3">
               <div>
                 <label class="block text-sm font-medium text-gray-700 mb-1">Gregorian DoD:</label>
                 <div class="flex space-x-3">
                    <input
                     type="number"
                     v-model.number="form.gregorianDod.day"
                     placeholder="DD"
                     min="1"
                     max="31"
                     class="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                   />
                    <input
                     type="number"
                     v-model.number="form.gregorianDod.month"
                     placeholder="MM"
                     min="1"
                     max="12"
                     class="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                   />
                    <input
                     type="number"
                     v-model.number="form.gregorianDod.year"
                     placeholder="YYYY"
                     min="0"
                     :max="new Date().getFullYear()"
                     class="block w-1/3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                   />
                 </div>
               </div>

               <div>
                 <label class="block text-sm font-medium text-gray-700 mb-1">Traditional DoD:</label>
                  <div class="grid grid-cols-3 gap-3">
                    <select
                      v-model="form.traditionalDod.tamilMonth"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    >
                      <option value="">TAMIL MONTH</option>
                       <option value="chithirai">Chithirai</option>
                      <option value="vaikasi">Vaikasi</option>
                      </select>
                    <select
                      v-model="form.traditionalDod.paksham"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    >
                      <option value="">PAKSHAM</option>
                       <option value="krishna">Krishna Paksham</option>
                      <option value="shukla">Shukla Paksham</option>
                    </select>
                     <select
                      v-model="form.traditionalDod.thithi"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    >
                      <option value="">THITHI</option>
                       <option value="prathama">Prathama</option>
                       <option value="dvitiya">Dvitiya</option>
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
            class="px-4 py-2 bg-gray-300 text-gray-800 font-medium rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-opacity-50 transition duration-150 ease-in-out"
          >
            X Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150 ease-in-out"
          >
            💾 Save Member
          </button>
        </div>
      </form>

    </div>
  </div>
</template>

<script>
import { reactive, watch } from 'vue';

export default {
  name: 'AddPersonModal',
  props: {
    isVisible: {
      type: Boolean,
      required: true,
    },
     // You might want to pass the culture setting as a prop
     // isIndianCulture: {
     //   type: Boolean,
     //   default: true, // Default based on your App.vue setting
     // }
  },
  emits: ['close', 'save'], // Declare emitted events
  setup(props, { emit }) {
    const form = reactive({
      name: '',
      nicknames: '',
      gender: 'UNKNOWN',
      isDobKnown: false,
      gregorianDob: { day: null, month: null, year: null },
      traditionalDob: { tamilMonth: '', tamilStar: '' },
      isPersonAlive: true,
      isDodKnown: false,
      gregorianDod: { day: null, month: null, year: null },
      traditionalDod: { tamilMonth: '', paksham: '', thithi: '' },
    });

    // Watch for changes in isPersonAlive to reset isDodKnown if person becomes alive
    watch(() => form.isPersonAlive, (newValue) => {
      if (newValue) {
        form.isDodKnown = false;
         // Optionally clear death date fields when person is marked alive
         form.gregorianDod = { day: null, month: null, year: null };
         form.traditionalDod = { tamilMonth: '', paksham: '', thithi: '' };
      }
    });

    // Watch for changes in isDobKnown to clear DOB fields if unknown
     watch(() => form.isDobKnown, (newValue) => {
       if (!newValue) {
         form.gregorianDob = { day: null, month: null, year: null };
         form.traditionalDob = { tamilMonth: '', tamilStar: '' };
       }
     });

     // Watch for changes in isDodKnown to clear DOD fields if unknown
      watch(() => form.isDodKnown, (newValue) => {
        if (!newValue) {
          form.gregorianDod = { day: null, month: null, year: null };
          form.traditionalDod = { tamilMonth: '', paksham: '', thithi: '' };
        }
      });


    const closeModal = () => {
      emit('close'); // Emit close event to parent
      resetForm(); // Reset form state when closing
    };

    const saveMember = () => {
      // Basic validation (name is required)
      if (!form.name.trim()) {
        alert('Name is required.'); // Replace with a more styled notification later
        return;
      }

      // Prepare data to send to backend
      const memberData = {
        name: form.name.trim(),
        nicknames: form.nicknames.split(',').map(name => name.trim()).filter(name => name), // Split and trim nicknames
        gender: form.gender,
        is_dob_known: form.isDobKnown,
        gregorian_dob: form.isDobKnown ? form.gregorianDob : null,
        traditional_dob: (form.isDobKnown /* && props.isIndianCulture */) ? form.traditionalDob : null, // Conditionally include traditional DOB
        is_alive: form.isPersonAlive,
        is_dod_known: !form.isPersonAlive ? form.isDodKnown : false, // Only relevant if not alive
        gregorian_dod: (!form.isPersonAlive && form.isDodKnown) ? form.gregorianDod : null,
        traditional_dod: (!form.isPersonAlive && form.isDodKnown /* && props.isIndianCulture */) ? form.traditionalDod : null, // Conditionally include traditional DOD
      };

      console.log('Saving member:', memberData);

      // TODO: Send memberData to your FastAPI backend API to add the person
      // Example using fetch:
      fetch('/api/add-person', { // Replace with your actual backend endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(memberData),
      })
      .then(response => {
        if (!response.ok) {
          // Handle backend errors
          return response.json().then(err => { throw new Error(err.detail || 'Failed to add person.'); });
        }
        return response.json(); // Assuming backend returns the new person data or success message
      })
      .then(data => {
        console.log('Person added successfully:', data);
        // TODO: Show success message (e.g., using the status display)
        // Inject updateStatus from App.vue if needed
        // updateStatus('Person added successfully!', 5000);

        emit('save', data); // Emit save event, optionally with the new person data
        closeModal(); // Close modal on success
      })
      .catch(error => {
        console.error('Error adding person:', error);
        // TODO: Show error message (e.g., using a modal or status display)
        alert(`Error adding person: ${error.message}`); // Replace with styled error
      });
    };

    const resetForm = () => {
      form.name = '';
      form.nicknames = '';
      form.gender = 'UNKNOWN';
      form.isDobKnown = false;
      form.gregorianDob = { day: null, month: null, year: null };
      form.traditionalDob = { tamilMonth: '', tamilStar: '' };
      form.isPersonAlive = true;
      form.isDodKnown = false;
      form.gregorianDod = { day: null, month: null, year: null };
      form.traditionalDod = { tamilMonth: '', paksham: '', thithi: '' };
    };

    // TODO: Fetch dropdown options (Gender, Tamil Months, Stars, Paksham, Thithi)
    // You would typically do this on component mount or when the modal becomes visible
    // Example:
    // onMounted(() => {
    //   fetchDropdownOptions();
    // });
    //
    // const fetchDropdownOptions = () => {
    //   fetch('/api/dropdown-options') // Replace with your backend endpoint
    //     .then(response => response.json())
    //     .then(data => {
    //       // Populate dropdown options data properties
    //       // e.g., this.genderOptions = data.genders;
    //     })
    //     .catch(error => console.error('Error fetching dropdown options:', error));
    // };


    return {
      form,
      // isVisible is a prop, no need to return it from setup
      closeModal,
      saveMember,
      // isIndianCulture: props.isIndianCulture, // Expose prop if needed in template
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
  right: 0;
  border-color: #6366f1; /* indigo-500 */
}

.toggle-label {
  transition: background-color 0.2s ease-in-out;
}

.toggle-checkbox:checked + .toggle-label {
  background-color: #6366f1; /* indigo-500 */
}
</style>
