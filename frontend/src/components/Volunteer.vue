<template>
  <div
    class="min-h-screen bg-white rounded-lg shadow-sm p-8 border border-gray-200"
  >
    <div class="flex justify-center mb-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl">
        <div
          class="rounded-lg p-6 text-center border border-gray-200 min-w-32 bg-gradient-to-br from-gray-100 to-blue-50"
        >
          <h3 class="text-3xl font-bold text-gray-900">
            {{ volunteerStats.hours }}
          </h3>
          <p class=" text-gray-500 mt-2">Total Hours</p>
        </div>
        <div
          class="rounded-lg p-6 text-center border border-gray-200 min-w-32 bg-gradient-to-br from-gray-100 to-green-50"
        >
          <h3 class="text-3xl font-bold text-gray-700">
            {{ volunteerStats.events }}
          </h3>
          <p class=" text-gray-500 mt-2">Events Attended</p>
        </div>
        <div
          class="rounded-lg p-6 text-center border border-gray-200 min-w-32 bg-gradient-to-br from-gray-100 to-yellow-50"
        >
          <h3 class="text-3xl font-bold text-gray-700">
            {{ volunteerStats.badges }}
          </h3>
          <p class=" text-gray-500 mt-2">Badges Earned</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-8 max-w-6xl mx-auto">
      <div>
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-medium text-gray-700">Upcoming Events</h3>
          <Button @click="showEventsDialog = true" variant="solid" size="sm">
            View All Events
          </Button>
        </div>
        <div class="space-y-3">
          <div
            v-for="event in upcomingEvents"
            :key="event.name"
            class="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div>
              <p class="font-medium text-gray-800">{{ event.name }}</p>
              <p class=" text-gray-500">{{ event.date }}</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-medium text-gray-700">
            Recommended Opportunities
          </h3>
          <Button
            @click="showOpportunitiesDialog = true"
            variant="solid"
            size="sm"
          >
            View All Opportunities
          </Button>
        </div>
        <div class="space-y-3">
          <div
            v-for="opportunity in recommendedOpportunities"
            :key="opportunity.name"
            class="p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <p class="font-medium text-gray-800">{{ opportunity.name }}</p>
            <p class=" text-gray-500">
              Skills: {{ opportunity.skills }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <Dialog
      v-model="showEventsDialog"
      :options="{ title: 'All Events', size: '4xl' }"
    >
      <template #body-content>
        <ListView
          :columns="eventColumns"
          :rows="allEvents"
          row-key="name"
          class="h-64"
        />
      </template>
    </Dialog>

    <Dialog
      v-model="showOpportunitiesDialog"
      :options="{ title: 'All Opportunities', size: '4xl' }"
    >
      <template #body-content>
        <ListView
          :columns="opportunityColumns"
          :rows="allOpportunities"
          row-key="name"
          class="h-64"
        />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { ListView, Dialog, Button } from "frappe-ui";

const volunteerStats = ref({
  hours: 125,
  events: 8,
  badges: 3,
});

const upcomingEvents = ref([
  { name: "Flood Relief Training", date: "Aug 25, 2025" },
  { name: "Community Outreach", date: "Sep 10, 2025" },
]);

const recommendedOpportunities = ref([
  { name: "First Aid Support", skills: "Medical, First Aid" },
  { name: "Social Media Management", skills: "Communications, Digital" },
]);

const allEvents = ref([
  {
    name: "Flood Relief Training",
    date: "Aug 25, 2025",
    location: "Community Center",
  },
  { name: "Community Outreach", date: "Sep 10, 2025", location: "Town Hall" },
  { name: "Tree Planting", date: "Sep 20, 2025", location: "City Park" },
]);

const allOpportunities = ref([
  {
    name: "First Aid Support",
    skills: "Medical, First Aid",
    organization: "Red Cross",
  },
  {
    name: "Social Media Management",
    skills: "Communications, Digital",
    organization: "NGO Connect",
  },
  {
    name: "Youth Mentorship",
    skills: "Teaching, Leadership",
    organization: "Future Leaders",
  },
]);

const eventColumns = ref([
  { label: "Event", key: "name" },
  { label: "Date", key: "date" },
  { label: "Location", key: "location" },
]);

const opportunityColumns = ref([
  { label: "Opportunity", key: "name" },
  { label: "Skills", key: "skills" },
  { label: "Organization", key: "organization" },
]);

const showEventsDialog = ref(false);
const showOpportunitiesDialog = ref(false);
</script>
