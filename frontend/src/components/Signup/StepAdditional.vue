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
        :options="internetOptions"
      />

      <Link
        v-model="localModel.profession"
        :label="__('Profession')"
        doctype="Profession"
      />
      <MultiSelect
        v-model="localModel.languages"
        doctype="Language"
        :label="__('Languages')"
      />
      <MultiSelect
        v-model="localModel.disabilities"
        :label="__('Disabilities')"
        doctype="Disability"
      />
      <FormControl
        v-model="localModel.reason_to_join"
        :label="__('Reason for Joining')"
        type="textarea"
        :rows="8"
      />

      <MultiSelect
        v-model="localModel.driving_licences"
        :label="__('Driving Licence')"
        doctype="Driving Licence Class"
      />
      <!-- <div class="w-full md:col-span-2 space-y-6">
        <ChildTable
          v-model="localModel.licences"
          :columns="[
            {
              key: 'licence_type',
              label: 'Type',
              type: 'link',
              doctype: 'Personnel License Type',
            },
            { key: 'institution', label: 'Institution', type: 'text' },
            { key: 'description', label: 'Description', type: 'text' },
            { key: 'valid_from', label: 'Valid From', type: 'date' },
            { key: 'valid_to', label: 'Valid To', type: 'date' },
          ]"
          :label="__('Certifications')"
        />
      </div> -->
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
const emit = defineEmits(["update:modelValue"]);

const localModel = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const internetOptions = [
  { label: "Yes", value: "Yes" },
  { label: "No", value: "No" },
  { label: "Sometimes", value: "Sometimes" },
];
</script>
