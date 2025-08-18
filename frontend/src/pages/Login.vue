<template>
  <div class="flex min-h-screen items-center justify-center">
    <Card
      :title="isLogin ? 'Login VMMS Portal' : 'Sign Up VMMS Portal'"
      class="w-full max-w-md"
    >
      <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
        <template v-if="!isLogin">
          <Input
            required
            name="fullname"
            type="text"
            placeholder="John Doe"
            label="Full Name"
            v-model="fullName"
          />
        </template>

        <Input
          required
          name="email"
          type="email"
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

        <div v-if="!isLogin" class="flex flex-col space-y-1">
          <label class="text-sm font-medium">Category</label>
          <div class="flex space-x-4">
            <label class="flex items-center space-x-1">
              <Checkbox
                size="sm"
                :value="false"
                v-model="category"
                label="Volunteer"
              />
            </label>
            <label class="flex items-center space-x-1">
              <Checkbox
                size="sm"
                :value="false"
                v-model="category"
                label="Member"
              />
              <span></span>
            </label>
          </div>
        </div>

        <Button
          :loading="isLogin ? session.login.loading : false"
          variant="solid"
        >
          {{ isLogin ? "Login" : "Sign Up" }}
        </Button>
      </form>

      <div class="mt-2 text-center">
        <ErrorMessage :message="isLogin ? session.login.error : ''" />
      </div>

      <div class="mt-4 text-center text-sm">
        <span v-if="isLogin">Don’t have an account? </span>
        <span v-else>Already have an account? </span>
        <Button
          class="text-blue-600 hover:underline"
          @click="isLogin = !isLogin"
          type="Button"
        >
          {{ isLogin ? "Sign up" : "Login" }}
        </Button>
      </div>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import Button from "frappe-ui/src/components/Button/Button.vue";
import { sessionStore } from "../stores/session";
import Card from "frappe-ui/src/components/Card.vue";
import Input from "frappe-ui/src/components/Input.vue";
import { ref } from "vue";
import ErrorMessage from "frappe-ui/src/components/ErrorMessage/ErrorMessage.vue";
import Checkbox from "frappe-ui/src/components/Checkbox/Checkbox.vue";

const isLogin = ref(true);
const fullName = ref("");
const userEmail = ref("");
const password = ref("");
const category = ref();

const session = sessionStore();

function submit() {
  if (isLogin.value) {
    session.login.submit({
      email: userEmail.value,
      password: password.value,
    });
  } else {
  }
}
</script>
