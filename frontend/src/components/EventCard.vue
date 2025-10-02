<template>
  <div class="bg-gray-50 py-2 px-4">
    <div class="max-w-3xl mx-auto space-y-2">
      <!-- Event Item -->
      <div
        class="flex flex-col md:flex-row items-stretch rounded-lg shadow-sm overflow-hidden bg-white cursor-pointer"
      >
        <!-- Date Badge -->
        <div
          class="flex flex-col items-center justify-center bg-red-50 px-6 py-4 border-b md:border-b-0 md:border-r border-gray-100 w-full md:w-40"
        >
          <div class="text-3xl font-bold text-red-600">
            {{ new Date(event.start_date).getDate() }}
          </div>
          <div class="text-sm text-gray-500">
            {{
              new Date(event.start_date).toLocaleString("default", {
                month: "short",
                year: "numeric",
              })
            }}
          </div>
          <img :src="event.banner_image" alt="" class="mt-1 rounded-md p-1" />
        </div>

        <!-- Event Details -->
        <div class="flex-1 p-5">
          <div
            class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-3 gap-2"
          >
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 mb-1">
                {{ event.title }}
              </h3>
              <p class="text-sm text-gray-600 mb-2 line-clamp-2">
                {{ event.short_description }}
              </p>
              <div class="flex items-center text-sm text-gray-500 mb-2">
                <MapPin class="w-4 h-4 mr-1.5 flex-shrink-0" />
                <span class="truncate">{{ event.venue }}</span>
              </div>
            </div>
            <span
              v-if="event.confirmStatus"
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
            >
              Confirmed
            </span>
          </div>

          <!-- Time + Date -->
          <div
            class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
          >
            <div
              class="flex flex-wrap items-center gap-4 text-sm text-gray-600"
            >
              <div class="flex items-center">
                <Clock class="w-4 h-4 mr-1.5 text-red-500" />
                <span>{{ event.start_time }}</span>
              </div>
              <div class="flex items-center">
                <Calendar class="w-4 h-4 mr-1.5 text-red-500" />
                <span>{{ event.start_date }}</span>
              </div>
            </div>

            <button
              @click="attendModal = true"
              class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors duration-200 w-full sm:w-auto"
            >
              <ChevronRight class="w-4 h-4 ml-1.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Badge, Button, toast } from "frappe-ui";
import { Calendar, Clock, MapPin, ChevronRight } from "lucide-vue-next";
import { inject, onMounted, ref } from "vue";
import { membershipStore } from "../stores/membership";
import AttendEventModal from "./Modals/AttendEventModal.vue";

const attendModal = ref(false);
const { events } = membershipStore();
const reloadConfirmStatus = inject<() => void>("reloadConfirmStatus");

onMounted(() => {});

defineProps<{
  event;
}>();

function handleConfirmed() {
  if (reloadConfirmStatus) {
    reloadConfirmStatus();
  }
  toast.success("You successfully registered for the event");
}
</script>
