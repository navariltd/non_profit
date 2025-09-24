<template>
  <div v-if="user.data">
    <div class="flex flex-col">
      <h1 class="text-3xl font-bold px-4 mt-5">
        Welcome, {{ user.data.full_name }}
      </h1>

      <!-- Role-based views -->
      <div v-if="roleResource.data">
        <Welcome
          v-if="!roleResource.data.is_volunteer && !roleResource.data.is_member"
        />

        <Volunteer
          v-else-if="roleResource.data.is_volunteer"
          v-bind="dashboardStats.data"
        />

        <Member
          :membership-status="currentMembership.data"
          v-else-if="roleResource.data.is_member"
        />
      </div>
    </div>

    <div
      class="flex flex-col gap-2 md:p-8 md:w-3/4 mx-auto"
      v-if="
        roleResource.data &&
        (roleResource.data.is_volunteer || roleResource.data.is_member)
      "
    >
      <div class="flex items-center justify-between m-2 p-2">
        <h1 class="text-xl font-semibold text-gray-900">Upcoming Events</h1>

        <div class="flex justify-center flex-1">
          <Button variant="solid" theme="red" @click="toggleEventViews">
            {{ toggleEventView ? "List" : "Calendar" }} View
          </Button>
        </div>

        <router-link :to="{ name: 'Events' }">
          <Button
            variant="subtle"
            size="lg"
            theme="red"
            icon-right="arrow-right"
          >
            View All Events
          </Button>
        </router-link>
      </div>

      <div
        v-if="events.data && events.data.length > 0"
        class="p-2 grid grid-cols-1 lg:grid-cols-3 gap-4"
      >
        <EventCard
          v-if="!toggleEventView"
          v-for="event in events.data.slice(0, 3)"
          :key="event.name"
          :event="event"
        />
      </div>

      <EventCalendar v-if="toggleEventView" :event="events.data" />

      <EmptyState
        v-if="events.data && events.data.length === 0"
        :type="'Events'"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { inject, onMounted, provide, ref, watch } from "vue";
import EmptyState from "../components/EmptyState.vue";
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

const { roleResource } = usersStore();
const { events, currentMembership } = membershipStore();
const toggleEventView = ref(false);

const user = inject<any>("$user");
let { isLoggedIn } = sessionStore();

onMounted(() => {
  if (!isLoggedIn) {
    toast.warning("You must be logged in to view this page.");
    setTimeout(() => {
      router.push({ name: "Login" });
    }, 500);
  } else {
    roleResource.reload();
    currentMembership.reload();
  }
});

watch(
  () => roleResource.data,
  (val) => {},
  { immediate: true }
);

const confirmEventStatus = createResource({
  url: "non_profit.non_profit.api.confirm_event_status",
  auto: true,
  onSuccess(data) {
    if (events.data) {
      events.data = events.data.map((e) => {
        const match = data.find((d: any) => d.event.name === e.name);
        return {
          ...e,
          confirmStatus: match ? match.confirmed : false,
        };
      });
    }
  },
});

function toggleEventViews() {
  toggleEventView.value = !toggleEventView.value;
}

const dashboardStats = createResource({
  url: "non_profit.non_profit.api.get_dashboard_stats",
  auto: true,
});
provide("reloadConfirmStatus", () => confirmEventStatus.reload());
</script>
