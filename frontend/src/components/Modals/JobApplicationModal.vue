<template>
  <Dialog
    v-model="show"
    class="text-base"
    :options="{
      title: __('Apply for this opportunity'),
      size: '2xl',
      actions: [
        {
          label: 'Submit',
          variant: 'solid',
          onClick: (close) => {
            submitResume(close);
          },
        },
      ],
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-6">
        <p class="text-gray-600">
          {{
            __(
              "Submit your resume and complete the form below to proceed with your application. Upon submission, it will be shared with the opportunity poster."
            )
          }}
        </p>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label class="block mb-1 font-semibold text-gray-800"
              >Applicant Name</label
            >
            <input
              v-model="form.applicant_name"
              type="text"
              class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-green-400 focus:ring focus:ring-green-100 outline-none"
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <label class="block mb-1 font-semibold text-gray-800"
              >Email Address</label
            >
            <input
              v-model="form.email"
              type="email"
              class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-green-400 focus:ring focus:ring-green-100 outline-none"
              placeholder="Enter your email address"
            />
          </div>

          <div>
            <label class="block mb-1 font-semibold text-gray-800"
              >Phone Number</label
            >
            <input
              v-model="form.phone"
              type="tel"
              class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-green-400 focus:ring focus:ring-green-100 outline-none"
              placeholder="Enter your phone number"
            />
          </div>

          <div>
            <label class="block mb-2 font-semibold text-gray-800">Resume</label>
            <div v-if="!resume">
              <FileUploader
                :fileTypes="['.pdf']"
                :validateFile="validateFile"
                @success="
                  (file) => {
                    resume = file;
                  }
                "
              >
                <template v-slot="{ progress, uploading, openFileSelector }">
                  <Button
                    @click="openFileSelector"
                    :loading="uploading"
                    class="bg-green-500 hover:bg-green-600 text-white font-semibold rounded-xl px-4 py-2"
                  >
                    {{
                      uploading
                        ? `Uploading ${progress}%`
                        : "Upload your resume"
                    }}
                  </Button>
                </template>
              </FileUploader>
            </div>
            <div
              v-else
              class="flex items-center p-3 border rounded-xl bg-gray-50"
            >
              <div class="border rounded-md p-2 mr-3 bg-white shadow-sm">
                <FileText class="h-6 w-6 text-gray-600" />
              </div>
              <div>
                <p class="font-medium text-gray-800">{{ resume.file_name }}</p>
                <p class="text-sm text-gray-500">
                  {{ getFileSize(resume.file_size) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block mb-2 font-semibold text-gray-800"
            >Cover Letter</label
          >
          <textarea
            v-model="form.cover_letter"
            rows="15"
            class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-green-400 focus:ring focus:ring-green-100 outline-none resize-none"
            placeholder="Write your cover letter here"
          ></textarea>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Dialog, FileUploader, Button, createResource, toast } from "frappe-ui";
import { FileText } from "lucide-vue-next";
import { ref, inject } from "vue";
import { getFileSize } from "@/utils/";
import { useRoute } from "vue-router";

const resume = ref(null);
const show = defineModel();
const user = inject("$user");
const application = defineModel("application");
const route = useRoute();

const props = defineProps({
  job: {
    type: String,
    required: false,
    default: "",
  },
});

const form = ref({
  applicant_name: "",
  email: "",
  phone: "",
  country: "",
  cover_letter: "",
});

const validateFile = (file) => {
  let extension = file.name.split(".").pop().toLowerCase();
  if (extension != "pdf") {
    return "Only PDF file is allowed";
  }
};

const opportunityApplication = createResource({
  url: "non_profit.non_profit.api.submit_job_application",
  makeParams(values) {
    return {
      job_opening: props.job,
      applicant_name: form.value.applicant_name,
      email: form.value.email,
      phone: form.value.phone,
      cover_letter: form.value.cover_letter,
      resume: resume.value?.file_name,
    };
  },
});

const submitResume = (close) => {
  opportunityApplication.submit(
    {},
    {
      validate() {
        if (!form.value.applicant_name) return "Applicant name is required";
        if (!form.value.email) return "Email is required";
      },
      onSuccess() {
        toast.success("Your application has been submitted successfully");
        application.value.reload();
        close();
      },
      onError(err) {
        toast.error(err.messages?.[0] || err);
      },
    }
  );
};
</script>
