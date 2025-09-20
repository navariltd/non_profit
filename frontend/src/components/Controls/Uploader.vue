<template>
  <div class="border-0">
    <button
      v-if="multi || !uploadedFiles.length"
      type="button"
      class="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-md bg-gray-50 hover:border-blue-400 transition-colors duration-300 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 mb-4"
      @dragover.prevent
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="acceptedFileTypes"
        :multiple="multi"
        @change="onFileSelect"
        class="hidden"
      />
      <div class="text-center mb-4 pointer-events-none">
        <Cloud class="mx-auto h-12 w-12 text-gray-400" />
        <div class="mt-4 text-sm text-gray-600">
          <span class="font-medium text-blue-600">Click to upload</span>
          or drag and drop
        </div>
        <p class="text-xs text-gray-500 mt-1">
          Supported formats: {{ supportedFormatsText }}
        </p>
        <p v-if="multi" class="text-xs text-blue-500 mt-1 font-medium">
          Multiple files can be selected
        </p>
      </div>
    </button>

    <div v-if="uploadedFiles.length" class="space-y-3">
      <div class="text-sm font-medium text-gray-700 mb-2">
        {{ uploadedFiles.length }} file(s) uploaded
      </div>
      <div
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
      >
        <div
          v-for="(file, index) in uploadedFiles"
          :key="file.file_name + index"
          class="bg-white p-4 rounded-md border space-y-2"
        >
          <div class="relative w-fit">
            <img
              v-if="isImage(file.file_url)"
              :src="file.file_url"
              alt="Uploaded preview"
              class="w-32 h-32 p-2 rounded-lg border object-cover"
            />

            <iframe
              v-else-if="isPDF(file.file_url)"
              :src="file.file_url"
              class="w-48 h-64 border rounded-lg"
            ></iframe>

            <div
              v-else
              class="flex items-center justify-center w-32 h-32 border rounded-lg bg-gray-100 text-gray-500"
            >
              <FileText class="w-10 h-10" />
            </div>

            <button
              v-if="!uploading"
              @click="removeFile(index)"
              class="absolute -top-2 -right-2 bg-gray-200 border rounded-full shadow h-6 w-6 text-red-500 hover:bg-red-100 flex items-center justify-center text-xs"
              title="Remove File"
            >
              ✕
            </button>
          </div>

          <div>
            <a
              :href="file.file_url"
              target="_blank"
              class="block font-medium text-blue-600 hover:underline truncate"
            >
              {{ file.file_name }}
            </a>
            <p v-if="file.file_size" class="text-xs text-gray-500 mt-1">
              {{ formatBytes(file.file_size) }}
            </p>
          </div>
        </div>
      </div>

      <button
        v-if="multi && uploadedFiles.length > 1 && !uploading"
        @click="clearAllFiles"
        type="button"
        class="mt-4 px-4 py-2 text-sm text-red-600 border border-red-300 rounded-md hover:bg-red-50 transition-colors"
      >
        Clear All Files
      </button>
    </div>

    <div v-if="uploading" class="space-y-1 mt-4">
      <div class="flex justify-between text-sm text-gray-600">
        <span>Uploading {{ currentUploadFile }}...</span>
        <span>{{ progress }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          class="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full animate-pulse transition-all duration-300"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
      <div class="text-xs text-gray-500 text-center">
        {{ uploadQueue.length }} file(s) remaining
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { toast } from "frappe-ui";
import { Cloud, FileText } from "lucide-vue-next";

const emit = defineEmits<{
  (e: "success", data: any): void;
  (e: "update:modelValue", value: string): void;
  (e: "filesChanged", files: any[]): void;
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
    multi?: boolean;
    maxFiles?: number;
  }>(),
  {
    modelValue: "",
    label: "",
    description: "",
    fileTypes: () => ["*/*"],
    required: false,
    uploadArgs: () => ({}),
    multi: false,
    maxFiles: 10,
  }
);

const fileInput = ref<HTMLInputElement | null>(null);
const uploading = ref(false);
const progress = ref(0);
const uploadedFiles = ref<any[]>([]);
const uploadQueue = ref<File[]>([]);
const currentUploadFile = ref<string>("");
let cancelRequested = false;

const triggerFileInput = () => fileInput.value?.click();

async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("cmd", "non_profit.non_profit.api.upload_file");

  for (const [key, value] of Object.entries(props.uploadArgs)) {
    formData.append(key, value);
  }

  const response = await fetch(
    "/api/method/non_profit.non_profit.api.upload_file",
    { method: "POST", body: formData }
  );

  if (!response.ok) throw new Error(await response.text());

  const result = await response.json();
  const fileData = result.message;

  const root = window.location.origin;
  fileData.file_url = fileData.file_url.startsWith("/")
    ? root + fileData.file_url
    : fileData.file_url;

  if (file.size) {
    fileData.file_size = file.size;
  }

  return fileData;
}

