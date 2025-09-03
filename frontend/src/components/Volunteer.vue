<template>
  <div>
    <div class="flex flex-col md:flex-row justify-evenly items-center m-8">
      <div></div>
      <div></div>
      <div class="flex items-center space-x-4 mb-6">
        <div class="flex items-center space-x-2 rounded-lg p-2">
          <Button
            variant="solid"
            size="lg"
            theme="green"
            @click="setAvailability = true"
          >
            Set Availability
          </Button>
        </div>
        <div
          class="relative cursor-pointer"
          @click="showNotificationDialog = true"
        >
          <div
            class="relative inline-block"
            :class="{ 'animate-bounce': hasNotification }"
          >
            <Bell class="text-xl" />

            <span
              v-if="hasNotification"
              class="absolute -top-1 -right-1 block h-3 w-3 rounded-full ring-2 ring-white bg-red-600"
            ></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Dialog -->
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
  </div>

  <Dialog v-model="setAvailability">
    <template #body-title>Choose Available Timeslots</template>
    <template #body-content>
      <div class="flex flex-col md:flex-row gap-2 p-2">
        <DateTimePicker
          v-model="availabilityslot.starts_on"
          variant="subtle"
          placeholder="From"
          :disabled="false"
          label="From"
        />

        <DateTimePicker
          v-model="availabilityslot.ends_on"
          variant="subtle"
          placeholder="To"
          :disabled="false"
          label="To"
        />
      </div>
    </template>
    <template #actions>
      <Button
        v-if="availabilityslot.starts_on && availabilityslot.ends_on"
        variant="solid"
        :loading="newSlot.loading"
        theme="blue"
        @click="createSlot"
      >
        Confirm Slots
      </Button>
      <ErrorMessage :message="newSlot.error" />
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import { reactive, ref } from "vue";
import {
  Dialog,
  Button,
  createResource,
  DateTimePicker,
  ErrorMessage,
} from "frappe-ui";
import Projects from "./Projects.vue";
import { Bell } from "lucide-vue-next";
import { usersStore } from "../stores/user";

const volunteerStats = ref({
  hours: 125,
  events: 8,
  badges: 3,
});

const { roleResource } = usersStore();

const isAvailable = ref(true);

const hasNotification = ref(true);
const showNotificationDialog = ref(false);
const setAvailability = ref(false);

const availabilityslot = reactive({
  employee: roleResource.data.employee,
  company: roleResource.data.company,
  branch: roleResource.data.branch,
  user: roleResource.data.name,
  starts_on: "",
  ends_on: "",
});

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

const newSlot = createResource({
  url: "non_profit.non_profit.api.create_availability_slot",
  makeParams(values) {
    return {
      slot_data: values,
    };
  },
});

const createSlot = () => {
  newSlot.submit(
    { doctype: "Volunteer Availability Slot", ...availabilityslot },
    {
      onSuccess(data) {
        setAvailability.value = false;
        console.log("submitted", data);
      },
      onError(err) {
        console.log("err", err);
      },
    }
  );
};
</script>
