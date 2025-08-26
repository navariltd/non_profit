<template>
  <div class="p-5">
    <header><h1 class="text-3xl">Events</h1></header>
  </div>
  <div
    class="p-8 grid grid-cols-1 lg:grid-cols-3 gap-4"
    v-for="event in events.data"
  >
    <EventCard :event="event" />
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { createResource } from "frappe-ui";
import EventCard from "../components/EventCard.vue";
const events = createResource({
  url: "non_profit.non_profit.api.get_events",
  auto: true,
  cache: ["events"],
});
</script>
