<template v-if="user.data">
  <div class="flex flex-col items- justify-center h-screen w-screen p-6">
    <Welcome
      v-if="
        roleResource.data &&
        !roleResource.data.employee &&
        !roleResource.data.non_profit_member
      "
      :name="user.data.full_name"
    />
    <Volunteer v-if="roleResource.data && roleResource.data.employee" />

    <Member
      :membership-status="currentMembership.data"
      v-if="roleResource.data && roleResource.data.non_profit_member"
    />
  </div>

  <hr />
  <!-- <div class="flex flex-col gap-2 p-5">
    <h1 class="text-xl m-2">Upcoming Events</h1>

    <div
      v-if="events.data && events.data.length > 0"
      v-for="event in events.data.filter((e) => e.status === 'Open')"
      class="p-8 grid grid-cols-1 lg:grid-cols-3 gap-4"
    >
      <EventCard :event="event" />
    </div>

    <EmptyState
      v-if="events.data && events.data.length === 0"
      :type="'Events'"
    />
    <router-link :to="{ name: 'Events' }">
      <Button variant="subtle" size="lg" theme="green">
        View All Events
      </Button>
    </router-link>
  </div> -->
</template>
<script lang="ts" setup>
import { inject, onMounted } from "vue";
import EmptyState from "../components/EmptyState.vue";
import EventCard from "../components/EventCard.vue";
import Member from "../components/Member.vue";
import Volunteer from "../components/Volunteer.vue";
import { membershipStore } from "../stores/membership";
import { usersStore } from "../stores/user";
import { Button, createResource, toast } from "frappe-ui";
import Welcome from "../components/Welcome.vue";

const { roleResource } = usersStore();
const { events, currentMembership } = membershipStore();

const user = inject<any>("$user");

onMounted(() => {
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
</script>
