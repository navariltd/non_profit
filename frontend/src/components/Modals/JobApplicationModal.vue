<template>
  <Dialog
    v-model="show"
    class="text-base"
    :options="{
      title: __('Apply for this opportunity'),
      size: '6xl',
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
              "Please complete the form below to proceed with your application. Your details will be shared with the opportunity poster."
            )
          }}
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-if="!hidePersonalInfo && !showOnlyDocsProfile"
            class="lg:col-span-2"
          >
            <h3 class="text-lg font-bold text-gray-800 mb-4">
              Personal Information
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <FormControl
                v-model="form.surname"
                :label="__('Surname')"
                type="text"
                :placeholder="__('Enter your surname')"
                :required="isPersonalInfoRequired"
              />

              <FormControl
                v-model="form.other_names"
                :label="__('Other Names')"
                type="text"
                :placeholder="__('Enter your other names')"
                :required="isPersonalInfoRequired"
              />

              <FormControl
                v-model="form.email_id"
                :label="__('Email Address')"
                type="email"
                :placeholder="__('Enter your email address')"
                :required="isPersonalInfoRequired"
              />

              <FormControl
                v-model="form.phone"
                :label="__('Phone Number')"
                type="tel"
                :placeholder="__('Enter your phone number')"
                :required="isPersonalInfoRequired"
              />

              <FormControl
                v-model="form.mpesa_mobile_phone"
                :label="__('MPESA Mobile Phone (if different)')"
                type="tel"
                :placeholder="__('Enter MPESA number')"
              />

              <Link
                v-model="form.gender"
                :label="__('Gender')"
                :placeholder="__('Select Gender')"
                doctype="Gender"
                :required="isPersonalInfoRequired"
              />

              <FormControl
                v-model="form.date_of_birth"
                :label="__('Date of Birth')"
                type="date"
              />

              <FormControl
                v-model="form.idpassport_number"
                :label="__('ID/Passport Number')"
                type="text"
                :placeholder="__('Enter ID or Passport number')"
                :required="isPersonalInfoRequired"
              />
            </div>
          </div>

          <!-- Additional Information -->
          <div v-if="!showOnlyDocsProfile" class="lg:col-span-2">
            <h3 class="text-lg font-bold text-gray-800 mb-4 mt-6">
              Additional Information
            </h3>
            <div
              class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-4"
            >
              <FormControl
                v-model="form.marital_status"
                :label="__('Marital Status')"
                type="select"
                :options="[
                  { label: 'Single', value: 'Single' },
                  { label: 'Married', value: 'Married' },
                  { label: 'Divorced', value: 'Divorced' },
                  { label: 'Widowed', value: 'Widowed' },
                ]"
                :placeholder="__('Select Status')"
              />

              <FormControl
                v-model="form.highest_level_of_education"
                :label="__('Highest Level of Education')"
                type="select"
                :options="[
                  { label: 'Nursery', value: 'Nursery' },
                  { label: 'Primary', value: 'Primary' },
                  { label: 'Secondary', value: 'Secondary' },
                  { label: 'Vocational', value: 'Vocational' },
                  {
                    label: 'Tertiary/University',
                    value: 'Tertiary/University',
                  },
                  { label: 'None', value: 'None' },
                ]"
                :placeholder="__('Select Education Level')"
              />

              <FormControl
                v-model="form.profession"
                :label="__('Profession')"
                type="text"
                :placeholder="__('e.g., Engineer, Teacher, Nurse')"
              />

              <FormControl
                v-model="form.place_of_work"
                :label="__('Place of Work')"
                type="text"
                :placeholder="__('Enter current place of work')"
              />

              <FormControl
                v-model="form.ward"
                :label="__('Region & Ward')"
                type="text"
                :placeholder="__('e.g., Nairobi, Starehe')"
              />

              <FormControl
                v-model="form.blood_group"
                :label="__('Blood Group')"
                type="select"
                :options="[
                  { label: 'A+', value: 'A+' },
                  { label: 'A-', value: 'A-' },
                  { label: 'B+', value: 'B+' },
                  { label: 'B-', value: 'B-' },
                  { label: 'AB+', value: 'AB+' },
                  { label: 'AB-', value: 'AB-' },
                  { label: 'O+', value: 'O+' },
                  { label: 'O-', value: 'O-' },
                ]"
                :placeholder="__('Select Blood Group')"
              />
            </div>

            <div
              class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-300"
            >
              <MultiSelect
                doctype="Training Program"
                v-model="form.trainings"
                :label="__('Trainings')"
                class="w-full"
              />
              <MultiSelect
                doctype="Language"
                v-model="form.languages"
                :label="__('Languages')"
                class="w-full"
              />
              <FormControl
                v-model="form.other_languages"
                :label="__('Other Languages')"
                type="textarea"
                :rows="6"
                :placeholder="
                  __(
                    'Tell us about other languages you speak (separate with commas or new lines)'
                  )
                "
              />
              <FormControl
                v-model="form.reason_to_join"
                :label="__('Reason for Joining')"
                type="textarea"
                :rows="6"
                :placeholder="__('Tell us why you want to join')"
              />
              <FormControl
                v-model="form.allergies"
                :label="__('Allergies')"
                type="textarea"
                :rows="6"
                :placeholder="
                  __(
                    'List any known allergies (separate with commas or new lines)'
                  )
                "
              />
              <FormControl
                v-model="form.disabilities"
                :label="__('Disabilities (if any)')"
                type="textarea"
                :rows="6"
                :placeholder="
                  __(
                    'List any disabilities (separate with commas or new lines)'
                  )
                "
              />
              <FormControl
                v-model="form.additional_skills"
                :label="__('Additional Skills')"
                type="textarea"
                :rows="6"
                :placeholder="
                  __(
                    'e.g., First Aid, Public Speaking, IT Skills (separate with commas or new lines)'
                  )
                "
              />
            </div>
          </div>
        </div>

        <hr class="border-t border-gray-300 my-4" />

        <div class="lg:col-span-2">
          <h3 class="text-lg font-bold text-gray-800 mb-4">
            Documents & Profile Photo
          </h3>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label class="block mb-2 font-semibold text-gray-800">{{
                __("Profile Photo")
              }}</label>
              <div v-if="!profilePhoto">
                <Uploader
                  label="Upload Profile Photo"
                  :required="false"
                  :fileTypes="['.jpg', '.jpeg', '.png']"
                  :maxSize="5"
                  :multiple="false"
                  :onError="handleError"
                  :onSuccess="(data) => (profilePhoto = data)"
                />
              </div>
              <div
                v-else
                class="flex items-center p-3 rounded-xl bg-gray-50 justify-between"
              >
                <div class="flex items-center">
                  <div class="border rounded-md p-2 mr-3 bg-white shadow-sm">
                    <FileText class="h-6 w-6 text-gray-600" />
                  </div>
                  <div>
                    <a
                      :href="profilePhoto.file_url"
                      target="_blank"
                      class="font-medium text-gray-800 hover:underline"
                    >
                      {{ profilePhoto.file_name }}
                    </a>
                  </div>
                </div>
                <Button
                  variant="subtle"
                  @click="profilePhoto = null"
                  class="text-red-500 hover:text-red-700 rounded-full p-1.5 flex items-center justify-center transition-colors duration-200 hover:bg-red-100"
                >
                  <span class="sr-only">Remove file</span>
                  ✕
                </Button>
              </div>
            </div>

            <div>
              <label class="block mb-2 font-semibold text-gray-800">{{
                __("Upload Resume")
              }}</label>
              <div v-if="!resume">
                <Uploader
                  label="Upload Resume"
                  :required="true"
                  :fileTypes="['.pdf', '.docx', '.doc']"
                  :maxSize="5"
                  :multiple="false"
                  :validateFile="validateFile"
                  :onSuccess="(file) => (resume = file)"
                  :onError="handleError"
                />
              </div>
              <div
                v-else
                class="flex items-center p-3 border rounded-xl bg-gray-50 justify-between"
              >
                <div class="flex items-center">
                  <div class="border rounded-md p-2 mr-3 bg-white shadow-sm">
                    <FileText class="h-6 w-6 text-gray-600" />
                  </div>
                  <div>
                    <a
                      :href="resume.file_url"
                      target="_blank"
                      class="font-medium text-gray-800 hover:underline"
                    >
                      {{ resume.file_name }}
                    </a>
                  </div>
                </div>
                <Button
                  variant="subtle"
                  @click="resume = null"
                  class="text-red-500 hover:text-red-700 rounded-full p-1.5 flex items-center justify-center transition-colors duration-200 hover:bg-red-100"
                >
                  <span class="sr-only">Remove file</span>
                  ✕
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div>
          <FormControl
            v-model="form.cover_letter"
            :label="__('Cover Letter')"
            type="textarea"
            :rows="15"
            :placeholder="__('Write your cover letter here')"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, inject, computed } from "vue";
