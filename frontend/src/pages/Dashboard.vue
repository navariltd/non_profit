<template>
  <Member
    v-if="roleResource.data.non_profit_member && !roleResource.data.volunteer"
  />

  <Volunteer
    v-if="!roleResource.data.non_profit_member && roleResource.data.volunteer"
  />
</template>
<script lang="ts" setup>
import Member from "../components/Member.vue";
import Volunteer from "../components/Volunteer.vue";
import { usersStore } from "../stores/user";
import { ref } from "vue";

const { roleResource } = usersStore();
</script>
