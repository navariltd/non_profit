<template>
  <div class="flex flex-col md:flex-row gap-4 p-5">
    <div
      v-if="membershipStatus"
      class="m-auto bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center text-center border border-gray-100 h-fit"
    >
      <div class="mb-4">
        <span class="text-2xl font-bold text-green-600"
          >Current Membership Plan</span
        >
      </div>
      <div class="w-full bg-gray-50 rounded-xl p-4 mb-4">
        <p class="text-lg font-semibold text-gray-800">
          {{ membershipStatus.membership_type }}
        </p>
        <p class="text-sm text-gray-500 mt-1">
          Status:
          <span
            :class="{
              'text-green-600 font-bold':
                membershipStatus.membership_status === 'Active',
              'text-red-600 font-bold':
                membershipStatus.membership_status !== 'Active',
            }"
          >
            {{ membershipStatus.membership_status }}
          </span>
        </p>
        <p class="text-sm text-gray-500 mt-1">
          Start Date:
          <span class="font-semibold text-gray-800">{{
            membershipStatus.from_date
          }}</span>
        </p>
        <p class="text-sm text-gray-500 mt-1">
          Renewal Due:
          <span class="font-semibold text-gray-800">{{
            membershipStatus.to_date
          }}</span>
        </p>
        <p class="text-sm text-gray-500 mt-1">
          Renewal Due:
          <span class="font-semibold text-gray-800">{{
            membershipStatus.to_date
          }}</span>
        </p>
        <p class="text-sm text-gray-500 mt-1">
          Amount:
          <span class="font-semibold text-gray-800">{{
            membershipStatus.amount
          }}</span>
        </p>
      </div>
      <Button class="mt-4 w-full rounded-xl" :variant="'solid'">
        Renew Membership
      </Button>
    </div>

    <div v-if="!membershipStatus"></div>
  </div>
</template>

<script lang="ts" setup>
import Button from "frappe-ui/src/components/Button/Button.vue";

interface Props {
  name?: string;
  membership_type?: string;
  from_date?: string;
  to_date?: string;
  membership_status?: string;
  amount?: number;
}

defineProps<{ membershipStatus: Props }>();
</script>
