<template>
  <div class="space-y-6">
    <div class="flex justify-end">
      <Button @click="editing = !editing" variant="solid" class="px-8">
        {{ editing ? "Cancel Edit" : "Edit" }}
      </Button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <FormControl
        v-model="form.first_name"
        label="First Name"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.other_names"
        label="Other Names"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.surname"
        label="Surname"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.full_name"
        label="Full Name"
        :readOnly="!editing"
      />
      <FormControl v-model="form.email" label="Email" :readOnly="!editing" />
      <FormControl v-model="form.phone" label="Phone" :readOnly="!editing" />
      <FormControl
        v-model="form.citizenship"
        :label="__('Citizenship')"
        type="select"
        :options="citizenshipOptions"
        :required="true"
      />
      <FormControl
        v-if="form.citizenship === 'Citizen'"
        v-model="form.id_number"
        label="ID Number"
        :readOnly="!editing"
      />
      <Link
        v-if="form.citizenship !== 'Citizen'"
        doctype="Country"
        v-model="form.country_of_citizenship"
        :label="__('Country of Citizenship')"
      />
      <FormControl
        v-if="form.citizenship !== 'Citizen'"
        v-model="form.passport_number"
        label="Passport Number"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.date_of_birth"
        label="Date of Birth"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.marital_status"
        label="Marital Status"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.number_of_dependants"
        label="Number of Dependants"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.blood_group"
        label="Blood Group"
        :readOnly="!editing"
      />
      <FormControl
        v-model="form.professional_summary"
        label="Professional Summary"
        :readOnly="!editing"
        textarea
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { Button, FormControl } from "frappe-ui";
import Link from "@/components/Controls/Link.vue";

const props = defineProps({
  form: {
    type: Object,
    default: () => ({
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
      professional_summary: "",
      citizenship: "",
      country_of_citizenship: "",
    }),
  },
});
const citizenshipOptions = [
  { label: "Citizen", value: "Citizen" },
  { label: "Non-citizen", value: "Non-citizen" },
  { label: "Refugee", value: "Refugee" },
  { label: "Migrant", value: "Migrant" },
  { label: "Other", value: "Other" },
];
const emit = defineEmits(["change"]);

const editing = ref(false);

watch(
  props.form,
  (newVal, oldVal) => {
    emit("change");
  },
  { deep: true }
);
</script>
