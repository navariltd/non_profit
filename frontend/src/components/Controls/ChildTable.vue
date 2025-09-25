<template>
  <div ref="tableRef" class="w-full">
    <div v-if="label" class="text-xs text-ink-gray-5 mb-2">{{ label }}</div>

    <div class="overflow-x-auto border rounded-md">
      <!-- Header -->
      <div
        class="grid items-center gap-4 p-3 bg-surface-gray-1 border-b"
        :style="{ gridTemplateColumns: gridColumnsStyle }"
      >
        <div
          v-for="col in normalizedColumns"
          :key="col.key"
          class="text-sm font-medium text-ink-gray-6"
        >
          {{ col.label }}
        </div>
        <div class="w-8"></div>
      </div>

      <!-- Rows -->
      <div
        v-for="(row, rowIndex) in rowsRef"
        :key="`row-${rowIndex}`"
        class="grid items-center gap-4 p-3 transition-all relative"
        :class="rowIndex % 2 === 0 ? 'bg-white' : 'bg-surface-white'"
        :style="{ gridTemplateColumns: gridColumnsStyle }"
      >
        <template v-for="col in normalizedColumns" :key="col.key">
          <div class="w-full">
            <!-- Simple types -->
            <FormControl
              v-if="['text', 'number', 'date'].includes(col.type)"
              v-model="row[col.key]"
              :label="null"
              :type="
                col.type === 'date'
                  ? 'date'
                  : col.type === 'number'
                    ? 'number'
                    : 'text'
              "
              :placeholder="col.placeholder"
              :rows="col.rows"
              v-bind="col.formProps || {}"
            />

            <!-- textarea -->
            <FormControl
              v-else-if="col.type === 'textarea'"
              v-model="row[col.key]"
              :label="null"
              type="textarea"
              :rows="col.rows || 3"
              v-bind="col.formProps || {}"
            />

            <!-- select -->
            <FormControl
              v-else-if="col.type === 'select'"
              v-model="row[col.key]"
              :label="null"
              type="select"
              :options="selectOptions(col)"
              v-bind="col.formProps || {}"
            />

            <!-- multiselect -->
            <MultiSelect
              v-else-if="col.type === 'multiselect'"
              v-model="row[col.key]"
              :label="null"
              v-bind="col.formProps || {}"
              :doctype="col.doctype"
              :options="col.options"
            />

            <!-- link -->
            <LinkControl
              v-else-if="col.type === 'link'"
              v-model="row[col.key]"
              :label="null"
              :doctype="col.doctype"
              v-bind="col.formProps || {}"
            />

            <!-- uploader (uses onSuccess prop callback) -->
            <div v-else-if="col.type === 'uploader'">
              <Uploader
                :label="null"
                :fileTypes="
                  col.formProps?.fileTypes || ['.pdf', '.jpg', '.png']
                "
                :multi="col.formProps?.multi || false"
                :onSuccess="
                  (file) => handleUploadSuccess(rowIndex, col.key, file)
                "
              />
              <div class="text-xs mt-1 text-ink-gray-5" v-if="row[col.key]">
                <template v-if="Array.isArray(row[col.key])">
                  <div v-for="(f, i) in row[col.key]" :key="i" class="truncate">
                    {{ f.file_name || f.name || f.file_url }}
                  </div>
                </template>
                <template v-else>
                  {{ row[col.key]?.file_name || row[col.key] }}
                </template>
              </div>
            </div>

            <!-- custom slot -->
            <div v-else-if="col.type === 'custom'">
              <slot :name="`col-${col.key}`" :row="row" :index="rowIndex" />
            </div>

            <!-- fallback -->
            <FormControl
              v-else
              v-model="row[col.key]"
              :label="null"
              type="text"
              v-bind="col.formProps || {}"
            />
          </div>
        </template>

        <!-- Actions -->
        <div class="flex items-center justify-end space-x-2">
          <Button
            variant="ghost"
            size="sm"
            @click="moveUp(rowIndex)"
            :disabled="rowIndex === 0"
            >▲</Button
          >
          <Button
            variant="ghost"
            size="sm"
            @click="moveDown(rowIndex)"
            :disabled="rowIndex === rowsRef.length - 1"
            >▼</Button
          >

          <div class="relative">
            <Button variant="ghost" @click.stop="toggleMenu(rowIndex)">
              <Ellipsis class="size-4 text-ink-gray-7 stroke-1.5" />
            </Button>

            <div
              v-if="menuOpenIndex === rowIndex"
              class="absolute right-0 top-9 w-36 bg-white border rounded shadow z-20"
              ref="menuDropdownRef"
            >
              <button
                class="w-full px-3 py-2 text-left text-sm hover:bg-surface-gray-2"
                @click="deleteRow(rowIndex)"
              >
                <Trash2 class="inline-block mr-2 size-4" /> Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-3 flex">
      <Button @click="addRow" variant="solid">
        <template #prefix><Plus class="size-4" /></template>
        Add Row
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { Button, FormControl } from "frappe-ui";
import Uploader from "@/components/Controls/Uploader.vue";
import MultiSelect from "@/components/Controls/MultiSelect.vue";
import LinkControl from "@/components/Controls/Link.vue";
import { Ellipsis, Plus, Trash2 } from "lucide-vue-next";
import { onClickOutside } from "@vueuse/core";

