<template>
  <!-- Child component -->
  <JobApplicationModal
    v-model="showModal"
    :show-only-docs="false"
    job="VOLUNTEER-001"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import JobApplicationModal from "../components/Modals/JobApplicationModal.vue";
import { Button } from "frappe-ui";

const showModal = ref(true);
</script>
