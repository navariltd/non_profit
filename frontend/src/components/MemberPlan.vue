<template>
  <div class="flex flex-col gap-8 p-6 border">
    <!-- Volunteer Section -->
    <div
      v-if="
        membershipList.data &&
        membershipList.data.length > 0 &&
        roleResource.data &&
        !roleResource.data.is_volunteer
      "
      class="rounded-2xl border bg-red-50 p-8 text-center shadow-sm"
    >
      <h2 class="text-2xl font-bold text-gray-900 mb-4">
        Not a volunteer yet?
      </h2>
      <p class="text-gray-700 mb-6 max-w-2xl mx-auto">
        Join the Kenya Red Cross Society as a volunteer and play an active role
        in supporting your community. You'll help deliver life-saving services,
        gain valuable skills through training, and be part of a global
        humanitarian movement dedicated to making a difference.
      </p>
      <RouterLink :to="{ name: 'VolunteerSignup' }">
        <Button
          variant="solid"
          theme="red"
          icon-right="arrow-right"
          class="px-8 py-4 rounded-xl text-lg font-semibold shadow-md"
        >
          Register as Volunteer
        </Button>
      </RouterLink>
    </div>
    <!-- Membership Cards -->
    <h1
      v-if="membershipList.data && membershipList.data.length > 0"
      class="text-3xl font-bold text-gray-800"
    >
      Your Memberships
    </h1>
    <div
      v-if="membershipList.data && membershipList.data.length > 0"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <Card
        v-for="membership in membershipList.data"
        :key="membership.name"
        class="flex flex-col rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 group"
      >
        <!-- Header -->
        <div class="p-6 border-b bg-gray-50 flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-900">
            {{ membership.membership_type }}
          </h2>
          <Badge
            :variant="'subtle'"
            :theme="
              getMembershipStatusTheme(membership.membership_status || '')
            "
            size="lg"
            class="border text-sm"
          >
            {{ membership.membership_status }}
          </Badge>
        </div>

        <!-- Body -->
        <div class="p-6 flex flex-col gap-4 flex-1">
          <!-- Dates -->
          <div class="flex justify-between text-sm text-gray-600">
            <div>
              <span class="block text-gray-500">Start</span>
              <span class="font-medium text-gray-800">
                {{ formatDate(membership.from_date) }}
              </span>
            </div>
            <div>
              <span class="block text-gray-500">Renewal Due</span>
              <span class="font-medium text-gray-800">
                {{ formatDate(membership.to_date) }}
              </span>
            </div>
          </div>

          <!-- Branch + Amount -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <span class="block text-gray-500">Branch / County</span>
              <span class="font-medium text-gray-800">
                {{ membership.company }}
              </span>
            </div>
            <div>
              <span class="block text-gray-500">Amount</span>
              <span class="font-semibold text-gray-900 text-lg">
                KES {{ membership.amount }}
              </span>
            </div>
          </div>
        </div>

        <!-- CTA Footer -->
        <div class="bg-gray-50 p-4 border-t">
          <Button :variant="'solid'" theme="red" class="w-full">
            Renew Membership
          </Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Badge, Card, createResource } from "frappe-ui";
import Button from "frappe-ui/src/components/Button/Button.vue";
import { RouterLink } from "vue-router";
import { usersStore } from "../stores/user";

const { roleResource } = usersStore();

interface Membership {
  name?: string;
  membership_type?: string;
  from_date?: string;
  to_date?: string;
  membership_status?: string;
  amount?: number;
  company?: string;
  type_details?: Record<string, any>;
}

const membershipList = createResource<Membership[]>({
  url: "non_profit.non_profit.api.get_current_membership",
  auto: true,
  cache: ["currentMembership"],
});

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
    default:
      return "gray";
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
</script>
