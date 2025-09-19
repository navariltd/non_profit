<template>
  <div class="min-h-screen bg-gray-50">
    <div
      v-if="projectDetail.loading"
      class="flex items-center justify-center min-h-screen"
    >
      <div
        class="flex flex-col justify-center items-center text-center text-red-800"
      >
        <Spinner class="w-12" />
        <p class="text-gray-600">Loading project details...</p>
      </div>
    </div>

    <div
      v-else-if="projectDetail.error"
      class="flex items-center justify-center min-h-screen"
    >
      <div class="text-center">
        <div
          class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <svg
            class="w-8 h-8 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          Error loading project
        </h3>
        <Button theme="red" @click="projectDetail.reload()">Try Again</Button>
      </div>
    </div>

    <div v-else-if="projectDetail.data" class="max-w-6xl mx-auto px-6 py-8">
      <div
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <h1 class="text-3xl font-bold text-gray-900">
                {{ projectDetail.data.project_name }}
              </h1>
              <Badge
                :theme="getStatusTheme(projectDetail.data.status)"
                class="px-3 py-1"
              >
                {{ projectDetail.data.status }}
              </Badge>
            </div>
            <p
              class="text-sm text-gray-500 font-mono bg-gray-50 px-2 py-1 rounded inline-block mb-4"
            >
              {{ projectDetail.data.name }}
            </p>
            <div class="flex items-center gap-6 text-sm text-gray-600">
              <span class="flex items-center gap-2">
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
                {{ projectDetail.data.project_type }}
              </span>
              <span class="flex items-center gap-2">
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {{ formatDate(projectDetail.data.expected_start_date) }} -
                {{ formatDate(projectDetail.data.expected_end_date) }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <Badge
              :theme="getPriorityTheme(projectDetail.data.priority)"
              class="px-3 py-1"
            >
              {{ projectDetail.data.priority }} Priority
            </Badge>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Project Progress
            </h2>
            <div class="space-y-4">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Completion</span>
                <span class="font-medium text-gray-900"
                  >{{ projectDetail.data.percent_complete }}%</span
                >
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="bg-red-600 h-3 rounded-full transition-all duration-500"
                  :style="{ width: `${projectDetail.data.percent_complete}%` }"
                ></div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
            <div
              v-if="projectDetail.data.notes"
              class="prose prose-sm max-w-none text-gray-700"
            >
              {{ projectDetail.data.notes }}
            </div>
            <div v-else class="text-gray-500 italic">
              No notes available for this project.
            </div>
          </div>
        </div>
        <div class="space-y-6">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Project Information
            </h2>
            <div class="space-y-4">
              <div>
                <label class="text-sm font-medium text-gray-600">Status</label>
                <p class="text-sm text-gray-900 mt-1 flex items-center gap-2">
                  <span
                    class="w-2 h-2 rounded-full"
                    :class="getStatusColor(projectDetail.data.status)"
                  ></span>
                  {{ projectDetail.data.status }}
                </p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-600">Active</label>
                <p class="text-sm text-gray-900 mt-1">
                  {{ projectDetail.data.is_active === "1" ? "Yes" : "No" }}
                </p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-lg border border-red-300 p-8">
            <h2
              class="flex flex-row items-center gap-2 text-2xl font-bold text-red-700 mb-4"
            >
              <Badge variant="subtle" theme="red">Action Required:</Badge>
              <span>Project Decision</span>
            </h2>

            <div class="mb-6">
              <p class="text-sm text-gray-700 font-medium mb-2">
                Important: Please review the official project documents before
                you decide.
              </p>
              <ul class="list-disc list-inside text-sm text-gray-700">
                <li>
                  <a
                    href="/files/contract.pdf"
                    target="_blank"
                    class="text-red-600 hover:underline"
                  >
                    Download Contract
                  </a>
                </li>
                <li>
                  <a
                    href="/files/tor.pdf"
                    target="_blank"
                    class="text-red-600 hover:underline"
                  >
                    Download Terms of Reference (ToR)
                  </a>
                </li>
              </ul>
            </div>

            <p class="text-sm text-gray-500 italic mb-6">
              Your decision to accept this project confirms your agreement to
              the terms outlined in both documents.
            </p>

            <div class="flex gap-3">
              <Button theme="red" class="flex-1" @click="acceptProject">
                Accept Project
              </Button>
              <Button
                theme="gray"
                variant="outline"
                class="flex-1"
                @click="rejectProject"
              >
                Reject Project
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { createResource, toast, Button, Badge, Spinner } from "frappe-ui";
import { computed, inject, onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const user = inject<any>("$user");

onMounted(() => {
  if (!user.data) {
    toast.warning("You must be logged in to view this page");
    setTimeout(() => {
      window.location.href = "/login";
    }, 500);
  }
});

const projectParams = computed(() => {
  return route.params.id;
});

const projectDetail = createResource({
  url: "non_profit.non_profit.api.get_project_details",
  auto: true,
  cache: ["project_detail", projectParams.value],
  makeParams() {
    return { project_name: projectParams.value };
  },
});

type BadgeTheme = "gray" | "blue" | "green" | "orange" | "red";

const getStatusTheme = (status: string): BadgeTheme | undefined => {
  const statusMap: Record<string, BadgeTheme> = {
    Open: "blue",
    Working: "orange",
    Completed: "green",
    Cancelled: "red",
    // 'On Hold' intentionally omitted as 'yellow' is not a valid theme
  };
  return statusMap[status] || "gray";
};

const getPriorityTheme = (priority: string): BadgeTheme | undefined => {
  const priorityMap: Record<string, BadgeTheme> = {
    High: "red",
    Medium: "orange",
    Low: "green",
  };
  return priorityMap[priority] || "gray";
};

const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    Open: "bg-blue-500",
    Working: "bg-orange-500",
    Completed: "bg-green-500",
    Cancelled: "bg-red-500",
    "On Hold": "bg-yellow-500",
  };
  return colorMap[status] || "bg-gray-500";
};

const formatDate = (dateString: string) => {
  if (!dateString) return "Not set";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

function acceptProject() {}

function rejectProject() {}
</script>
