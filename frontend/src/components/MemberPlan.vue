<template>
  <div class="flex flex-col md:flex-row gap-6 p-6 border">
    <!-- Current Membership Card -->
    <Card
      v-if="membershipStatus"
      class="flex flex-col -1/4 rounded-2xl p-6 h-full shadow-sm hover:shadow-md transition-all duration-300 group"
    >
      <!-- Header -->
      <div class="mb-4">
        <h2
          class="text-xl font-semibold text-gray-900 group-hover:text-red-600 transition-colors"
        >
          Current Membership Plan
        </h2>
      </div>

      <!-- Membership Info -->
      <div class="mb-4">
        <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">
            {{ membershipStatus.membership_type }}
          </h3>

          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">Status:</span>
            <Badge
              :variant="'subtle'"
              :theme="
                getMembershipStatusTheme(
                  membershipStatus.membership_status || ''
                )
              "
              size="lg"
              class="border border-red-200 text-red-700 bg-red-50"
            >
              {{ membershipStatus.membership_status }}
            </Badge>
          </div>
        </div>
      </div>

      <!-- Details -->
      <div
        class="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-6 text-sm text-gray-600 mb-6"
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
          <span class="font-semibold text-gray-900 text-lg">
            KES {{ membershipStatus.amount }}
          </span>
        </div>
      </div>

      <!-- Action Button -->
      <div class="mt-auto">
        <Button :variant="'solid'" theme="red" class="w-full">
          Renew Membership
        </Button>
      </div>
    </Card>

    
  </div>
</template>

<script lang="ts" setup>
import { Badge, Card } from "frappe-ui";
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
