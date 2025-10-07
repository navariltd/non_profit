<template>
  <div>
    <div class="w-full">
      <Combobox v-model="selectedValue" nullable>
        <Popover class="w-full" v-model:show="showOptions">
          <template #target="{ togglePopover }">
            <ComboboxInput
              v-if="!props.readOnly"
              ref="search"
              class="search-input form-input w-full focus-visible:!ring-0"
              type="text"
              :value="query"
              @change="
                (e) => {
                  query = e.target.value;
                  showOptions = true;
                }
              "
              autocomplete="off"
              @focus="() => togglePopover()"
              @keydown.delete.capture.stop="removeLastValue"
              :placeholder="props.label || 'Select...'"
            />

            <div
              v-else
              class="w-full min-h-[2.5rem] border border-gray-300 rounded px-3 py-2 bg-gray-100 text-gray-700 flex items-center"
            >
              <span class="text-ink-gray-5">
                {{ props.label }}
              </span>
            </div>
          </template>

          <template #body="{ isOpen, close }">
            <div v-show="isOpen">
              <div
                class="mt-1 rounded-lg bg-surface-white py-1 text-base border-2"
              >
                <ComboboxOptions
                  class="my-1 min-h-[6rem] max-h-[12rem] overflow-y-auto px-1.5"
                  static
                >
                  <ComboboxOption
                    v-for="option in options"
                    :key="option.value"
                    :value="option"
                    v-slot="{ active }"
                  >
                    <li
                      :class="[
                        'flex cursor-pointer items-center rounded px-2 py-1 text-base',
                        { 'bg-surface-gray-2': active },
                      ]"
                      @click="
                        () => {
                          addValue(option);
                          closeDropdown(close);
                        }
                      "
                    >
                      <div class="flex flex-col gap-1 p-1 min-w-32">
                        <div class="text-base font-medium text-ink-gray-8">
                          {{ option.label || option.value }}
                        </div>
                        <div
                          v-if="option.value !== option.label"
                          class="text-sm text-ink-gray-5"
                        >
                          {{ option.value }}
                        </div>
                      </div>
                    </li>
                  </ComboboxOption>

                  <div class="h-10"></div>
                  <div
                    v-if="props.allowCreate"
                    class="absolute bottom-2 left-1 w-[99%] pt-2 bg-white border-t"
                  >
                    <Button
                      variant="ghost"
                      class="w-full !justify-start"
                      :label="`Add New`"
                      @click="
                        () => {
                          close();
                          showCreateDialog = true;
                        }
                      "
                    >
                      <template #prefix>
                        <Plus class="h-4 w-4 stroke-1.5" />
                      </template>
                    </Button>
                  </div>
                </ComboboxOptions>
              </div>
            </div>
          </template>
        </Popover>
      </Combobox>
    </div>

    <div v-if="displayValues.length" class="grid grid-cols-2 gap-2 mt-1">
      <div
        v-for="item in displayValues"
        :key="item.childtable_id || item.link_value"
        class="flex items-center justify-between break-all bg-surface-gray-2 text-ink-gray-7 word-wrap p-2 rounded-md mr-2"
      >
        <span class="break-all">{{ item.label }}</span>
        <X
          v-if="!props.readOnly"
          class="size-4 stroke-1.5 cursor-pointer"
          @click="removeValue(item)"
        />
      </div>
    </div>

    <CreateNewEntryDialog
      v-model="showCreateDialog"
      :doctype="linkDoctype"
      @created="(newName) => addValue({ value: newName, label: newName })"
    />
  </div>
</template>

<script setup>
import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxOption,
} from "@headlessui/vue";
import { createResource, Popover, Button } from "frappe-ui";
import { ref, computed, nextTick, watch, onMounted } from "vue";
import { watchDebounced } from "@vueuse/core";
import { X, Plus } from "lucide-vue-next";
import CreateNewEntryDialog from "../Modals/CreateNewEntryDialog.vue";

