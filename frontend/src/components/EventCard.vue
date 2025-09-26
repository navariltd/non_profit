<template>
  <div
    class="flex flex-col border cursor-pointer border-gray-200 rounded-xl p-5 h-full bg-white hover:border-red-300 hover:shadow-md transition-all duration-300 group"
  >
    <!-- Event Header -->
    <div class="flex items-center justify-between mb-3">
      <h3
        class="text-lg font-semibold text-gray-900 group-hover:text-red-600 transition-colors"
      >
        {{ event.subject }}
      </h3>
      <Badge
        v-if="event.confirmStatus"
        theme="green"
        size="sm"
        variant="solid"
        class="shadow-sm"
      >
        Confirmed
      </Badge>
    </div>

    <!-- Dates & Times -->
    <div class="flex items-center space-x-2 text-sm text-gray-600 mb-1">
      <Calendar class="w-4 h-4 text-red-500" />
      <span class="font-medium">Kick Off:</span>
      <span>{{ event.starts_on }}</span>
    </div>

    <div class="flex items-center space-x-2 text-sm text-gray-600">
      <Clock class="w-4 h-4 text-red-500" />
      <span class="font-medium">Adjourn:</span>
      <span>{{ event.ends_on }}</span>
    </div>

    <!-- Tags -->
    <div
      class="flex flex-wrap gap-2 mt-auto pt-4 border-t border-gray-100 text-xs"
    >
      <Badge class="bg-red-50 text-red-700 border border-red-200">
        {{ event.event_type }}
      </Badge>
    </div>

    <!-- Action Button -->
    <div class="mt-4">
      <Button
        variant="solid"
        theme="red"
        size="sm"
        class="w-full rounded-lg"
        @click="attendModal = true"
      >
        View Event
      </Button>
    </div>
  </div>

  <!-- Modal -->
  <AttendEventModal
    v-model="attendModal"
    :event="event"
    @confirmed="handleConfirmed"
  />
</template>

<script lang="ts" setup>
import { Badge, Button, toast } from "frappe-ui";
import { Calendar, Clock } from "lucide-vue-next";
import { inject, onMounted, ref } from "vue";
import { membershipStore } from "../stores/membership";
import AttendEventModal from "./Modals/AttendEventModal.vue";

const attendModal = ref(false);
const { events } = membershipStore();
const reloadConfirmStatus = inject<() => void>("reloadConfirmStatus");

onMounted(() => {});

export interface Event {
  name: string;
  subject: string;
  event_category: string;
  event_type: string;
  starts_on: Date;
  ends_on: Date;
  status: string;
  description: string;
  confirmStatus?: boolean;
  color?: string;
}

defineProps<{
  event: Event;
}>();

function handleConfirmed() {
  if (reloadConfirmStatus) {
    reloadConfirmStatus();
  }
  toast.success("You successfully registered for the event");
}
</script>
