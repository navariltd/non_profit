<template>
  <div class="p-5">
    <header class="flex justify-between items-center mt-5">
      <h1 class="text-3xl">Events</h1>
      <Button variant="solid" theme="red" @click="toggleEventViews">
        {{ toggleEventView ? "List" : "Calendar" }} View</Button
      >
    </header>
  </div>
  <div class="p-8 grid grid-cols-1 lg:grid-cols-3 gap-4">
    <EventCard
      v-if="!toggleEventView"
      v-for="event in events.data"
      :event="event"
    />
  </div>
  <div class="px-8">
    <EventCalendar v-if="toggleEventView" :event="events.data" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, provide, ref } from "vue";
import EventCard from "../components/EventCard.vue";
import { membershipStore } from "../stores/membership";
import { Button, createResource } from "frappe-ui";

const { events } = membershipStore();
const toggleEventView = ref(false);

onMounted(() => {
  confirmEventStatus.data;
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

function toggleEventViews() {
  toggleEventView.value = !toggleEventView.value;
}

provide("reloadConfirmStatus", () => confirmEventStatus.reload());
</script>
