<template>
  <div
    class="flex flex-col border border-gray-200 rounded-lg p-4 h-full hover:border-gray-300 hover:shadow-sm transition-all duration-200 bg-white"
  >
    <div class="flex flex-col space-y-3 mb-4 flex-1">
      <div class="text-lg font-semibold text-gray-900 leading-tight">
        {{ event.name }}
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
      @click="attendStatus = true"
    >
      View
    </Button>
  </div>
  <Dialog v-model="attendStatus">
    <template #body-title>
      <h3 class="text-2xl font-semibold text-ink-gray-9">Confirm Attendance</h3>
    </template>
    <template #body-content>
      <p class="text-gray-700">
        Confirm you want to attend:
        <span class="font-bold">
          {{ event.name }}
        </span>
      </p>
    </template>
    <template #actions>
      <div class="flex space-x-2">
        <Button variant="solid" @click=""> Confirm </Button>
        <Button @click="attendStatus = false"> Cancel </Button>
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import { Badge, Button, Dialog } from "frappe-ui";
import { Calendar, Clock, MapPin } from "lucide-vue-next";
import { ref } from "vue";

const attendStatus = ref(false);

export interface Event {
  name: string;
  subject: string;
  event_category: string;
  event_type: string;
  starts_on: Date;
  ends_on: Date;
  status: string;
}

defineProps<{
  event: Event;
}>();
</script>
