<template>
  <div v-if="!user?.data" class="text-center py-20">
    <LogIn class="w-16 h-16 text-gray-400 mx-auto mb-4" />
    <h2 class="text-3xl font-bold text-gray-900 mb-4">
      Authentication Required
    </h2>

    <Button
      variant="solid"
      class="bg-red-600 hover:bg-red-700 text-white"
      @click="redirectToLogin"
    >
      <template #prefix>
        <LogIn class="w-4 h-4" />
      </template>
      {{ "Login to View Dashboard" }}
    </Button>
  </div>
<div v-else class="max-w-7xl mx-auto">
    <div class="flex flex-col">
      <h1 class="text-3xl font-bold px-4 mt-5">
        Welcome, {{ user?.data?.full_name }}
      </h1>

      <div v-if="roleResource?.data">
        <Welcome
          v-if="
            !roleResource?.data?.is_volunteer && !roleResource?.data?.is_member
          "
        />

        <Volunteer
          v-else-if="roleResource?.data?.is_volunteer"
          v-bind="dashboardStats?.data"
        />

        <Member
          :membership-status="currentMembership?.data"
          v-else-if="roleResource?.data?.is_member"
        />
      </div>
    </div>

    <div
      class="flex flex-col gap-2 md:p-8 mx-auto"
      v-if="
        roleResource?.data &&
        (roleResource?.data?.is_volunteer || roleResource?.data?.is_member)
      "
    >
      <div class="flex items-center justify-between m-2 p-2">
        <h1 class="text-xl font-semibold text-gray-900">Upcoming Events</h1>

        <div class="flex justify-center flex-1">
          <Button variant="solid" theme="red" @click="toggleEventViews">
            {{ toggleEventView ? "List" : "Calendar" }} View
          </Button>
        </div>
      </div>

      <div
        v-if="events?.data && events?.data.length > 0 && !toggleEventView"
        class="p-2 grid grid-cols-1 lg:grid-cols-3 gap-4"
      >
        <EventCard
          v-for="event in events?.data.slice(0, 3)"
          :key="event.name"
          :event="event"
        />
      </div>

      <EventCalendar v-if="toggleEventView" :event="events?.data" />

      <EmptyState
        v-if="events?.data && events?.data.length === 0"
        type="Events"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { provide, ref, watch } from "vue";
import EmptyState from "../components/EmptyState.vue";
import { LogIn } from "lucide-vue-next";
import EventCard from "../components/EventCard.vue";
import Member from "../components/MemberPlan.vue";
import Volunteer from "../components/Volunteer.vue";
import { membershipStore } from "../stores/membership";
import { usersStore } from "../stores/user";
import { Button, createResource, toast } from "frappe-ui";
import Welcome from "../components/Welcome.vue";
import EventCalendar from "../components/EventCalendar.vue";
import router from "../router";
import { sessionStore } from "../stores/session";

const { roleResource, userResource } = usersStore();
const { events, currentMembership } = membershipStore();
const { isLoggedIn } = sessionStore();

const toggleEventView = ref(false);

const user = userResource;

import { onMounted } from "vue";

onMounted(() => {
  if (isLoggedIn) {
    roleResource.reload();
    currentMembership.reload();
    events.reload();
  }
});

function redirectToLogin() {
  router.push("/login");
}

const confirmEventStatus = createResource({
  url: "non_profit.non_profit.api.confirm_event_status",
  auto: true,
  onSuccess(data: any) {
    if (events?.data) {
      events.data = events.data.map((e: any) => {
        const match = data.find((d: any) => d.event.name === e.name);
        return {
          ...e,
          confirmStatus: match ? match.confirmed : false,
        };
      });
    }
  },
});

const dashboardStats = createResource({
  url: "non_profit.non_profit.api.get_dashboard_stats",
  auto: true,
});

function toggleEventViews() {
  toggleEventView.value = !toggleEventView.value;
}

provide("reloadConfirmStatus", () => confirmEventStatus.reload());
</script>
