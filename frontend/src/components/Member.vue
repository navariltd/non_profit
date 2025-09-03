<template>
  <div class="flex flex-col md:flex-row gap-4 p-5">
    <div></div>
    <div
      class="m-auto w-1/4 bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center text-center border border-gray-100 h-fit"
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
        <p class="text-lg font-medium">{{ membershipStatus.level }} Tier</p>
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
</template>

<script lang="ts" setup>
import { ListView } from "frappe-ui";
import Button from "frappe-ui/src/components/Button/Button.vue";
import { ref } from "vue";

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
