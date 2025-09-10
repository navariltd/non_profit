<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Volunteer Signup</h1>

    <!-- Button to open modal -->
    <Button @click="showModal = true"> Apply for Volunteer Position </Button>

    <!-- Child component -->
    <JobApplicationModal
      v-model="showModal"
      :show-only-docs="false"
      job="VOLUNTEER-001"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import JobApplicationModal from "../components/Modals/JobApplicationModal.vue";
import { Button } from "frappe-ui";

const showModal = ref(true);
</script>
