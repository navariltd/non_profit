<template>
  <div class="flex min-h-screen items-center justify-center">
    <Card
      :title="isLogin ? 'Login VMMS Portal' : 'Sign Up VMMS Portal'"
      :class="isLogin ? 'w-full max-w-md' : 'w-full max-w-2xl'"
    >
      <form class="flex flex-col space-y-4 w-full" @submit.prevent="submit">
        <template v-if="isLogin">
          <Input
            required
            name="email"
            type="text"
            placeholder="johndoe@email.com"
            label="Email"
            v-model="userEmail"
          />
          <Input
            required
            name="password"
            type="password"
            placeholder="••••••"
            label="Password"
            v-model="password"
          />
        </template>

        <template v-else>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              required
              name="firstname"
              type="text"
              placeholder="John"
              label="First Name"
              v-model="signUpForm.firstName"
            />
            <Input
              required
              name="lastname"
              type="text"
              placeholder="Doe"
              label="Last Name"
              v-model="signUpForm.lastName"
            />
          </div>
          <div class="w-full border p-4 rounded-lg bg-white">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="flex flex-col">
                <label for="branch" class="text-gray-600 text-sm mb-2"
                  >Branch/County</label
                >
                <Link
                  id="branch"
                  doctype="Branch"
                  v-model="signUpForm.branch"
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
                  v-model="signUpForm.region"
                  placeholder="Region"
                  class="w-full"
                  readonly
                />
              </div>
            </div>
          </div>

          <Input
            required
            name="email"
            type="text"
            placeholder="johndoe@email.com"
            label="Email"
            v-model="signUpForm.email"
          />
          <Input
            required
            type="text"
            variant="subtle"
            placeholder="+254123456789"
            label="PhoneNumber"
            v-model="signUpForm.phone_number"
          />
          <div>
            <label class="text-gray-600 text-sm mb-3">Gender</label>

            <Select
              required
              v-model="signUpForm.gender"
              class=""
              :options="genderOptions"
              placeholder="Female"
            />
          </div>
          <div class="flex flex-col space-y-1">
            <label class="text-sm font-medium">Please select Category</label>
            <div class="flex space-x-4">
              <label class="flex items-center space-x-1">
                <Checkbox
                  size="sm"
                  :value="false"
                  v-model="signUpForm.categoryVolunteer"
                  label="Volunteer"
                />
              </label>
              <label class="flex items-center space-x-1">
                <Checkbox
                  size="sm"
                  v-model="signUpForm.categoryMember"
                  label="Member"
                />
              </label>
              <Button
                v-if="signUpForm.categoryVolunteer"
                type="button"
                variant="subtle"
                @click="openVolunteerModal()"
                >Add Volunteer Details</Button
              >
            </div>
          </div>
        </template>

        <Button
          :loading="isLogin ? session.login.loading : createSignUp.loading"
          variant="solid"
          type="submit"
        >
          {{ isLogin ? "Login" : "Sign Up" }}
        </Button>
      </form>

      <div class="mt-2 text-center">
        <ErrorMessage
          :message="isLogin ? session.login.error : createSignUp.error"
        />
      </div>

      <div class="mt-4 text-center text-sm">
        <span v-if="isLogin">Don’t have an account? </span>
        <span v-else>Already have an account? </span>
        <Button
          class="text-blue-600 hover:underline"
          @click="isLogin = !isLogin"
          type="button"
        >
          {{ isLogin ? "Sign up" : "Login" }}
        </Button>
      </div>
    </Card>
  </div>

  <Dialog :options="{ size: '4xl' }" v-model="membershipDialog">
    <template #body-title>
      <h3 class="text-2xl font-semibold text-ink-gray-9">
        Select Membership Type
      </h3>
    </template>
    <template #body-content>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <VmmsPortalCard
          class="cursor-pointer"
          v-for="membershipType in membershipTypes.data"
          :key="membershipType.name"
          :membershipType="membershipType"
          @click="selectMembership(membershipType.name)"
        />
      </div>
    </template>
  </Dialog>

  <Dialog
    :options="{
      title: 'Successfully Registered',
      message: 'Await communication via email from RedCross',
      size: 'lg',
      icon: {
        name: 'alert-triangle',
        appearance: 'warning',
      },
    }"
    v-model="signInState"
  />

  <Dialog :options="{ size: '6xl' }" v-model="showVolunteerModal">
    <template #body-title>
      <h3 class="text-2xl font-semibold text-ink-gray-9">
        Additional Details for Volunteer Signup
      </h3>
    </template>
    <template #body-content>
      <div class="">
        <VolunteerSignup
          :initial-data="volunteerDataToSubmit"
          @volunteer-data-submitted="handleVolunteerDataSubmitted"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import Button from "frappe-ui/src/components/Button/Button.vue";
