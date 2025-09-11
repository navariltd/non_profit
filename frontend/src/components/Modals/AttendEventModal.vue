<template>
  <Dialog v-model="isOpen">
    <template #body-title>
      <h3 class="text-xl font-medium text-gray-900">Event Details</h3>
    </template>

    <template #body-content>
      <div v-if="event" class="space-y-4">
        <h4 class="text-lg font-semibold text-gray-800">
          {{ event.subject }}
        </h4>

        <div v-if="event.description" class="bg-gray-50 rounded-lg p-3">
          <p class="text-sm text-gray-600">{{ event.description }}</p>
        </div>

        <div class="grid gap-2 text-sm">
          <div class="flex justify-between">
            <span class="font-medium">Start</span>
            <span>{{ event.starts_on }}</span>
          </div>
          <div class="flex justify-between">
            <span class="font-medium">End</span>
            <span>{{ event.ends_on }}</span>
          </div>
          <div class="flex justify-between">
            <span class="font-medium">Status</span>
            <Badge
              :variant="event.confirmStatus ? 'subtle' : 'outline'"
              :theme="event.confirmStatus ? 'green' : 'red'"
              size="sm"
            >
              {{ event.confirmStatus ? "Confirmed" : "Not Confirmed" }}
            </Badge>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex space-x-2 justify-end">
        <Button variant="outline" theme="gray" size="sm" @click="close">
          Close
        </Button>
        <Button
          v-if="event && !event.confirmStatus"
          variant="solid"
          theme="red"
          size="sm"
          :loading="confirmEvent.loading"
          @click="submit(event)"
        >
          Confirm Attendance
        </Button>
      </div>
      <ErrorMessage v-if="confirmEvent.error" :error="confirmEvent.error" />
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import {
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  createResource,
  toast,
} from "frappe-ui";
import { computed } from "vue";
import type { Event } from "../EventCard.vue";

const props = defineProps<{
  modelValue: boolean;
  event: Event | null;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "confirmed"): void;
}>();

const isOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit("update:modelValue", val),
});

function close() {
  isOpen.value = false;
  confirmEvent.reset();
}

const confirmEvent = createResource({
  url: "non_profit.non_profit.api.attend_event",
  onSuccess() {
    isOpen.value = false;
    emit("confirmed");
  },
});

function submit(event: Event) {
  confirmEvent.submit({ ...event });
}
</script>
