<template>
  <div class="max-w-5xl mx-auto py-10 space-y-8">
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

    <div v-else>
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

      <div
        v-if="application.data && !canViewApplication"
        class="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-xl p-6 mt-6"
      >
        <h3 class="text-xl font-semibold mb-2">Application Restricted</h3>
        <p>You don't have enough permissions to view this application.</p>
      </div>

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
            :disabled="!canEditResource?.data"
          >
            <template #prefix>
              <Edit3 class="w-4 h-4" />
            </template>
            {{ isEditing ? "Cancel" : "Edit" }}
          </Button>
        </div>

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
              <TextEditor
                editor-class="min-h-[20rem] w-full rounded-b-lg border-t-0 p-2"
                :content="form.cover_letter"
                @change="(val) => (form.cover_letter = val)"
                :bubbleMenu="true"
                :fixed-menu="true"
              />
            </p>
          </div>

          <div class="grid grid-cols-1 gap-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p class="text-sm text-gray-500 mb-1">Profile Photo</p>
                <div v-if="application?.data?.profile_photo" class="space-y-3">
                  <img
                    :src="application.data.profile_photo"
                    alt="Profile"
                    class="rounded-lg border w-full max-w-xs"
                  />
                </div>
                <p v-else class="text-gray-500">No photo uploaded</p>
              </div>
              <div>
                <p class="text-sm text-gray-500 mb-1">Resume</p>
                <div
                  v-if="application?.data?.resume_attachment"
                  class="space-y-3"
                >
                  <a
                    :href="application.data.resume_attachment"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 font-medium truncate block"
                  >
                    View / Download Resume
                  </a>

                  <iframe
                    :src="application.data.resume_attachment"
                    class="w-full h-64 border rounded-lg"
                  ></iframe>
                </div>
                <p v-else class="text-gray-500">No resume uploaded</p>
              </div>
            </div>

            <div>
              <p class="text-sm text-gray-500 mb-3">
                Documents ({{ form.documents.length }})
              </p>
              <div
                v-if="form.documents.length > 0"
                class="space-y-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
              >
                <div
                  v-for="(doc, index) in form.documents"
                  :key="index"
                  class="border rounded-lg p-4 bg-gray-50"
                >
                  <div class="flex items-start gap-3">
                    <div class="flex-shrink-0">
                      <div
                        v-if="isPDF(doc.file_url)"
                        class="w-16 h-20 bg-red-100 rounded border flex items-center justify-center"
                      >
                        <svg
                          class="w-8 h-8 text-red-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            d="M4 18h12a1 1 0 001-1V7.414a1 1 0 00-.293-.707L13.414 3.414A1 1 0 0012.586 3H4a1 1 0 00-1 1v14a1 1 0 001 1z"
                          />
                        </svg>
                      </div>
                      <div
                        v-else-if="isWord(doc.file_url)"
                        class="w-16 h-20 bg-blue-100 rounded border flex items-center justify-center"
                      >
                        <svg
                          class="w-8 h-8 text-blue-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            d="M4 3a1 1 0 000 2h12a1 1 0 100-2H4zM3 7a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM4 11a1 1 0 100 2h8a1 1 0 100-2H4z"
                          />
                        </svg>
                      </div>
                      <div
                        v-else
                        class="w-16 h-20 bg-gray-100 rounded border flex items-center justify-center"
                      >
                        <svg
                          class="w-8 h-8 text-gray-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                          <path
                            fill-rule="evenodd"
                            d="M4 5a2 2 0 012-2v1a1 1 0 001 1h6a1 1 0 001-1V3a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5z"
                          />
                        </svg>
                      </div>
                    </div>

                    <div class="flex-1 min-w-0">
                      <a
                        :href="doc.file_url"
                        target="_blank"
                        class="text-blue-600 hover:text-blue-800 font-medium truncate block"
                      >
                        {{ doc.file_name }}
                      </a>
                      <p class="text-sm text-gray-500 mt-1">
                        {{ getFileType(doc.file_name) }}
                        <span v-if="doc.file_size">
                          • {{ formatBytes(doc.file_size) }}</span
                        >
                      </p>
                      <p
                        v-if="doc.uploaded_on"
                        class="text-xs text-gray-400 mt-1"
                      >
                        Uploaded {{ timeAgo(doc.uploaded_on) }}
                      </p>
                    </div>
                  </div>

                  <div v-if="isPDF(doc.file_url)" class="mt-4">
                    <iframe
                      :src="doc.file_url"
                      class="w-full h-40 border rounded-lg"
                    ></iframe>
                  </div>
                </div>
              </div>
              <p
                v-else
                class="text-gray-500 py-8 text-center border rounded-lg bg-gray-50"
              >
                No documents uploaded
              </p>
            </div>
          </div>
        </div>

        <form v-else class="space-y-10" @submit.prevent="updateApplication">
          <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <span class="mb-2 !pt-4 text-lg font-semibold text-gray-800">
              {{ __("Cover Letter") }}
            </span>
            <div
              class="mt-6 mb-2 font-semibold text-gray-800 border border-gray-300 rounded-lg"
            >
              <TextEditor
                editor-class="min-h-[20rem] w-full rounded-b-lg border-t-0 p-2"
                :content="form.cover_letter"
                @change="(val) => (form.cover_letter = val)"
                :bubbleMenu="true"
                :fixed-menu="true"
              />
            </div>
          </div>

          <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <h3 class="text-xl font-semibold text-gray-800 mb-6">Documents</h3>
            <div class="grid grid-cols-1 gap-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label class="block mb-2 font-semibold text-gray-800">
                    Profile Photo
                  </label>
                  <Uploader
                    label="Upload Profile Photo"
                    :fileTypes="['.jpg', '.jpeg', '.png']"
                    :maxSize="5"
                    :onSuccess="handleProfilePhotoUpload"
                    :onError="handleError"
                  />
                </div>

                <div>
                  <label class="block mb-2 font-semibold text-gray-800">
                    Resume
                  </label>
                  <Uploader
                    label="Upload Resume"
                    :fileTypes="['.pdf', '.docx', '.doc']"
                    :maxSize="10"
                    :onSuccess="handleResumeUpload"
                    :onError="handleError"
                  />
                  <div
                    v-if="resume"
                    class="mt-3 p-3 border rounded-lg bg-white"
                  >
                    <a
                      :href="resume.file_url"
                      target="_blank"
                      class="text-blue-600 hover:text-blue-800 font-medium truncate block"
                    >
                      {{ resume.file_name }}
                    </a>
                    <p class="text-sm text-gray-500">
                      {{ getFileType(resume.file_name) }}
                      <span v-if="resume.file_size">
                        • {{ formatBytes(resume.file_size) }}</span
                      >
                    </p>
                    <Button
                      variant="subtle"
                      size="sm"
                      class="mt-2 text-red-600"
                      @click="removeResume"
                    >
                      Remove
                    </Button>
                  </div>
                  <p v-else class="text-gray-500">No resume uploaded</p>
                </div>
              </div>

              <div>
                <label class="block mb-2 font-semibold text-gray-800">
                  Other Documents (Certificates, etc.)
                </label>
                <Uploader
                  label="Upload Documents"
                  :fileTypes="[
                    '.pdf',
                    '.docx',
                    '.doc',
                    '.jpg',
                    '.jpeg',
                    '.png',
                  ]"
                  :maxSize="10"
                  :multi="true"
                  :maxFiles="10"
                  :onSuccess="handleDocumentUpload"
                  :onError="handleError"
                />
              </div>
            </div>
          </div>

          <div class="flex justify-end">
            <Button
              type="submit"
              variant="solid"
              class="bg-red-700 hover:bg-red-800 text-white px-6 py-3 rounded-lg"
              :loading="updateApplicationResource.loading"
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
import { Button, TextEditor, toast, createResource } from "frappe-ui";
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

