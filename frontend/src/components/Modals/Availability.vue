<template>
  <Dialog
    v-model="setAvailability"
    :options="{ size: calendarView ? '7xl' : '3xl' }"
  >
    <template #body-title>
      <h3 class="text-xl font-bold text-gray-900">
        Choose Available Timeslots
      </h3>
    </template>
    <template #body-content>
      <!-- Selection Type -->
      <div class="p-4 bg-red-50 rounded-lg mb-4">
        <p class="text-red-700 mb-3">
          Choose how you want to set your availability:
        </p>
        <div class="flex gap-4">
          <label class="flex items-center cursor-pointer">
            <input
              type="radio"
              v-model="selectionType"
              value="single"
              class="mr-2"
            />
            <span class="text-sm">Single Day</span>
          </label>
          <label class="flex items-center cursor-pointer">
            <input
              type="radio"
              v-model="selectionType"
              value="range"
              class="mr-2"
            />
            <span class="text-sm">Date Range</span>
          </label>
        </div>
      </div>

      <div v-if="selectionType === 'single'" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <DatePicker
            v-model="singleDay.date"
            variant="subtle"
            placeholder="Select Date"
            label="Date"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Start Time</label
            >
            <Select v-model="singleDay.startTime" :options="timeOptions" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >End Time</label
            >
            <Select v-model="singleDay.endTime" :options="timeOptions" />
          </div>
        </div>

        <div class="text-sm text-gray-600 bg-gray-50 p-3 rounded">
          <strong>Single Day:</strong> Select a specific date and set your
          available hours for that day. Check "All Day" if you're available for
          the entire day.
        </div>
      </div>

      <!-- Date Range Selection -->
      <div v-if="selectionType === 'range'" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <DatePicker
            v-model="dateRange.startDate"
            variant="subtle"
            placeholder="Start Date"
            label="Start Date"
          />
          <DatePicker
            v-model="dateRange.endDate"
            variant="subtle"
            placeholder="End Date"
            label="End Date"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Daily Start Time</label
            >
            <Select v-model="dateRange.dailyStartTime" :options="timeOptions" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Daily End Time</label
            >
            <Select v-model="dateRange.dailyEndTime" :options="timeOptions" />
          </div>
        </div>

        <div class="text-sm text-gray-600 bg-gray-50 p-3 rounded">
          <strong>Date Range:</strong> Select a start and end date, then set the
          time slots that will apply to each day within this range. For example,
          if you select Jan 1-5 with 9:00 AM - 5:00 PM, you'll be available from
          9 AM to 5 PM every day from January 1st to 5th.
        </div>
      </div>

      <!-- Calendar View -->
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
          @click="validateAndSubmitSlot"
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
  DatePicker,
  ErrorMessage,
  Calendar,
  Select,
} from "frappe-ui";
import { computed, reactive, ref, watch } from "vue";
import { usersStore } from "../../stores/user";
import { generateTimeOptions } from "../../utils/timeUtils";

const { roleResource, presentSlots } = usersStore();
const setAvailability = ref(true);
const calendarView = ref(false);
const selectionType = ref("single");

const emit = defineEmits(["success"]);

const singleDay = reactive({
  date: "",
  allDay: false,
  startTime: "",
  endTime: "",
});

const dateRange = reactive({
  startDate: "",
  endDate: "",
  dailyStartTime: "",
  dailyEndTime: "",
});

const timeOptions = ref([...generateTimeOptions(30)]);

const availableEndTimes = computed(() => {
  if (!singleDay.startTime) return timeOptions.value;

  const startIndex = timeOptions.value.findIndex(
    (time) => time.value === singleDay.startTime
  );
  return timeOptions.value.slice(startIndex + 1);
});

const availableRangeEndTimes = computed(() => {
  if (!dateRange.dailyStartTime) return timeOptions.value;

  const startIndex = timeOptions.value.findIndex(
    (time) => time.value === dateRange.dailyStartTime
  );
  return timeOptions.value.slice(startIndex + 1);
});
const newSlot = createResource({
  url: "non_profit.non_profit.api.create_availability_slot",
  makeParams(values) {
    return { slot_data: { ...values } };
  },
  onSuccess() {
    presentSlots.fetch().then(() => {
      console.log("Refreshed slots:", presentSlots.data);

      calendarView.value = true;
    });
    resetForm();
    emit("success");
  },
});

function resetForm() {
  singleDay.date = "";
  singleDay.allDay = false;
  singleDay.startTime = "";
  singleDay.endTime = "";
  dateRange.startDate = "";
  dateRange.endDate = "";
  dateRange.dailyStartTime = "";
  dateRange.dailyEndTime = "";
  newSlot.error = "";
}

function validateAndSubmitSlot() {
  newSlot.error = "";

  if (selectionType.value === "single") {
    if (!singleDay.date) {
      newSlot.error = "Please select a date";
      return;
    }

    if (!singleDay.allDay && (!singleDay.startTime || !singleDay.endTime)) {
      newSlot.error = "Please select start and end times";
      return;
    }

    if (!singleDay.allDay && singleDay.startTime >= singleDay.endTime) {
      newSlot.error = "Start time must be before end time";
      return;
    }

    // Submit single day slot
    const slotData = {
      employee: roleResource.data.employee,
      company: roleResource.data.company,
      user: roleResource.data.name,
      starts_on: singleDay.allDay
        ? `${singleDay.date} 00:00:00`
        : `${singleDay.date} ${singleDay.startTime}:00`,
      ends_on: singleDay.allDay
        ? `${singleDay.date} 23:59:59`
        : `${singleDay.date} ${singleDay.endTime}:00`,
    };

    newSlot.submit(slotData);
  } else if (selectionType.value === "range") {
    if (!dateRange.startDate || !dateRange.endDate) {
      newSlot.error = "Please select both start and end dates";
      return;
    }

    if (!dateRange.dailyStartTime || !dateRange.dailyEndTime) {
      newSlot.error = "Please select daily start and end times";
      return;
    }

    if (dateRange.startDate > dateRange.endDate) {
      newSlot.error = "Start date must be before or equal to end date";
      return;
    }

    // Extract time for comparison
    if (dateRange.dailyStartTime >= dateRange.dailyEndTime) {
      newSlot.error = "Daily start time must be before daily end time";
      return;
    }

    const slotData = {
      employee: roleResource.data.employee,
      company: roleResource.data.company,
      user: roleResource.data.name,
      starts_on: `${dateRange.startDate} ${dateRange.dailyStartTime}:00`,
      ends_on: `${dateRange.endDate} ${dateRange.dailyEndTime}:00`,
      is_range: true, // You might want to add this flag to your API
      daily_start_time: dateRange.dailyStartTime,
      daily_end_time: dateRange.dailyEndTime,
    };

    newSlot.submit(slotData);
  }
}

watch(
  () => singleDay.allDay,
  (allDay) => {
    if (allDay) {
      singleDay.startTime = "";
      singleDay.endTime = "";
    }
  }
);

watch(
  () => singleDay.startTime,
  () => {
    if (singleDay.endTime && singleDay.startTime >= singleDay.endTime) {
      singleDay.endTime = "";
    }
  }
);

watch(
  () => dateRange.dailyStartTime,
  () => {
    if (
      dateRange.dailyEndTime &&
      dateRange.dailyStartTime >= dateRange.dailyEndTime
    ) {
      dateRange.dailyEndTime = "";
    }
  }
);

watch(setAvailability, (isOpen) => {
  if (!isOpen) {
    resetForm();
  }
});

watch(selectionType, () => {
  newSlot.error = "";
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
