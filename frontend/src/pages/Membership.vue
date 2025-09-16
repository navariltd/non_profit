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
  <Dialog v-model="registerDialog" class="">
    <template #body-title>
      <h3 class="text-2xl font-bold text-gray-900">
        Register as a <span class="text-red-600">Member</span>
      </h3>
    </template>

    <template #body-content>
      <form @submit.prevent="submit" class="space-y-6">
        <p class="text-gray-600">
          Please fill in the details below to complete your membership
          registration.
        </p>

        <div class="bg-white border rounded-lg p-4 shadow-sm">
          <div class="flex w-full flex-col">
            <label for="branch" class="text-sm font-medium text-gray-700 mb-1">
              Branch/County
            </label>
            <Link
              required
              id="branch"
              doctype="Company"
              v-model="membershipForm.branch"
              placeholder="Select Branch"
              class="w-full"
            />
          </div>
        </div>

        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="font-medium text-gray-800">
            Membership Type:
            <span class="text-red-600">{{
              membershipForm.membership_type
            }}</span>
          </p>
          <p class="text-gray-700">
            Amount:
            <span class="font-semibold">KES {{ membershipForm.amount }}</span>
          </p>
        </div>

        <ErrorMessage
          v-if="createMembership.error"
          class="text-center border rounded-md p-2 border-red-500 bg-red-50 text-sm"
          :message="createMembership.error"
        />

        <div class="flex justify-end gap-3 pt-2">
          <Button
            variant="outline"
            theme="red"
            class="rounded-lg px-5"
            @click="cleanUpMembershipForm()"
          >
            Cancel
          </Button>
          <Button
            variant="solid"
            theme="red"
            :loading="createMembership.loading"
            class="rounded-lg px-6"
          >
            Register
          </Button>
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
  membershipForm.branch = "";
  createMembership.error = "";
}

const registerDialog = ref(false);
const membershipForm = reactive({
  membership_type: "",
  amount: 0,
  branch: "",
  member_name: user.data ? user.data.full_name : "",
  email_id: user.data ? user.data.email : "",
});

function selectMembershipType(membershipType: any) {
  membershipForm.membership_type = membershipType.membership_type;
  membershipForm.amount = membershipType.amount;
  registerDialog.value = true;
}




const submit = () => {
  if (!membershipForm.branch) {
    createMembership.error = "Please select a branch";
    return;
  }

  createMembership.submit({ ...membershipForm });
};
</script>
