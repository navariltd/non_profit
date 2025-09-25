<template>
  <section>
    <h2 class="text-xl font-bold text-red-700 mb-4">
      {{ __("Documents & Photo") }}
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Uploader
        label="Upload Profile Photo"
        :fileTypes="['.jpg', '.png']"
        :onSuccess="(f) => (localForm.profile_photo = f)"
      />
      <Uploader
        label="Upload Resume"
        :fileTypes="['.pdf', '.docx', '.doc']"
        :onSuccess="(f) => (localForm.resume = f)"
      />
    </div>

    <div class="mt-6">
      <Uploader
        label="Upload Supporting Documents"
        :fileTypes="['.pdf', '.jpg', '.png']"
        :multi="true"
        :onSuccess="addDocument"
      />
    </div>
  </section>
</template>

<script setup>
import { reactive, watch } from "vue";
import { TextEditor } from "frappe-ui";
import Uploader from "@/components/Controls/Uploader.vue";

const props = defineProps({ modelValue: Object, documents: Array });
const emit = defineEmits(["update:modelValue"]);

const localForm = reactive({ ...props.modelValue });
watch(localForm, (val) => emit("update:modelValue", val), { deep: true });

function addDocument(file) {
  props.documents.push(file);
}
</script>
