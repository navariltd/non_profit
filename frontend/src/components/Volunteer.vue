<template>
  <div>
    <!-- Top Buttons -->
    <div class="flex flex-row justify-end items-center m-6 space-x-4">
      <Button
        variant="solid"
        size="lg"
        theme="blue"
        @click="setAvailability = true"
        class="rounded-xl shadow-md"
      >
        Set Availability
      </Button>

      <!-- Notification Bell -->
      <div
        class="relative cursor-pointer"
        @click="showNotificationDialog = true"
      >
        <div
          class="relative inline-block"
          :class="{ 'animate-bounce': hasNotification }"
        >
          <Bell class="h-7 w-7 text-gray-700" />
          <span
            v-if="hasNotification"
            class="absolute -top-1 -right-1 block h-3 w-3 rounded-full bg-red-600 ring-2 ring-white"
          ></span>
        </div>
      </div>
    </div>

    <!-- Notification Dialog -->
    <Dialog :options="{ size: '7xl' }" v-model="showNotificationDialog">
      <template #body-title>
        <h3 class="text-2xl font-bold text-gray-900">New Project Assignment</h3>
      </template>

      <template #body-content>
        <!-- Projects Available -->
        <div v-if="assignedProjects.length" class="space-y-6">
          <p class="text-lg text-gray-700">
            You have been assigned to the following project(s):
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="project in assignedProjects"
              :key="project.name"
              class="bg-white rounded-2xl shadow-md border border-gray-200 p-6"
            >
              <!-- Project Header -->
              <div class="flex items-center justify-between border-b pb-3 mb-4">
                <div>
                  <h4 class="text-xl font-semibold text-gray-900">
                    {{ project.project_name }}
                  </h4>
                  <p class="text-sm text-gray-500">Code: {{ project.name }}</p>
                </div>
                <Badge :theme="priorityTheme(project.priority)">
                  {{ project.priority }}
                </Badge>
              </div>

              <!-- Project Info -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-700">
                <p>
                  <span class="font-semibold">Deployment:</span>
                  {{ project.deployment_name }}
                </p>
                <p>
                  <span class="font-semibold">Status:</span>
                  {{ project.status }}
                </p>
                <p>
                  <span class="font-semibold">Type:</span>
                  {{ project.project_type }}
                </p>
                <p>
                  <span class="font-semibold">Active:</span>
                  {{ project.is_active }}
                </p>
                <p>
                  <span class="font-semibold">Start Date:</span>
                  {{ project.expected_start_date }}
                </p>
                <p>
                  <span class="font-semibold">End Date:</span>
                  {{ project.expected_end_date }}
                </p>
                <p>
                  <span class="font-semibold">Completion:</span>
                  {{ project.percent_complete }}%
                </p>
              </div>

              <!-- Notes -->
              <div v-if="project.notes" class="mt-4">
                <h5 class="font-semibold text-gray-800 mb-2">Notes:</h5>
                <div
                  class="prose prose-sm text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200"
                  v-html="project.notes"
                ></div>
              </div>

              <!-- Task Info -->
              <div
                v-if="project.task"
                class="mt-6 bg-gray-50 p-4 rounded-lg border"
              >
                <h5 class="text-lg font-semibold text-gray-900">
                  Assigned Task
                </h5>
                <div
                  class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700 mt-2"
                >
                  <p>
                    <span class="font-semibold">Task:</span>
                    {{ project.task.name }}
                  </p>
                  <p>
                    <span class="font-semibold">Subject:</span>
                    {{ project.task.subject }}
                  </p>
                  <p>
                    <span class="font-semibold">Status:</span>
                    {{ project.task.status }}
                  </p>
                  <p>
                    <span class="font-semibold">Priority:</span>
                    {{ project.task.priority }}
                  </p>
                  <p>
                    <span class="font-semibold">Start:</span>
                    {{ project.task.exp_start_date || "N/A" }}
                  </p>
                  <p>
                    <span class="font-semibold">End:</span>
                    {{ project.task.exp_end_date || "N/A" }}
                  </p>
                </div>

                <!-- Task Description -->
                <div v-if="project.task.description" class="mt-3">
                  <h6 class="font-semibold text-gray-800">Description:</h6>
                  <div
                    class="prose prose-sm text-gray-700 bg-white p-3 rounded-lg border"
                    v-html="project.task.description"
                  ></div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex justify-end space-x-3 mt-6">
                <Button
                  variant="outline"
                  theme="red"
                  @click="rejectAssignment(project)"
                  class="rounded-xl px-5"
                >
                  Reject
                </Button>
                <Button
                  variant="solid"
                  theme="green"
                  @click="acceptAssignment(project)"
                  class="rounded-xl shadow px-5"
                >
                  Accept
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-else
          class="flex flex-col items-center justify-center text-center py-16 text-gray-500"
        >
          <Bell class="h-12 w-12 mb-3 text-gray-400" />
          <p class="text-lg font-medium">No new notifications</p>
          <p class="text-sm text-gray-400">
            You're all caught up! We'll notify you when new assignments arrive.
          </p>
        </div>
      </template>
    </Dialog>

    <!-- Availability Dialog -->
    <Dialog v-model="setAvailability">
      <template #body-title>
        <h3 class="text-xl font-bold text-gray-900">
          Choose Available Timeslots
        </h3>
      </template>
      <template #body-content>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-2">
          <DateTimePicker
            v-model="availabilityslot.starts_on"
            variant="subtle"
            placeholder="From"
            label="From"
          />
          <DateTimePicker
            v-model="availabilityslot.ends_on"
            variant="subtle"
            placeholder="To"
            label="To"
          />
        </div>
      </template>
      <template #actions>
        <Button
          v-if="availabilityslot.starts_on && availabilityslot.ends_on"
          variant="solid"
          theme="blue"
          :loading="newSlot.loading"
          @click="createSlot"
          class="rounded-xl shadow-md"
        >
          Confirm Slots
        </Button>
        <ErrorMessage :message="newSlot.error" />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from "vue";
