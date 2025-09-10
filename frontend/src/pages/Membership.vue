<template>
  <div>
    <div>
      <div class="justify-start mb-5 w-full">
        <Member
          v-if="currentMembership.data"
          :membershipStatus="currentMembership.data"
        />
        <EmptyState v-else type="Membership" />
      </div>
    </div>
    <div>
      <h1 class="text-3xl px-12">Select plan to continue</h1>
      <div
        v-if="membershipTypes.data?.length > 0"
        class="flex justify-center mt-10"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="membershipType in membershipTypes.data"
            :key="membershipType.name"
            :to="{ name: 'Login' }"
            class="flex justify-center cursor-pointer"
          >
            <VmmsPortalCard
              :membershipType="membershipType"
              @click="selectMembershipType(membershipType)"
            />
          </div>
        </div>
      </div>
      <EmptyState v-else type="" />
    </div>
  </div>
  <Dialog v-model="registerDialog">
    <template #body-title>
      <h3 class="text-2xl font-semibold">Register as a Member</h3>
    </template>
    <template #body-content>
      <form action="" @submit.prevent="submit" class="space-y-4">
        <div class="space-y-4">
          <p class="text-gray-700">
            Please fill in the details below to register as a member.
          </p>
          <div class="w-full border p-4 rounded-lg bg-white">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="flex flex-col">
                <label for="branch" class="text-gray-600 text-sm mb-2"
                  >Branch/County</label
                >
                <Link
                  required
                  id="branch"
                  doctype="Branch"
                  v-model="membershipForm.branch"
                  placeholder="Branch"
                  class="w-full"
                />
              </div>
              <div class="flex flex-col">
                <label for="region" class="text-gray-600 text-sm mb-2"
                  >Region</label
                >
                <Input
                  id="region"
                  doctype="Company"
                  v-model="membershipForm.region"
                  placeholder="Region"
                  class="w-full"
                  readonly
                />
              </div>
            </div>
          </div>
          <div class="bg-blue-50 p-4 rounded-lg">
            <p class="">
              Register for membership: {{ membershipForm.membership_type }}
            </p>
            <p class="">Amount: {{ membershipForm.amount }}</p>
          </div>
        </div>
        <div class="flex justify-end mt-3 gap-2">
          <Button
            variant="outline"
            theme="red"
            @click="cleanUpMembershipForm()"
          >
            Cancel
          </Button>
          <Button variant="solid" :loading="createMembership.loading">
            Register
          </Button>
        </div>

        <div class="">
          <ErrorMessage
            class="mt-2 text-center border rounded-md p-1 border-red-500"
            :message="createMembership.error"
          />
        </div>
      </form>
    </template>
    <template #actions="{ close }"> </template>
  </Dialog>
</template>
<script lang="ts" setup>
import { inject, onMounted, reactive, ref, watch } from "vue";
import { membershipStore } from "../stores/membership";
import {
  Dialog,
  Button,
  createResource,
  Input,
  ErrorMessage,
  toast,
} from "frappe-ui";
import Member from "../components/MemberPlan.vue";
import EmptyState from "../components/EmptyState.vue";

const { membershipTypes, currentMembership } = membershipStore();
interface RegionOption {
  label: string;
  value: string;
  company: string;
}
const branchOptions = ref<RegionOption[]>([]);
const user = inject<any>("$user");
const branches = createResource({
  url: "non_profit.non_profit.api.get_branches",
  auto: true,
  onSuccess(data: any) {
    branchOptions.value = data.map((branch) => {
      return {
        label: branch.name,
        value: branch.name,
        company: branch.company,
      };
    });
  },
});

const createMembership = createResource({
  url: "non_profit.non_profit.user.create_membership",
  onSuccess(data: any) {
    toast.success("Membership created successfully");
    currentMembership.reload();
    registerDialog.value = false;
    cleanUpMembershipForm();
  },
});

function cleanUpMembershipForm() {
  registerDialog.value = false;
  membershipForm.membership_type = "";
  membershipForm.amount = 0;
  membershipForm.region = "";
  membershipForm.branch = "";
  createMembership.error = "";
}

const registerDialog = ref(false);
const membershipForm = reactive({
  membership_type: "",
  amount: 0,
  region: "",
  branch: "",
  member_name: user.data ? user.data.full_name : "",
  email_id: user.data ? user.data.email : "",
});

function selectMembershipType(membershipType: any) {
  membershipForm.membership_type = membershipType.membership_type;
  membershipForm.amount = membershipType.amount;
  registerDialog.value = true;
}

onMounted(() => {
  branches.fetch();
});
watch(
  () => membershipForm.branch,
  (newBranch) => {
    const selectedBranch = branchOptions.value.find(
      (b) => b.value === newBranch
    );

    if (selectedBranch) {
      membershipForm.region = selectedBranch.company;
    } else {
      membershipForm.region = "";
    }

    if (newBranch) {
      createMembership.error = "";
    }
  }
);

const submit = () => {
  if (!membershipForm.branch) {
    createMembership.error = "Please select a branch";
    return;
  }

  createMembership.submit({ ...membershipForm });
};
</script>
