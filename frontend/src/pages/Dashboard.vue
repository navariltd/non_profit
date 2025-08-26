<template>
  <Volunteer v-if="roleResource.data.volunteer" />

  <Member v-if="roleResource.data.non_profit_member" />

  <hr />
  <div class="flex flex-col gap-2 p-5">
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
  </div>
</template>
<script lang="ts" setup>
import EmptyState from "../components/EmptyState.vue";
import EventCard from "../components/EventCard.vue";
import Member from "../components/Member.vue";
import Volunteer from "../components/Volunteer.vue";
import { membershipStore } from "../stores/membership";
import { usersStore } from "../stores/user";
import { Button } from "frappe-ui";

const { roleResource } = usersStore();
const { events } = membershipStore();
</script>