import { sessionStore } from "../stores/session";
import Card from "frappe-ui/src/components/Card.vue";
import Input from "frappe-ui/src/components/Input.vue";
import { onMounted, reactive, ref, watch } from "vue";
import ErrorMessage from "frappe-ui/src/components/ErrorMessage/ErrorMessage.vue";
import Checkbox from "frappe-ui/src/components/Checkbox/Checkbox.vue";
import { createResource, Select } from "frappe-ui";
import Dialog from "frappe-ui/src/components/Dialog/Dialog.vue";
import VmmsPortalCard from "../components/VmmsPortalCard.vue";
import { membershipStore } from "../stores/membership";
import { useRouter } from "vue-router";
import Link from "../components/Controls/Link.vue";
import {
  SignUp,
  VolunteerSignupData,
  initialForm,
  resetSignUpForm,
} from "../utils/volunteer";
import VolunteerSignup from "../components/VolunteerSignup.vue";

const company = ref("");
const router = useRouter();
const isLogin = ref(true);
const userEmail = ref("");
const password = ref("");
const membershipDialog = ref(false);
const signInState = ref(false);
interface RegionOption {
  label: string;
  value: string;
  company: string;
}
const regionOptions = ref<RegionOption[]>([]);
const branchOptions = ref<RegionOption[]>([]);
const volunteerDataToSubmit = ref<VolunteerSignupData | null>(null);
const showVolunteerModal = ref(false);
const { membershipTypes } = membershipStore();

const signUpForm = reactive<SignUp>({ ...initialForm });

const session = sessionStore();
const genderOptions = [
  { label: "Male", value: "Male" },
  { label: "Female", value: "Female" },
  { label: "Other", value: "Other" },
];

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

onMounted(() => {
  branches.fetch();
});
watch(
  () => signUpForm.branch,
  (newBranch) => {
    const selectedBranch = branchOptions.value.find(
      (b) => b.value === newBranch
    );

    if (selectedBranch) {
      signUpForm.region = selectedBranch.company;
    } else {
      signUpForm.region = "";
    }
  }
);

const createSignUp = createResource({
  url: "non_profit.non_profit.user.sign_up",
  onSuccess(data: any) {
    signInState.value = true;
    console.log("show signup data after success", signUpForm);
    resetSignUpForm(signUpForm);
    volunteerDataToSubmit.value = null;
    isLogin.value = true;
  },
});

function submit() {
  if (isLogin.value) {
    session.login.submit({
      usr: userEmail.value,
      pwd: password.value,
    });
  } else {
    if (!signUpForm.categoryVolunteer && !signUpForm.categoryMember) {
      createSignUp.error =
        "Please select at least one category (Volunteer or Member).";
      return;
    }

    if (signUpForm.categoryMember && !signUpForm.membershipType) {
      createSignUp.error = "Please select a membership type from the dialog.";
      membershipDialog.value = true;
      return;
    }

    if (signUpForm.categoryVolunteer && !volunteerDataToSubmit.value) {
      createSignUp.error = "Please fill in the additional volunteer details.";
      setTimeout(() => {
        showVolunteerModal.value = true;
      }, 2500);
      return;
    }

    createSignUp.submit({
      first_name: signUpForm.firstName,
      last_name: signUpForm.lastName,
      region: signUpForm.region,
      branch: signUpForm.branch,
      email: signUpForm.email,
      password: signUpForm.password,
      category_volunteer: signUpForm.categoryVolunteer,
      category_member: signUpForm.categoryMember,
      membership_type: signUpForm.membershipType,
      gender: signUpForm.gender,
      phone_number: signUpForm.phone_number,
      ...(signUpForm.categoryVolunteer ? volunteerDataToSubmit.value : {}),
    });
  }
}
function selectMembership(membershipType: string) {
  signUpForm.membershipType = membershipType;
  membershipDialog.value = false;
}
watch(
  () => signUpForm.categoryMember,
  (newValue) => {
    if (newValue) {
      membershipDialog.value = true;
    } else {
      signUpForm.membershipType = "";
      membershipDialog.value = false;
    }
  }
);
watch(
  () => signUpForm.categoryVolunteer,
  (newValue) => {
    if (newValue && !volunteerDataToSubmit.value) {
      showVolunteerModal.value = true;
    }
  }
);

function openVolunteerModal() {
  showVolunteerModal.value = true;
}

function handleVolunteerDataSubmitted(data) {
  volunteerDataToSubmit.value = data;
  showVolunteerModal.value = false;
}
</script>
