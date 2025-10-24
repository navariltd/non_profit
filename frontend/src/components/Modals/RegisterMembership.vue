<template>
  <Dialog v-model="registerDialog">
    <template #body-title>
      <h3 class="text-2xl font-bold text-gray-900" id="modal-title">
        Register as a <span class="text-red-600">Member</span>
      </h3>
    </template>

    <template #body-content>
      <div class="py-4">
        <form action="" @submit.prevent="submit">
          <div
            class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6 p-4 bg-white border border-red-400 rounded-2xl shadow-sm"
          >
            <div class="space-y-1">
              <FormControl
                type="text"
                label="Membership Type"
                placeholder="Select membership type"
                class="w-full text-sm"
                v-model="membershipForm.membership_type"
                :value="props.membership_type"
                readonly
              />
            </div>

            <div class="space-y-1">
              <FormControl
                type="number"
                label="Amount"
                placeholder="Enter amount"
                class="w-full text-sm"
                v-model="membershipForm.amount"
                :value="props.amount"
                readonly
              />
            </div>
          </div>

          <FormControl
            type="autocomplete"
            label="Branch / County"
            placeholder="Select branch or county to register with"
            class="w-full mb-4"
            :options="branches.data"
            v-model="branch"
          />
          <FormControl
            type="text"
            label="Phone Number (MPesa Phone Number to be used for payment)"
            placeholder="eg. 0712345678"
            class="w-full"
            v-model="membershipForm.phone"
          />

          <ErrorMessage
            v-if="createMembership.error"
            class="text-center border rounded-md p-2 border-red-500 bg-red-50 text-sm my-3"
            :message="createMembership.error"
          />
          <div class="mt-4 gap-2 flex items-end justify-end">
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
        </form>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import {
  createListResource,
  Dialog,
  FormControl,
  Button,
  createResource,
  Input,
} from "frappe-ui";
import ErrorMessage from "frappe-ui/src/components/ErrorMessage/ErrorMessage.vue";
import { reactive, ref, toRaw, watch, watchEffect } from "vue";
import { isValidPhone } from "../../utils/volunteer";

const registerDialog = defineModel();
const branch = ref("");

const membershipForm = reactive({
  phone: "",
  amount: 0,
  membership_type: "",
});

const props = defineProps({
  membership_type: String,
  amount: Number,
});

watchEffect(() => {
  membershipForm.membership_type = props.membership_type;
  membershipForm.amount = props.amount;
});

watch(branch, (newValue) => {
  const selectedBranch = toRaw(newValue);
  if (selectedBranch) {
    membershipForm.branch = selectedBranch.value;
  } else {
    membershipForm.branch = "";
  }
});

const branches = createListResource({
  doctype: "Company",
  filters: { is_group: 0 },
  cache: "branches",
  transform: (data) =>
    data.map((item) => ({ label: item.name, value: item.name })),
});

const createMembership = createResource({
  url: "non_profit.non_profit.user.create_membership",
  makeParams() {
    return { ...membershipForm };
  },
});

function submit() {
  if (!branch.value || !membershipForm.phone) {
    createMembership.error =
      "Please fill in all required fields before submitting.";
    return;
  }
  if (!isValidPhone(membershipForm.phone)) {
    createMembership.error = "Please enter a valid phone number.";
    return;
  }

  createMembership.error = "";
  createMembership.submit(
    {},
    {
      onSuccess(data) {},
      onError(error) {},
    }
  );
}

watch(registerDialog, (isOpen) => {
  if (!isOpen) {
    branch.value = "";
    membershipForm.phone = "";
    createMembership.error = "";
  }
});
</script>
