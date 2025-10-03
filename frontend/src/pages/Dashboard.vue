<template>
  <div
    v-if="user?.data == 'Guest'"
    class="flex flex-col items-center justify-center py-20 h-[75vh] bg-gray-50 m-8 md:m-16 text-center px-4"
  >
    <div class="bg-red-100 rounded-full p-6 mb-6 shadow-md">
      <LogIn class="w-12 h-12 text-red-600" />
    </div>

    <h2 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4">
      🔒 Authentication Required
    </h2>

    <p class="text-gray-600 mb-8 max-w-md">
      Please log in to access your personalized dashboard and continue exploring
      our features.
    </p>

    <div
      variant="solid"
      class="bg-red-600 hover:bg-red-700 text-white px-8 py-3 flex items-center gap-3 rounded-xl shadow-lg cursor-pointer"
      @click="redirectToLogin"
    >
      <LogIn class="w-5 h-5" />
      Login
    </div>
  </div>
  <div v-if="user?.data && user?.data !== 'Guest'" class="max-w-7xl mx-auto">
    <div class="flex flex-col gap-2 mb-6">
      <h1 class="text-3xl md:text-4xl font-bold text-gray-900">
        👋 Welcome back, {{ user?.data?.full_name }}!
      </h1>
    </div>

    <div v-if="roleResource?.loading" class="text-center py-20">
      <p>Setting Up Dashboard...</p>
      <ProgressSpinner />
    </div>

    <div v-else-if="roleResource?.data">
      <Welcome
        v-if="
          !roleResource?.data?.is_volunteer && !roleResource?.data?.is_member
        "
      />
      <div v-if="roleResource?.data" class="mb-8 h-full">
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

      <section
        v-if="
          roleResource?.data &&
          (roleResource?.data?.is_volunteer || roleResource?.data?.is_member)
        "
        class="flex flex-col gap-4 md:p-6 bg-white shadow"
      >
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-semibold text-gray-900">
            Upcoming Events
          </h2>
          <router-link to="/events">
            <button
              class="inline-flex items-center gap-1 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
            >
              View All
              <ChevronRight class="w-4 h-4" />
            </button>
          </router-link>
        </div>

        <div
          v-if="events?.data && events?.data.length > 0 && !toggleEventView"
          class="grid md:grid-cols-3 gap-4"
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
      </section>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, provide, onMounted } from "vue";
import { LogIn, ChevronRight } from "lucide-vue-next";
import { Button, createResource } from "frappe-ui";

import EventCard from "../components/EventCard.vue";
import EventCalendar from "../components/EventCalendar.vue";
import Member from "../components/MemberPlan.vue";
import Volunteer from "../components/Volunteer.vue";
import Welcome from "../components/Welcome.vue";
import EmptyState from "../components/EmptyState.vue";

import router from "../router";
import { usersStore } from "../stores/user";
import { membershipStore } from "../stores/membership";
import { sessionStore } from "../stores/session";

const { roleResource, userResource } = usersStore();
const { events, currentMembership } = membershipStore();
const { isLoggedIn } = sessionStore();

const toggleEventView = ref(false);
const user = userResource;

import ProgressSpinner from "../components/Common/ProgressSpinner.vue";

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

provide("reloadConfirmStatus", () => confirmEventStatus.reload());

function toggleEventViews() {
  toggleEventView.value = !toggleEventView.value;
}
</script>

<style scoped>
.max-h-screen::-webkit-scrollbar {
  width: 8px;
}
.max-h-screen::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}
</style>
