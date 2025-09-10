<template v-if="user.data">
  <div class="flex flex-col">
    <Welcome
      v-if="
        roleResource.data &&
        !roleResource.data.is_volunteer &&
        !roleResource.data.non_profit_member
      "
      :name="user.data.full_name"
    />

    <Volunteer v-if="roleResource.data && roleResource.data.is_volunteer" />

    <Member
      :membership-status="currentMembership.data"
      v-if="roleResource.data && roleResource.data.non_profit_member"
    />
  </div>

  <hr />
  <div
    class="flex flex-col gap-2 md:p-8 md:w-3/4 mx-auto"
    v-if="
      (roleResource.data && roleResource.data.is_volunteer) ||
      (roleResource.data && roleResource.data.non_profit_member)
    "
  >
    <div class="flex justify-between items-center m-2">
      <h1 class="text-xl m-2">Upcoming Events</h1>
      <router-link :to="{ name: 'Events' }">
        <Button variant="subtle" size="lg" theme="blue">
          View All Events
        </Button></router-link
      >
    </div>

    <div
      v-if="events.data && events.data.length > 0"
      class="p-2 grid grid-cols-1 lg:grid-cols-3 gap-4"
    >
      <EventCard v-for="event in events.data.slice(0, 3)" :event="event" />
    </div>

    <EmptyState
      v-if="events.data && events.data.length === 0"
      :type="'Events'"
    />
  </div>
</template>
<script lang="ts" setup>
import { inject, onMounted, provide, toRaw, watch } from "vue";
import EmptyState from "../components/EmptyState.vue";
import EventCard, { Event } from "../components/EventCard.vue";
import Member from "../components/MemberPlan.vue";
import Volunteer from "../components/Volunteer.vue";
import { membershipStore } from "../stores/membership";
import { usersStore } from "../stores/user";
import { Button, createResource, toast } from "frappe-ui";
import Welcome from "../components/Welcome.vue";

const { roleResource } = usersStore();
const { events, currentMembership } = membershipStore();

const user = inject<any>("$user");

onMounted(() => {
  confirmEventStatus.data;
  const { roleResource } = usersStore();

  if (!user.data) {
    toast.warning("You must be logged in to view this page.");
    setTimeout(() => {
      window.location.href = `account/login?redirect-to=${window.location.pathname}`;
    }, 500);
  } else {
    roleResource.reload();
  }
});

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

provide("reloadConfirmStatus", () => confirmEventStatus.reload());
</script>
