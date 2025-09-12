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
        <Button
          v-if="!user.data?.name && job.data?.is_internal"
          variant="solid"
          class="bg-red-600 hover:bg-red-700 text-white"
          @click="redirectToLogin"
        >
          <template #prefix>
            <LogIn class="w-4 h-4" />
          </template>
          {{ __("Login to Apply") }}
        </Button>

        <Button
          v-else-if="isApplied"
          variant="outline"
          class="border-red-500 text-red-600 hover:bg-red-50"
          @click="goToApplicationDetail"
        >
          <template #prefix>
            <Check class="w-4 h-4 text-red-600" />
          </template>
          {{ __("View Application") }}
        </Button>

        <Button
          v-else
          variant="solid"
          class="bg-red-600 hover:bg-red-700 text-white"
          @click="goToNewApplication"
        >
          <template #prefix>
            <SendHorizonal class="w-4 h-4" />
          </template>
          {{ __("Apply Now") }}
        </Button>
      </div>
    </header>

    <div v-if="job.data" class="mx-auto px-4 sm:px-6 pt-6">
      <div
        class="p-6 bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-all"
      >
        <div class="space-y-6 mb-10">
          <div class="flex items-start gap-4">
            <div>
              <img
                v-if="job.data.company_logo"
                :src="job.data.company_logo"
                class="w-16 h-16 rounded-lg object-contain cursor-pointer bg-gray-50 border"
                :alt="job.data.company"
                @click="redirectToWebsite(job.data.company_website)"
              />
              <div
                v-else
                class="w-16 h-16 flex items-center justify-center rounded-lg bg-red-100 text-red-700 font-semibold text-xl cursor-default"
              >
                {{ getCompanyAbbr(job.data.company) }}
              </div>
            </div>

            <div>
              <h1 class="text-3xl font-bold text-gray-900 mb-1">
                {{ job.data.job_title }}
              </h1>
              <div class="text-lg font-medium text-red-600">
                {{ job.data.company }}
                <span
                  v-if="job.data.branch"
                  class="text-gray-500 ml-2 text-base"
                >
                  • {{ job.data.branch }}
                </span>
              </div>
              <div
                v-if="job.data.location || job.data.country"
                class="text-sm text-gray-500 mt-1"
              >
                {{ job.data.location
                }}<span v-if="job.data.country">, {{ job.data.country }}</span>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-3 mt-4">
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
              class="bg-red-50 text-red-700 border border-red-200"
            >
              <template #prefix>
                <ClipboardType class="w-4 h-4 stroke-2 text-red-600" />
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
import { inject, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { sessionStore } from "../stores/session";
import {
  Check,
  SendHorizonal,
  LogIn,
  CalendarDays,
  SquareUserRound,
  FileText,
  ClipboardType,
} from "lucide-vue-next";

const router = useRouter();
const user = inject("$user");
const dayjs = inject("$dayjs");
const { brand } = sessionStore();
const props = defineProps({
  job: {
    type: String,
    required: true,
  },
});

const job = createResource({
  url: "non_profit.non_profit.api.get_job_details",
  params: { job: props.job },
  cache: ["job", props.job],
  auto: true,
});

const jobApplication = createResource({
  url: "non_profit.non_profit.api.get_list",
  makeParams() {
    return {
      doctype: "Job Applicant",
      filters: {
        job_title: props.job,
        email_id: user.data?.email,
      },
      fields: ["name"],
    };
  },
  auto: true,
  reloadOn: () => !!user.data?.email,
});

const isApplied = computed(() => jobApplication.data?.length > 0);
const applicationId = computed(() => jobApplication.data?.[0]?.name || null);

const redirectToLogin = () => {
  const currentPath = router.currentRoute.value.fullPath;
  router.push({
    name: "Login",
    query: { "redirect-to": currentPath },
  });
};

const goToNewApplication = () => {
  router.push({
    name: "NewJobApplication",
  });
};

const goToApplicationDetail = () => {
  if (applicationId.value) {
    router.push({
      name: "JobApplicationDetail",
      params: { id: applicationId.value },
    });
  }
};

const redirectToWebsite = (url) => {
  window.open(url, "_blank");
};

const getCompanyAbbr = (name) =>
  name
    ? name
        .split(" ")
        .map((word) => word[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "NA";

usePageMeta(() => ({
  title: job.data?.job_title,
  icon: brand.favicon,
}));
</script>
