<template>
  <div
    class="flex flex-col bg-white border border-gray-200 rounded-xl p-5 h-full shadow-sm hover:shadow-md hover:border-gray-300 transition-all duration-200"
  >
    <!-- Header -->
    <div class="mb-3">
      <h2 class="text-xl font-semibold text-gray-900 leading-tight">
        {{ job.job_title }}
      </h2>
      <div class="text-sm text-gray-500 mt-1">
        {{ job.company }}
        <span v-if="job.department" class="text-gray-400">
          • {{ job.department }}</span
        >
      </div>
    </div>

    <!-- Details -->
    <div class="flex flex-wrap gap-x-5 gap-y-2 mb-4 text-sm text-gray-600">
      <div v-if="job.designation" class="flex items-center gap-1">
        <span class="font-medium text-gray-700">{{ job.designation }}</span>
      </div>
      <div v-if="job.branch" class="flex items-center gap-1">
        <span>{{ job.branch }}</span>
      </div>
      <div class="flex items-center gap-1" v-if="job.location || job.country">
        <MapPin class="w-4 h-4 text-gray-400" />
        <span
          >{{ job.location }}{{ job.country ? `, ${job.country}` : "" }}</span
        >
      </div>
    </div>

    <!-- Description -->
    <p v-if="job.description" class="description text-sm text-gray-700 mb-4">
      {{ job.description }}
    </p>

    <!-- Job Meta Info -->
    <div class="grid grid-cols-2 gap-y-2 text-sm text-gray-600 mb-4">
      <div v-if="job.vacancies" class="flex gap-1">
        <span class="font-medium text-gray-800">{{ job.vacancies }}</span>
        <span>{{ job.vacancies > 1 ? __("vacancies") : __("vacancy") }}</span>
      </div>
      <div v-if="job.applicants" class="flex gap-1">
        <span class="font-medium text-gray-800">{{ job.applicants }}</span>
        <span>{{
          job.applicants > 1 ? __("applicants") : __("applicant")
        }}</span>
      </div>
      <div v-if="job.posted_on">
        <span class="text-gray-500">Posted:</span>
        <span class="font-medium text-gray-800">{{
          dayjs(job.posted_on).fromNow()
        }}</span>
      </div>
      <div v-if="job.closes_on">
        <span class="text-gray-500">Closes:</span>
        <span class="font-medium text-gray-800">{{
          dayjs(job.closes_on).format("MMM D, YYYY")
        }}</span>
      </div>
      <div v-if="job.closed_on">
        <span class="text-gray-500">Closed:</span>
        <span class="font-medium text-gray-800">{{
          dayjs(job.closed_on).format("MMM D, YYYY")
        }}</span>
      </div>
    </div>

    <!-- Badges -->
    <div class="flex flex-wrap gap-2 mt-auto">
      <Badge
        v-if="job.employment_type"
        class="bg-blue-50 text-blue-700 border border-blue-200"
      >
        {{ job.employment_type }}
      </Badge>
      <Badge
        v-if="job.status"
        class="bg-green-50 text-green-700 border border-green-200"
      >
        {{ job.status }}
      </Badge>
      <Badge class="bg-gray-50 text-gray-600 border border-gray-200">
        {{ dayjs(job.creation).fromNow() }}
      </Badge>
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue";
import { Badge } from "frappe-ui";
import { MapPin } from "lucide-vue-next";

const dayjs = inject("$dayjs");
const props = defineProps({
  job: {
    type: Object,
    default: null,
  },
});
</script>

<style>
.description {
  display: -webkit-box;
  -webkit-line-clamp: 2; /* truncate to 2 lines */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}
</style>