import { useRoute } from "vue-router";
import { usersStore } from "../../stores/user";
import { Dialog, FormControl, toast, createResource, Button } from "frappe-ui";
import Link from "@/components/Controls/Link.vue";
import MultiSelect from "@/components/Controls/MultiSelect.vue";
import Uploader from "@/components/Controls/Uploader.vue";
import { FileText } from "lucide-vue-next";

const resume = ref(null);
const profilePhoto = ref(null);
const show = defineModel();
const application = defineModel("application");

const user = inject("$user");
const { roleResource } = usersStore();

const props = defineProps({
  job: { type: String, required: false, default: "" },
});

const form = ref({
  surname: "",
  other_names: "",
  email_id: "",
  phone: "",
  mpesa_mobile_phone: "",
  gender: "",
  date_of_birth: "",
  idpassport_number: "",
  marital_status: "",
  highest_level_of_education: "",
  profession: "",
  place_of_work: "",
  reason_to_join: "",
  allergies: "",
  disabilities: "",
  languages: "",
  other_languages: "",
  trainings: "",
  blood_group: "",
  additional_skills: "",
  ward: "",
  cover_letter: "",
});

const hidePersonalInfo = computed(() => roleResource.data?.name);
const showOnlyDocsProfile = computed(() => roleResource.data?.employee);
const isPersonalInfoRequired = computed(() => !showOnlyDocsProfile.value);

