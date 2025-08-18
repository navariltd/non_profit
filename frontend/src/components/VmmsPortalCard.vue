<template>
  <div
    class="bg-white rounded-lg border-2 border-gray-100 hover:border-red-300 p-6 transition-all duration-200 hover:shadow-md group"
  >
    <div class="flex items-center justify-between mb-4">
      <span
        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-red-800"
      >
        {{ membershipType.name }}
      </span>
      <div class="w-2 h-2 bg-green-400 rounded-full"></div>
    </div>

    <h3
      class="text-lg font-semibold text-gray-900 mb-2 group-hover:text-red-600 transition-colors"
    >
      {{ membershipType.membership_type }}
    </h3>

    <div class="flex items-baseline mb-4">
      <span class="text-2xl font-bold text-gray-900">
        KES {{ membershipType.amount }}</span
      >
      <span class="ml-1 text-sm text-gray-500">/year</span>
    </div>

    <div class="space-y-1 text-sm text-gray-600">
      <p>✓ Full membership access</p>
      <p>✓ All benefits included</p>
    </div>

    <div class="mt-2">
      <Badge> Signup </Badge>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Badge from "frappe-ui/src/components/Badge/Badge.vue";

interface MembershipType {
  name: string;
  membership_type: string;
  amount: number;
}

defineProps<{
  membershipType: MembershipType;
}>();
</script>
