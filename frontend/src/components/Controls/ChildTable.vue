<template>
  <div ref="tableRef" class="w-full relative">
    <div v-if="label" class="text-xs text-ink-gray-5 mb-2">{{ label }}</div>

    <div class="block lg:hidden">
      <div
        class="flex items-center justify-between mb-3 p-2 bg-surface-gray-1 rounded-lg"
      >
        <div class="flex items-center gap-2">
          <input
            type="checkbox"
            @change="toggleSelectAll"
            :checked="allSelected"
            :disabled="rowsRef.length === 0"
            class="cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
          />
          <span class="text-sm font-medium text-ink-gray-6">
            {{
              selectedRows.size > 0
                ? `${selectedRows.size} selected`
                : "Select All"
            }}
          </span>
        </div>

        <div class="flex items-center gap-1">
          <Button
            v-if="selectedRows.size > 0"
            @click="duplicateSelected"
            variant="ghost"
            size="sm"
            class="!p-1"
            title="Duplicate"
          >
            <Copy class="size-3" />
          </Button>
          <Button
            v-if="selectedRows.size > 0"
            @click="deleteSelected"
            variant="ghost"
            size="sm"
            class="!p-1"
            title="Delete"
          >
            <Trash2 class="size-3 text-red-600" />
          </Button>
          <Button
            @click="addRow"
            variant="solid"
            size="sm"
            class="inline-flex items-center !px-2 !py-1 text-xs gap-1"
          >
            + Add
          </Button>
        </div>
      </div>

      <div class="space-y-2">
        <div
          v-for="(row, rowIndex) in rowsRef"
          :key="`mobile-row-${rowIndex}`"
          class="border rounded-lg p-3 transition-all relative"
          :class="[
            selectedRows.has(rowIndex)
              ? 'bg-blue-50 border-blue-200'
              : 'bg-white',
            editingRow === rowIndex ? 'ring-2 ring-blue-300' : '',
          ]"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <input
                type="checkbox"
                :checked="selectedRows.has(rowIndex)"
                @change="toggleRowSelection(rowIndex)"
                class="cursor-pointer"
              />
              <span class="text-xs font-medium text-ink-gray-6">
                Row {{ rowIndex + 1 }}
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              @click.stop="openEditModal(rowIndex)"
              class="!p-1"
            >
              <Edit class="size-3 text-ink-gray-7 stroke-1.5" />
            </Button>
          </div>

          <div class="space-y-2">
            <div
              v-for="field in visibleFields.slice(0, 3)"
              :key="field.fieldname"
              class="flex flex-col gap-1"
            >
              <label class="text-xs text-ink-gray-5 font-medium">
                {{ field.label }}
              </label>

              <div
                class="w-full cursor-pointer min-h-[32px] flex items-center"
                @click="startEditing(rowIndex, field.fieldname)"
              >
                <component
                  v-if="
                    editingRow === rowIndex && editingField === field.fieldname
                  "
                  :is="getFieldComponent(field)"
                  v-model="row[field.fieldname]"
                  v-bind="getFieldProps(field, rowIndex)"
                  @blur="stopEditing"
                  ref="editInputRef"
                  class="w-full text-sm"
                />

                <div v-else class="text-sm text-ink-gray-7 truncate">
                  <template v-if="field.fieldtype === 'Check'">
                    <input
                      type="checkbox"
                      :checked="row[field.fieldname]"
                      disabled
                      class="cursor-pointer"
                    />
                  </template>

                  <template
                    v-else-if="
                      ['Attach', 'Attach Image', 'Image'].includes(
                        field.fieldtype
                      )
                    "
                  >
                    <span class="text-blue-600 truncate text-xs">
                      {{
                        row[field.fieldname]?.file_name ||
                        row[field.fieldname]?.name ||
                        row[field.fieldname] ||
                        "-"
                      }}
                    </span>
                  </template>

                  <template v-else>
                    {{ formatFieldValue(row[field.fieldname], field) || "-" }}
                  </template>
                </div>
              </div>
            </div>

            <div v-if="visibleFields.length > 3" class="pt-1">
              <button
                @click="openEditModal(rowIndex)"
                class="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                <span>View all {{ visibleFields.length }} fields</span>
                <svg
                  class="size-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="rowsRef.length === 0"
        class="p-8 text-center text-ink-gray-5 border rounded-lg"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="mx-auto h-8 w-8 mb-2 text-ink-gray-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 3c-4.97 0-9 1.343-9 3v12c0 1.657 4.03 3 9 3s9-1.343 9-3V6c0-1.657-4.03-3-9-3z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M3 9c0 1.657 4.03 3 9 3s9-1.343 9-3"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M3 15c0 1.657 4.03 3 9 3s9-1.343 9-3"
          />
        </svg>
        <div class="text-sm">No Data</div>
        <Button @click="addRow" variant="solid" size="sm" class="mt-3">
          <template #prefix><Plus class="size-3" /></template>
          Add First Row
        </Button>
      </div>
    </div>

    <div class="hidden lg:block">
      <div class="overflow-x-auto border rounded-md relative">
        <div
          class="grid items-center gap-4 p-3 bg-surface-gray-1 border-b text-xs sticky top-0 z-10"
          :style="{ gridTemplateColumns: gridColumnsStyle }"
        >
          <div class="w-8 flex items-center justify-center">
            <input
              type="checkbox"
              @change="toggleSelectAll"
              :checked="allSelected"
              :disabled="rowsRef.length === 0"
              class="cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <div
            v-for="field in visibleFields"
            :key="field.fieldname"
            class="font-medium text-ink-gray-6 truncate"
            :title="field.label"
          >
            {{ field.label }}
          </div>
          <div class="w-8"></div>
        </div>

        <div
          v-for="(row, rowIndex) in rowsRef"
          :key="`desktop-row-${rowIndex}`"
          class="grid items-center gap-4 p-3 transition-all relative group"
          :class="[
            rowIndex % 2 === 0 ? 'bg-white' : 'bg-surface-white',
            selectedRows.has(rowIndex) ? 'bg-blue-50' : '',
            editingRow === rowIndex ? 'ring-2 ring-blue-300' : '',
          ]"
          :style="{ gridTemplateColumns: gridColumnsStyle }"
        >
          <div class="w-8 flex items-center justify-center">
            <input
              type="checkbox"
              :checked="selectedRows.has(rowIndex)"
              @change="toggleRowSelection(rowIndex)"
              class="cursor-pointer"
            />
          </div>

          <template v-for="field in visibleFields" :key="field.fieldname">
            <div
              class="w-full cursor-pointer"
              @click="startEditing(rowIndex, field.fieldname)"
            >
              <component
                v-if="
                  editingRow === rowIndex && editingField === field.fieldname
                "
                :is="getFieldComponent(field)"
                v-model="row[field.fieldname]"
                v-bind="getFieldProps(field, rowIndex)"
                @blur="stopEditing"
                ref="editInputRef"
              />

              <div
                v-else
                class="text-sm text-ink-gray-7 truncate min-h-[32px] flex items-center"
                :title="formatFieldValue(row[field.fieldname], field) || '-'"
              >
                <template v-if="field.fieldtype === 'Check'">
                  <input
                    type="checkbox"
                    :checked="row[field.fieldname]"
                    disabled
                    class="cursor-pointer"
                  />
                </template>

                <template
                  v-else-if="
                    ['Attach', 'Attach Image', 'Image'].includes(
                      field.fieldtype
                    )
                  "
                >
                  <span class="text-blue-600 truncate">
                    {{
                      row[field.fieldname]?.file_name ||
                      row[field.fieldname]?.name ||
                      row[field.fieldname] ||
                      "-"
                    }}
                  </span>
                </template>

                <template v-else>
                  {{ formatFieldValue(row[field.fieldname], field) || "-" }}
                </template>
              </div>
            </div>
          </template>

          <div
            class="flex items-center justify-end opacity-90 group-hover:opacity-100 transition-opacity"
          >
            <Button
              variant="ghost"
              size="sm"
              @click.stop="openEditModal(rowIndex)"
              class="relative"
            >
              <Edit class="size-4 text-ink-gray-7 stroke-1.5" />
            </Button>
          </div>
        </div>

        <div
          v-if="rowsRef.length === 0"
          class="p-8 text-center text-ink-gray-5"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="mx-auto h-10 w-10 mb-2 text-ink-gray-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 3c-4.97 0-9 1.343-9 3v12c0 1.657 4.03 3 9 3s9-1.343 9-3V6c0-1.657-4.03-3-9-3z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3 9c0 1.657 4.03 3 9 3s9-1.343 9-3"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3 15c0 1.657 4.03 3 9 3s9-1.343 9-3"
            />
          </svg>
          <div class="text-sm">No Data</div>
        </div>
      </div>

      <div class="mt-3 flex items-center justify-between">
        <Button @click="addRow" variant="solid" size="sm">
          <template #prefix><Plus class="size-4" /></template>
          Add Row
        </Button>

        <div v-if="selectedRows.size > 0" class="flex items-center gap-2">
          <span class="text-xs text-ink-gray-6"
            >{{ selectedRows.size }} selected</span
          >
          <Button
            @click="duplicateSelected"
            variant="ghost"
            size="sm"
            title="Duplicate"
          >
            <Copy class="size-4 text-ink-gray-7" />
          </Button>
          <Button
            @click="deleteSelected"
            variant="ghost"
            size="sm"
            title="Delete"
          >
            <Trash2 class="size-4 text-red-600" />
          </Button>
        </div>
      </div>
    </div>

    <div
      v-if="editModalOpen"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4"
      @click.self="closeEditModal"
    >
      <div
        class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[95vh] overflow-hidden flex flex-col m-2"
      >
        <div
          class="flex items-center justify-between p-3 sm:p-4 border-b bg-surface-gray-1"
        >
          <h3 class="text-base sm:text-lg font-semibold text-ink-gray-7">
            Edit Row
          </h3>
          <button
            @click="closeEditModal"
            class="text-ink-gray-5 hover:text-ink-gray-7 transition-colors p-1"
          >
            <X class="size-4 sm:size-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6">
          <template v-for="(section, sIndex) in modalLayout" :key="sIndex">
            <div
              class="border-t pt-4 sm:pt-6 mt-4 sm:mt-6 first:border-t-0 first:pt-0 first:mt-0"
            >
              <h4
                v-if="section.label"
                class="text-sm sm:text-base font-semibold text-ink-gray-7 mb-3 sm:mb-4"
              >
                {{ section.label }}
              </h4>

              <div class="flex flex-col md:flex-row -mx-1 sm:-mx-2">
                <div
                  v-for="(col, cIndex) in section.columns"
                  :key="cIndex"
                  class="flex-1 px-1 sm:px-2"
                >
                  <div
                    v-for="field in col"
                    :key="field.fieldname"
                    class="mb-3 sm:mb-4"
                  >
                    <template v-if="field.fieldtype === 'Check'">
                      <div class="flex items-center gap-2">
                        <FormControl
                          :type="'checkbox'"
                          v-model="editModalData[field.fieldname]"
                          v-bind="getFieldProps(field)"
                        />
                        <label class="text-sm text-ink-gray-7">
                          {{ field.label }}
                          <span v-if="field.reqd" class="text-red-500">*</span>
                        </label>
                      </div>
                    </template>

                    <template v-else>
                      <label class="block text-sm text-ink-gray-7 mb-1">
                        {{ field.label }}
                        <span v-if="field.reqd" class="text-red-500">*</span>
                      </label>

                      <component
                        :is="getFieldComponent(field)"
                        v-model="editModalData[field.fieldname]"
                        v-bind="getFieldProps(field)"
                        :rows="field.fieldtype === 'Long Text' ? 8 : 4"
                        :required="field.reqd"
                        class="text-sm"
                      />
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <div
          class="flex items-center justify-end gap-2 p-3 sm:p-4 border-t bg-surface-gray-1 flex-wrap"
        >
          <Button
            @click="closeEditModal"
            variant="ghost"
            size="sm"
            class="flex-1 sm:flex-none"
          >
            Cancel
          </Button>
          <Button
            @click="saveEditModal"
            variant="solid"
            size="sm"
            class="flex-1 sm:flex-none"
          >
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from "vue";
import {
  Button,
  FormControl,
  createResource,
  Textarea,
  TextEditor,
  TextInput,
} from "frappe-ui";
import Uploader from "./Uploader.vue";
import LinkControl from "./Link.vue";
import { Plus, Trash2, Copy, Edit, X } from "lucide-vue-next";

