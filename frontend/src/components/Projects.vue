<template>
  <div class="bg-white rounded-lg shadow-sm p-8 border border-gray-200">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-medium text-gray-700">All Projects</h3>
    </div>
    <div class="overflow-x-auto">
      <ListView
        :columns="projectColumns"
        :rows="projects"
        row-key="name"
        :options="{
          onRowClick: showProjectDetails,
        }"
      >
        <ListHeader>
          <ListHeaderItem
            v-for="column in projectColumns"
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
            v-for="project in projects"
            :key="project.name"
            :row="project"
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
      :options="{
        title: selectedProject ? selectedProject.name : '',
        size: 'md',
      }"
    >
      <template #body-content>
        <div v-if="selectedProject">
          <p class="text-sm font-medium text-gray-500 mb-2">
            Status:
            <span class="text-gray-900">{{ selectedProject.status }}</span>
          </p>
          <p class="text-sm font-medium text-gray-500 mb-2">
            Project Manager:
            <span class="text-gray-900">{{ selectedProject.manager }}</span>
          </p>
          <p class="text-sm font-medium text-gray-500 mb-4">Description:</p>
          <p class="text-gray-700">{{ selectedProject.description }}</p>
          <div class="mt-4">
            <h4 class="text-sm font-medium text-gray-500 mb-2">
              Skills Required:
            </h4>
            <ul class="list-disc list-inside text-gray-700">
              <li v-for="skill in selectedProject.skills" :key="skill">
                {{ skill }}
              </li>
            </ul>
          </div>
          <div class="mt-4 flex justify-end gap-2">
            <Button
              variant="solid"
              size="sm"
              color="blue"
              @click="applyForProject"
            >
              Apply
            </Button>
            <Button variant="solid" size="sm" @click="showDetailsDialog = false"
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

const projects = ref([
  {
    name: "Youth Skills Development",
    status: "Active",
    manager: "Jane Doe",
    description:
      "A project to provide vocational training and mentorship to young adults in underserved communities. Volunteers will help with curriculum development and one-on-one mentorship.",
    skills: ["Mentorship", "Training", "Curriculum Design", "Communication"],
  },
  {
    name: "Community Garden",
    status: "Pending",
    manager: "John Smith",
    description:
      "Help build and maintain a community garden to promote sustainable living and provide fresh produce to local food banks. This project requires physical labor and knowledge of gardening.",
    skills: ["Gardening", "Physical Labor", "Project Management", "Teamwork"],
  },
  {
    name: "Tech for Good",
    status: "Active",
    manager: "Emily White",
    description:
      "A technology initiative to build simple websites and apps for local non-profit organizations. Looking for software developers and designers to contribute their skills.",
    skills: [
      "Software Development",
      "Web Design",
      "Project Management",
      "UI/UX Design",
    ],
  },
  {
    name: "Environmental Cleanup",
    status: "Closed",
    manager: "Michael Brown",
    description:
      "Organize and lead local cleanup events in parks and public spaces. This is a one-time project focused on environmental conservation.",
    skills: ["Team Leadership", "Environmental Science", "Event Planning"],
  },
]);

const projectColumns = ref([
  { label: "Project Name", key: "name", width: 3, icon: "package" },
  { label: "Status", key: "status", width: 2, icon: "activity" },
  { label: "Manager", key: "manager", width: 2, icon: "user" },
]);

const showDetailsDialog = ref(false);
type Project = {
  name: string;
  status: string;
  manager: string;
  description: string;
  skills: string[];
};

const selectedProject = ref<Project | null>(null);

const showProjectDetails = (row) => {
  selectedProject.value = row;
  showDetailsDialog.value = true;
};

const applyForProject = () => {
  if (selectedProject.value) {
    console.log(`Applying for project: ${selectedProject.value.name}`);
    // Add logic here to handle the application, e.g., an API call.
    showDetailsDialog.value = false;
  }
};
</script>
