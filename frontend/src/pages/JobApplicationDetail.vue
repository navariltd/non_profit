<template>
  <div class="max-w-5xl mx-auto py-10 space-y-8">
    <!-- Login prompt -->
    <div v-if="!isLoggedIn" class="text-center py-20">
      <h2 class="text-3xl font-bold text-gray-900 mb-4">Please Log In</h2>
      <p class="text-gray-600 mb-8">
        You need to be logged in to view and manage your application.
      </p>
      <Button
        variant="solid"
        class="bg-red-600 hover:bg-red-700 text-white"
        @click="redirectToLogin"
      >
        <template #prefix>
          <LogIn class="w-4 h-4" />
        </template>
        {{ __("Login to View Application") }}
      </Button>
    </div>

    <!-- Application content -->
    <div v-else>
      <!-- Job Card -->
      <div
        v-if="job.data"
        class="p-6 rounded-xl shadow-sm border border-gray-200 bg-gradient-to-r from-red-50 to-white"
      >
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
            <router-link
              :to="{ name: 'JobDetail', params: { job: job.data.name } }"
            >
              <h1 class="text-3xl font-bold text-gray-900 mb-1">
                {{ job.data.job_title }}
              </h1>
            </router-link>
            <div class="text-lg font-medium text-red-600">
              {{ job.data.company }}
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
      </div>

      <!-- Restricted message -->
      <div
        v-if="application.data && !canViewApplication"
        class="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-xl p-6 mt-6"
      >
        <h3 class="text-xl font-semibold mb-2">Application Restricted</h3>
        <p>You don't have enough permissions to view this application.</p>
      </div>

      <!-- Application Detail -->
      <div
        v-if="application.data && canViewApplication"
        class="bg-white rounded-xl shadow-sm p-6 border border-gray-200 mt-6"
      >
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-red-700">Your Application</h2>
          <Button
            variant="solid"
            @click="isEditing = !isEditing"
            class="px-4 py-2 rounded-lg"
          >
            <template #prefix>
              <Edit3 class="w-4 h-4" />
            </template>
            {{ isEditing ? "Cancel" : "Edit" }}
          </Button>
        </div>

        <!-- View Mode -->
        <div v-if="!isEditing" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p class="text-sm text-gray-500">Full Name</p>
              <p class="text-lg font-semibold text-gray-800 pt-2">
                {{ form.applicant_name }}
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Email</p>
              <p class="text-lg font-semibold text-gray-800 pt-2">
                {{ form.email_id }}
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Phone</p>
              <p class="text-lg font-semibold text-gray-800 pt-2">
                {{ form.phone }}
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Applied On</p>
              <p class="text-lg font-semibold text-gray-800 pt-2">
                {{ formatDate(form.creation) }}
                <span class="text-gray-500 text-sm">
                  ({{ timeAgo(application.data.creation) }})
                </span>
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Last Modified</p>
              <p class="text-lg font-semibold text-gray-800 pt-2">
                {{ formatDate(form.modified) }}
                <span class="text-gray-500 text-sm">
                  ({{ timeAgo(application.data.modified) }})
                </span>
              </p>
            </div>
          </div>

          <div>
            <p class="text-sm text-gray-500 mb-1">Cover Letter</p>
            <p
              class="text-gray-800 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg border"
            >
              {{ form.cover_letter || "No cover letter added." }}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p class="text-sm text-gray-500 mb-1">Profile Photo</p>
              <div v-if="profilePhoto" class="space-y-3">
                <img
                  :src="profilePhoto.file_url"
                  alt="Profile"
                  class="rounded-lg border w-full max-w-xs"
                />
                <p class="text-sm text-gray-600">
                  {{ profilePhoto.file_name }}
                </p>
              </div>
              <p v-else class="text-gray-500">No photo uploaded</p>
            </div>

            <div>
              <p class="text-sm text-gray-500 mb-1">Resume</p>
              <div v-if="resume" class="space-y-3">
                <iframe
                  v-if="isPDF(resume.file_url)"
                  :src="resume.file_url"
                  class="w-full h-64 border rounded-lg"
                ></iframe>
                <a
                  v-else
                  :href="resume.file_url"
                  target="_blank"
                  class="text-blue-600 underline"
                >
                  {{ resume.file_name }}
                </a>
              </div>
              <p v-else class="text-gray-500">No resume uploaded</p>
            </div>
          </div>
        </div>

        <!-- Edit Mode -->
        <form v-else class="space-y-10" @submit.prevent="updateApplication">
          <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <h3 class="text-xl font-semibold text-gray-800 mb-6">
              Cover Letter
            </h3>
            <FormControl
              v-model="form.cover_letter"
              :label="__('Cover Letter')"
              type="textarea"
              :rows="10"
              placeholder="Write your cover letter here"
            />
          </div>

          <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <h3 class="text-xl font-semibold text-gray-800 mb-6">Documents</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block mb-2 font-semibold text-gray-800"
                  >Profile Photo</label
                >
                <Uploader
                  v-if="!profilePhoto"
                  label="Upload Profile Photo"
                  :fileTypes="['.jpg', '.jpeg', '.png']"
                  :maxSize="5"
                  :onSuccess="(file) => (profilePhoto = file)"
                  :onError="handleError"
                />
                <div
                  v-else
                  class="flex justify-between p-3 rounded-lg bg-white border"
                >
                  <div class="grid grid-cols-1 gap-4 justify-between">
                    <img
                      :src="profilePhoto.file_url"
                      class="w-16 h-16 rounded-lg object-cover"
                    />
                    <a
                      :href="profilePhoto.file_url"
                      target="_blank"
                      class="font-medium text-gray-800"
                      >{{ profilePhoto.file_name }}</a
                    >
                  </div>
                  <Button
                    variant="subtle"
                    @click="profilePhoto = null"
                    class="text-red-500 hover:text-red-700"
                    >✕</Button
                  >
                </div>
              </div>

              <div>
                <label class="block mb-2 font-semibold text-gray-800"
                  >Resume</label
                >
                <Uploader
                  v-if="!resume"
                  label="Upload Resume"
                  :fileTypes="['.pdf', '.docx', '.doc']"
                  :maxSize="5"
                  :onSuccess="(file) => (resume = file)"
                  :onError="handleError"
                />
                <div
                  v-else
                  class="flex justify-between p-3 rounded-lg bg-white border"
                >
                  <div class="grid grid-cols-1 gap-4 justify-between">
                    <iframe
                      v-if="isPDF(resume.file_url)"
                      :src="resume.file_url"
                      class="w-full h-64 border rounded-lg mb-2"
                    ></iframe>
                    <a
                      :href="resume.file_url"
                      target="_blank"
                      class="font-medium text-gray-800"
                      >{{ resume.file_name }}</a
                    >
                  </div>
                  <Button
                    variant="subtle"
                    @click="resume = null"
                    class="text-red-500 hover:text-red-700"
                    >✕</Button
                  >
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end">
            <Button
              type="submit"
              variant="solid"
              class="bg-red-700 hover:bg-red-800 text-white px-6 py-3 rounded-lg"
            >
              Save Changes
            </Button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Button, FormControl, toast, createResource } from "frappe-ui";