const props = withDefaults(
  defineProps<{
    modelValue?: Record<string, any>[];
    doctype: string;
    label?: string;
  }>(),
  { modelValue: () => [], label: "" }
);
const emit = defineEmits<{
  (e: "update:modelValue", value: Record<string, any>[]): void;
}>();

const rowsRef = ref<Record<string, any>[]>([]);
const tableRef = ref<HTMLElement | null>(null);
const selectedRows = ref(new Set<number>());
const editingRow = ref<number | null>(null);
const editingField = ref<string | null>(null);
const editInputRef = ref<any>(null);
const editModalOpen = ref(false);
const editModalRowIndex = ref<number | null>(null);
const editModalData = ref<Record<string, any>>({});
const isUpdating = ref(false);

const fieldComponentMap: Record<string, any> = {
  Attach: Uploader,
  "Attach Image": Uploader,
  Image: Uploader,
  Autocomplete: TextInput,
  Barcode: TextInput,
  Button: Button,
  Check: "checkbox",
  Code: TextEditor,
  Color: "color",
  Currency: "number",
  Data: TextInput,
  Date: "date",
  Datetime: "datetime-local",
  Duration: TextInput,
  "Dynamic Link": LinkControl,
  Float: "number",
  Geolocation: "map",
  Heading: "heading",
  HTML: "html",
  "HTML Editor": TextEditor,
  Icon: "icon",
  Int: "number",
  JSON: Textarea,
  Link: LinkControl,
  "Long Text": Textarea,
  "Markdown Editor": TextEditor,
  Password: "password",
  Percent: "number",
  Phone: "tel",
  Rating: "rating",
  "Read Only": TextInput,
  Select: "select",
  Signature: "signature",
  "Small Text": Textarea,
  Table: "childtable",
  "Table MultiSelect": "multiselecttable",
  Text: TextInput,
  "Text Editor": TextEditor,
  Time: "time",
};

