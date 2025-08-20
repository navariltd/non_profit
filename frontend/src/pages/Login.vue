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
            <Select
              :options="[
                {
                  label: 'Male',
                  value: 'Male',
                },
                {
                  label: 'Female',
                  value: 'Female',
                },
              ]"
              required
              name="gender"
              type="text"
              placeholder="Female"
              label="Gender"
              v-model="signUpForm.gender"
            />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="flex flex-col">
              <span class="text-gray-600 test-sm mb-2">Region</span>
              <Select
                :options="regionOptions"
                required
                name="region"
                type="select"
                placeholder="Eastern Region"
                label="Region"
                v-model="signUpForm.region"
              />
            </div>
            <div class="flex flex-col">
              <span class="text-gray-600 test-sm mb-2">Branch</span>
              <Select
                :options="branchOptions"
                required
                name="branch"
                type="text"
                placeholder="Eastern Region Branch"
                label="Branch"
                v-model="signUpForm.branch"
              />
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
            name="password"
            type="password"
            placeholder="••••••"
            label="Password"
            v-model="signUpForm.password"
          />
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
                  :value="false"
                  v-model="signUpForm.categoryMember"
                  label="Member"
                  @change="onMemberChange"
                />
              </label>
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
      message: 'Await communication via email',
      size: 'lg',
      icon: {
        name: 'alert-triangle',
        appearance: 'warning',
      },
      actions: [
        {
          label: 'Confirm',
          variant: 'solid',
          onClick: () => {
            router.push({ name: 'VMMSPortalSignup' });
          },
        },
      ],
    }"
    v-model="signInState"
  />
</template>

<script setup lang="ts">
import Button from "frappe-ui/src/components/Button/Button.vue";
import { sessionStore } from "../stores/session";
import Card from "frappe-ui/src/components/Card.vue";
import Input from "frappe-ui/src/components/Input.vue";
import { reactive, ref } from "vue";
import ErrorMessage from "frappe-ui/src/components/ErrorMessage/ErrorMessage.vue";
import Checkbox from "frappe-ui/src/components/Checkbox/Checkbox.vue";
import { createResource } from "frappe-ui";
import Select from "frappe-ui/src/components/Select/Select.vue";
import Dialog from "frappe-ui/src/components/Dialog/Dialog.vue";
import VmmsPortalCard from "../components/VmmsPortalCard.vue";
import { membershipStore } from "../stores/membership";
import { useRouter } from "vue-router";

const router = useRouter();
const isLogin = ref(true);
const userEmail = ref("");
const password = ref("");
const dialog4 = ref(false);
const membershipDialog = ref(false);
const signInState = ref(false);
interface RegionOption {
  label: string;
  value: string;
}
const regionOptions = ref<RegionOption[]>([]);
const branchOptions = ref<RegionOption[]>([]);

const { membershipTypes } = membershipStore();

const signUpForm = reactive({
  firstName: "",
  lastName: "",
  region: "",
  branch: "",
  email: "",
  password: "",
  categoryVolunteer: false,
  categoryMember: false,
  membershipType: "",
  gender: "",
});

const session = sessionStore();

createResource({
  url: "non_profit.non_profit.api.get_branches",
  auto: true,
  onSuccess(data: any) {
    branchOptions.value = data.map((branch) => {
      return { label: branch.name, value: branch.value };
    });
  },
});

const region = createResource({
  url: "non_profit.non_profit.api.get_regions",
  auto: true,
  onSuccess(data: any) {
    regionOptions.value = data.map((region) => {
      return { label: region.name, value: region.value };
    });
  },
});

const createSignUp = createResource({
  url: "non_profit.non_profit.user.sign_up",
  onSuccess(data: any) {
    signInState.value = true;
  },
  // onError(error: any) {
  //   console.error("Sign up failed:", error);
  // },
});

function submit() {
  if (isLogin.value) {
    

    session.login.submit({
      usr: userEmail.value,
      pwd: password.value,
    });
  } else {
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
    });
  }
}

function selectMembership(membershipType: string) {
  signUpForm.membershipType = membershipType;
  membershipDialog.value = false;
}
function onMemberChange(checked: boolean) {
  if (checked) {
    membershipDialog.value = true;
  } else {
    signUpForm.membershipType = "";
  }
}
</script>
