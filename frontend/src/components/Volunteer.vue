<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">Volunteer Dashboard</h1>
        <div class="flex items-center space-x-4">
          <div
            class="flex items-center space-x-2 border border-gray-700 rounded-lg p-2"
          >
            <Switch
              size="sm"
              label="Set Availability"
              description="If On, you will receive notifications for new projects"
              :disabled="false"
              v-model="isAvailable"
            />
          </div>

          <div
            class="relative cursor-pointer"
            @click="showNotificationDialog = true"
          >
            <FeatherIcon
              name="bell"
              class="w-6 h-6 text-gray-600 hover:text-gray-800"
            />
            <span
              v-if="hasNotification"
              class="absolute top-0 right-0 block h-2 w-2 rounded-full ring-2 ring-white bg-red-400"
            ></span>
          </div>
        </div>
      </div>

      <p class="text-gray-600 -mt-6 mb-8 text-center">
        Track your volunteer activities and discover new opportunities
      </p>

      <div class="mb-12">
        <h2 class="text-xl font-semibold text-gray-700 mb-6 text-center">
          Your Impact
        </h2>
        <div class="flex justify-center">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
            <div
              class="bg-white rounded-lg shadow-lg p-6 text-center border border-gray-200 bg-gradient-to-br from-blue-50 to-blue-100"
            >
              <h3 class="text-4xl font-bold text-blue-700 mb-2">
                {{ volunteerStats.hours }}
              </h3>
              <p class="text-gray-600 font-medium">Total Hours</p>
            </div>
            <div
              class="bg-white rounded-lg shadow-lg p-6 text-center border border-gray-200 bg-gradient-to-br from-green-50 to-green-100"
            >
              <h3 class="text-4xl font-bold text-green-700 mb-2">
                {{ volunteerStats.events }}
              </h3>
              <p class="text-gray-600 font-medium">Events Attended</p>
            </div>
            <div
              class="bg-white rounded-lg shadow-lg p-6 text-center border border-gray-200 bg-gradient-to-br from-yellow-50 to-yellow-100"
            >
              <h3 class="text-4xl font-bold text-yellow-700 mb-2">
                {{ volunteerStats.badges }}
              </h3>
              <p class="text-gray-600 font-medium">Badges Earned</p>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div
          class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
        >
          <div
            class="p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50"
          >
            <h3 class="text-xl font-semibold text-gray-700">Upcoming Events</h3>
            <p class="text-gray-600 text-sm mt-1">
              Stay connected with your volunteer community
            </p>
          </div>
          <div class="p-6">
            <Events />
          </div>
        </div>

        <div
          class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
        >
          <div
            class="p-6 border-b border-gray-100 bg-gradient-to-r from-green-50 to-emerald-50"
          >
            <h3 class="text-xl font-semibold text-gray-700">
              Current Projects
            </h3>
            <p class="text-gray-600 text-sm mt-1">
              Your ongoing volunteer commitments
            </p>
          </div>
          <div class="p-6">
            <Projects />
          </div>
        </div>
      </div>
    </div>
  </div>

  <Dialog v-model="showNotificationDialog">
    <template #body-title>
      <h3 class="text-2xl font-semibold text-gray-900">
        New Project Assignment
      </h3>
    </template>
    <template #body-content>
      <div v-if="assignedProject">
        <p class="text-lg text-gray-700 mb-4">
          You have been assigned to the following project:
        </p>
        <div class="bg-gray-50 p-4 rounded-md">
          <p class="text-base font-semibold text-gray-800">
            {{ assignedProject.name }}
          </p>
          <p class="text-sm text-gray-600 mt-1">
            Manager: {{ assignedProject.manager }}
          </p>
          <p class="text-sm text-gray-600 mt-1">
            Status: {{ assignedProject.status }}
          </p>
          <p class="text-sm text-gray-600 mt-2 italic">
            "{{ assignedProject.description }}"
          </p>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex space-x-2">
        <Button variant="solid" color="green" @click="acceptAssignment">
          Accept
        </Button>
        <Button variant="solid" theme="red" @click="rejectAssignment">
          Reject
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { Dialog, Button, FeatherIcon } from "frappe-ui";
import Projects from "./Projects.vue";
import Events from "../pages/Events.vue";
import Switch from "frappe-ui/src/components/Switch/Switch.vue";

const volunteerStats = ref({
  hours: 125,
  events: 8,
  badges: 3,
});

const isAvailable = ref(true);

const hasNotification = ref(true);
const showNotificationDialog = ref(false);

const assignedProject = ref({
  name: "Community Garden",
  status: "Pending",
  manager: "John Smith",
  description:
    "Help build and maintain a community garden to promote sustainable living and provide fresh produce to local food banks. This project requires physical labor and knowledge of gardening.",
});

const toggleAvailability = () => {
  isAvailable.value = !isAvailable.value;
};

const acceptAssignment = () => {
  hasNotification.value = false;
  showNotificationDialog.value = false;
};

const rejectAssignment = () => {
  hasNotification.value = false;
  showNotificationDialog.value = false;
};
</script>