const props = defineProps({
  label: String,
  size: { type: String, default: "sm" },
  doctype: { type: String, required: true },
  mainField: { type: String, default: null },
  filters: { type: Object, default: () => ({}) },
  validate: { type: Function, default: null },
  errorMessage: {
    type: Function,
    default: (value) => `${value} is an Invalid value`,
  },
  required: Boolean,
  allowCreate: { type: Boolean, default: false },
  readOnly: { type: Boolean, default: false },
});

const values = defineModel();
const emit = defineEmits(["change"]);

const search = ref(null);
const error = ref(null);
const query = ref("");
const text = ref("");
const showOptions = ref(false);
const showCreateDialog = ref(false);
const linkFieldName = ref(props.mainField);
const linkDoctype = ref(null);
const displayValues = ref([]);

const isLinkValue = (value) => {
  return value && typeof value === "string";
};

const childtableMeta = createResource({
  url: "frappe.desk.form.load.getdoctype",
  params: {
    doctype: props.doctype,
    with_parent: 1,
  },
  auto: true,
  onSuccess(data) {
    if (!linkFieldName.value) {
      const linkField = data.docs[0].fields.find((f) => f.fieldtype === "Link");

      if (linkField) {
        linkFieldName.value = linkField.fieldname;
        linkDoctype.value = linkField.options;
      } else {
        console.error(
          "[MultiSelect] No link field found in childtable:",
          props.doctype
        );
      }
    } else {
      const field = data.docs[0].fields.find(
        (f) => f.fieldname === linkFieldName.value
      );

      if (field && field.fieldtype === "Link") {
        linkDoctype.value = field.options;
      } else {
        console.error("[MultiSelect] Field not found or not a Link field:", {
          fieldname: linkFieldName.value,
          field: field,
        });
      }
    }
  },
  onError(error) {
    console.error("[MultiSelect] Error fetching childtable meta:", error);
  },
});

const childtableEntries = createResource({
  url: "frappe.client.get_list",
  makeParams() {
    if (!values.value?.length) {
      return null;
    }

    const childIds = values.value.filter(
      (v) => typeof v === "string" && !isLinkValue(v)
    );

    if (!childIds.length) {
      return null;
    }

    const params = {
      doctype: props.doctype,
      fields: ["name", linkFieldName.value],
      filters: [["name", "in", childIds]],
    };

    return params;
  },
  auto: false,
  onSuccess(data) {},
  onError(error) {
    console.error("[MultiSelect] Error fetching childtable entries:", error);
  },
});

const linkLabelsResource = createResource({
  url: "non_profit.non_profit.api.custom_search_link",
  method: "GET",
  auto: false,
  onSuccess(data) {},
  onError(error) {
    console.error("[MultiSelect] Error fetching link labels:", error);
  },
});

const resolveValues = async () => {
  if (!values.value?.length || !linkFieldName.value) {
    displayValues.value = [];
    return;
  }

  const resolved = [];
  const linkValuesToFetch = [];

  for (const val of values.value) {
    if (typeof val === "string") {
      if (isLinkValue(val)) {
        resolved.push({
          link_value: val,
          label: null,
          childtable_id: null,
        });
        linkValuesToFetch.push(val);
      } else {
        if (!childtableEntries.data) {
          await childtableEntries.reload();
        }
        const entry = childtableEntries.data?.find((e) => e.name === val);
        if (entry) {
          const linkVal = entry[linkFieldName.value];
          resolved.push({
            link_value: linkVal,
            label: null,
            childtable_id: val,
          });
          linkValuesToFetch.push(linkVal);
        }
      }
    } else if (typeof val === "object" && val !== null) {
      const linkVal = val[linkFieldName.value] || val.name;
      resolved.push({
        link_value: linkVal,
        label: null,
        childtable_id: val.name || null,
      });
      linkValuesToFetch.push(linkVal);
    }
  }

  displayValues.value = resolved;

  if (linkValuesToFetch.length && linkDoctype.value) {
    await linkLabelsResource.update({
      params: {
        doctype: linkDoctype.value,
        txt: "",
        filters: JSON.stringify({ name: ["in", linkValuesToFetch] }),
        ignore_user_permissions: 1,
      },
    });
    await linkLabelsResource.reload();

    if (linkLabelsResource.data) {
      displayValues.value = resolved.map((item) => {
        const match = linkLabelsResource.data.find(
          (opt) => opt.value === item.link_value
        );
        return {
          ...item,
          label: match ? match.label || match.value : item.link_value,
        };
      });
    }
  }
};

