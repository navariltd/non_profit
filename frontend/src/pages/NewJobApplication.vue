<template>
  <div class="max-w-5xl mx-auto py-10 space-y-8">
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
          <h1 class="text-3xl font-bold text-gray-900 mb-1">
            {{ job.data.job_title }}
          </h1>
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
      v-if="isApplied"
      class="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center"
    >
      <h2 class="text-xl font-semibold text-yellow-800 mb-4">
        You’ve already applied for this job.
      </h2>
      <Button
        variant="solid"
        class="bg-red-700 hover:bg-red-800 text-white"
        @click="
          router.push({
            name: 'JobApplicationDetail',
            params: { id: applicationId },
          })
        "
      >
        View Your Application
      </Button>
    </div>

    <div
      v-else
      class="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
    >
      <h2 class="text-2xl font-bold text-red-700 mb-6">
        Apply for this Opportunity
      </h2>

      <form class="space-y-10" @submit.prevent="submitApplication">
        <div
          v-if="!user.data?.name"
          class="bg-gray-50 rounded-xl p-6 border border-gray-200"
        >
          <h3 class="text-xl font-semibold text-gray-800 mb-6">
            Personal Information
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormControl
              v-model="form.surname"
              :label="__('Surname')"
              type="text"
              placeholder="Enter surname"
              required
            />
            <FormControl
              v-model="form.other_names"
              :label="__('Other Names')"
              type="text"
              placeholder="Enter other names"
              required
            />
            <FormControl
              v-model="form.email_id"
              :label="__('Email Address')"
              type="email"
              placeholder="Enter email"
              required
            />
            <FormControl
              v-model="form.phone"
              :label="__('Phone Number')"
              type="tel"
              placeholder="Enter phone number"
              required
            />
          </div>
        </div>

        <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 class="text-xl font-semibold text-gray-800 mb-6">Documents</h3>
          <div class="grid grid-cols-1 gap-6">
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
                <div class="grid grid-cols-1 gap-4 justify-between w-full">
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

          <div class="mt-6">
            <label class="block mb-2 font-semibold text-gray-800"
              >Supporting Documents</label
            >
            <Uploader
              label="Upload Supporting Documents"
              :multi="true"
              :fileTypes="['.pdf', '.docx', '.doc', '.jpg', '.png']"
              :maxSize="10"
              :onSuccess="(file) => documents.push(file)"
              :onError="handleError"
            />
          </div>
        </div>

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

        <div class="flex justify-end">
          <Button
            type="submit"
            variant="solid"
            class="bg-red-700 hover:bg-red-800 text-white px-6 py-3 rounded-lg"
          >
            Save Application
          </Button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Button,
  FormControl,
  toast,
  createResource,
  TextEditor,
} from "frappe-ui";
import Uploader from "@/components/Controls/Uploader.vue";

const route = useRoute();
const router = useRouter();
const user = inject("$user");
const jobId = route.params?.job || "";

const isPDF = (url) => url?.toLowerCase().endsWith(".pdf");

const job = createResource({
  url: "non_profit.non_profit.api.get_job_details",
  params: { job: jobId },
  cache: ["job", jobId],
  auto: true,
});

const form = ref({
  surname: "",
  other_names: "",
  email_id: "",
  phone: "",
  cover_letter: "",
});

const resume = ref(null);
const profilePhoto = ref(null);
const documents = ref([]);

const jobApplication = createResource({
  url: "frappe.client.get_list",
  makeParams() {
    return {
      doctype: "Job Applicant",
      filters: { job_title: jobId, email_id: user.data?.email },
      fields: ["name"],
    };
  },
  auto: true,
  reloadOn: () => !!user.data?.email,
});

const isApplied = computed(() => jobApplication.data?.length > 0);
const applicationId = computed(() => jobApplication.data?.[0]?.name || null);

const opportunityApplication = createResource({
  url: "non_profit.non_profit.api.create_job_application",
  makeParams() {
    return {
      job_opening: jobId,
      ...form.value,
      resume: resume.value,
      documents: documents.value,
    };
  },
});

const submitApplication = () => {
  opportunityApplication.submit(
    {},
    {
      validate: () => {
        if (!form.value.cover_letter) return "Cover Letter is required";
      },
      onSuccess: (response) => {
        const applicationId = response?.name || response?.application_id;
        toast.success("Application submitted successfully");
        router.push({
          name: "JobApplicationDetail",
          params: { id: applicationId },
        });
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
</script>
