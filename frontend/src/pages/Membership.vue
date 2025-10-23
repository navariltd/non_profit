<template>
  <NoPermission v-if="user?.data == 'Guest'" :page="'Membership'" />
  <div
    class="space-y-4 mx-auto px-4"
    v-if="user?.data && user?.data !== 'Guest'"
  >
    <ErrorMessage
      v-if="currentMembership.error || membershipTypes.error"
      class="text-center border rounded-md p-2 border-red-500 bg-red-50 text-sm my-auto mt-20"
      message="Failed to get Membership Details"
    />

    <div
      v-else-if="currentMembership.data"
      class="w-full flex flex-col items-center"
    >
      <Member
        v-if="currentMembership.data.length > 0"
        :membershipStatus="currentMembership.data"
      />
      <EmptyState v-else type="Membership" class="mt-6" />
    </div>

    <div
      v-if="currentMembership.data"
      class="p-2 pt-2 md:p-8 bg-gray-50 rounded-2xl shadow-md text-center mb-20"
    >
      <h1 class="text-3xl font-bold text-gray-800">Select a New Plan</h1>

      <div v-if="membershipTypes.data?.length > 0" class="mt-10">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          <div
            v-for="membershipType in membershipTypes.data"
            :key="membershipType.name"
            class="flex justify-center"
          >
            <VmmsPortalCard
              class="w-full max-w-sm transition hover:scale-105 hover:shadow-lg cursor-pointer"
              :membershipType="membershipType"
              @click="selectMembershipType(membershipType)"
            />
          </div>
        </div>
      </div>

      <EmptyState v-else type="Membership Type" class="mt-10" />
    </div>

    <div
      v-if="registerDialog"
      class="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div
        class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
      >
        <div
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          aria-hidden="true"
          @click="cleanUpMembershipForm"
        ></div>

        <span
          class="hidden sm:inline-block sm:align-middle sm:h-screen"
          aria-hidden="true"
          >&#8203;</span
        >

        <div
          class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle w-full max-w-xl md:max-w-3xl"
        >
          <div class="bg-gray-50 px-4 py-5 sm:px-6 border-b">
            <h3 class="text-2xl font-bold text-gray-900" id="modal-title">
              Register as a <span class="text-red-600">Member</span>
            </h3>
          </div>

          <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <form @submit.prevent="submit" class="space-y-6">
              <p class="text-gray-600">
                Please fill in the details below to complete your membership
                registration.
              </p>

              <div class="bg-white border rounded-lg p-4 shadow-sm">
                <Link
                  id="branch"
                  :label="'Branch / County'"
                  doctype="Company"
                  :required="true"
                  :filters="{ is_group: 0 }"
                  v-model="membershipForm.branch"
                  class="w-full"
                  :readonly="payNow"
                />
              </div>

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

              <ErrorMessage
                v-if="!payNow && createMembership.error"
                class="text-center border rounded-md p-2 border-red-500 bg-red-50 text-sm"
                :message="createMembership.error"
              />

              <div
                v-if="!payNow"
                class="flex flex-col sm:flex-row justify-end gap-3 pt-2"
              >
                <Button
                  type="button"
                  variant="outline"
                  theme="red"
                  class="rounded-lg px-5"
                  @click="cleanUpMembershipForm"
                >
                  Cancel
                </Button>

                <Button
                  type="submit"
                  variant="solid"
                  theme="green"
                  :loading="createMembership.loading"
                  class="rounded-lg px-6"
                >
                  Register
                </Button>
              </div>

              <div v-if="payNow" class="flex flex-col space-y-4">
                <span
                  class="text-center text-blue-800 border rounded-md p-2 border-blue-500 bg-blue-50 text-sm"
                >
                  Registration Initiated! Please proceed to pay for your
                  membership below.
                </span>

                <Input
                  :type="'text'"
                  :ref_for="true"
                  size="sm"
                  variant="subtle"
                  :disabled="false"
                  label="Enter Mpesa Phone Number to Pay"
                  v-model="membershipForm.phone_number"
                  required
                />

                <ErrorMessage
                  v-if="createMembership.error"
                  class="text-center border rounded-md p-2 border-red-500 bg-red-50 text-sm"
                  :message="createMembership.error"
                />

                <div class="flex flex-col sm:flex-row justify-end gap-3 pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    theme="red"
                    class="rounded-lg px-5"
                    @click="cleanUpMembershipForm"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="button"
                    variant="solid"
                    theme="red"
                    icon-right="credit-card"
                    class="rounded-lg px-6"
                    @click="payMembership"
                    :loading="renewMembership.loading"
                  >
                    Pay Now
                  </Button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, createResource, ErrorMessage, Input, toast } from "frappe-ui";
import { inject, reactive, ref, watch } from "vue";
import Link from "../components/Controls/Link.vue";
import EmptyState from "../components/EmptyState.vue";
import Member from "../components/MemberPlan.vue";
import { membershipStore } from "../stores/membership";
import { isValidPhone } from "../utils/volunteer";

const { membershipTypes, currentMembership } = membershipStore();
const user = inject < any > "$user";
const membershipId = ref < string > "";

const registerDialog = ref(false);
const payNow = ref(false);
const membershipForm = reactive({
  membership_type: "",
  amount: 0,
  branch: "",
  member_name: user.data ? user.data.full_name : "",
  email_id: user.data ? user.data.email : "",
  phone_number: "",
});

const createMembership = createResource({
  url: "non_profit.non_profit.user.create_membership",
  onSuccess(data) {
    membershipId.value = data;
    toast.success("Membership created successfully");
    currentMembership.reload();
    membershipTypes.reload();
    payNow.value = true;
  },
});

const renewMembership = createResource({
  url: "non_profit.non_profit.user.renew_membership",
  makeParams() {
    return {
      id: membershipId.value,
      phone_number: membershipForm.phone_number,
    };
  },
  onSuccess() {
    toast.success(
      "Membership payment initiated successfully! Check your phone for a prompt."
    );
  },
  onError(error) {
    toast.error(error.message || "Failed to initiate membership payment.");
  },
});

function cleanUpMembershipForm() {
  registerDialog.value = false;
  membershipForm.membership_type = "";
  membershipForm.amount = 0;
  membershipForm.branch = "";
  membershipForm.phone_number = "";
  payNow.value = false;
  createMembership.error = "";
}

function selectMembershipType(membershipType) {
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

function payMembership() {
  if (!membershipForm.phone_number) {
    createMembership.error = "Please enter your phone number";
    return;
  }

  if (!isValidPhone(membershipForm.phone_number)) {
    createMembership.error =
      "Please enter a valid Kenyan phone number.eg. (+254123456789)";
    return;
  }
  createMembership.error = "";

  const membershipId = currentMembership.data?.[0]?.name;

  if (membershipId) {
    renewMembership.submit({
      membership: membershipId,
      phone_number: membershipForm.phone_number,
    });
  } else {
    toast.info(
      "Payment can only be initiated after a membership document has been created."
    );
  }
}

watch(registerDialog, (newValue) => {
  if (newValue === false) {
    cleanUpMembershipForm();
  }
});
</script>
