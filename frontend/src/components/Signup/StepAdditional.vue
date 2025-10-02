<template>
  <section>
    <h2 class="text-xl font-bold text-red-700 mb-4">
      {{ __("Additional Information") }}
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <FormControl
        v-model="localModel.access_to_internet"
        :label="__('Access to Internet')"
        type="select"
        :required="true"
        :options="internetOptions"
      />

      <Link
        v-model="localModel.profession"
        :label="__('Profession')"
        :required="true"
        doctype="Profession"
      />

      <FormControl
        v-model="localModel.reason_to_join_krcs"
        :label="__('Reason for Joining')"
        type="select"
        :required="true"
        :options="reasonsOptions"
      />

      <MultiSelect
        v-model="localModel.languages"
        doctype="Language"
        :label="__('Languages')"
      />

      <MultiSelect
        v-model="localModel.driving_licence"
        :label="__('Driving Licence')"
        doctype="Driving Licence Class"
      />

      <div class="w-full md:col-span-2 space-y-6">
        <ChildTable
          v-model="localModel.disabilities"
          doctype="Employee Disability"
          label="Disabilities"
          :autoEditGrid="true"
          :field-queries="disabilityQueries"
          :form-data="localModel"
          @validationErrors="onChildErrors('disabilities', $event)"
        />

        <ChildTable
          v-model="localModel.education"
          :doctype="'Employee Education'"
          :autoEditGrid="true"
          label="Education"
          @validationErrors="onChildErrors('education', $event)"
        />

        <ChildTable
          v-model="localModel.licences"
          :doctype="'Personnel Licence'"
          :autoEditGrid="true"
          label="Licences"
          @validationErrors="onChildErrors('licences', $event)"
        />

        <ChildTable
          v-model="localModel.certification"
          :doctype="'Certification'"
          :autoEditGrid="true"
          label="Certifications"
          @validationErrors="onChildErrors('certification', $event)"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { FormControl } from "frappe-ui";
import MultiSelect from "@/components/Controls/MultiSelect.vue";
import Link from "@/components/Controls/Link.vue";
import ChildTable from "../Controls/ChildTable.vue";

const props = defineProps({
  modelValue: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["update:modelValue", "update:errors"]);

const localModel = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

function onChildErrors(tableName, errMap) {
  const newErrors = {
    ...props.errors,
    [tableName]: Object.fromEntries(errMap),
  };
  emit("update:errors", newErrors);
}

const reasonsOptions = [
  { label: "Humanitarian", value: "Humanitarian" },
  { label: "Social Cohesion", value: "Social Cohesion" },
  { label: "Personal", value: "Personal" },
];

const internetOptions = [
  { label: "Yes", value: "Yes" },
  { label: "No", value: "No" },
  { label: "Sometimes", value: "Sometimes" },
];

const disabilityQueries = {
  disability: (row, allRows, formData) => {
    return {
      disability_category: row.disability_category || null,
    };
  },
};
</script>
