<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl md:text-4xl mb-4 text-center font-bold text-gray-900">
      👋 Welcome back, {{ form?.full_name }}!
    </h1>

    <div v-if="loading" class="text-center py-20">
      <p class="text-gray-600">Loading user details...</p>
    </div>

    <div v-else class="bg-white shadow-md rounded p-4">
      <!-- Tabs -->
      <div class="flex border-b mb-4">
        <button
          v-for="(tab, i) in tabs"
          :key="i"
          @click="goToTab(i)"
          :class="[
            'py-2 px-4 font-medium transition-colors',
            currentTab === i
              ? 'border-b-2 border-red-600 text-red-600'
              : 'text-gray-600',
          ]"
        >
          {{ tab.title }}
        </button>
      </div>

      <component
        :is="tabs[currentTab].component"
        :form="form"
        @change="trackChanges"
      />

      <div class="flex justify-between items-center gap-4 mt-6">
        <div>
          <span
            v-if="hasUnsavedChanges"
            class="text-sm text-orange-600 font-medium"
          >
            You have unsaved changes
          </span>
        </div>
        <div class="flex gap-4">
          <button
            v-if="currentTab > 0"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
            @click="prevTab"
          >
            Back
          </button>
          <button
            v-if="currentTab < tabs.length - 1"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded"
            :disabled="saveInProgress"
            @click="nextTab"
          >
            Save & Continue
          </button>
          <button
            v-if="currentTab === tabs.length - 1"
            class="px-4 py-2 bg-red-700 hover:bg-red-800 text-white rounded"
            :disabled="saveInProgress"
            @click="saveProfile"
          >
            Save Profile
          </button>
        </div>
      </div>
    </div>

    <ErrorModal v-model="showErrorDialog" :errors="flatErrors" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { createResource, toast } from "frappe-ui";

import PersonalInfo from "@/components/Profile/PersonalInfo.vue";
import ContactLocation from "@/components/Profile/ContactLocation.vue";
import CitizenshipDocuments from "@/components/Profile/CitizenshipDocuments.vue";
import QualificationsSkills from "@/components/Profile/QualificationsSkills.vue";
import HealthDisabilities from "@/components/Profile/HealthDisabilities.vue";
import ErrorModal from "@/components/Modals/ErrorModal.vue";

const loading = ref(true);
const saveInProgress = ref(false);
const showErrorDialog = ref(false);
const currentTab = ref(0);
const hasUnsavedChanges = ref(false);
const changedFields = ref(new Set());
const flatErrors = ref("");

const originalFormData = ref({});

const tabs = [
  { title: "Personal Info", component: PersonalInfo },
  { title: "Contact & Location", component: ContactLocation },
  { title: "Citizenship & Documents", component: CitizenshipDocuments },
  { title: "Qualifications & Skills", component: QualificationsSkills },
  { title: "Health & Disabilities", component: HealthDisabilities },
];

const form = reactive({
  first_name: "",
  other_names: "",
  surname: "",
  full_name: "",
  email: "",
  phone: "",
  id_number: "",
  passport_number: "",
  date_of_birth: "",
  marital_status: "",
  number_of_dependants: "",
  blood_group: "",

  administrative_location: "",
  sub_county: "",
  county: "",
  ward: "",
  address__location: "",
  access_to_internet: "",

  citizenship: "",
  country_of_citizenship: "",
  supporting_documents: [],
  attachments: [],

  qualifications: [],
  skills: [],
  additional_skills: [],
  certification: [],
  licences: [],
  driving_licence: [],
  languages: [],

  health_information: "",
  allergies: [],
  disabilities: [],

  profile_photo: null,

  professional_summary: "",
  work_experience: [],
  education_history: [],
  awards: [],
  projects: [],
  references: [],
});

function populateForm(data) {
  Object.keys(form).forEach((key) => {
    if (data[key] !== undefined && data[key] !== null) form[key] = data[key];
  });
  originalFormData.value = JSON.parse(JSON.stringify(form));
  changedFields.value.clear();
  hasUnsavedChanges.value = false;
}

function trackChanges(field) {
  const currentValue = JSON.stringify(form[field]);
  const originalValue = JSON.stringify(originalFormData.value[field]);

  if (currentValue !== originalValue) {
    changedFields.value.add(field);
    hasUnsavedChanges.value = true;
  } else {
    changedFields.value.delete(field);
    hasUnsavedChanges.value = changedFields.value.size > 0;
  }
}

const userDetailsResource = createResource({
  url: "non_profit.non_profit.api.get_user_details",
  auto: true,
  onSuccess(data) {
    if (data) populateForm(data);
    loading.value = false;
  },
  onError(err) {
    toast.error(err.message || "Failed to fetch user details");
    loading.value = false;
  },
});

const saveUserResource = createResource({
  url: "non_profit.non_profit.api.save_user_details",
  makeParams() {
    const payload = {};
    changedFields.value.forEach((f) => (payload[f] = form[f]));
    return payload;
  },
  onSuccess() {
    toast.success("Profile saved successfully");
    originalFormData.value = JSON.parse(JSON.stringify(form));
    changedFields.value.clear();
    hasUnsavedChanges.value = false;
    saveInProgress.value = false;
  },
  onError(err) {
    toast.error(err.message || "Failed to save profile");
    saveInProgress.value = false;
  },
});

async function saveProfile() {
  if (!changedFields.value.size) return;
  saveInProgress.value = true;
  await saveUserResource.submit();
}

function goToTab(i) {
  currentTab.value = i;
}

function nextTab() {
  goToTab(Math.min(currentTab.value + 1, tabs.length - 1));
}

function prevTab() {
  goToTab(Math.max(currentTab.value - 1, 0));
}

onMounted(() => {
  if (!userDetailsResource.data) userDetailsResource.reload();
});
</script>