import Uploader from "@/components/Controls/Uploader.vue";
import { Edit3, LogIn } from "lucide-vue-next";

import { formatDistanceToNow, parseISO } from "date-fns";

const router = useRouter();
const user = inject("$user");
const isLoggedIn = computed(() => !!user.data?.name);

const route = useRoute();
const applicationId = route.params?.id || "";
const isEditing = ref(false);

const form = ref({
  applicant_name: "",
  surname: "",
  other_names: "",
  email_id: "",
  phone: "",
  cover_letter: "",
  job_title: "",
  creation: "",
  modified: "",
});

const resume = ref(null);
const profilePhoto = ref(null);

const isPDF = (url) => url?.toLowerCase().endsWith(".pdf");

const job = createResource({
  url: "frappe.client.get",
  makeParams() {
    return {
      doctype: "Job Opening",
      name: form.value.job_title,
    };
  },
  auto: false,
});

const application = createResource({
  url: "frappe.client.get",
  makeParams() {
    return {
      doctype: "Job Applicant",
      name: applicationId,
    };
  },
  onSuccess(data) {
    if (!data) return toast.error("Application not found.");
    form.value = {
      applicant_name: data.applicant_name || "",
      surname: data.surname || "",
      other_names: data.other_names || "",
      email_id: data.email_id || "",
      phone: data.phone || "",
      cover_letter: data.cover_letter || "",
      job_title: data.job_title || "",
      creation: data.creation || "",
      modified: data.modified || "",
    };
    if (data.resume_attachment)
      resume.value = {
        file_name: data.resume_attachment,
        file_url: `/files/${data.resume_attachment}`,
      };
    if (data.profile_photo)
      profilePhoto.value = {
        file_name: data.profile_photo,
        file_url: `/files/${data.profile_photo}`,
      };
    if (data.job_title) job.submit({ name: data.job_title });
  },
  auto: true,
});

const canViewApplication = computed(() => {
  return user.data?.email === form.value.email_id;
});

const updateApplicationResource = createResource({
  url: "non_profit.non_profit.api.update_job_application",
  makeParams() {
    return {
      id: applicationId,
      cover_letter: form.value.cover_letter,
      resume: resume.value?.name,
      profile_photo: profilePhoto.value?.name,
    };
  },
});

const redirectToLogin = () => {
  const currentPath = router.currentRoute.value.fullPath;
  router.push({
    name: "Login",
    query: { "redirect-to": currentPath },
  });
};

const updateApplication = () => {
  updateApplicationResource.submit(
    {},
    {
      onSuccess: () => {
        toast.success("Application updated successfully");
        isEditing.value = false;
        application.reload();
      },
      onError: (err) => toast.error(err.messages?.[0] || err),
    }
  );
};

const handleError = (error) => toast.error(error.message || "Upload error.");
const redirectToWebsite = (url) => window.open(url, "_blank");
const getCompanyAbbr = (name) =>
  name
    ? name
        .split(" ")
        .map((word) => word[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "NA";

const formatDate = (date) => {
  if (!date) return "N/A";
  return new Date(date).toLocaleDateString();
};

const timeAgo = (date) => {
  if (!date) return "";
  return formatDistanceToNow(parseISO(date), { addSuffix: true });
};
</script>
