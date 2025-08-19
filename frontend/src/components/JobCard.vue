<template>
  <div
    class="flex flex-col border rounded-md p-3 h-full hover:border-outline-gray-3"
  >
    <div class="flex space-x-4 mb-4">
      <div class="flex flex-col space-y-2 flex-1">
        <!-- Job Title -->
        <span class="text-lg font-bold text-ink-gray-9 leading-5">
          {{ job.job_title }}
        </span>
        <!-- Designation -->
        <div v-if="job.designation" class="text-sm text-ink-gray-6">
          {{ job.designation }}
        </div>

        <!-- Location -->
        <div class="flex items-center space-x-1 text-sm text-ink-gray-7">
          <MapPin class="size-3" />
          <span>
            {{ job.location }}{{ job.country ? `, ${job.country}` : "" }}
          </span>
        </div>

        <!-- Vacancies -->
        <div v-if="job.vacancies" class="text-sm text-ink-gray-7">
          {{ job.vacancies }}
          {{ job.vacancies > 1 ? __("vacancies") : __("vacancy") }}
        </div>

        <!-- Applicants -->
        <div
          v-if="job.applicants"
          class="flex items-center space-x-1 text-sm text-ink-gray-7"
        >
          <User class="size-3" />
          <span>
            {{ job.applicants }}
            {{ job.applicants > 1 ? __("applicants") : __("applicant") }}
          </span>
        </div>
      </div>
    </div>

    <!-- Badges -->
    <div class="flex flex-wrap gap-2 mt-auto">
      <Badge v-if="job.employment_type">
        {{ job.employment_type }}
      </Badge>
      <Badge>
        {{ dayjs(job.creation).fromNow() }}
      </Badge>
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue";
import { Badge } from "frappe-ui";
import { MapPin, User } from "lucide-vue-next";

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
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-overflow: ellipsis;
  width: 100%;
  overflow: hidden;
  margin-top: auto;
  line-height: 1.5;
}
</style>
