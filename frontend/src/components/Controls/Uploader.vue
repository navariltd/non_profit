<template>
  <div class="border-0">
    <button
      v-if="!uploadedFile"
      type="button"
      class="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-md bg-gray-50 hover:border-blue-400 transition-colors duration-300 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      @dragover.prevent
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="acceptedFileTypes"
        @change="onFileSelect"
        class="hidden"
      />
      <div class="text-center mb-4 pointer-events-none">
        <Cloud class="mx-auto h-12 w-12 text-gray-400" />
        <div class="mt-4 text-sm text-gray-600">
          <span class="font-medium text-blue-600">
            {{ "Click to upload" }}
          </span>
          {{ "or drag and drop" }}
        </div>
        <p class="text-xs text-gray-500 mt-1">
          {{ "Supported formats:" }}
          {{ supportedFormatsText }}
        </p>
      </div>
    </button>

    <div v-else class="space-y-3">
      <div
        class="flex items-center space-x-3 p-3 bg-gray-100 rounded-lg relative"
      >
        <FileText class="size-6 text-gray-500" />
        <div class="flex-1 min-w-0">
          <p class="font-medium text-gray-800 truncate">
            {{ uploadedFile.file_name }}
          </p>
          <p class="text-sm text-gray-500">
            {{ formatBytes(uploadedFile.file_size) }}
          </p>
        </div>
        <button
          v-if="uploading"
          @click="cancelUpload"
          class="absolute top-2 right-2 text-gray-400 hover:text-red-600"
          title="Cancel Upload"
        >
          ✕
        </button>
      </div>

      <div v-if="uploading" class="space-y-1">
        <div class="flex justify-between text-sm text-gray-600">
          <span>{{ "Uploading..." }}</span>
          <span>{{ progress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            class="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full animate-pulse"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Button, toast } from "frappe-ui";
import { Cloud, FileText } from "lucide-vue-next";

const emit = defineEmits<{
  (e: "success", data: any): void;
}>();

const props = withDefaults(
  defineProps<{
    modelValue: string;
    label?: string;
    description?: string;
    fileTypes?: string[];
    validateFile?: (file: File) => string | void;
    required?: boolean;
    uploadArgs?: { [key: string]: any };
  }>(),
  {
    modelValue: "",
    label: "",
    description: "",
    fileTypes: () => ["*/*"],
    required: false,
    uploadArgs: () => ({}),
  }
);

const fileInput = ref<HTMLInputElement | null>(null);
const uploading = ref(false);
const progress = ref(0);
const uploadedFile = ref<any>(null);
let cancelRequested = false;

const triggerFileInput = () => {
  fileInput.value?.click();
};

const cancelUpload = () => {
  cancelRequested = true;
  uploading.value = false;
  progress.value = 0;
  uploadedFile.value = null;
  toast.error("Upload cancelled");
};

async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("cmd", "non_profit.non_profit.api.upload_file");

  if (props.uploadArgs) {
    for (const [key, value] of Object.entries(props.uploadArgs)) {
      formData.append(key, value);
    }
  }

  const response = await fetch(
    "/api/method/non_profit.non_profit.api.upload_file",
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Upload failed: ${errorText}`);
  }

  const result = await response.json();
  const fileData = result.message;

  const root = window.location.origin;
  fileData.file_url = fileData.file_url.startsWith("/")
    ? root + fileData.file_url
    : fileData.file_url;

  return fileData;
}

const simulateProgress = async () => {
  return new Promise<void>((resolve) => {
    const start = Date.now();
    const tick = () => {
      if (cancelRequested) return;

      const elapsed = Date.now() - start;
      const target = Math.min(90, Math.floor((elapsed / 1500) * 90));
      progress.value = target;

      if (elapsed >= 3000) return resolve();
      requestAnimationFrame(tick);
    };
    tick();
  });
};

const onFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (!target.files?.length) return;
  handleFile(target.files[0]);
};

const onDrop = (e: DragEvent) => {
  if (!e.dataTransfer?.files?.length) return;
  handleFile(e.dataTransfer.files[0]);
};

const handleFile = async (file: File) => {
  cancelRequested = false;

  if (props.validateFile) {
    const errorMessage = props.validateFile(file);
    if (errorMessage) {
      toast.error(errorMessage);
      return;
    }
  }

  uploadedFile.value = {
    file_name: file.name,
    file_size: file.size,
    file_url: null,
  };
  uploading.value = true;
  progress.value = 0;

  try {
    await simulateProgress();
    if (cancelRequested) return;

    const data = await uploadFile(file);
    uploadedFile.value = data;

    emit("success", data);
    progress.value = 100;
    toast.success("File uploaded successfully.");
  } catch (err: any) {
    console.error(err);
    toast.error("Upload failed: " + (err.message || "Unknown error"));
    removeFile();
  } finally {
    uploading.value = false;
  }
};

const removeFile = () => {
  uploadedFile.value = null;
  if (fileInput.value) fileInput.value.value = "";
};

const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

const acceptedFileTypes = computed(() => {
  if (Array.isArray(props.fileTypes) && props.fileTypes.length > 0) {
    const normalizedFileTypes = props.fileTypes.map((type) =>
      type.startsWith(".") ? type : `.${type}`
    );

    const mimeTypes = normalizedFileTypes
      .map((type) => {
        if (type === ".jpg" || type === ".jpeg") return "image/jpeg";
        if (type === ".png") return "image/png";
        if (type === ".pdf") return "application/pdf";
        return null;
      })
      .filter(Boolean);

    return [...normalizedFileTypes, ...mimeTypes].join(",");
  }
  return "*/*";
});

const supportedFormatsText = computed(() => {
  if (Array.isArray(props.fileTypes) && props.fileTypes.length > 0) {
    return props.fileTypes
      .map((t) => t.replace(".", ""))
      .join(", ")
      .toUpperCase();
  }
  return "ANY";
});
</script>

<style scoped>
.preview {
  max-width: 100%;
}
</style>
