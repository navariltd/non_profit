<template>
  <section>
    <h2 class="text-xl font-bold text-red-700 mb-4">
      {{ __("Organization & Personal Info") }}
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="space-y-6">
        <div>
          <Link
            v-model="localModel.company"
            :label="__('Branch / County')"
            doctype="Company"
            :required="true"
            :filters="{ is_group: 0 }"
          />
          <p v-if="errors.company" class="text-sm text-red-600 mt-1">
            {{ errors.company }}
          </p>
        </div>
        <div>
          <!-- <Link
          v-model="localModel.company"
          :label="__('County of Residence')"
          doctype="County"
          :required="true"
        />
        <p v-if="errors.county" class="text-sm text-red-600 mt-1">
          {{ errors.county }}
        </p> -->
        </div>
        <div v-if="localModel.company">
          <Link
            v-model="localModel.sub_county"
            :label="__('Sub County')"
            doctype="Sub County"
            :required="true"
            :filters="{ county: localModel.company }"
          />
          <p v-if="errors.sub_county" class="text-sm text-red-600 mt-1">
            {{ errors.sub_county }}
          </p>
        </div>
        <div v-if="localModel.sub_county">
          <Link
            v-model="localModel.location"
            :label="__('Location')"
            doctype="Administrative Location"
            :required="true"
            :filters="{ sub_county: localModel.sub_county }"
          />
          <p v-if="errors.location" class="text-sm text-red-600 mt-1">
            {{ errors.location }}
          </p>
        </div>
        <div>
          <FormControl
            v-model="localModel.ward"
            :label="__('Ward')"
            type="text"
          />
          <p v-if="errors.ward" class="text-sm text-red-600 mt-1">
            {{ errors.ward }}
          </p>
        </div>
        <div>
          <FormControl
            v-model="localModel.citizenship"
            :label="__('Citizenship')"
            type="select"
            :options="citizenshipOptions"
            :required="true"
          />
          <p v-if="errors.citizenship" class="text-sm text-red-600 mt-1">
            {{ errors.citizenship }}
          </p>
        </div>
        <div v-if="localModel.citizenship === 'Citizen'">
          <FormControl
            :required="localModel.citizenship === 'Citizen'"
            v-model="localModel.id_number"
            :label="__('National ID')"
            type="text"
          />
          <p v-if="errors.id_number" class="text-sm text-red-600 mt-1">
            {{ errors.id_number }}
          </p>
        </div>
        <div v-if="localModel.citizenship !== 'Citizen'">
          <FormControl
            :required="localModel.citizenship !== 'Citizen'"
            v-model="localModel.passport_number"
            :label="__('Passport Number')"
            type="text"
          />
          <p v-if="errors.passport_number" class="text-sm text-red-600 mt-1">
            {{ errors.passport_number }}
          </p>
        </div>
      </div>

      <div class="space-y-6">
        <FormControl
          v-model="localModel.date_of_birth"
          :label="__('Date of Birth')"
          type="date"
          :required="true"
        />
        <p v-if="errors.date_of_birth" class="text-sm text-red-600 mt-1">
          {{ errors.date_of_birth }}
        </p>

        <FormControl
          v-model="localModel.marital_status"
          :label="__('Marital Status')"
          type="select"
          :options="maritalOptions"
        />
        <p v-if="errors.marital_status" class="text-sm text-red-600 mt-1">
          {{ errors.marital_status }}
        </p>

        <FormControl
          v-model="localModel.number_of_dependants"
          :label="__('Number of Dependants')"
          type="number"
        />
        <p v-if="errors.number_of_dependants" class="text-sm text-red-600 mt-1">
          {{ errors.number_of_dependants }}
        </p>

        <FormControl
          v-model="localModel.mpesa_mobile_phone"
          :label="__('Mobile Money (M-Pesa) phone if different')"
          type="tel"
        />
        <p v-if="errors.mpesa_mobile_phone" class="text-sm text-red-600 mt-1">
          {{ errors.mpesa_mobile_phone }}
        </p>

        <FormControl
          v-model="localModel.blood_group"
          :label="__('Blood Group')"
          type="select"
          :options="bloodGroupOptions"
        />
        <p v-if="errors.blood_group" class="text-sm text-red-600 mt-1">
          {{ errors.blood_group }}
        </p>

        <FormControl
          v-model="localModel.has_insurance"
          :label="__('KRCS Insurance')"
          type="select"
          :options="yesNoOptions"
        />
        <p v-if="errors.has_insurance" class="text-sm text-red-600 mt-1">
          {{ errors.has_insurance }}
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { FormControl } from "frappe-ui";
import Link from "@/components/Controls/Link.vue";
import ChildTable from "../Controls/ChildTable.vue";
import { computed } from "vue";

const props = defineProps({
  modelValue: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["update:modelValue"]);

const localModel = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});

const maritalOptions = [
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
  { label: "Don't Know", value: "Don't Know" },
];

const yesNoOptions = [
  { label: "Yes", value: "Yes" },
  { label: "No", value: "No" },
];

const citizenshipOptions = [
  { label: "Citizen", value: "Citizen" },
  { label: "Non-citizen", value: "Non-citizen" },
  { label: "Refugee", value: "Refugee" },
  { label: "Migrant", value: "Migrant" },
  { label: "Other", value: "Other" },
];
</script>
