<template>
  <div class="space-y-8">
    <!-- Membership Status -->
    <div class="w-full">
      <Member
        v-if="currentMembership.data"
        :membershipStatus="currentMembership.data"
      />
      <EmptyState v-else type="Membership" />
    </div>

    <!-- Membership Types -->
    <div class="p-4 bg-gray-50 rounded-xl shadow-sm">
      <h1 class="text-3xl font-bold text-gray-800">
        Select a Plan to Continue
      </h1>

      <div v-if="membershipTypes.data?.length > 0" class="mt-10">
        <div
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 place-items-stretch"
        >
          <div
            v-for="membershipType in membershipTypes.data"
            :key="membershipType.name"
            class="flex"
          >
            <VmmsPortalCard
              class="w-full transition hover:scale-105 hover:shadow-lg cursor-pointer"
              :membershipType="membershipType"
              @click="selectMembershipType(membershipType)"
            />
          </div>
        </div>
      </div>

      <EmptyState v-else type="Membership Type" class="mt-10" />
    </div>

    <div class="w-full justify-center text-center">
      <Dialog v-model="registerDialog">
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

            <!-- Branch -->
            <div class="bg-white border rounded-lg p-4 shadow-sm">
              <Link
                id="branch"
                :label="'Branch / County'"
                doctype="Company"
                :required="true"
                :filters="{ is_group: 0 }"
                v-model="membershipForm.branch"
                class="w-full"
              />
            </div>

            <!-- Membership Info -->
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
              <p class="font-medium text-gray-800">
                Membership Type:
                <span class="text-red-600">
                  {{ membershipForm.membership_type }}
                </span>
              </p>
              <p class="text-gray-700 mt-1">
                Amount:
                <span class="font-semibold"
                  >KES {{ membershipForm.amount }}</span
                >
              </p>
            </div>

            <!-- Error -->
            <ErrorMessage
              v-if="createMembership.error"
              class="text-center border rounded-md p-2 border-red-500 bg-red-50 text-sm"
              :message="createMembership.error"
            />

            <!-- Actions -->
            <div class="flex justify-end gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                theme="red"
                class="rounded-lg px-5"
                @click="cleanUpMembershipForm()"
              >
                Cancel
              </Button>
              <Button
                type="submit"
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
      </Dialog>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { inject, reactive, ref } from "vue";
import { membershipStore } from "../stores/membership";
import { Dialog, Button, createResource, ErrorMessage, toast } from "frappe-ui";
import Member from "../components/MemberPlan.vue";
import EmptyState from "../components/EmptyState.vue";
import Link from "../components/Controls/Link.vue";

const { membershipTypes, currentMembership } = membershipStore();

const user = inject<any>("$user");

const registerDialog = ref(false);
const membershipForm = reactive({
  membership_type: "",
  amount: 0,
  branch: "",
  member_name: user.data ? user.data.full_name : "",
  email_id: user.data ? user.data.email : "",
});

const createMembership = createResource({
  url: "non_profit.non_profit.user.create_membership",
  onSuccess() {
    toast.success("Membership created successfully");
    currentMembership.reload();
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

function selectMembershipType(membershipType: any) {
  membershipForm.membership_type = membershipType.membership_type;
  membershipForm.amount = membershipType.amount;
  registerDialog.value = true;
}

function submit() {
  if (!membershipForm.branch) {
    createMembership.error = "Please select a branch";
    return;
  }
  createMembership.submit({ ...membershipForm });
}
</script>
