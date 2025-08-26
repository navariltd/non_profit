<template>
  <div class="p-5">
    <header><h1 class="text-3xl">Projects</h1></header>
  </div>
  <div
    class="p-8 grid grid-cols-1 lg:grid-cols-3 gap-4"
    v-for="project in projects.data"
  >
    <ProjectCard :project="project" />
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { createResource } from "frappe-ui";
import ProjectCard from "../components/ProjectCard.vue";

const projects = createResource({
  url: "non_profit.non_profit.api.get_projects",
  auto: true,
  cache: ["projects"],
});
</script>