/* Props */
const props = withDefaults(
  defineProps<{
    modelValue?: Record<string, any>[];
    columns?: Array<any> | string[];
    label?: string;
    minRows?: number;
  }>(),
  {
    modelValue: () => [],
    columns: () => [],
    label: "",
    minRows: 1,
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", value: Record<string, any>[]): void;
}>();

/* Local state (per-instance) */
const rowsRef = ref<Record<string, any>[]>([]);
const tableRef = ref<HTMLElement | null>(null);
const menuDropdownRef = ref<HTMLElement | null>(null);
const menuOpenIndex = ref<number | null>(null);

/* normalize columns */
const normalizedColumns = computed(() => {
  return (props.columns || []).map((c: any, idx: number) => {
    if (typeof c === "string") {
      return {
        key: c.toLowerCase().replace(/\s+/g, "_"),
        label: c,
        type: "text",
        formProps: {},
      };
    }
    const key =
      c.key ||
      (c.label ? c.label.toLowerCase().replace(/\s+/g, "_") : `col_${idx}`);
    return {
      key,
      label: c.label || c.key || `Column ${idx + 1}`,
      type: c.type || "text",
      options: c.options || null,
      doctype: c.doctype || null,
      placeholder: c.placeholder || "",
      rows: c.rows,
      formProps: c.formProps || {},
    };
  });
});

const gridColumnsStyle = computed(() => {
  const cols = normalizedColumns.value.length;
  return [...Array(cols).fill("1fr"), "auto"].join(" ");
});

/* ensure row object has keys for each column */
function ensureRowShape(row: Record<string, any>) {
  const shaped: Record<string, any> = { ...(row || {}) };
  normalizedColumns.value.forEach((col) => {
    if (!(col.key in shaped))
      shaped[col.key] = col.type === "multiselect" ? [] : "";
  });
  return shaped;
}

/* initialize rowsRef from modelValue */
function initializeRows() {
  rowsRef.value = (props.modelValue || []).map((r) => ensureRowShape(r));
  while (rowsRef.value.length < (props.minRows || 1)) addRow();
}

onMounted(() => initializeRows());

watch(
  () => props.modelValue,
  (nv) => {
    if (nv && Array.isArray(nv))
      rowsRef.value = nv.map((r: any) => ensureRowShape(r));
  },
  { deep: true }
);

watch(
  rowsRef,
  (nv) => {
    // emit shallow copy of rows to avoid reactivity issues
    emit(
      "update:modelValue",
      nv.map((r) => ({ ...r }))
    );
  },
  { deep: true }
);

/* CRUD */
function addRow() {
  const newRow: Record<string, any> = {};
  normalizedColumns.value.forEach(
    (col) => (newRow[col.key] = col.type === "multiselect" ? [] : "")
  );
  rowsRef.value.push(newRow);
}

function deleteRow(idx: number) {
  if (rowsRef.value.length > (props.minRows || 1)) rowsRef.value.splice(idx, 1);
  menuOpenIndex.value = null;
}

function moveUp(idx: number) {
  if (idx <= 0) return;
  const r = rowsRef.value.splice(idx, 1)[0];
  rowsRef.value.splice(idx - 1, 0, r);
}

function moveDown(idx: number) {
  if (idx >= rowsRef.value.length - 1) return;
  const r = rowsRef.value.splice(idx, 1)[0];
  rowsRef.value.splice(idx + 1, 0, r);
}

/* menu handling (scoped per table) */
function toggleMenu(idx: number) {
  menuOpenIndex.value = menuOpenIndex.value === idx ? null : idx;
}

/* close menu when clicking outside the table container */
onClickOutside(tableRef, () => {
  menuOpenIndex.value = null;
});

/* select options helper */
function selectOptions(col: any) {
  if (col.options && Array.isArray(col.options)) {
    return col.options.map((o: any) =>
      typeof o === "string"
        ? { label: o, value: o }
        : { label: o.label || o.value, value: o.value }
    );
  }
  // NOTE: For doctype-based fetching you can add createResource here
  return [];
}

/* handle uploader result (Uploader uses onSuccess prop in your codebase) */
function handleUploadSuccess(rowIndex: number, key: string, file: any) {
  const target = rowsRef.value[rowIndex];
  if (!target) return;
  const col = normalizedColumns.value.find((c) => c.key === key);
  const multi = col?.formProps?.multi || false;
  if (multi) {
    if (!Array.isArray(target[key])) target[key] = [];
    target[key].push(file);
  } else {
    target[key] = file;
  }
}

/* expose API */
defineExpose({ addRow, deleteRow, moveUp, moveDown, rowsRef });
</script>

<style scoped>
/* subtle hover on alternating rows */
.grid > .bg-surface-white:hover {
  background-color: #f8fafb;
}
</style>
