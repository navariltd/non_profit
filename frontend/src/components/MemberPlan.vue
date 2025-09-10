<template>
  <div class="flex flex-col md:flex-row gap-4 p-15">
    <div
      v-if="membershipStatus"
      class="flex flex-col bg-white border border-gray-200 rounded-xl p-6 h-full shadow-sm hover:shadow-md hover:border-gray-300 transition-all duration-200"
    >
      <div class="mb-4">
        <h2 class="text-xl font-semibold text-gray-900 leading-tight">
          Current Membership Plan
        </h2>
      </div>

      <div class="mb-4">
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-1">
            {{ membershipStatus.membership_type }}
          </h3>

          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">Status:</span>
            <Badge
              :variant="'subtle'"
              :ref_for="true"
              :theme="
                getMembershipStatusTheme(
                  membershipStatus.membership_status
                    ? membershipStatus.membership_status
                    : ''
                )
              "
              size="lg"
              label="Badge"
              class="border"
            >
              {{ membershipStatus.membership_status }}
            </Badge>
          </div>
        </div>
      </div>

      <div
        class="grid grid-cols-1 sm:grid-cols-2 gap-y-3 gap-x-4 text-sm text-gray-600 mb-4"
      >
        <div class="flex flex-col">
          <span class="text-gray-500">Start Date</span>
          <span class="font-medium text-gray-800">{{
            membershipStatus.from_date
          }}</span>
        </div>
        <div class="flex flex-col">
          <span class="text-gray-500">Renewal Due</span>
          <span class="font-medium text-gray-800">{{
            membershipStatus.to_date
          }}</span>
        </div>
        <div class="flex flex-col sm:col-span-2">
          <span class="text-gray-500">Amount</span>
          <span class="font-semibold text-gray-900 text-lg">{{
            membershipStatus.amount
          }}</span>
        </div>
      </div>

      <!-- Action Button -->
      <div class="mt-auto">
        <Button :variant="'solid'" class="w-full"> Renew Membership </Button>
      </div>
    </div>

    <router-link
      v-if="!membershipStatus"
      :to="{ name: 'Membership' }"
      class="w-full md:w-1/3"
    >
      <div
        class="flex flex-col bg-white border border-gray-200 rounded-xl p-6 h-full shadow-sm"
      >
        <div class="text-center text-gray-500">
          <h3 class="text-lg font-medium text-gray-900 mb-2">
            No Active Membership
          </h3>
          <p class="text-sm">Click to Subscribe to a membership plan to get started.</p>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script lang="ts" setup>
import { Badge } from "frappe-ui";
import Button from "frappe-ui/src/components/Button/Button.vue";
import { RouterLink } from "vue-router";

interface Props {
  name?: string;
  membership_type?: string;
  from_date?: string;
  to_date?: string;
  membership_status?: string;
  amount?: number;
}

defineProps<{ membershipStatus: Props }>();

function getMembershipStatusTheme(status: string) {
  switch (status) {
    case "Current":
      return "green";
    case "Expired":
      return "red";
    case "Pending":
      return "orange";
    case "Cancelled":
      return "gray";
  }
}
</script>
