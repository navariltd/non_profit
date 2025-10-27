<template>
  <div>
    <div v-if="label" class="text-xs text-ink-gray-5 mb-1">
      {{ __(label) }}
      <span class="text-ink-red-3" v-if="attrs.required">*</span>
    </div>
    <Combobox
      v-model="selectedValue"
      nullable
      v-slot="{ open: isComboboxOpen }"
    >
      <div class="w-full">
        <div ref="triggerRef">
          <slot
            name="target"
            v-bind="{ open: openDropdown, togglePopover: toggleDropdown }"
          >
            <div class="w-full">
              <button
                class="flex w-full items-center justify-between focus:outline-none"
                :class="inputClasses"
                @click="toggleDropdown"
                :disabled="attrs.readonly"
              >
                <div class="flex items-center">
                  <slot name="prefix" />
                  <span
                    class="overflow-hidden text-ellipsis whitespace-nowrap text-base leading-5"
                    v-if="selectedValue"
                  >
                    {{ displayValue(selectedValue) }}
                  </span>
                  <span class="text-base leading-5 text-ink-gray-4" v-else>
                    {{ placeholder || "" }}
                  </span>
                </div>
                <ChevronDown class="h-4 w-4 stroke-1.5" />
              </button>
            </div>
          </slot>
        </div>
      </div>

      <Teleport to="body">
        <div
          v-show="showOptions"
          ref="dropdownRef"
          class="fixed z-[9999] mt-1 rounded-lg bg-surface-white py-1 text-base border-2 shadow-lg"
          :style="dropdownStyle"
        >
          <div class="relative px-1.5 pt-0.5">
            <ComboboxInput
              ref="search"
              class="form-input w-full"
              type="text"
              @change="(e) => (query = e.target.value)"
              :value="query"
              autocomplete="off"
              placeholder="Search"
            />
            <button
              class="absolute right-1.5 inline-flex h-7 w-7 items-center justify-center"
              @click="selectedValue = null"
            >
              <X class="h-4 w-4 stroke-1.5 text-ink-gray-7" />
            </button>
          </div>
          <ComboboxOptions
            ref="optionsContainer"
            class="my-1 max-h-[12rem] overflow-y-auto px-1.5"
            static
            @scroll="handleScroll"
          >
            <div
              class="mt-1.5"
              v-for="group in groups"
              :key="group.key"
              v-show="group.items.length > 0"
            >
              <div
                v-if="group.group && !group.hideLabel"
                class="px-2.5 py-1.5 text-sm font-medium text-ink-gray-4"
              >
                {{ group.group }}
              </div>
              <ComboboxOption
                as="template"
                v-for="option in group.items"
                :key="option.value"
                :value="option"
                v-slot="{ active, selected }"
              >
                <li
                  :class="[
                    'flex items-center rounded px-2.5 py-2 text-base',
                    { 'bg-surface-gray-2': active },
                  ]"
                >
                  <slot
                    name="item-prefix"
                    v-bind="{ active, selected, option }"
                  />
                  <slot name="item-label" v-bind="{ active, selected, option }">
                    <div class="flex flex-col space-y-1 text-ink-gray-8">
                      <div>{{ option.label }}</div>
                      <div
                        v-if="
                          option.description &&
                          option.description != option.label
                        "
                        class="text-xs text-ink-gray-7"
                        v-html="option.description"
                      ></div>
                    </div>
                  </slot>
                </li>
              </ComboboxOption>
            </div>
            <li
              v-if="!isLoading && groups.length == 0"
              class="mt-1.5 rounded-md px-2.5 py-1.5 text-base text-ink-gray-5"
            >
              No results found
            </li>
            <li
              v-if="isLoading"
              class="flex items-center justify-center py-2 text-sm text-ink-gray-5"
            >
              <svg
                class="animate-spin h-4 w-4 mr-2 text-ink-gray-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8H4z"
                ></path>
              </svg>
              Loading more...
            </li>
          </ComboboxOptions>

          <div v-if="slots.footer" class="border-t p-1.5 pb-0.5">
            <slot name="footer" v-bind="{ value: search?.el._value, close }" />
          </div>
        </div>
      </Teleport>
    </Combobox>
  </div>
</template>

<script setup>
import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/vue";
import { ChevronDown, X } from "lucide-vue-next";
import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  ref,
  useAttrs,
  useSlots,
  watch,
} from "vue";

const props = defineProps({
  modelValue: String,
  options: Array,
  size: String,
  label: String,
  variant: String,
  placeholder: String,
  disabled: Boolean,
  filterable: Boolean,
  pageLength: { type: Number, default: 10 },
  loadMore: { type: Function, default: null },
});

const emit = defineEmits(["update:modelValue", "update:query", "change"]);

const query = ref("");
const showOptions = ref(false);
const search = ref(null);
const triggerRef = ref(null);
const dropdownRef = ref(null);
const dropdownStyle = ref({});
const optionsContainer = ref(null);

