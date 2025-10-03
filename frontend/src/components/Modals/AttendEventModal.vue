<template>
  <Dialog v-model="isOpen">
    <template #body-title>
      <div class="flex items-center gap-2">
        <CalendarCheck class="w-6 h-6 text-green-600" />
        <h3 class="text-xl font-semibold text-gray-900">
          Confirm Your Attendance
        </h3>
      </div>
    </template>

    <template #body-content>
      <div class="space-y-4">
        <p class="text-gray-700">
          You're about to register for this event. Once confirmed, you'll
          receive:
        </p>

        <div
          class="bg-green-50 border border-green-100 rounded-lg p-4 space-y-2"
        >
          <div class="flex items-start gap-3">
            <Check class="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
            <span class="text-sm text-gray-700">
              <span class="font-semibold">Confirmation email</span> with event
              details
            </span>
          </div>
        </div>

        <div class="bg-red-50 border border-red-100 rounded-lg p-3">
          <p class="text-sm text-gray-700">
            <span class="font-semibold text-red-900">📅 Important:</span>
            Make sure to mark your calendar and arrive on time!
          </p>
        </div>
      </div>

      <div
        class="border p-2 mt-3 rounded-lg space-y-2"
        v-if="user.data === 'Guest'"
      >
        <span>Please fill out the following information:</span>
        <form action="" @submit.prevent="submit">
          <Input
            required
            name="first_name"
            type="text"
            placeholder="John"
            label="First Name"
            v-model="attendData.first_name"
          />

          <Input
            required
            name="last_name"
            type="text"
            placeholder="Doe"
            label="Last Name"
            v-model="attendData.last_name"
          />

          <Input
            required
            name="email"
            type="email"
            placeholder="johndoe@email.com"
            label="Email"
            v-model="attendData.email"
          />

          <Input
            required
            name="phone"
            type="text"
            placeholder="+254712345678"
            label="Phone Number"
            v-model="attendData.phone"
          />
        </form>
      </div>
    </template>

    <template #actions="{ close }">
      <div class="space-y-3">
        <div class="flex space-x-2 justify-end">
          <Button variant="outline" theme="gray" size="sm" @click="close">
            Cancel
          </Button>
          <Button
            variant="solid"
            theme="green"
            size="sm"
            @click="submit"
            :loading="confirmEvent.loading"
          >
            <span class="flex items-center gap-2">
              <Check class="w-4 h-4" />
              Confirm Attendance
            </span>
          </Button>
        </div>
        <ErrorMessage
          v-if="confirmEvent.error"
          :message="confirmEvent.error"
          class="text-center border border-red-400 rounded-md p-2"
        />
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import { Button, Dialog, ErrorMessage, createResource, Input } from "frappe-ui";
import { CalendarCheck, Check } from "lucide-vue-next";
import { inject, reactive, ref } from "vue";

const isOpen = ref(false);
const user = inject<any>("$user");

const attendData = reactive({
  event: "",
  first_name: user.data !== "Guest" ? user.data.first_name : "",
  last_name: user.data !== "Guest" ? user.data.last_name : "",
  phone: user.data !== "Guest" ? user.data.phone : "",
  email: user.data !== "Guest" ? user.data.email : "",
});

const confirmEvent = createResource({
  url: "non_profit.non_profit.api.attend_event",
  onSuccess() {
    isOpen.value = false;
  },
});

function submit(event: Event) {
  alert("Registration functionality to be implemented.");
}
</script>
