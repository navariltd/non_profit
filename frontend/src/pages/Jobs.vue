<template>
  <div class="m-3 flex flex-row items-center justify-center">
   these are jobs
  </div>

 
</template>

<script lang="ts" setup>
import { session } from "../data/session"

function submit(e) {
	const formData = new FormData(e.target)
	session.login.submit({
		email: formData.get("email"),
		password: formData.get("password"),
	})
}
</script>
