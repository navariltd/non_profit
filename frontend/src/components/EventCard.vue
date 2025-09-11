<template>
  <div
    class="flex flex-col border border-gray-200 rounded-lg p-4 h-full hover:border-gray-300 hover:shadow-sm transition-all duration-200 bg-white"
  >
    <div class="flex flex-col space-y-3 mb-4 flex-1">
      <div class="flex items-center justify-between">
        <div class="text-lg font-semibold text-gray-900 leading-tight">
          {{ event.name }}
        </div>
        <Badge
          v-if="event.confirmStatus"
          theme="green"
          size="sm"
          variant="solid"
        >
          Confirmed
        </Badge>
      </div>

      <span class="font-medium text-gray-700 leading-5 text-sm">
        {{ event.subject }}
      </span>

      <div class="flex items-center space-x-2 text-sm">
        <Calendar class="w-3 h-3 flex-shrink-0" />
        <span>Kick Off</span>
        <span>{{ event.starts_on }}</span>
      </div>

      <div class="flex items-center space-x-2 text-sm">
        <Clock class="w-3 h-3 flex-shrink-0" />
        <span>Adjourn</span>
        <span>{{ event.ends_on }}</span>
      </div>
    </div>

    <div class="flex flex-wrap gap-2 mt-auto pt-3 border-t border-gray-100">
      <Badge>
        {{ event.status }}
      </Badge>
      <Badge>
        {{ event.event_category }}
      </Badge>
      <Badge>
        {{ event.event_type }}
      </Badge>
    </div>

    <Button
      :variant="'solid'"
      :ref_for="true"
      theme="gray"
      size="sm"
      label="Button"
      :loading="false"
      :disabled="false"
      tooltip="Hover for more!"
      class="m-3"
      @click="attendModal = true"
    >
      View
    </Button>
  </div>
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