watch(
  [() => values.value, linkFieldName],
  () => {
    resolveValues();
  },
  { deep: true }
);

onMounted(() => {
  if (values.value?.length) {
    resolveValues();
  }
});

const selectedValue = computed({
  get: () => query.value || "",
  set: (val) => {
    query.value = "";
    if (val) {
      showOptions.value = false;
    }
    val && addValue(val);
  },
});

const serializeFilters = (f) => {
  if (!f) return "{}";
  return typeof f === "string" ? f : JSON.stringify(f);
};

watchDebounced(
  query,
  (val) => {
    val = val || "";
    if (text.value === val) return;
    text.value = val;
    reload(val);
  },
  { debounce: 300, immediate: true }
);

const filterOptions = createResource({
  url: "non_profit.non_profit.api.custom_search_link",
  method: "POST",
  cache: [text.value, linkDoctype.value, serializeFilters(props.filters)],
  auto: false,
  makeParams() {
    if (!linkDoctype.value) {
      return null;
    }

    const params = {
      txt: text.value,
      doctype: linkDoctype.value,
      filters: serializeFilters(props.filters),
    };

    return params;
  },
  onError(error) {
    console.error("[MultiSelect] Error fetching filter options:", error);
  },
});

watch(
  linkDoctype,
  (newVal) => {
    if (newVal) {
      filterOptions.reload();
    }
  },
  { immediate: true }
);

const options = computed(() => {
  if (!filterOptions.data) {
    return [];
  }

  const currentLinkValues = displayValues.value.map((v) => v.link_value);

  const filtered = filterOptions.data.filter(
    (option) => !currentLinkValues.includes(option.value)
  );

  return filtered;
});

function reload(val) {
  if (!linkDoctype.value) {
    console.warn("[MultiSelect] Cannot reload, link doctype not set");
    return;
  }

  filterOptions.update({
    params: {
      txt: val,
      doctype: linkDoctype.value,
      filters: serializeFilters(props.filters),
    },
  });
  filterOptions.reload();
}

const addValue = (option) => {
  error.value = null;
  if (!option) return;

  let linkValue, labelValue;

  if (typeof option === "string") {
    linkValue = option.trim();
    labelValue = option.trim();
  } else {
    linkValue = option.value;
    labelValue = option.label || option.value;
  }

  if (displayValues.value.some((item) => item.link_value === linkValue)) {
    query.value = "";
    return;
  }

  if (props.validate && !props.validate(linkValue)) {
    error.value = props.errorMessage(linkValue);
    console.error("[MultiSelect] Validation failed:", error.value);
    return;
  }

  displayValues.value.push({
    link_value: linkValue,
    label: labelValue,
    childtable_id: null,
  });

  if (!values.value) {
    values.value = [];
  }
  values.value = [...values.value, linkValue];

  emit("change", values.value);

  query.value = "";
  showOptions.value = false;
};

const removeValue = (item) => {
  displayValues.value = displayValues.value.filter(
    (v) => v.link_value !== item.link_value
  );

  if (item.childtable_id) {
    values.value = values.value.filter((v) => v !== item.childtable_id);
  } else {
    values.value = values.value.filter((v) => v !== item.link_value);
  }

  emit("change", values.value);
};

const closeDropdown = (closeFunction) => {
  closeFunction();
  showOptions.value = false;
};

const removeLastValue = () => {
  if (query.value) return;
  if (displayValues.value.length) {
    const lastItem = displayValues.value[displayValues.value.length - 1];
    removeValue(lastItem);
    nextTick(() => {
      if (displayValues.value.length) {
        setFocus();
      }
    });
  }
};

function setFocus() {
  search.value?.$el?.focus();
}

defineExpose({ setFocus });

const labelClasses = computed(() => {
  return [
    { sm: "text-xs", md: "text-base" }[props.size || "sm"],
    "text-ink-gray-5",
  ];
});
</script>