const documents = ref([]);
const profilePhoto = ref(null);

const isPDF = (url) => url?.toLowerCase().endsWith(".pdf");
const isWord = (url) => /\.(doc|docx)$/i.test(url);

const getFileType = (filename) => {
  const ext = filename?.split(".").pop()?.toUpperCase();
  return ext || "Unknown";
};

const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

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
      profile_photo: data.profile_photo || null,
      modified: data.modified || "",
      documents: [],
      resume: null,
    };

    if (data.job_title) job.submit({ name: data.job_title });

    files.fetch();
  },
  auto: true,
});

const files = createResource({
  url: "frappe.client.get_list",
  makeParams() {
    return {
      doctype: "File",
      filters: {
        attached_to_doctype: "Job Applicant",
        attached_to_name: applicationId,
      },
      fields: ["name", "file_name", "file_url", "file_size", "creation"],
      order_by: "creation asc",
    };
  },
  onSuccess(data) {
    if (!data) return;

    const filesList = data.map((f) => ({
      name: f.name,
      file_name: f.file_name,
      file_url: f.file_url,
      file_size: f.file_size,
      uploaded_on: f.creation,
    }));

    form.value.documents = filesList.filter(
      (f) => !f.file_name.toLowerCase().includes("resume")
    );

    profilePhoto.value = form.value.profile_photo || null;
  },
  auto: false,
});

const canViewApplication = computed(() => {
  return user.data?.email === form.value.email_id;
});

const canEditResource = createResource({
  url: "non_profit.non_profit.api.can_edit_job_application",
  makeParams() {
    return { applicant_id: applicationId };
  },
  onSuccess(data) {
    console.log("Can Edit Response:", data);

    if (!data) {
      toast.warning(data?.reason || "This application cannot be edited.");
    }
  },
  auto: true,
});

const updateApplicationResource = createResource({
  url: "non_profit.non_profit.api.update_job_application",
  makeParams() {
    return {
      id: applicationId,
      cover_letter: form.value.cover_letter,
      documents: documents.value,
      profile_photo: profilePhoto.value,
      resume: resume.value,
    };
  },
});

const handleProfilePhotoUpload = (file) => {
  profilePhoto.value = file;
  toast.success("Profile photo uploaded successfully");
};

const handleDocumentUpload = (file) => {
  const newDocument = {
    file_name: file.file_name,
    file_url: file.file_url,
    file_size: file.file_size,
    uploaded_on: new Date().toISOString(),
  };
  documents.value.push(newDocument);
  toast.success(`Document "${file.file_name}" uploaded successfully`);
};

const resume = ref(null);

const handleResumeUpload = (file) => {
  resume.value = {
    file_name: file.file_name,
    file_url: file.file_url,
    file_size: file.file_size,
    uploaded_on: new Date().toISOString(),
  };
  toast.success(`Resume "${file.file_name}" uploaded successfully`);
};

const removeResume = () => {
  if (confirm("Are you sure you want to remove the resume?")) {
    resume.value = null;
    toast.success("Resume removed successfully");
  }
};

const removeProfilePhoto = () => {
  if (confirm("Are you sure you want to remove the profile photo?")) {
    profilePhoto.value = null;
    toast.success("Profile photo removed");
  }
};

const removeDocument = (index) => {
  const doc = documents.value[index];
  if (confirm(`Are you sure you want to remove "${doc.file_name}"?`)) {
    documents.value.splice(index, 1);
    toast.success("Document removed successfully");
  }
};

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
