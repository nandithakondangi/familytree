<template>
  <div class="p-6 space-y-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
      GlassyDatePicker Examples
    </h2>
    
    <!-- Basic Usage -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
        Basic Usage
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Date of Birth
          </label>
          <GlassyDatePicker
            v-model="dob"
            placeholder="Select date of birth"
            theme-color="indigo"
            :disabled-date="disableFutureDates"
          />
          <p class="text-xs text-gray-500 mt-1">Selected: {{ dob || 'None' }}</p>
          <p class="text-xs text-gray-400 mt-1">Type: {{ typeof dob }}</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Appointment Time
          </label>
          <GlassyDatePicker
            v-model="appointment"
            type="datetime"
            format="YYYY-MM-DD HH:mm"
            placeholder="Select appointment time"
            theme-color="green"
          />
          <p class="text-xs text-gray-500 mt-1">Selected: {{ appointment || 'None' }}</p>
        </div>
      </div>
    </div>

    <!-- Different Themes -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
        Different Themes
      </h3>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Blue Theme
          </label>
          <GlassyDatePicker
            v-model="blueDate"
            placeholder="Blue theme"
            theme-color="blue"
            size="sm"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Green Theme
          </label>
          <GlassyDatePicker
            v-model="greenDate"
            placeholder="Green theme"
            theme-color="green"
            size="sm"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Orange Theme
          </label>
          <GlassyDatePicker
            v-model="orangeDate"
            placeholder="Orange theme"
            theme-color="orange"
            size="sm"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Yellow Theme
          </label>
          <GlassyDatePicker
            v-model="yellowDate"
            placeholder="Yellow theme"
            theme-color="yellow"
            size="sm"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Danger Theme
          </label>
          <GlassyDatePicker
            v-model="dangerDate"
            placeholder="Danger theme"
            theme-color="danger"
            size="sm"
          />
        </div>
      </div>
    </div>

    <!-- Different Sizes -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
        Different Sizes
      </h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Small Size
          </label>
          <GlassyDatePicker
            v-model="smallDate"
            placeholder="Small size"
            theme-color="indigo"
            size="sm"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Medium Size (Default)
          </label>
          <GlassyDatePicker
            v-model="mediumDate"
            placeholder="Medium size"
            theme-color="indigo"
            size="md"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Large Size
          </label>
          <GlassyDatePicker
            v-model="largeDate"
            placeholder="Large size"
            theme-color="indigo"
            size="lg"
          />
        </div>
      </div>
    </div>

    <!-- Different Types -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
        Different Types
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Date Only
          </label>
          <GlassyDatePicker
            v-model="dateOnly"
            type="date"
            format="YYYY-MM-DD"
            placeholder="Select date"
            theme-color="indigo"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Date & Time
          </label>
          <GlassyDatePicker
            v-model="dateTime"
            type="datetime"
            format="YYYY-MM-DD HH:mm"
            placeholder="Select date and time"
            theme-color="green"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Time Only
          </label>
          <GlassyDatePicker
            v-model="timeOnly"
            type="time"
            format="HH:mm"
            placeholder="Select time"
            theme-color="blue"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Month Only
          </label>
          <GlassyDatePicker
            v-model="monthOnly"
            type="month"
            format="YYYY-MM"
            placeholder="Select month"
            theme-color="orange"
          />
        </div>
      </div>
    </div>

    <!-- States -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
        Different States
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            With Pre-selected Value
          </label>
          <GlassyDatePicker
            v-model="preselectedDate"
            placeholder="Has a value"
            theme-color="indigo"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Disabled
          </label>
          <GlassyDatePicker
            v-model="disabledDate"
            placeholder="Disabled"
            theme-color="indigo"
            :disabled="true"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Not Editable
          </label>
          <GlassyDatePicker
            v-model="nonEditableDate"
            placeholder="Not editable"
            theme-color="indigo"
            :editable="false"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Not Clearable
          </label>
          <GlassyDatePicker
            v-model="nonClearableDate"
            placeholder="Not clearable"
            theme-color="indigo"
            :clearable="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import GlassyDatePicker from './GlassyDatePicker.vue';

// Reactive data for examples
const dob = ref('');
const appointment = ref('');
const blueDate = ref('');
const greenDate = ref('');
const orangeDate = ref('');
const yellowDate = ref('');
const dangerDate = ref('');
const smallDate = ref('');
const mediumDate = ref('');
const largeDate = ref('');
const dateOnly = ref('');
const dateTime = ref('');
const timeOnly = ref('');
const monthOnly = ref('');
const preselectedDate = ref('2024-01-15');
const disabledDate = ref('2024-01-15');
const nonEditableDate = ref('2024-01-15');
const nonClearableDate = ref('2024-01-15');

// Function to disable future dates
const disableFutureDates = (date) => {
  return date > new Date(new Date().setHours(23, 59, 59, 999));
};
</script> 