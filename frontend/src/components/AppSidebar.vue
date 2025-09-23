<template>
  <div
    class="flex h-full flex-col justify-between transition-all duration-300 ease-in-out border-r bg-surface-menu-bar"
    :class="sidebarStore.isSidebarCollapsed ? 'w-14' : 'w-56'"
  >
    <div
      class="flex flex-col overflow-hidden"
      :class="sidebarStore.isSidebarCollapsed ? 'items-center' : ''"
    >
      <UserDropdown :isCollapsed="sidebarStore.isSidebarCollapsed" />
      <div class="flex flex-col" v-if="sidebarSettings.data">
        <SidebarLink
          v-for="link in sidebarLinks"
          :link="link"
          :isCollapsed="sidebarStore.isSidebarCollapsed"
          class="mx-2 my-0.5"
        />
      </div>
      <div
        v-if="sidebarSettings.data?.web_pages?.length || isModerator"
        class="mt-4"
      >
        <div
          class="flex items-center justify-between pr-2 cursor-pointer"
          :class="sidebarStore.isSidebarCollapsed ? 'pl-3' : 'pl-4'"
          @click="toggleWebPages"
        >
          <div
            v-if="!sidebarStore.isSidebarCollapsed"
            class="flex items-center text-sm text-ink-gray-5 my-1"
          >
            <span class="grid h-5 w-6 flex-shrink-0 place-items-center">
              <ChevronRight
                class="h-4 w-4 stroke-1.5 text-ink-gray-9 transition-all duration-300 ease-in-out"
                :class="{ 'rotate-90': !sidebarStore.isWebpagesCollapsed }"
              />
            </span>
            <span class="ml-2">
              {{ __("More") }}
            </span>
          </div>
          <Button
            v-if="isModerator && !readOnlyMode"
            variant="ghost"
            @click="openPageModal()"
          >
            <template #icon>
              <Plus class="h-4 w-4 text-ink-gray-7 stroke-1.5" />
            </template>
          </Button>
        </div>
        <div
          v-if="sidebarSettings.data?.web_pages?.length"
          class="flex flex-col transition-all duration-300 ease-in-out"
          :class="!sidebarStore.isWebpagesCollapsed ? 'block' : 'hidden'"
        >
          <SidebarLink
            v-for="link in sidebarSettings.data.web_pages"
            :link="link"
            :isCollapsed="sidebarStore.isSidebarCollapsed"
            class="mx-2 my-0.5"
            :showControls="isModerator ? true : false"
            @openModal="openPageModal"
            @deletePage="deletePage"
          />
        </div>
      </div>
    </div>
    <div class="m-2 flex flex-col gap-1">
      <div
        v-if="readOnlyMode && !sidebarStore.isSidebarCollapsed"
        class="z-10 m-2 bg-surface-modal py-2.5 px-3 text-xs text-ink-gray-7 leading-5 rounded-md"
      >
        {{
          __(
            "This site is being updated. You will not be able to make any changes. Full access will be restored shortly."
          )
        }}
      </div>

      <div
        class="flex items-center mt-4"
        :class="
          sidebarStore.isSidebarCollapsed ? 'flex-col space-y-3' : 'flex-row'
        "
      >
        <div
          class="flex items-center flex-1"
          :class="
            sidebarStore.isSidebarCollapsed
              ? 'flex-col space-y-3'
              : 'flex-row space-x-3'
          "
        >
          <Tooltip v-if="readOnlyMode && sidebarStore.isSidebarCollapsed">
            <CircleAlert
              class="size-4 stroke-1.5 text-ink-gray-7 cursor-pointer"
            />
            <template #body>
              <div
                class="max-w-[30ch] rounded bg-surface-gray-7 px-2 py-1 text-center text-p-xs text-ink-white shadow-xl"
              >
                {{
                  __(
                    "This site is being updated. You will not be able to make any changes. Full access will be restored shortly."
                  )
                }}
              </div>
            </template>
          </Tooltip>
          <Tooltip :text="__('Powered by VMMS Portal')">
            <Zap
              class="size-4 stroke-1.5 text-ink-gray-7 cursor-pointer"
              @click="redirectToWebsite()"
            />
          </Tooltip>
          <Tooltip v-if="showOnboarding" :text="__('Help')">
            <CircleHelp
              class="size-4 stroke-1.5 text-ink-gray-7 cursor-pointer"
              @click="
                () => {
                  showHelpModal = minimize ? true : !showHelpModal;
                  minimize = !showHelpModal;
                }
              "
            />
          </Tooltip>
        </div>
        <Tooltip
          :text="
            sidebarStore.isSidebarCollapsed ? __('Expand') : __('Collapse')
          "
        >
          <CollapseSidebar
            class="size-4 text-ink-gray-7 duration-300 stroke-1.5 ease-in-out cursor-pointer"
            :class="{
              '[transform:rotateY(180deg)]': sidebarStore.isSidebarCollapsed,
            }"
            @click="toggleSidebar()"
          />
        </Tooltip>
      </div>
    </div>
  </div>
  <PageModal
    v-model="showPageModal"
    v-model:reloadSidebar="sidebarSettings"
    :page="pageToEdit"
  />
