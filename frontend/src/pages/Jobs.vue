<template>
  <div class="">
    <header
      class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
    >
      <Breadcrumbs
        class="h-7"
        :items="[{ label: __('Jobs'), route: { name: 'Jobs' } }]"
      />
      <router-link
        v-if="user.data?.name"
        :to="{ name: 'JobForm', params: { jobName: 'new' } }"
      >
        <Button v-if="!readOnlyMode" variant="solid">
          <template #prefix>
            <Plus class="h-4 w-4" />
          </template>
          {{ __("New Job") }}
        </Button>
      </router-link>
    </header>

    <div>
      <!-- Top Filters -->
      <div
        class="flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:items-center justify-between w-full md:w-4/5 mx-auto p-5"
      >
        <div class="text-xl font-semibold text-ink-gray-7 mb-4 md:mb-0">
          {{ __("{0} Open Jobs").format(jobCount) }}
        </div>

        <div
          class="grid grid-cols-1 gap-2"
          :class="user.data ? 'md:grid-cols-5' : 'md:grid-cols-6'"
        >
          <!-- Search -->
          <FormControl
            type="text"
            :placeholder="__('Search')"
            v-model="searchQuery"
            class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
            @input="updateJobs"
          >
            <template #prefix>
              <Search class="w-4 h-4 stroke-1.5 text-ink-gray-5" />
            </template>
          </FormControl>

          <!-- Country filter -->
          <Link
            v-if="user.data"
            doctype="Country"
            v-model="country"
            :placeholder="__('Country')"
            class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
          />

          <!-- Company filter -->
          <Link
            doctype="Company"
            v-model="company"
            :placeholder="__('Company')"
            class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
            @change="updateJobs"
          />

          <!-- Employment Type filter -->
          <Link
            doctype="Employment Type"
            v-model="jobType"
            :placeholder="__('Employment Type')"
            class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
            @change="updateJobs"
          />

          <!-- Designation filter -->
          <Link
            doctype="Designation"
            v-model="designation"
            :placeholder="__('Designation')"
            class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
            @change="updateJobs"
          />

          <!-- Department filter -->
          <Link
            doctype="Department"
            v-model="department"
            :placeholder="__('Department')"
            class="min-w-40 lg:min-w-0 lg:w-32 xl:w-40"
            @change="updateJobs"
          />
        </div>
      </div>

      <!-- Job List -->
      <div v-if="jobs.data?.length" class="w-full md:w-4/5 mx-auto p-5 pt-0">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <router-link
            v-for="job in jobs.data"
            :key="job.name"
            :to="{ name: 'JobDetail', params: { job: job.name } }"
          >
            <JobCard :job="job" />
          </router-link>
        </div>
      </div>
      <EmptyState v-else type="Job Openings" />
    </div>
  </div>
</template>

<script setup>
import {
  Button,
  Breadcrumbs,
  createResource,
  FormControl,
  usePageMeta,
} from "frappe-ui";
import { Plus, Search } from "lucide-vue-next";
import { sessionStore } from "../stores/session";
import { inject, ref, onMounted, watch } from "vue";
import JobCard from "@/components/JobCard.vue";
import Link from "@/components/Controls/Link.vue";
import EmptyState from "@/components/EmptyState.vue";

const user = inject("$user");
const { brand } = sessionStore();

const jobType = ref(null);
const designation = ref(null);
const department = ref(null);
const searchQuery = ref("");
const country = ref(null);
const company = ref(null); // ✅ new filter

const filters = ref({});
const orFilters = ref({});
const jobCount = ref(0);
const readOnlyMode = window.read_only_mode;

onMounted(() => {
  let queries = new URLSearchParams(location.search);
  if (queries.has("type")) {
    jobType.value = queries.get("type");
  }
  updateJobs();
});

const jobs = createResource({
  url: "non_profit.non_profit.api.get_job_openings",
  cache: ["jobs"],
});

const updateJobs = () => {
  updateFilters();
  jobs.update({
    params: {
      filters: filters.value,
      orFilters: orFilters.value,
    },
  });
  jobs.reload();
};

const updateFilters = () => {
  filters.value.status = "Open";

  if (jobType.value) {
    filters.value.employment_type = jobType.value;
  } else {
    delete filters.value.employment_type;
  }

  if (designation.value) {
    filters.value.designation = designation.value;
  } else {
    delete filters.value.designation;
  }

  if (department.value) {
    filters.value.department = department.value;
  } else {
    delete filters.value.department;
  }

  if (company.value) {
    filters.value.company = company.value;
  } else {
    delete filters.value.company;
  }

  if (searchQuery.value) {
    orFilters.value = {
      job_title: ["like", `%${searchQuery.value}%`],
      company: ["like", `%${searchQuery.value}%`],
      location: ["like", `%${searchQuery.value}%`],
    };
  } else {
    orFilters.value = {};
  }

  if (country.value) {
    filters.value.country = country.value;
  } else {
    delete filters.value.country;
  }
};

watch([country, company, jobType, designation, department], () => updateJobs());

watch(jobs, () => {
  jobCount.value = jobs.data?.length || 0;
});

usePageMeta(() => ({
  title: __("Jobs"),
  icon: brand.favicon,
}));
</script>
