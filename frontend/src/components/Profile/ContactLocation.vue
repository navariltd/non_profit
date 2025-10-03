<template>
  <div class="space-y-6">
    <div class="flex justify-end">
      <Button @click="editing = !editing">
        {{ editing ? "Cancel Edit" : "Edit" }}
      </Button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Link
        doctype="County"
        v-model="form.county"
        label="County"
        :readOnly="!editing"
      />
      <Link
        v-if="form.county"
        doctype="Sub County"
        v-model="form.sub_county"
        label="Sub County"
        :readOnly="!editing"
        :filters="{ county: form.county }"
      />
      <FormControl
        v-model="form.ward"
        label="Ward"
        :readOnly="!editing"
        type="text"
      />
      <Link
        v-if="form.sub_county"
        doctype="Administrative Location"
        v-model="form.administrative_location"
        label="Administrative Location"
        :readOnly="!editing"
        :filters="{ sub_county: form.sub_county }"
      />
      <FormControl
        v-model="form.access_to_internet"
        label="Access to Internet"
        :readOnly="!editing"
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
      county: "",
      sub_county: "",
      ward: "",
      administrative_location: "",
      address__location: "",
      access_to_internet: "",
    }),
  },
  doctype: {
    type: String,
    default: "User", // Frappe Doctype to save/update
  },
});

const emit = defineEmits(["change"]);

const editing = ref(false);

watch(
  props.form,
  () => {
    emit("change");
  },
  { deep: true }
);
</script>
