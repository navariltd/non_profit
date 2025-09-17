<template>
  <Dialog
    v-model="setAvailability"
    :options="{ size: calendarView ? '7xl' : 'lg' }"
  >
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

      <div class="p-3" v-if="calendarView">
        <Calendar
          :config="{
            defaultMode: 'Month',
            eventIcons: {},
            allowCustomClickEvents: true,
            enableShortcuts: false,
          }"
          :events="calendarSlots"
        />
      </div>
    </template>
    <template #actions>
      <div class="flex flex-row justify-end space-x-2 w-full items-center">
        <Button
          variant="outline"
          theme="red"
          @click="calendarView = !calendarView"
        >
          {{ calendarView ? "Hide" : "Show" }} Calendar Slots
        </Button>
        <Button
          variant="solid"
          theme="red"
          :loading="newSlot.loading"
          @click="validateSlot"
          class="rounded-xl shadow-md"
        >
          Confirm Slots
        </Button>
      </div>
      <ErrorMessage :message="newSlot.error" class="mt-2 text-center" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import {
  Dialog,
  Button,
  createResource,
  DateTimePicker,
  ErrorMessage,
  Calendar,
} from "frappe-ui";
import { computed, reactive, ref, watch } from "vue";
import { usersStore } from "../../stores/user";
const { roleResource, presentSlots } = usersStore();
const setAvailability = ref(true);
const calendarView = ref(false);

const emit = defineEmits(["success"]);

const availabilityslot = reactive({
  employee: roleResource.data.employee,
  company: roleResource.data.company,
  user: roleResource.data.name,
  starts_on: "",
  ends_on: "",
});

const newSlot = createResource({
  url: "non_profit.non_profit.api.create_availability_slot",
  makeParams(values) {
    return { slot_data: { ...values } };
  },
  onSuccess() {
    availabilityslot.starts_on = "";
    availabilityslot.ends_on = "";

    emit("success");
    setAvailability.value = false;
  },
});

function validateSlot() {
  if (availabilityslot.starts_on >= availabilityslot.ends_on) {
    newSlot.error = "From time must be before To time";
  }

  if (!availabilityslot.starts_on || !availabilityslot.ends_on) {
    newSlot.error = "Both From and To times are required";
  }

  if (!newSlot.error) {
    newSlot.submit({ ...availabilityslot });
  }
}

watch(
  () => [availabilityslot.starts_on, availabilityslot.ends_on],
  ([starts_on, ends_on]) => {
    if (starts_on >= ends_on) {
      newSlot.error = "From time must be before To time";
    } else {
      newSlot.error = "";
    }
  }
);
watch(setAvailability, (isOpen) => {
  if (!isOpen) {
    availabilityslot.starts_on = "";
    availabilityslot.ends_on = "";
    newSlot.error = "";
  }
});
function getDatesBetween(start: string, end: string) {
  const dates: string[] = [];
  let current = new Date(start);
  const last = new Date(end);

  while (current <= last) {
    dates.push(new Date(current).toISOString().slice(0, 10));
    current.setDate(current.getDate() + 1);
  }

  return dates;
}

const calendarSlots = computed(() => {
  if (!presentSlots.data) return [];

  return presentSlots.data.flatMap((slot) => {
    const days = getDatesBetween(slot.starts_on, slot.ends_on);
    const startTime = new Date(slot.starts_on).toTimeString().slice(0, 8);
    const endTime = new Date(slot.ends_on).toTimeString().slice(0, 8);

    return days.map((day) => {
      return {
        title: "Available",
        id: `${slot.name}-${day}`,
        fromDate: `${day} ${startTime}`,
        toDate: `${day} ${endTime}`,
        fromTime: `${day} ${startTime}`,
        toTime: `${day} ${endTime}`,
        color: "green",
      };
    });
  });
});
</script>
