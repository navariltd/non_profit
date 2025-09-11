<template>
  <div
    class="bg-white cursor-pointer rounded-xl border border-gray-200 hover:border-red-400 p-6 transition-all duration-200 hover:shadow-lg"
  >
    <!-- Badge + Status -->
    <div class="flex items-center justify-between mb-3">
      <span
        class="px-3 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700"
      >
        {{ membershipType.name }}
      </span>
    </div>

    <!-- Title -->
    <h3 class="text-lg font-semibold text-gray-900 mb-2">
      {{ membershipType.membership_type }}
    </h3>

    <!-- Price -->
    <div class="flex items-baseline mb-4">
      <span class="text-2xl font-bold text-gray-900">
        KES {{ membershipType.amount }}
      </span>
      <span class="ml-1 text-sm text-gray-500">/year</span>
    </div>

    <!-- Features -->
    <ul class="space-y-1 text-sm text-gray-600 mb-6">
      <li>✓ Full membership access</li>
      <li>✓ All benefits included</li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import { Badge } from "frappe-ui";

interface MembershipType {
  name: string;
  membership_type: string;
  amount: number;
}

defineProps<{
  membershipType: MembershipType;
}>();
</script>
