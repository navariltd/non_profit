<template>
  <div class="bg-white border-b border-gray-200 shadow-sm">
    <h1 class="text-3xl font-bold text-center text-red-700 py-6">
      {{ __("Volunteer Signup") }}
    </h1>
  </div>

  <div v-if="!isLoggedIn" class="text-center py-20">
    <LogIn class="w-16 h-16 text-gray-400 mx-auto mb-4" />
    <h2 class="text-3xl font-bold text-gray-900 mb-4">Login Required</h2>
    <p class="text-gray-600 mb-8">
      Please log in to submit your volunteer application.
    </p>
    <Button
      variant="solid"
      class="bg-red-600 hover:bg-red-700 text-white"
      @click="redirectToLogin"
    >
      <template #prefix>
        <LogIn class="w-4 h-4" />
      </template>
      {{ __("Login to Continue") }}
    </Button>
  </div>

  <div
    v-else-if="alreadyApplied && applicationStatus !== 'Draft'"
    class="text-center py-10"
  >
    <PendingApproval />
  </div>

  <div
    v-else-if="
      !alreadyApplied || (alreadyApplied && applicationStatus === 'Draft')
    "
    class="min-h-screen flex flex-col"
  >
    <main class="flex-1 container mx-auto px-6 py-10">
      <div class="bg-white shadow-lg rounded-2xl p-8">
        <div class="w-full mb-10">
          <div
            v-if="alreadyApplied && applicationStatus === 'Draft'"
            class="text-center mb-6"
          >
            <h2 class="text-xl font-semibold text-orange-600">
              Continue Your Draft Application
            </h2>
            <p class="text-gray-600 text-sm">
              Complete and submit your volunteer application
            </p>
          </div>

          <div class="flex items-center justify-between relative">
            <div
              v-for="(step, i) in steps"
              :key="i"
              class="flex-1 flex flex-col items-center text-center relative group"
            >
              <div
                v-if="i < steps.length"
                class="absolute top-6 left-1/2 w-full h-1 -translate-x-1/2"
                :class="i < currentStep ? 'bg-red-600' : 'bg-gray-300'"
              ></div>

              <div
                class="relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-500 ease-in-out"
                :class="[
                  i < currentStep
                    ? 'bg-red-600 border-red-600 text-white shadow-md'
                    : i === currentStep
                      ? 'bg-white border-red-600 text-red-600 font-bold shadow-md scale-110'
                      : 'bg-gray-200 border-gray-300 text-gray-500',
                ]"
              >
                <span class="text-lg">{{ i + 1 }}</span>
              </div>
            </div>
          </div>
        </div>

        <section v-if="currentStep === 0">
          <StepOrganization v-model="form" :errors="errors" />
        </section>
        <section v-if="currentStep === 1">
          <StepAdditional v-model="form" :errors="errors" />
        </section>
        <section v-if="currentStep === 2">
          <StepDocuments
            v-model="form"
            :documents="documents"
            :errors="errors"
          />
        </section>

        <section v-if="currentStep === 3" class="space-y-6">
          <h2 class="text-2xl font-bold text-red-700">
            {{ __("Review Your Application") }}
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-gray-700">
            <div
              v-for="(value, key) in summaryData"
              :key="key"
              class="p-4 border rounded-md"
            >
              <p class="text-sm font-semibold text-gray-500 capitalize">
                {{ formatLabel(key) }}
              </p>
              <p class="mt-1">{{ formatValue(value) }}</p>
            </div>
          </div>
        </section>

        <div class="flex justify-end gap-4 mt-10">
          <Button v-if="currentStep > 0" @click="prevStep">
            {{ __("Back") }}
          </Button>
          <Button
            v-if="currentStep < steps.length - 1"
            @click="nextStep"
            variant="solid"
            :loading="saveInProgress"
          >
            {{ __("Save & Continue") }}
          </Button>
          <Button
            v-if="currentStep === steps.length - 1"
            class="bg-red-700 text-white"
            variant="solid"
            :loading="saveInProgress"
            @click="showSubmitDialog = true"
          >
            {{
              alreadyApplied && applicationStatus === "Draft"
                ? __("Submit Application")
                : __("Submit Application")
            }}
          </Button>
        </div>
      </div>
    </main>
  </div>

  <Dialog v-model="showSubmitDialog">
    <template #body-title>
      <h2 class="text-lg font-bold text-gray-900">
        {{ __("Confirm Submission") }}
      </h2>
    </template>

    <template #body-content>
      <p class="text-gray-700 leading-relaxed">
        {{ __("Are you sure you want to submit this application?") }}
      </p>
      <p class="mt-2 text-sm text-red-600 font-medium">
        {{ __("You won't be able to make further edits after submission.") }}
      </p>
    </template>

    <template #actions>
      <div class="flex flex-col gap-3 sm:flex-row sm:justify-end">
        <Button
          variant="outline"
          class="w-full sm:w-auto py-3"
          @click="showSubmitDialog = false"
        >
          {{ __("Cancel") }}
        </Button>
        <Button
          variant="solid"
          class="w-full sm:w-auto bg-red-700 hover:bg-red-800 text-white py-3"
          @click="confirmSubmit"
        >
          <template #prefix>
            <FeatherIcon name="check-circle" class="w-4" />
          </template>
          {{ __("Submit") }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from "vue";
import { Button, toast, createResource, Dialog } from "frappe-ui";
import { LogIn } from "lucide-vue-next";
import PendingApproval from "@/components/PendingApproval.vue";
import StepOrganization from "@/components/Signup/StepOrganization.vue";
import StepAdditional from "@/components/Signup/StepAdditional.vue";
import StepDocuments from "@/components/Signup/StepDocuments.vue";
import { usersStore } from "../stores/user";
import { sessionStore } from "../stores/session";
import { useRouter } from "vue-router";

const { userResource } = usersStore();
const { isLoggedIn } = sessionStore();
const user = userResource;
const router = useRouter();

const currentStep = ref(0);
const steps = [
  { title: "Organization & Personal Info" },
  { title: "Additional Info" },
  { title: "Documents" },
  { title: "Review & Submit" },
];

const applicationId = ref(null);
const alreadyApplied = ref(false);
const applicationStatus = ref(null);
const documents = ref([]);
const saveInProgress = ref(false);
const showSubmitDialog = ref(false);

const form = reactive({
  company: "",
  mpesa_mobile_phone: "",
  date_of_birth: "",
  id_number: "",
  passport_number: "",
  marital_status: "",
  education: "",
  profession: "",
  access_to_internet: "",
  citizenship: "",
  number_of_dependants: null,
  reason_to_join: "",
  disabilities: "",
  has_insurance: "",
  languages: [],
  driving_licences: [],
  licences: [],
  blood_group: "",
  additional_skills: "",
  ward: "",
});

const errors = reactive({});

const stepFields = {
  0: [
    "company",
    "ward",
    "date_of_birth",
    "id_number",
    "passport_number",
    "mpesa_mobile_phone",
    "number_of_dependants",
    "marital_status",
    "blood_group",
    "has_insurance",
    "citizenship",
    "education",
  ],
  1: [
    "access_to_internet",
    "profession",
    "languages",
    "disabilities",
    "reason_to_join",
    "driving_licences",
    "licences",
  ],
  2: ["documents"],
};

function getCurrentStepData() {
  const currentStepData = {};
  const currentStepFieldList = stepFields[currentStep.value] || [];

  currentStepFieldList.forEach((field) => {
    if (field === "documents") {
      currentStepData.documents = documents.value;
    } else {
      currentStepData[field] = form[field];
    }
  });

  currentStepData.is_volunteer = true;
  if (user.data?.email) {
    currentStepData.email_id = user.data.email;
  }

  return currentStepData;
}

const jobApplication = createResource({
  url: "non_profit.non_profit.api.get_list",
  makeParams() {
    return {
      doctype: "Job Applicant",
      filters: {
        email_id: user.data?.email,
        is_volunteer: true,
      },
      fields: ["*"],
    };
  },
  auto: true,
  reloadOn: () => !!user.data?.email,
  onSuccess(data) {
    if (data?.length) {
      const application = data[0];
      alreadyApplied.value = true;
      applicationStatus.value =
        application.status || application.workflow_state;
      applicationId.value = application.name;

      if (applicationStatus.value === "Draft") {
        populateForm(application);
        toast.info("Continuing your draft application...");
      }
    } else {
      form.email_id = user.data?.email || "";
    }
  },
});

const submitApplicationResource = createResource({
  url: "non_profit.non_profit.api.submit_job_application",
  makeParams() {
    return {
      id: applicationId.value,
    };
  },
});

const confirmSubmit = async () => {
  submitApplicationResource.submit(
    {},
    {
      onSuccess: () => {
        toast.success("Application submitted successfully");
        showSubmitDialog.value = false;
        alreadyApplied.value = true;
      },
      onError: (err) => {
        toast.error(err.messages?.[0] || "Submission failed");
      },
    }
  );
};

const createApplication = createResource({
  url: "non_profit.non_profit.api.create_job_application",
  makeParams() {
    return getCurrentStepData();
  },
  onSuccess(data) {
    applicationId.value = data.name;
    toast.success("Application saved successfully");
    saveInProgress.value = false;
  },
  onError(error) {
    console.error("Create application error:", error);
    toast.error("Failed to save application");
    saveInProgress.value = false;
  },
});

const updateApplication = createResource({
  url: "non_profit.non_profit.api.update_job_application",
  makeParams() {
    const stepData = getCurrentStepData();
    return {
      id: applicationId.value,
      ...stepData,
    };
  },
  onSuccess(data) {
    toast.success("Application updated successfully");
    saveInProgress.value = false;
  },
  onError(error) {
    console.error("Update application error:", error);
    toast.error("Failed to update application");
    saveInProgress.value = false;
  },
});

const summaryData = computed(() => ({
  company: form.company,
  mpesa_mobile_phone: form.mpesa_mobile_phone,
  date_of_birth: form.date_of_birth,
  id_number: form.id_number,
  passport_number: form.passport_number,
  marital_status: form.marital_status,
  profession: form.profession,
  citizenship: form.citizenship,
  access_to_internet: form.access_to_internet,
  reason: form.reason_to_join,
  disabilities: form.disabilities,
  languages: form.languages,
  number_of_dependants: form.number_of_dependants,
  driving_licences: form.driving_licences,
  has_insurance: form.has_insurance,
  blood_group: form.blood_group,
  additional_skills: form.additional_skills,
  ward: form.ward,
}));

function formatLabel(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
}

function formatValue(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  return value || "—";
}

function populateForm(data) {
  Object.keys(form).forEach((key) => {
    if (data[key] !== undefined && data[key] !== null) {
      form[key] = data[key];
    }
  });

  if (data.languages && Array.isArray(data.languages)) {
    form.languages = data.languages;
  }
  if (data.driving_licences && Array.isArray(data.driving_licences)) {
    form.driving_licences = data.driving_licences;
  }
  if (data.licences && Array.isArray(data.licences)) {
    form.licences = data.licences;
  }

  if (data.documents && Array.isArray(data.documents)) {
    documents.value = data.documents;
  }
}

function redirectToLogin() {
  router.push("/login");
}

function validateStep(stepIndex) {
  let valid = true;
  Object.keys(errors).forEach((k) => (errors[k] = ""));

  if (stepIndex === 0) {
    if (!form.company) {
      errors.company = __("Branch is required");
      valid = false;
    }
    if (!form.mpesa_mobile_phone) {
      errors.mpesa_mobile_phone = __("Phone number is required");
      valid = false;
    }
  }

  if (stepIndex === 1) {
    if (!form.date_of_birth) {
      errors.date_of_birth = __("Date of birth is required");
      valid = false;
    }
    if (!form.id_number && !form.passport_number) {
      errors.id_number = __("Passport / ID number is required");
      valid = false;
    }
  }

  return valid;
}

async function saveApplication() {
  saveInProgress.value = true;

  try {
    if (!applicationId.value) {
      await createApplication.submit();
    } else {
      await updateApplication.submit();
    }
  } catch (error) {
    console.error("Save error:", error);
    saveInProgress.value = false;
  }
}

async function nextStep() {
  if (!validateStep(currentStep.value)) {
    toast.error("Please fix errors before continuing.");
    return;
  }

  await saveApplication();

  if (!saveInProgress.value && currentStep.value < steps.length - 1) {
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

async function submitResume() {
  for (let i = 0; i < steps.length - 1; i++) {
    if (!validateStep(i)) {
      currentStep.value = i;
      toast.error("Please complete required fields.");
      return;
    }
  }

  await saveApplication();

  if (!saveInProgress.value) {
    toast.success("Application submitted successfully!");

    jobApplication.reload();
  }
}
</script>
