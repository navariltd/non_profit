<template>
  <div>
    <header
      class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-4 py-3 sm:px-6"
    >
      <Breadcrumbs
        class="h-7"
        :items="[
          { label: __('Jobs'), route: { name: 'Jobs' } },
          {
            label: job.data?.job_title,
            route: { name: 'JobDetail', params: { job: job.data?.name } },
          },
        ]"
      />

      <div class="flex items-center gap-2">
        <!-- <Button
          @click="redirectToWebsite(job.data.route)"
          v-if="job.data?.route"
        >
          <template #prefix>
            <SquareArrowOutUpRight class="w-4 h-4 stroke-1.5" />
          </template>
          {{ __("Visit Website") }}
        </Button> -->

        <Button
          v-if="!jobApplication.data?.length"
          variant="solid"
          @click="openApplicationModal()"
        >
          <template #prefix>
            <SendHorizonal class="w-4 h-4" />
          </template>
          {{ __("Apply") }}
        </Button>

        <Button v-else variant="outline" disabled>
          <template #prefix>
            <Check class="w-4 h-4 text-green-600" />
          </template>
          {{ __("Application submitted") }}
        </Button>
      </div>
    </header>

    <div v-if="job.data" class="mx-auto px-4 sm:px-6 pt-6">
      <div class="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
        <div class="space-y-6 mb-10">
          <div class="flex items-start gap-4">
            <div>
              <img
                v-if="job.data.company_logo"
                :src="job.data.company_logo"
                class="w-14 h-14 rounded-lg object-contain cursor-pointer bg-gray-50"
                :alt="job.data.company"
                @click="redirectToWebsite(job.data.company_website)"
              />
              <div
                v-else
                class="w-14 h-14 flex items-center justify-center rounded-lg bg-gray-100 text-gray-700 font-semibold text-lg cursor-default"
              >
                {{ getCompanyAbbr(job.data.company) }}
              </div>
            </div>

            <div>
              <h1 class="text-2xl font-semibold text-gray-900 mb-1">
                {{ job.data.job_title }}
              </h1>
              <div class="text-sm font-medium text-gray-500">
                {{ job.data.company }}
                <span
                  v-if="job.data.location || job.data.country"
                  class="text-gray-400"
                >
                  — {{ job.data.location
                  }}<span v-if="job.data.country"
                    >, {{ job.data.country }}</span
                  >
                </span>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-3">
            <Badge
              size="lg"
              class="bg-gray-50 text-gray-700 border border-gray-200"
            >
              <template #prefix>
                <CalendarDays class="w-4 h-4 stroke-2 text-gray-500" />
              </template>
              {{ dayjs(job.data.creation).fromNow() }}
            </Badge>

            <Badge
              size="lg"
              class="bg-blue-50 text-blue-700 border border-blue-200"
            >
              <template #prefix>
                <ClipboardType class="w-4 h-4 stroke-2 text-blue-600" />
              </template>
              {{ job.data.employment_type }}
            </Badge>

            <Badge
              v-if="job.data.applicant_count"
              size="lg"
              class="bg-green-50 text-green-700 border border-green-200"
            >
              <template #prefix>
                <SquareUserRound class="w-4 h-4 stroke-2 text-green-600" />
              </template>
              {{ job.data.applicant_count }}
              {{
                job.data.applicant_count == 1
                  ? __("applicant")
                  : __("applicants")
              }}
            </Badge>
          </div>
        </div>

        <div class="flex items-center justify-between my-4">
          <div class="flex-1 h-px bg-gray-200"></div>
          <FileText class="w-4 h-4 mx-3 text-gray-400" />
          <div class="flex-1 h-px bg-gray-200"></div>
        </div>

        <div
          v-html="job.data.description"
          class="prose prose-sm max-w-none text-gray-700 mt-8 prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-gray-200 prose-th:border-gray-200 prose-th:bg-gray-50"
        ></div>
      </div>

      <JobApplicationModal
        v-model="showApplicationModal"
        v-model:application="jobApplication"
        :job="job.data.name"
      />
    </div>
  </div>
</template>

<script setup>
import {
  Badge,
  Button,
  Breadcrumbs,
  createResource,
  usePageMeta,
} from "frappe-ui";
import { inject, ref } from "vue";
import { sessionStore } from "../stores/session";
import JobApplicationModal from "@/components/Modals/JobApplicationModal.vue";
import {
  Check,
  SendHorizonal,
  Pencil,
  CalendarDays,
  SquareUserRound,
  SquareArrowOutUpRight,
  FileText,
  ClipboardType,
} from "lucide-vue-next";

const user = inject("$user");
const dayjs = inject("$dayjs");
const { brand } = sessionStore();
const showApplicationModal = ref(false);
const readOnlyMode = window.read_only_mode;

const props = defineProps({
  job: {
    type: String,
    required: true,
  },
});

// Job details
const job = createResource({
  url: "non_profit.non_profit.api.get_job_details",
  params: { job: props.job },
  cache: ["job", props.job],
  auto: true,
  onSuccess: () => {
    if (user.data?.name) {
      jobApplication.submit();
    }
  },
});

// Job Application
const jobApplication = createResource({
  url: "frappe.client.get_list",
  makeParams() {
    return {
      doctype: "Job Applicant",
      filters: {
        job_title: job.data?.name,
        user: user.data?.name,
      },
    };
  },
});

const openApplicationModal = () => {
  showApplicationModal.value = true;
};

const redirectToWebsite = (url) => {
  window.open(url, "_blank");
};

// Company initials fallback
const getCompanyAbbr = (name) => {
  if (!name) return "NA";
  return name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
};

usePageMeta(() => ({
  title: job.data?.job_title,
  icon: brand.favicon,
}));
</script>