function getFieldComponent(field: any) {
  const comp = fieldComponentMap[field.fieldtype];

  const formControlTypes = [
    "Int",
    "Float",
    "Currency",
    "Data",
    "Date",
    "Datetime",
    "Time",
    "Email",
    "Password",
    "Tel",
    "Search",
    "Check",
  ];

  if (comp && typeof comp !== "string") return comp;
  if (formControlTypes.includes(field.fieldtype)) return FormControl;

  return comp || FormControl;
}

function getFieldProps(field: any, rowIndex?: number) {
  const props: Record<string, any> = {};

  switch (field.fieldtype) {
    case "Data":
      props.type = "text";
      break;
    case "Check":
      props.type = "checkbox";
      break;

    case "Int":
    case "Float":
    case "Currency":
      props.type = "number";
      break;

    case "Date":
      props.type = "date";
      break;

    case "Datetime":
      props.type = "datetime-local";
      break;

    case "Time":
      props.type = "time";
      break;

    case "Email":
      props.type = "email";
      break;

    case "Password":
      props.type = "password";
      break;

    case "Tel":
      props.type = "tel";
      break;

    case "Search":
      props.type = "search";
      break;

    case "Select":
      props.type = "select";
      props.options = getSelectOptions(field);
      break;

    case "Attach":
    case "Attach Image":
    case "Image":
      props.fileTypes = [".pdf", ".jpg", ".png", ".doc", ".docx"];
      props.multi = false;
      props.maxFileSize = 10;
      props.success = (file: any) => {
        if (rowIndex !== undefined)
          handleUploadSuccess(rowIndex, field.fieldname, file);
      };
      break;
  }

  return props;
}

