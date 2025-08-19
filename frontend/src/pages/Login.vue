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
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              required
              name="region"
              type="text"
              placeholder="Eastern Region"
              label="Region"
              v-model="signUpForm.region"
            />
            <Input
              required
              name="branch"
              type="text"
              placeholder="Eastern Region Branch"
              label="Branch"
              v-model="signUpForm.branch"
            />
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
            <label class="text-sm font-medium">Category</label>
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
                />
              </label>
            </div>
          </div>
        </template>

        <Button
          :loading="isLogin ? session.login.loading : createVolunteer.loading"
          variant="solid"
          type="submit"
        >
          {{ isLogin ? "Login" : "Sign Up" }}
        </Button>
      </form>

      <div class="mt-2 text-center">
        <ErrorMessage
          :message="isLogin ? session.login.error : createVolunteer.error"
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

const isLogin = ref(true);
const userEmail = ref("");
const password = ref("");

const signUpForm = reactive({
  firstName: "",
  lastName: "",
  region: "",
  branch: "",
  email: "",
  password: "",
  categoryVolunteer: false,
  categoryMember: false,
});

const session = sessionStore();

const createVolunteer = createResource({
  url: "non_profit.non_profit.user.sign_up",
  onSuccess(data: any) {
    console.log("Sign up successful:", data);
  },
  onError(error: any) {
    console.error("Sign up failed:", error);
  },
});

function submit() {
  if (isLogin.value) {
    session.login.submit({
      usr: signUpForm.email,
      pwd: signUpForm.password,
    });
  } else {
    console.log("Submitting sign up form:", signUpForm);
    
    createVolunteer.submit({
      first_name: signUpForm.firstName,
      last_name: signUpForm.lastName,
      region: signUpForm.region,
      branch: signUpForm.branch,
      email: signUpForm.email,
      password: signUpForm.password,
      category_volunteer: signUpForm.categoryVolunteer,
      category_member: signUpForm.categoryMember,
    });
  }
}
</script>
