<template>
  <div>
    <!-- <label class="block mb-1" :class="labelClasses" v-if="label">
      {{ label }}
      <span class="text-ink-red-3" v-if="required">*</span>
    </label> -->

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

    <div v-if="values.length" class="grid grid-cols-2 gap-2 mt-1">
      <div
        v-for="item in values"
        :key="item.value"
        class="flex items-center justify-between break-all bg-surface-gray-2 text-ink-gray-7 word-wrap p-2 rounded-md mr-2"
      >
        <span class="break-all">{{ item.label || item.value }}</span>
        <X
          v-if="!props.readOnly"
          class="size-4 stroke-1.5 cursor-pointer"
          @click="removeValue(item.value)"
        />
      </div>
    </div>

    <CreateNewEntryDialog
      v-model="showCreateDialog"
      :doctype="props.doctype"
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
import { ref, computed, nextTick, useAttrs } from "vue";
import { watchDebounced } from "@vueuse/core";
import { X, Plus } from "lucide-vue-next";
import CreateNewEntryDialog from "../Modals/CreateNewEntryDialog.vue";

const props = defineProps({
  label: String,
  size: { type: String, default: "sm" },
  doctype: { type: String, required: true },
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
const attrs = useAttrs();
const emails = ref([]);
const search = ref(null);
const error = ref(null);
const query = ref("");
const text = ref("");
const showOptions = ref(false);
const showCreateDialog = ref(false);
const emit = defineEmits(["change"]);

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
  cache: [text.value, props.doctype, serializeFilters(props.filters)],
  auto: true,
  params: {
    txt: text.value,
    doctype: props.doctype,
    filters: serializeFilters(props.filters),
  },
});

const options = computed(() => {
  if (!filterOptions.data) return [];
  return filterOptions?.data?.filter(
    (option) => !values?.value?.some((item) => item.value === option.value)
  );
});

function reload(val) {
  filterOptions.update({
    params: {
      txt: val,
      doctype: props.doctype,
      filters: serializeFilters(props.filters),
    },
  });
  filterOptions.reload();
}

const addValue = (option) => {
  error.value = null;
  if (option) {
    let valueToAdd, labelToAdd;

    if (typeof option === "string") {
      valueToAdd = option.trim();
      labelToAdd = option.trim();
    } else {
      valueToAdd = option.value;
      labelToAdd = option.label || option.value;
    }

    if (
      valueToAdd &&
      !values.value?.some((item) => item.value === valueToAdd)
    ) {
      if (props.validate && !props.validate(valueToAdd)) {
        error.value = props.errorMessage(valueToAdd);
        return;
      }

      const newItem = { value: valueToAdd, label: labelToAdd };

      if (!values.value) {
        values.value = [newItem];
      } else {
        values.value.push(newItem);
      }
      emit("change", values.value);
      showOptions.value = false;
    }
    !error.value && (query.value = "");
  }
};

const closeDropdown = (closeFunction) => {
  closeFunction();
  showOptions.value = false;
};

const removeValue = (value) => {
  values.value = values.value.filter((item) => item.value !== value);
  emit("change", values.value);
};

const removeLastValue = () => {
  if (query.value) return;
  let emailRef = emails.value[emails.value.length - 1]?.$el;
  if (document.activeElement === emailRef) {
    values.value.pop();
    nextTick(() => {
      if (values.value.length) {
        emailRef = emails.value[emails.value.length - 1].$el;
        emailRef?.focus();
      } else {
        setFocus();
      }
    });
  } else {
    emailRef?.focus();
  }
};

function setFocus() {
  search.value.$el.focus();
}

defineExpose({ setFocus });

const labelClasses = computed(() => {
  return [
    { sm: "text-xs", md: "text-base" }[props.size || "sm"],
    "text-ink-gray-5",
  ];
});
</script>
