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
              v-model="signUpForm.first_name"
            />
            <Input
              required
              name="lastname"
              type="text"
              placeholder="Doe"
              label="Last Name"
              v-model="signUpForm.last_name"
            />
          </div>
          <!-- <div class="w-full border p-4 rounded-lg bg-white">
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
          </div> -->

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
            v-model="signUpForm.phone"
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
</template>

<script setup lang="ts">
import Button from "frappe-ui/src/components/Button/Button.vue";
import { sessionStore } from "../stores/session";
import Card from "frappe-ui/src/components/Card.vue";
import Input from "frappe-ui/src/components/Input.vue";
import { onMounted, reactive, ref } from "vue";
import ErrorMessage from "frappe-ui/src/components/ErrorMessage/ErrorMessage.vue";
import { createResource, Select } from "frappe-ui";
import Dialog from "frappe-ui/src/components/Dialog/Dialog.vue";
import { SignUp, initialForm, resetSignUpForm } from "../utils/volunteer";

const isLogin = ref(true);
const userEmail = ref("");
const password = ref("");
const signInState = ref(false);
interface RegionOption {
  label: string;
  value: string;
  company: string;
}
const branchOptions = ref<RegionOption[]>([]);

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

const createSignUp = createResource({
  url: "non_profit.non_profit.user.create_user",
  onSuccess() {
    signInState.value = true;
    resetSignUpForm(signUpForm);
    isLogin.value = true;
  },
});

function isValidPhone(phone: string) {
  const regex = /^\+254\d{9}$/;
  return regex.test(phone);
}

function submit() {
  if (isLogin.value) {
    session.login.submit({
      usr: userEmail.value,
      pwd: password.value,
    });
  } else {
    if (!isValidPhone(signUpForm.phone)) {
      createSignUp.error =
        "Please enter a valid Kenyan phone number.eg. (+254123456789)";
      return;
    }
    createSignUp.submit({
      ...signUpForm,
    });
  }
}
</script>
