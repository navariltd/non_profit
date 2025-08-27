<template>
  <div class="flex flex-col lg:flex-row min-h-screen">
    <main class="flex-1 min-w-0">
      <header
        class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-4 py-3 sm:px-6"
      >
        <div class="flex items-center space-x-2">
          <Breadcrumbs
            class="h-7 text-sm sm:text-base"
            :items="[{ label: __('Jobs'), route: { name: 'Jobs' } }]"
          />
          <div class="text-lg font-semibold text-ink-gray-7 hidden sm:block">
            {{ __("{0} Open Jobs").format(jobCount) }}
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <Button
            variant="ghost"
            class="lg:hidden p-2"
            @click="showFilters = !showFilters"
          >
            <Filter class="h-4 w-4" />
          </Button>
          <router-link
            v-if="user.data?.name"
            :to="{ name: 'JobForm', params: { jobName: 'new' } }"
          >
            <Button
              v-if="!readOnlyMode"
              variant="solid"
              class="whitespace-nowrap"
            >
              <template #prefix>
                <Plus class="h-4 w-4" />
              </template>
              <span class="hidden sm:inline">{{ __("New Job") }}</span>
              <span class="sm:hidden">{{ __("New") }}</span>
            </Button>
          </router-link>
        </div>
      </header>

      <div class="flex justify-center border-b px-4 py-3 bg-gray-50">
        <div class="w-full max-w-4xl">
          <TabButtons
            :buttons="courseTabs"
            v-model="currentTab"
            class="w-full justify-center sm:justify-start"
          />
        </div>
      </div>

      <div class="w-full max-w-7xl mx-auto px-4 py-6">
        <div class="mb-4 lg:hidden">
          <FormControl
            type="text"
            :placeholder="__('Search jobs...')"
            v-model="searchQuery"
            class="w-full"
            @input="updateJobs"
          >
            <template #prefix>
              <Search class="w-4 h-4 stroke-1.5 text-ink-gray-5" />
            </template>
          </FormControl>
        </div>

        <div
          v-if="jobs.data?.length"
          class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5"
        >
          <router-link
            v-for="job in jobs.data"
            :key="job.name"
            :to="{ name: 'JobDetail', params: { job: job.name } }"
            class="transition-transform hover:scale-[1.02]"
          >
            <JobCard :job="job" />
          </router-link>
        </div>
        <EmptyState v-else type="Job Openings" />
      </div>
    </main>

    <aside
      :class="[
        'w-full lg:w-80 xl:w-96 border-l bg-surface-white p-5 space-y-4 lg:sticky lg:top-0 lg:h-screen lg:overflow-y-auto transition-transform duration-300',
        showFilters ? 'block' : 'hidden lg:block',
      ]"
    >
      <div class="flex items-center justify-between mb-2">
        <div class="text-lg font-semibold text-ink-gray-7">
          {{ __("Filters") }}
        </div>
        <Button
          variant="ghost"
          class="lg:hidden p-1"
          @click="showFilters = false"
        >
          <X class="h-4 w-4" />
        </Button>
      </div>

      <FormControl
        type="text"
        :placeholder="__('Search jobs...')"
        v-model="searchQuery"
        class="w-full hidden lg:block"
        @input="updateJobs"
      >
        <template #prefix>
          <Search class="w-4 h-4 stroke-1.5 text-ink-gray-5" />
        </template>
      </FormControl>

      <div class="text-sm font-medium text-ink-gray-6 pt-2">
        {{ __("Organization") }}
      </div>

      <MultiSelect
        doctype="Company"
        v-model="companies"
        :label="__('Companies')"
        class="w-full"
        @change="updateJobs"
      />

      <MultiSelect
        doctype="Branch"
        v-model="branches"
        :label="__('Branches')"
        :filters="branchFilters"
        class="w-full"
        @change="updateJobs"
      />

      <div class="text-sm font-medium text-ink-gray-6 pt-2">
        {{ __("Job Details") }}
      </div>

      <Link
        doctype="Employment Type"
        v-model="jobType"
        :placeholder="__('Employment Type')"
        class="w-full"
        @change="updateJobs"
      />

      <Link
        doctype="Designation"
        v-model="designation"
        :placeholder="__('Designation')"
        class="w-full"
        @change="updateJobs"
      />

      <Link
        doctype="Department"
        v-model="department"
        :placeholder="__('Department')"
        class="w-full"
        @change="updateJobs"
      />

      <Button variant="outline" class="w-full mt-4" @click="clearFilters">
        {{ __("Clear All Filters") }}
      </Button>
    </aside>
  </div>
</template>
<script setup>
import {
  Button,
  Breadcrumbs,
  createResource,
  FormControl,
  usePageMeta,
  TabButtons,
} from "frappe-ui";
import { Plus, Search, Filter, X } from "lucide-vue-next";
import { sessionStore } from "../stores/session";
import { inject, ref, onMounted, watch, computed } from "vue";
import JobCard from "@/components/JobCard.vue";
import Link from "@/components/Controls/Link.vue";
import EmptyState from "@/components/EmptyState.vue";
import MultiSelect from "@/components/Controls/MultiSelect.vue";

const user = inject("$user");
const { brand } = sessionStore();

const jobType = ref(null);
const designation = ref(null);
const department = ref(null);
const searchQuery = ref("");
const companies = ref([]);
const branches = ref([]);
const showFilters = ref(false);

const branchesMultiselect = ref(null);

const filters = ref({});
const orFilters = ref({});
const jobCount = ref(0);
const readOnlyMode = window.read_only_mode;

const currentTab = ref("Live");

const courseTabs = computed(() => {
  let tabs = [
    { label: __("Live") },
    { label: __("New") },
    { label: __("Upcoming") },
  ];
  if (
    user.data?.is_moderator ||
    user.data?.is_instructor ||
    user.data?.is_evaluator
  ) {
    tabs.push({ label: __("Created") });
    tabs.push({ label: __("Unpublished") });
  } else if (user.data) {
    tabs.push({ label: __("Enrolled") });
  }
  return tabs;
});

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

  if (jobType.value) filters.value.employment_type = jobType.value;
  else delete filters.value.employment_type;

  if (designation.value) filters.value.designation = designation.value;
  else delete filters.value.designation;

  if (department.value) filters.value.department = department.value;
  else delete filters.value.department;

  if (companies.value?.length) {
    filters.value.company = ["in", companies.value];
  } else {
    delete filters.value.company;
  }

  if (branches.value?.length) {
    filters.value.branch = ["in", branches.value];
  } else {
    delete filters.value.branch;
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
};

const branchFilters = computed(() => {
  if (companies.value?.length) {
    return { company: ["in", companies.value] };
  }
  return {};
});

const clearFilters = () => {
  companies.value = [];
  branches.value = [];
  jobType.value = null;
  designation.value = null;
  department.value = null;
  searchQuery.value = "";
  updateJobs();
};

watch([jobType, designation, department], () => updateJobs());

watch(companies, (newCompanies, oldCompanies) => {
  updateJobs();
  if (JSON.stringify(newCompanies) !== JSON.stringify(oldCompanies)) {
    branches.value = [];
    if (branchesMultiselect.value) {
      branchesMultiselect.value.reload();
    }
  }
});

watch(branches, () => updateJobs());

watch(jobs, () => {
  jobCount.value = jobs.data?.length || 0;
});

usePageMeta(() => ({
  title: __("Jobs"),
  icon: brand.favicon,
}));
</script>
