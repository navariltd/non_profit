<template>
  <form action="" @submit.prevent="submit">
    <div class="">
      <div class="mb-6">
        <h4 class="text-md font-medium mb-3 text-gray-700">Personal Details</h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Input
            name="mobile_money_number"
            type="text"
            placeholder="+254123456789"
            label="Mobile Money Number"
            v-model="volunteerForm.mobile_money_number"
          />
          <Input
            name="date_of_birth"
            type="date"
            label="Date of Birth"
            v-model="volunteerForm.date_of_birth"
          />
          <Input
            name="idpassport"
            type="text"
            placeholder="ID/Passport Number"
            label="ID/Passport Number"
            v-model="volunteerForm.idpassport"
          />

          <div class="flex flex-col">
            <label class="text-gray-600 text-sm mb-2">Marital Status</label>
            <Select
              v-model="volunteerForm.marital_status"
              class=""
              :options="maritalStatusOptions"
            />
          </div>
          <div class="flex flex-col">
            <label class="text-gray-600 text-sm mb-2">Blood Group</label>
            <Select
              v-model="volunteerForm.blood_group"
              class=""
              :options="bloodGroupOptions"
            />
          </div>
        </div>
      </div>

      <div class="mb-6">
        <h4 class="text-md font-medium mb-3 text-gray-700">
          Professional Information
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <h4 class="text-sm mb-2 font-medium text-gray-700">
              Education Level
            </h4>
            <Select
              v-model="volunteerForm.education"
              class=""
              :options="educationLevelOptions"
            />
          </div>
          <Input
            name="profession"
            type="text"
            placeholder="e.g., Teacher, Engineer"
            label="Profession"
            v-model="volunteerForm.profession"
          />
          <Input
            name="place_of_work"
            type="text"
            placeholder="Company/Organization"
            label="Place of Work"
            v-model="volunteerForm.place_of_work"
          />
        </div>
      </div>

      <div class="mb-6">
        <Textarea
          variant="subtle"
          size="sm"
          placeholder="Placeholder"
          label="Reason to Join Red Cross"
          v-model="volunteerForm.reason_to_join"
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div>
          <label class="text-gray-600 text-sm mb-2 block"
            >Languages Spoken</label
          >
          <div class="flex flex-col gap-2 border rounded-lg p-2">
            <Checkbox
              v-for="lang in languageOptions"
              :key="lang"
              size="sm"
              :value="lang"
              :label="lang"
              :model-value="volunteerForm.languages.includes(lang)"
              @update:model-value="(checked) => toggleLanguage(lang, checked)"
            />
          </div>
        </div>

        <div>
          <Textarea
            variant="subtle"
            size="sm"
            placeholder="e.g., CPR, Programming"
            label="Additional Skills"
            v-model="additionalSkillsString"
          />
        </div>
      </div>

      <div class="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div>
          <Textarea
            variant="subtle"
            size="sm"
            placeholder="e.g., Peanuts, Penicillin"
            label="Known Allergies"
            v-model="allergiesString"
          />
        </div>

        <div>
          <label class="text-gray-600 text-sm mb-2 block"></label>
          <Textarea
            variant="subtle"
            size="sm"
            placeholder="e.g., Blindness"
            label="Disabilities (if any)"
            v-model="disabilitiesString"
          />
        </div>
      </div>

      <div class="mt-6">
        <Textarea
          variant="subtle"
          size="sm"
          placeholder="e.g., First Aid, CPR"
          label="Previous KRCS Trainings"
          v-model="krcsTrainingsString"
        />
      </div>
    </div>

    <div class="flex flex-col justify-center gap-2 mt-5">
      <ErrorMessage
        :message="emptyVolunteerFormError"
        class="w-full border border-red-500 rounded-lg p-2"
      />
      <Button variant="solid" type="submit" size="md" class="w-full">
        Finish
      </Button>
    </div>
  </form>
</template>
<script setup lang="ts">
import Input from "frappe-ui/src/components/Input.vue";
import { computed, reactive, ref, toRaw } from "vue";
import { Checkbox, Button, Select, Textarea, ErrorMessage } from "frappe-ui";
import { membershipStore } from "../stores/membership";
import { VolunteerSignupData, initialVolunteerForm } from "../utils/volunteer";

const { membershipTypes } = membershipStore();
const emit = defineEmits(["volunteer-data-submitted"]);

const volunteerForm = reactive<VolunteerSignupData>({
  ...initialVolunteerForm,
});
const emptyVolunteerFormError = ref("");

const maritalStatusOptions = [
  { label: "Single", value: "Single" },
  { label: "Married", value: "Married" },
  { label: "Divorced", value: "Divorced" },
  { label: "Widowed", value: "Widowed" },
];

const bloodGroupOptions = [
  { label: "A+", value: "A+" },
  { label: "A-", value: "A-" },
  { label: "B+", value: "B+" },
  { label: "B-", value: "B-" },
  { label: "AB+", value: "AB+" },
  { label: "AB-", value: "AB-" },
  { label: "O+", value: "O+" },
  { label: "O-", value: "O-" },
];

// Options for multi-select fields
const languageOptions = ["English", "Swahili", "French", "Arabic", "Spanish"];

const educationLevelOptions = [
  { label: "Nursery", value: "Nursery" },
  { label: "Primary", value: "Primary" },
  { label: "Secondary", value: "Secondary" },
  { label: "Vocational", value: "Vocational" },
  { label: "Tertiary/University", value: "Tertiary/University" },
  { label: "None", value: "None" },
];

function toggleLanguage(lang: string, checked: boolean) {
  if (checked && !volunteerForm.languages.includes(lang)) {
    volunteerForm.languages.push(lang);
    console.log(volunteerForm.languages);
  } else if (!checked) {
    volunteerForm.languages = volunteerForm.languages.filter((l) => l !== lang);
  }
}
const allergiesString = computed({
  get: () => volunteerForm.allergies.join(", "),
  set: (val: string) => {
    volunteerForm.allergies = val
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  },
});

const disabilitiesString = computed({
  get: () => volunteerForm.disabilities.join(", "),
  set: (val: string) => {
    volunteerForm.disabilities = val
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  },
});

const krcsTrainingsString = computed({
  get: () => volunteerForm.krcs_trainings.join(", "),
  set: (val: string) => {
    volunteerForm.krcs_trainings = val
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  },
});

const additionalSkillsString = computed({
  get: () => volunteerForm.additional_skills.join(", "),
  set: (val: string) => {
    volunteerForm.additional_skills = val
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  },
});
function submit() {
  const rawVolunteerForm = toRaw(volunteerForm);

  for (const key of Object.keys(rawVolunteerForm)) {
    const value = rawVolunteerForm[key];
    if (typeof value === "string" && !value.trim()) {
      emptyVolunteerFormError.value =
        "Please fill in all required volunteer details.";
      return;
    } else if (Array.isArray(value) && value.length === 0) {
      emptyVolunteerFormError.value =
        "Please fill in all required volunteer details.";
      return;
    }
  }
  emptyVolunteerFormError.value = "";

  emit("volunteer-data-submitted", rawVolunteerForm);
}
</script>
