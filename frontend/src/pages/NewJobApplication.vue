<template>
  <div class="max-w-5xl mx-auto py-10 space-y-8">
    <!-- Job Header -->
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

    <!-- Already Applied Notice -->
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

    <!-- Application Form -->
    <div
      v-else
      class="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
    >
      <h2 class="text-2xl font-bold text-red-700 mb-6">
        Apply for this Opportunity
      </h2>

      <form class="space-y-10" @submit.prevent="submitApplication">
        <!-- Personal Information -->
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

        <!-- Documents -->
        <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 class="text-xl font-semibold text-gray-800 mb-6">Documents</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Profile Photo -->
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
                    class="w-24 h-24 rounded-lg object-cover"
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

            <!-- Resume -->
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
        </div>

        <!-- Cover Letter -->
        <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 class="text-xl font-semibold text-gray-800 mb-6">Cover Letter</h3>
          <FormControl
            v-model="form.cover_letter"
            :label="__('Cover Letter')"
            type="textarea"
            :rows="10"
            placeholder="Write your cover letter here"
          />
        </div>

        <!-- Submit Button -->
        <div class="flex justify-end">
          <Button
            type="submit"
            variant="solid"
            class="bg-red-700 hover:bg-red-800 text-white px-6 py-3 rounded-lg"
          >
            Submit Application
          </Button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Button, FormControl, toast, createResource } from "frappe-ui";
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
  url: "non_profit.non_profit.api.submit_job_application",
  makeParams() {
    return {
      job_opening: jobId,
      ...form.value,
      resume: resume.value?.name,
      profile_photo: profilePhoto.value?.name,
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
