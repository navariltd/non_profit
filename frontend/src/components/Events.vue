<template>
  <div class="bg-white rounded-lg shadow-sm p-8 border border-gray-200">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-medium text-gray-700">All Events</h3>
    </div>
    <div class="overflow-x-auto">
      <ListView
        :columns="eventColumns"
        :rows="events"
        row-key="name"
        :options="{
          onRowClick: showEventDetails,
        }"
      >
        <ListHeader>
          <ListHeaderItem
            v-for="column in eventColumns"
            :key="column.key"
            :item="column"
          >
            <template #prefix="{ item }">
              <FeatherIcon :name="item.icon" class="h-4 w-4" />
            </template>
          </ListHeaderItem>
        </ListHeader>
        <ListRows>
          <ListRow
            v-for="event in events"
            :key="event.name"
            :row="event"
            class="cursor-pointer hover:bg-gray-100 transition-colors"
          >
            <template #default="{ column, item }">
              <ListRowItem :item="item" :align="column.align">
                <template #default>
                  {{ item.label || item }}
                </template>
              </ListRowItem>
            </template>
          </ListRow>
        </ListRows>
      </ListView>
    </div>

    <Dialog
      v-model="showDetailsDialog"
      :options="{ title: selectedEvent ? selectedEvent.name : '', size: 'md' }"
    >
      <template #body-content>
        <div v-if="selectedEvent">
          <p class="text-sm font-medium text-gray-500 mb-2">
            Date: <span class="text-gray-900">{{ selectedEvent.date }}</span>
          </p>
          <p class="text-sm font-medium text-gray-500 mb-2">
            Location:
            <span class="text-gray-900">{{ selectedEvent.location }}</span>
          </p>
          <p class="text-sm font-medium text-gray-500 mb-4">Description:</p>
          <p class="text-gray-700">{{ selectedEvent.description }}</p>
          <div class="mt-4">
            <h4 class="text-sm font-medium text-gray-500 mb-2">
              Skills Required:
            </h4>
            <ul class="list-disc list-inside text-gray-700">
              <li v-for="skill in selectedEvent.skills" :key="skill">
                {{ skill }}
              </li>
            </ul>
          </div>
          <div class="mt-4 flex justify-end gap-2">
            <Button variant="solid" size="sm" color="blue" @click="attendEvent">
              Attend
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="showDetailsDialog = false"
              >Close</Button
            >
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import {
  ListView,
  Dialog,
  Button,
  ListHeader,
  ListHeaderItem,
  ListRows,
  ListRow,
  ListRowItem,
  FeatherIcon,
} from "frappe-ui";

const events = ref([
  {
    name: "Flood Relief Training",
    date: "Aug 25, 2025",
    location: "Community Center",
    description:
      "This training session will prepare volunteers for flood relief efforts. Topics will include first aid, shelter management, and community support strategies.",
    skills: ["First Aid", "Community Support", "Teamwork"],
  },
  {
    name: "Community Outreach",
    date: "Sep 10, 2025",
    location: "Town Hall",
    description:
      "Join us in reaching out to local residents to understand their needs and provide information on available resources. This event focuses on active listening and communication.",
    skills: ["Communication", "Active Listening", "Problem Solving"],
  },
  {
    name: "Tree Planting",
    date: "Sep 20, 2025",
    location: "City Park",
    description:
      "Help us reforest City Park by planting new trees. This is a great opportunity to contribute to environmental conservation and meet other like-minded volunteers.",
    skills: ["Physical Labor", "Teamwork", "Gardening"],
  },
  {
    name: "Youth Mentorship Program",
    date: "Oct 5, 2025",
    location: "Local High School",
    description:
      "Become a mentor to a high school student and guide them through their academic and personal development. This is a long-term commitment.",
    skills: ["Mentorship", "Leadership", "Communication", "Patience"],
  },
]);

const eventColumns = ref([
  { label: "Event Name", key: "name", width: 3, icon: "calendar" },
  { label: "Date", key: "date", width: 2, icon: "clock" },
  { label: "Location", key: "location", width: 2, icon: "map-pin" },
]);

const showDetailsDialog = ref(false);
type Event = {
  name: string;
  date: string;
  location: string;
  description: string;
  skills: string[];
};

const selectedEvent = ref<Event | null>(null);

const showEventDetails = (row) => {
  selectedEvent.value = row;
  showDetailsDialog.value = true;
};

// New function to handle the "Attend" button click
const attendEvent = () => {
  if (selectedEvent.value) {
    console.log(`Attending event: ${selectedEvent.value.name}`);
    // You can add more logic here, such as:
    // - Sending a request to your backend API to register the user for the event.
    // - Showing a success message to the user.
    // - Updating a status property on the event object.
    showDetailsDialog.value = false;
  }
};
</script>
