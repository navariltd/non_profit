<template>
  <div class="space-y-6">
    <div class="flex justify-end">
      <Button @click="editing = !editing">{{
        editing ? "Cancel Edit" : "Edit"
      }}</Button>
    </div>

    <ChildTable
      v-model="form.allergies"
      doctype="Allergy Table"
      label="Allergies"
      :autoEditGrid="false"
      :readOnly="!editing"
    />

    <ChildTable
      v-model="form.disabilities"
      doctype="Employee Disability"
      label="Disabilities"
      :autoEditGrid="false"
      :readOnly="!editing"
    />

    <FormControl
      v-model="form.health_information"
      label="Health Information"
      :readOnly="!editing"
      textarea
    />
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Button, FormControl } from "frappe-ui";
import ChildTable from "@/components/Controls/ChildTable.vue";

const props = defineProps({
  form: Object,
});

const editing = ref(false);
</script>
