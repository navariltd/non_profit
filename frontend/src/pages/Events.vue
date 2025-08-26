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
import EventCard from "../components/EventCard.vue";
import { membershipStore } from "../stores/membership";

const { events } = membershipStore();
</script>
