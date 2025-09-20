import { defineStore } from "pinia";
import { createResource, createListResource } from "frappe-ui";
import { useRouter } from "vue-router";

const router = useRouter();

export const usersStore = defineStore("lms-users", () => {
  let userResource = createResource({
    url: "lms.lms.api.get_user_info",
    onError(error) {
      if (error && error.exc_type === "AuthenticationError") {
        router.push("/login");
      }
    },
    auto: true,
  });

  const allUsers = createResource({
    url: "lms.lms.api.get_all_users",
    cache: ["allUsers"],
  });

  const roleResource = createResource({
    url: "non_profit.non_profit.api.get_user_info",
    auto: true,
    cache: ["roles"],
  });

  const presentSlots = createResource({
    url: "non_profit.non_profit.api.get_present_slots",
    cache: "presentSlots",
    auto: true,
  });

  return {
    userResource,
    allUsers,
    roleResource,
    presentSlots,
  };
});