const doctypeMeta = createResource({
  url: "frappe.desk.form.load.getdoctype",
  params: { doctype: props.doctype, with_parent: 1 },
  auto: true,
});

const doctypeFields = computed(() => {
  if (!doctypeMeta.data?.docs) return [];

  const targetDoc = doctypeMeta.data.docs.find(
    (d: any) => d.name === props.doctype
  );
  if (!targetDoc?.fields) return [];

  const fields = targetDoc.fields.filter((f: any) => !f.hidden);

  const fieldOrder = targetDoc.field_order
    ? targetDoc.field_order.split("\n").map((f: string) => f.trim())
    : [];

  if (fieldOrder.length > 0) {
    return fields.sort((a: any, b: any) => {
      const posA = fieldOrder.indexOf(a.fieldname);
      const posB = fieldOrder.indexOf(b.fieldname);

      if (posA !== -1 && posB !== -1) {
        return posA - posB;
      }

      if (posA !== -1) return -1;
      if (posB !== -1) return 1;

      return (a.idx || 0) - (b.idx || 0);
    });
  }

  return fields.sort((a: any, b: any) => (a.idx || 0) - (b.idx || 0));
});

const visibleFields = computed(() => {
  const vf = doctypeFields.value.filter(
    (f: any) =>
      f.in_list_view && !["Section Break", "Column Break"].includes(f.fieldtype)
  );
  return vf.length > 0
    ? vf
    : doctypeFields.value
        .filter(
          (f: any) => !["Section Break", "Column Break"].includes(f.fieldtype)
        )
        .slice(0, 5);
});