</template>

<script setup>
import UserDropdown from "@/components/UserDropdown.vue";
import CollapseSidebar from "@/components/Icons/CollapseSidebar.vue";
import SidebarLink from "@/components/SidebarLink.vue";
import {
  ref,
  onMounted,
  inject,
  onUnmounted,
} from "vue";
import { getSidebarLinks } from "@/utils";
import { usersStore } from "@/stores/user";
import { sessionStore } from "@/stores/session";
import { useSidebar } from "@/stores/sidebar";
import { useSettings } from "@/stores/settings";
import { Button, Tooltip } from "frappe-ui";
import PageModal from "@/components/Modals/PageModal.vue";
import { useRouter } from "vue-router";
import {
  CircleAlert,
  ChevronRight,
  Plus,
  CircleHelp,
  Zap,
} from "lucide-vue-next";
import {
  showHelpModal,
  minimize,
} from "frappe-ui/frappe";

const { user } = sessionStore();
const { userResource } = usersStore();
let sidebarStore = useSidebar();
const socket = inject("$socket");
const sidebarLinks = ref(getSidebarLinks());
const showPageModal = ref(false);
const isModerator = ref(false);
const pageToEdit = ref(null);
const settingsStore = useSettings();
const { sidebarSettings } = settingsStore;
const showOnboarding = ref(false);
const readOnlyMode = window.read_only_mode;

onMounted(() => {
  setSidebarLinks();
});

const setSidebarLinks = () => {
  sidebarSettings.reload(
    {},
    {
      onSuccess(data) {
        Object.keys(data).forEach((key) => {
          if (!parseInt(data[key])) {
            sidebarLinks.value = sidebarLinks.value.filter(
              (link) => link.label.toLowerCase().split(" ").join("_") !== key
            );
          }
        });
      },
    }
  );
};

const openPageModal = (link) => {
  showPageModal.value = true;
  pageToEdit.value = link;
};

const toggleSidebar = () => {
  sidebarStore.isSidebarCollapsed = !sidebarStore.isSidebarCollapsed;
  localStorage.setItem(
    "isSidebarCollapsed",
    JSON.stringify(sidebarStore.isSidebarCollapsed)
  );
};

const toggleWebPages = () => {
  sidebarStore.isWebpagesCollapsed = !sidebarStore.isWebpagesCollapsed;
  localStorage.setItem(
    "isWebpagesCollapsed",
    JSON.stringify(sidebarStore.isWebpagesCollapsed)
  );
};

const redirectToWebsite = () => {
  window.open(
    "https://github.com/navariltd/non_profit/tree/ft/volunteer-member-portal",
    "_blank"
  );
};

onUnmounted(() => {
  socket.off("publish_lms_notifications");
});
</script>
