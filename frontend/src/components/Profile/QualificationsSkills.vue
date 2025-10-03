<template>
  <div class="space-y-6">
    <div class="flex justify-end">
      <Button @click="editing = !editing">{{
        editing ? "Cancel Edit" : "Edit"
      }}</Button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <ChildTable
        v-model="form.qualifications"
        doctype="Employee Qualification"
        label="Qualifications"
        :autoEditGrid="false"
        :readOnly="!editing"
      />

      <ChildTable
        v-model="form.skills"
        doctype="Volunteer Skill"
        label="Skills"
        :autoEditGrid="false"
        :readOnly="!editing"
      />

      <ChildTable
        v-model="form.additional_skills"
        doctype="Additional Skill"
        label="Additional Skills"
        :autoEditGrid="false"
        :readOnly="!editing"
      />

      <ChildTable
        v-model="form.certification"
        doctype="Certification"
        label="Certifications"
        :autoEditGrid="false"
        :readOnly="!editing"
      />

      <ChildTable
        v-model="form.licences"
        doctype="Personnel Licence"
        label="Licences"
        :autoEditGrid="false"
        :readOnly="!editing"
      />

      <ChildTable
        v-model="form.driving_licence"
        doctype="Driving Licence"
        label="Driving Licence"
        :autoEditGrid="false"
        :readOnly="!editing"
      />

      <ChildTable
        v-model="form.languages"
        doctype="Volunteer Language"
        label="Languages"
        :autoEditGrid="false"
        :readOnly="!editing"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Button } from "frappe-ui";
import ChildTable from "@/components/Controls/ChildTable.vue";

const props = defineProps({
  form: Object,
});

const editing = ref(false);
</script>