const modalLayout = computed(() => {
  const layout: any[] = [];
  let currentSection: any = { type: "section", columns: [[]] };

  for (const field of doctypeFields.value) {
    if (field.fieldtype === "Section Break") {
      if (currentSection.columns.some((col: any) => col.length > 0)) {
        layout.push(currentSection);
      }

      currentSection = { type: "section", label: field.label, columns: [[]] };
    } else if (field.fieldtype === "Column Break") {
      currentSection.columns.push([]);
    } else {
      currentSection.columns[currentSection.columns.length - 1].push(field);
    }
  }

  if (currentSection.columns.some((col: any) => col.length > 0)) {
    layout.push(currentSection);
  }

  return layout;
});

const gridColumnsStyle = computed(() => {
  const cols = visibleFields.value.length;
  return ["40px", ...Array(cols).fill("1fr"), "40px"].join(" ");
});

function initializeRows() {
  if (isUpdating.value) return;
  rowsRef.value = (props.modelValue || []).map((r) => ensureRowShape(r));
}

function ensureRowShape(row: Record<string, any>) {
  const shaped: Record<string, any> = { ...(row || {}) };
  doctypeFields.value.forEach((field: any) => {
    if (
      !["Section Break", "Column Break"].includes(field.fieldtype) &&
      !(field.fieldname in shaped)
    ) {
      shaped[field.fieldname] = getDefaultValue(field);
    }
  });
  return shaped;
}

function getDefaultValue(field: any) {
  if (field.fieldtype === "Check") return 0;
  if (["Int", "Float", "Currency"].includes(field.fieldtype)) return 0;

  return field.default || "";
}

onMounted(() => {
  watch(
    () => doctypeMeta.data,
    () => {
      if (doctypeMeta.data) initializeRows();
    },
    { immediate: true }
  );
});