const simulateProgress = () => {
  return new Promise<void>((resolve) => {
    const start = Date.now();
    const tick = () => {
      if (cancelRequested) return;
      const elapsed = Date.now() - start;
      const target = Math.min(90, Math.floor((elapsed / 1500) * 90));
      progress.value = target;
      if (elapsed >= 1000) return resolve();
      requestAnimationFrame(tick);
    };
    tick();
  });
};

const validateFiles = (files: File[]): File[] => {
  const validFiles: File[] = [];

  for (const file of files) {
    if (
      props.multi &&
      props.maxFiles &&
      uploadedFiles.value.length + validFiles.length >= props.maxFiles
    ) {
      toast.error(`Maximum ${props.maxFiles} files allowed`);
      break;
    }

    if (file.size > props.maxFileSize * 1024 * 1024) {
      toast.error(
        `File ${file.name} is too large. Maximum size is ${props.maxFileSize}MB`
      );
      continue;
    }

    if (props.validateFile) {
      const errorMessage = props.validateFile(file);
      if (errorMessage) {
        toast.error(errorMessage);
        continue;
      }
    }

    const isDuplicate = uploadedFiles.value.some(
      (uploadedFile) => uploadedFile.file_name === file.name
    );

    if (isDuplicate) {
      toast.error(`File ${file.name} is already uploaded`);
      continue;
    }

    validFiles.push(file);
  }

  return validFiles;
};

const onFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (!target.files?.length) return;

  const files = Array.from(target.files);
  handleFiles(files);

  target.value = "";
};

const onDrop = (e: DragEvent) => {
  if (!e.dataTransfer?.files?.length) return;
  const files = Array.from(e.dataTransfer.files);
  handleFiles(files);
};

const handleFiles = async (files: File[]) => {
  const validFiles = validateFiles(files);

  if (!validFiles.length) return;

  if (!props.multi && uploadedFiles.value.length > 0) {
    uploadedFiles.value = [];
  }

  uploadQueue.value = [...validFiles];
  uploading.value = true;

  for (let i = 0; i < validFiles.length; i++) {
    const file = validFiles[i];
    currentUploadFile.value = file.name;
    progress.value = 0;

    try {
      await simulateProgress();
      const data = await uploadFile(file);
      uploadedFiles.value.push(data);
      emit("success", data);
      progress.value = 100;

      if (!props.multi) {
        emit("update:modelValue", data.file_url);
      }

      toast.success(`${file.name} uploaded successfully.`);
    } catch (err: any) {
      console.error(err);
      toast.error(
        `Failed to upload ${file.name}: ` + (err.message || "Unknown error")
      );
    }

    uploadQueue.value.shift();
  }

  uploading.value = false;
  currentUploadFile.value = "";

  emit("filesChanged", uploadedFiles.value);
};

const removeFile = (index: number) => {
  const removedFile = uploadedFiles.value[index];
  uploadedFiles.value.splice(index, 1);

  if (!props.multi && uploadedFiles.value.length === 0) {
    emit("update:modelValue", "");
  }

  emit("filesChanged", uploadedFiles.value);
  toast.success(`${removedFile.file_name} removed successfully.`);
};

const clearAllFiles = () => {
  if (
    confirm(
      `Are you sure you want to remove all ${uploadedFiles.value.length} files?`
    )
  ) {
    uploadedFiles.value = [];
    if (fileInput.value) fileInput.value.value = "";

    if (!props.multi) {
      emit("update:modelValue", "");
    }

    emit("filesChanged", []);
    toast.success("All files removed successfully.");
  }
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
  if (props.fileTypes?.length > 0) {
    const normalized = props.fileTypes.map((t) =>
      t.startsWith(".") ? t : `.${t}`
    );
    const mimeTypes = normalized
      .map((t) => {
        if (t === ".jpg" || t === ".jpeg") return "image/jpeg";
        if (t === ".png") return "image/png";
        if (t === ".pdf") return "application/pdf";
        if (t === ".doc") return "application/msword";
        if (t === ".docx")
          return "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
        if (t === ".xls") return "application/vnd.ms-excel";
        if (t === ".xlsx")
          return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        return null;
      })
      .filter(Boolean);
    return [...normalized, ...mimeTypes].join(",");
  }
  return "*/*";
});

const supportedFormatsText = computed(() =>
  props.fileTypes?.length
    ? props.fileTypes
        .map((t) => t.replace(".", ""))
        .join(", ")
        .toUpperCase()
    : "ANY"
);

const isImage = (url: string) => /\.(jpg|jpeg|png|gif|webp)$/i.test(url);
const isPDF = (url: string) => /\.pdf$/i.test(url);
</script>
