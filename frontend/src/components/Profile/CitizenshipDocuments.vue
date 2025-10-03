<template>
  <div class="space-y-6">
    <div class="flex justify-end">
      <Button @click="editing = !editing">{{
        editing ? "Cancel Edit" : "Edit"
      }}</Button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <FormControl
        v-model="form.citizenship"
        label="Citizenship"
        :readOnly="!editing"
      />
      <Link
        v-model="form.country_of_citizenship"
        label="Country of Citizenship"
        :readOnly="!editing"
      />
    </div>

    <ChildTable
      v-model="form.supporting_documents"
      doctype="Supporting Document"
      label="Supporting Documents"
      :autoEditGrid="false"
      :readOnly="!editing"
    />

    <ChildTable
      v-model="form.attachments"
      doctype="Attachment"
      label="Attachments"
      :autoEditGrid="false"
      :readOnly="!editing"
    />
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Button, FormControl } from "frappe-ui";
import Link from "@/components/Controls/Link.vue";
import ChildTable from "@/components/Controls/ChildTable.vue";

const props = defineProps({
  form: Object,
});

const editing = ref(false);
</script>