const attrs = useAttrs();
const slots = useSlots();
const isLoading = ref(false);
const stopLoading = ref(false);

const valuePropPassed = computed(() => "value" in attrs);
const selectedValue = computed({
  get() {
    return valuePropPassed.value ? attrs.value : props.modelValue;
  },
  set(val) {
    query.value = "";
    if (val) showOptions.value = false;
    emit(valuePropPassed.value ? "change" : "update:modelValue", val);
  },
});

function toggleDropdown() {
  showOptions.value = !showOptions.value;
  if (showOptions.value) updateDropdownPosition();
}
function openDropdown() {
  showOptions.value = true;
  updateDropdownPosition();
}
function close() {
  showOptions.value = false;
}

function updateDropdownPosition() {
  nextTick(() => {
    if (triggerRef.value) {
      const rect = triggerRef.value.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const isNearBottom = rect.bottom > viewportHeight * 0.75;
      const dropdownHeight = dropdownRef.value?.offsetHeight || 200;
      dropdownStyle.value = {
        top: isNearBottom
          ? `${rect.top + window.scrollY - dropdownHeight - 8}px`
          : `${rect.bottom + window.scrollY + 4}px`,
        left: `${rect.left + window.scrollX}px`,
        width: `${rect.width}px`,
      };
    }
  });
}

const groups = computed(() => {
  if (!props.options || props.options.length == 0) return [];
  let groups = props.options[0]?.group
    ? props.options
    : [{ group: "", items: props.options }];
  return groups.map((group, i) => ({
    key: i,
    group: group.group,
    hideLabel: group.hideLabel || false,
    items: props.filterable ? filterOptions(group.items) : group.items,
  }));
});

function filterOptions(options) {
  if (!query.value) return options;
  return options.filter((option) =>
    [option.label, option.value].some((t) =>
      (t || "").toLowerCase().includes(query.value.toLowerCase())
    )
  );
}

function displayValue(option) {
  if (typeof option === "string") {
    let allOptions = groups.value.flatMap((g) => g.items);
    let selected = allOptions.find((o) => o.value === option);
    return selected?.label || option;
  }
  return option?.label;
}

async function handleScroll(e) {
  if (isLoading.value || stopLoading.value || !props.loadMore) return;
  const el = e.target;
  const scrollRatio = el.scrollTop / (el.scrollHeight - el.clientHeight);
  if (scrollRatio >= 0.6) {
    isLoading.value = true;
    const currentLength = props.options.length;
    const more = await props.loadMore(query.value, props.pageLength);
    const newOptions = [...props.options, ...(more || [])];
    const unique = newOptions.filter(
      (v, i, a) => a.findIndex((t) => t.value === v.value) === i
    );
    if (unique.length === currentLength) stopLoading.value = true;
    emit("change", unique);
    isLoading.value = false;
  }
}

watch(query, (q) => emit("update:query", q));

watch(showOptions, (val) => {
  if (val) {
    nextTick(() => search.value.el.focus());
    window.addEventListener("scroll", updateDropdownPosition, true);
    window.addEventListener("resize", updateDropdownPosition);
  } else {
    window.removeEventListener("scroll", updateDropdownPosition, true);
    window.removeEventListener("resize", updateDropdownPosition);
  }
});

onMounted(() => {
  document.addEventListener("click", handleOutsideClick, true);
  document.addEventListener("focusin", handleOutsideClick, true);
});
onUnmounted(() => {
  document.removeEventListener("click", handleOutsideClick, true);
  document.removeEventListener("focusin", handleOutsideClick, true);
  window.removeEventListener("scroll", updateDropdownPosition, true);
  window.removeEventListener("resize", updateDropdownPosition);
});

function handleOutsideClick(e) {
  if (
    showOptions.value &&
    !triggerRef.value.contains(e.target) &&
    !dropdownRef.value.contains(e.target)
  ) {
    showOptions.value = false;
  }
}

const textColor = computed(() =>
  props.disabled ? "text-ink-gray-5" : "text-ink-gray-8"
);
const inputClasses = computed(() => {
  const s = {
    sm: "text-base rounded h-7",
    md: "text-base rounded h-8",
    lg: "text-lg rounded-md h-10",
    xl: "text-xl rounded-md h-10",
  }[props.size];
  const p = {
    sm: "py-1.5 px-2",
    md: "py-1.5 px-2.5",
    lg: "py-1.5 px-3",
    xl: "py-1.5 px-3",
  }[props.size];
  const v = props.disabled ? "disabled" : props.variant;
  const vc = {
    subtle:
      "border border-gray-100 bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm",
    outline:
      "border border-outline-gray-2 bg-surface-white hover:border-outline-gray-3 hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm",
    disabled:
      "border bg-surface-menu-bar placeholder-ink-gray-3 border-outline-gray-2",
  }[v];
  return [s, p, vc, textColor.value, "transition-colors w-full"];
});
defineExpose({ query });
</script>
