<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header
      class="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3 sm:px-6 shadow-sm"
    >
      <div class="flex items-center space-x-4">
        <Breadcrumbs
          class="h-7 text-sm sm:text-base text-gray-600"
          :items="[{ label: 'Jobs', route: { name: 'Jobs' } }]"
        />
        <div class="hidden sm:block text-xl font-bold text-red-600">
          {{ __("{0} Open Jobs").format(jobCount) }}
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <Button
          variant="ghost"
          class="lg:hidden p-2 text-gray-700 hover:bg-gray-100"
          @click="showFilters = !showFilters"
        >
          <Filter class="h-5 w-5" />
        </Button>
      </div>
    </header>

    <div class="flex flex-col-reverse lg:flex-row flex-1">
      <aside
        :class="[
          'w-full lg:w-96 xl:w-[28rem] border-r border-gray-200 bg-white p-6 space-y-6 lg:sticky lg:top-0 lg:h-[calc(100vh-65px)] overflow-y-auto transition-transform duration-300 transform',
          'scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent',
          showFilters ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          'fixed inset-0 z-20 lg:relative lg:block',
        ]"
      >
        <div class="flex items-center justify-between lg:hidden mb-4">
          <div class="text-xl font-semibold text-gray-800">
            {{ __("Filters") }}
          </div>
          <Button variant="ghost" class="p-2" @click="showFilters = false">
            <X class="h-5 w-5 text-gray-600" />
          </Button>
        </div>

        <div class="space-y-4">
          <FormControl
            type="text"
            :placeholder="__('Search jobs...')"
            v-model="searchQuery"
            class="w-full"
            @input="updateJobs"
          >
            <template #prefix>
              <Search class="w-5 h-5 text-gray-400" />
            </template>
          </FormControl>
          <Button
            variant="ghost"
            class="w-full justify-center text-red-600 hover:bg-red-50 border border-red-200"
            @click="clearFilters"
          >
            <span class="text-sm font-medium">{{ __("Clear All") }}</span>
          </Button>
        </div>

        <div class="space-y-6 mt-6">
          <div class="space-y-4">
            <div class="text-lg font-semibold text-gray-700">
              {{ __("Job Details") }}
            </div>
            <div class="grid grid-cols-2 gap-4">
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
            </div>
          </div>

          <div class="space-y-4">
            <div class="text-lg font-semibold text-gray-700">
              {{ __("Location") }}
            </div>
            <MultiSelectList
              doctype="Company"
              v-model="companies"
              :label="__('Branch / Region')"
              class="w-full"
              @change="updateJobs"
              :cols="2"
            />
          </div>
        </div>
      </aside>

      <main class="flex-1 min-w-0 p-4 sm:p-6 lg:p-8">
        <div class="flex justify-start mb-6 lg:mb-8">
          <TabButtons
            :buttons="jobTabs"
            v-model="currentTab"
            class="w-full sm:w-auto"
            active-class="bg-red-600 text-white"
            inactive-class="text-gray-700 hover:bg-gray-100"
          />
        </div>
        <div
          v-if="jobs.data?.length"
          class="grid gap-6 grid-cols-[repeat(auto-fit,minmax(250px,1fr))]"
        >
          <router-link
            v-for="job in jobs.data"
            :key="job.name"
            :to="{ name: 'JobDetail', params: { job: job.name } }"
            class="transition-transform duration-300 hover:scale-[1.02] transform"
          >
            <JobCard :job="job" />
          </router-link>
        </div>
        <EmptyState v-else type="Job Openings" />
      </main>
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
  TabButtons,
} from "frappe-ui";
import { Search, Filter, X } from "lucide-vue-next";
import { sessionStore } from "../stores/session";
import { inject, ref, onMounted, watch, computed } from "vue";
import JobCard from "@/components/JobCard.vue";
import Link from "@/components/Controls/Link.vue";
import EmptyState from "@/components/EmptyState.vue";
import MultiSelectList from "@/components/Controls/MultiSelectList.vue";

const user = inject("$user");
const { brand } = sessionStore();

const jobType = ref(null);
const designation = ref(null);
const department = ref(null);
const searchQuery = ref("");
const companies = ref([]);
const showFilters = ref(false);
const filters = ref({});
const orFilters = ref({});
const jobCount = ref(0);
const readOnlyMode = window.read_only_mode;
const currentTab = ref("Open");

const jobTabs = computed(() => [
  { label: __("Open"), value: "Open" },
  { label: __("Recently Posted"), value: "Recently Posted" },
  { label: __("Upcoming"), value: "Upcoming" },
  { label: __("Ending Soon"), value: "Ending Soon" },
  // { label: __("Closed"), value: "Closed" },
]);

onMounted(() => {
  const queries = new URLSearchParams(location.search);
  if (queries.has("type")) jobType.value = queries.get("type");
  updateJobs();
});

const jobs = createResource({
  url: "non_profit.non_profit.api.get_job_openings",
  cache: ["jobs"],
});

const updateJobs = () => {
  updateFilters();
  jobs.update({
    params: { filters: filters.value, orFilters: orFilters.value },
  });
  jobs.reload();
};

const updateFilters = () => {
  filters.value.status = currentTab.value;
  if (jobType.value) filters.value.employment_type = jobType.value;
  else delete filters.value.employment_type;
  if (designation.value) filters.value.designation = designation.value;
  else delete filters.value.designation;
  if (department.value) filters.value.department = department.value;
  else delete filters.value.department;
  if (companies.value?.length) filters.value.company = ["in", companies.value];
  else delete filters.value.company;
  if (searchQuery.value) {
    orFilters.value = {
      job_title: ["like", `%${searchQuery.value}%`],
      company: ["like", `%${searchQuery.value}%`],
      location: ["like", `%${searchQuery.value}%`],
    };
  } else orFilters.value = {};
};

const clearFilters = () => {
  companies.value = [];
  jobType.value = null;
  designation.value = null;
  department.value = null;
  searchQuery.value = "";
  updateJobs();
};

watch([jobType, designation, department, currentTab], updateJobs);
watch(companies, () => {
  updateJobs();
});
watch(jobs, () => (jobCount.value = jobs.data?.length || 0));

usePageMeta(() => ({ title: __("Jobs"), icon: brand.favicon }));
</script>