const validateFile = (file) => {
  let extension = file.name.split(".").pop().toLowerCase();
  if (!["pdf", "docx", "doc"].includes(extension)) {
    return "Only PDF and Word documents are allowed";
  }
};

const opportunityApplication = createResource({
  url: "non_profit.non_profit.api.submit_job_application",
  makeParams(values) {
    return {
      job_opening: props.job,
      ...form.value,
      resume: resume.value?.name,
      profile_photo: profilePhoto.value?.name,
    };
  },
});

const submitResume = (close) => {
  opportunityApplication.submit(
    {},
    {
      validate() {
        if (!hidePersonalInfo) {
          if (!form.value.surname) return "Surname is required";
          if (!form.value.other_names) return "Other names are required";
          if (!form.value.email_id) return "Email is required";
          if (!form.value.phone) return "Phone number is required";
          if (!form.value.idpassport_number)
            return "ID/Passport number is required";
        }
      },
      onSuccess() {
        if (opportunityApplication?.data?.success) {
          toast.success("Your application has been submitted successfully");
          application.value.reload();
          close();
        } else {
          toast.error(
            opportunityApplication?.data?.message ||
              "An error occurred while submitting your application. Please try again."
          );
        }
      },
      onError(err) {
        toast.error(err.messages?.[0] || err);
      },
    }
  );
};

const handleError = (error) => {
  toast.error(error.message || "An error occurred during upload.");
};
</script>
