<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Header Section -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">
          Membership Dashboard
        </h1>
        <p class="text-gray-600">
          Manage your membership and view your account details
        </p>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Membership Status Card - Takes up left column -->
        <div class="lg:col-span-1">
          <div
            class="bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center text-center border border-gray-100 h-fit"
          >
            <div
              class="w-16 h-16 flex items-center justify-center rounded-full bg-gradient-to-r from-green-400 to-green-600 shadow-md"
            >
              <span class="text-white text-2xl font-bold">M</span>
            </div>
            <div class="mt-4">
              <p class="text-gray-500 text-sm tracking-wide">
                Your Membership Status
              </p>
              <p
                class="text-3xl font-extrabold mt-2 transition"
                :class="{
                  'text-green-600': membershipStatus.status === 'Active',
                  'text-red-600': membershipStatus.status !== 'Active',
                }"
              >
                {{ membershipStatus.status }}
              </p>
              <p class="text-lg font-medium text-gray-700">
                {{ membershipStatus.level }} Tier
              </p>
              <p class="text-sm text-gray-500 mt-1">
                Next Renewal Due:
                <span class="font-semibold text-gray-800">{{
                  membershipStatus.dueDate
                }}</span>
              </p>
            </div>
            <Button class="mt-6 w-full rounded-xl" :variant="'solid'">
              Renew Membership
            </Button>
          </div>
        </div>

        <!-- Right Column - Events and Payment History -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Events Section -->
          <div
            class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
          >
            <div class="p-6 border-b border-gray-100">
              <h3 class="text-xl font-semibold text-gray-700">
                Upcoming Events
              </h3>
            </div>
            <div class="p-6">
              <Events />
            </div>
          </div>

          <!-- Payment History Section -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-100">
            <div class="p-6 border-b border-gray-100">
              <h3 class="text-xl font-semibold text-gray-700">
                Payment History
              </h3>
            </div>
            <div class="p-6">
              <ListView
                :columns="[
                  { label: 'Date', key: 'date' },
                  { label: 'Type', key: 'type' },
                  { label: 'Amount', key: 'amount' },
                ]"
                :rows="paymentHistory"
                row-key="date"
              >
              </ListView>
              <Button class="mt-4 rounded-xl" :variant="'solid'">
                View Full History
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { ListView } from "frappe-ui";
import Button from "frappe-ui/src/components/Button/Button.vue";
import { ref } from "vue";
import Events from "../pages/Events.vue";
// TODO: Replace with actual API calls or store data
const membershipStatus = ref({
  status: "Active",
  level: "Gold",
  dueDate: "Dec 31, 2025",
});
const paymentHistory = ref([
  {
    date: "Jan 15, 2025",
    type: { label: "Membership", color: "red" },
    amount: "Ksh. 5,000",
  },
  {
    date: "Nov 20, 2024",
    type: { label: "Donation", color: "green" },
    amount: "Ksh. 2,000",
  },
  {
    date: "Aug 10, 2024",
    type: { label: "Membership", color: "red" },
    amount: "Ksh. 5,000",
  },
]);
</script>