watch(
  () => props.modelValue,
  (nv) => {
    if (isUpdating.value) return;
    if (nv && Array.isArray(nv) && doctypeFields.value.length > 0) {
      const newRows = nv.map((r: any) => ensureRowShape(r));
      if (JSON.stringify(newRows) !== JSON.stringify(rowsRef.value)) {
        rowsRef.value = newRows;
      }
    }
  },
  { deep: true }
);

watch(
  rowsRef,
  (nv) => {
    if (isUpdating.value) return;
    isUpdating.value = true;
    nextTick(() => {
      emit(
        "update:modelValue",
        nv.map((r) => ({ ...r }))
      );
      nextTick(() => {
        isUpdating.value = false;
      });
    });
  },
  { deep: true }
);

function addRow() {
  const newRow: Record<string, any> = {};
  doctypeFields.value.forEach((field: any) => {
    if (!["Section Break", "Column Break"].includes(field.fieldtype)) {
      newRow[field.fieldname] = getDefaultValue(field);
    }
  });
  rowsRef.value.push(newRow);
}

function duplicateSelected() {
  const indices = Array.from(selectedRows.value).sort((a, b) => b - a);
  indices.forEach((idx) => {
    const duplicate = { ...rowsRef.value[idx] };
    rowsRef.value.splice(idx + 1, 0, duplicate);
  });
  selectedRows.value.clear();
}

function deleteSelected() {
  const indices = Array.from(selectedRows.value).sort((a, b) => b - a);
  indices.forEach((idx) => rowsRef.value.splice(idx, 1));
  selectedRows.value.clear();
}

function toggleRowSelection(idx: number) {
  if (selectedRows.value.has(idx)) {
    selectedRows.value.delete(idx);
  } else {
    selectedRows.value.add(idx);
  }
}

const allSelected = computed(() => {
  return (
    rowsRef.value.length > 0 && selectedRows.value.size === rowsRef.value.length
  );
});

function toggleSelectAll() {
  if (allSelected.value) {
    selectedRows.value.clear();
  } else {
    rowsRef.value.forEach((_, idx) => selectedRows.value.add(idx));
  }
}

function startEditing(rowIndex: number, fieldname: string) {
  editingRow.value = rowIndex;
  editingField.value = fieldname;
  nextTick(() => {
    if (editInputRef.value?.el) {
      editInputRef.value.el.focus();
    }
  });
}

function stopEditing() {
  setTimeout(() => {
    editingRow.value = null;
    editingField.value = null;
  }, 150);
}

function openEditModal(idx: number) {
  editModalRowIndex.value = idx;
  editModalData.value = { ...rowsRef.value[idx] };
  editModalOpen.value = true;
}

function closeEditModal() {
  editModalOpen.value = false;
  editModalRowIndex.value = null;
  editModalData.value = {};
}

function saveEditModal() {
  if (editModalRowIndex.value !== null) {
    rowsRef.value[editModalRowIndex.value] = { ...editModalData.value };
  }
  closeEditModal();
}

function getSelectOptions(field: any) {
  if (field.options) {
    return field.options.split("\n").map((opt: string) => ({
      label: opt.trim(),
      value: opt.trim(),
    }));
  }
  return [];
}

function formatFieldValue(value: any, field: any) {
  if (value === null || value === undefined || value === "") return "";

  if (field.fieldtype === "Currency") {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value);
  }

  if (field.fieldtype === "Float") {
    return parseFloat(value).toFixed(2);
  }

  return value;
}

function handleUploadSuccess(rowIndex: number, fieldname: string, file: any) {
  if (rowsRef.value[rowIndex]) {
    rowsRef.value[rowIndex][fieldname] = file;
  }
}

defineExpose({
  addRow,
  rowsRef,
  selectedRows,
  doctypeFields,
});
</script>

<style scoped>
.group:hover {
  background-color: #f8fafb;
}
</style>
