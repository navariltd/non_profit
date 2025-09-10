<template>
  <div class="">
    <div class="flex flex-col justify-center h-screen space-y-4 p-12">
      <h1 class="text-3xl font-bold">Welcome {{ name }}</h1>
      <p class="text-3xl text-gray-600">
        Join us and make a difference. Sign up to become a volunteer or a
        member.
      </p>
      <div class="flex flex-row gap-4 mt-6">
        <Button
          variant="solid"
          icon-right="arrow-right"
          @click="navigateTo('volunteer/signup')"
          >Sign Up as Volunteer</Button
        >
        <Button
          variant="solid"
          icon-right="arrow-right"
          @click="navigateTo('membership')"
          >Sign Up as Member
        </Button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Button } from "frappe-ui";
import router from "../router";

defineProps({
  name: {
    type: String,
    required: false,
    default: "User",
  },
});

function navigateTo(path: string) {
  router.push("/" + path);
}
</script>