import {
  Dialog,
  Button,
  createResource,
  DateTimePicker,
  ErrorMessage,
  Badge,
} from "frappe-ui";
import { Bell } from "lucide-vue-next";
import { usersStore } from "../stores/user";

interface Task {
  name: string;
  subject: string;
  description: string;
  exp_start_date: string | null;
  exp_end_date: string | null;
  priority: string;
  status: string;
  project: string;
}

interface Project {
  deployment_name: string;
  expected_end_date: string;
  expected_start_date: string;
  is_active: string;
  name: string;
  notes: string;
  percent_complete: number;
  priority: string;
  project_name: string;
  project_type: string;
  status: string;
  task?: Task;
}

const { roleResource } = usersStore();

const hasNotification = ref(false);
const showNotificationDialog = ref(false);
const setAvailability = ref(false);

const assignedProjects = ref<Project[]>([]);

const availabilityslot = reactive({
  employee: roleResource.data.employee,
  company: roleResource.data.company,
  branch: roleResource.data.branch,
  user: roleResource.data.name,
  starts_on: "",
  ends_on: "",
});

// API resource for assignment decisions
const assignmentDecision = createResource({
  url: "non_profit.non_profit.api.accept_assignment",
  makeParams(values) {
    return values; // we'll pass { name, accepted }
  },
});

// Accept a project
const acceptAssignment = (project: Project) => {
  assignmentDecision.submit(
    { name: project.deployment_name, accepted: true },
    {
      onSuccess() {
        assignedProjects.value = assignedProjects.value.filter(
          (p) => p.deployment_name !== project.deployment_name
        );
        if (assignedProjects.value.length === 0) {
          hasNotification.value = false;
          showNotificationDialog.value = false;
        }
      },
    }
  );
};

// Reject a project
const rejectAssignment = (project: Project) => {
  assignmentDecision.submit(
    { name: project.deployment_name, accepted: false },
    {
      onSuccess() {
        assignedProjects.value = assignedProjects.value.filter(
          (p) => p.deployment_name !== project.deployment_name
        );
        if (assignedProjects.value.length === 0) {
          hasNotification.value = false;
          showNotificationDialog.value = false;
        }
      },
    }
  );
};

// Resource for creating availability slots
const newSlot = createResource({
  url: "non_profit.non_profit.api.create_availability_slot",
  makeParams(values) {
    return { slot_data: values };
  },
});

// Resource for fetching assigned projects
const project = createResource({
  url: "non_profit.non_profit.api.fetch_assigned_projects",
  auto: true,
  onSuccess(data) {
    if (data.length) {
      hasNotification.value = true;
      assignedProjects.value = Array.isArray(data) ? data : [data];
    } else {
      hasNotification.value = false;
    }
  },
});

// Create availability slot
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

// Priority theme
function priorityTheme(priority: string) {
  switch (priority) {
    case "High":
      return "red";
    case "Medium":
      return "orange";
    case "Low":
      return "green";
    default:
      return "gray";
  }
}
</script>
