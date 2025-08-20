import { defineStore } from "pinia";
import { createResource } from "frappe-ui";

export const membershipStore = defineStore("membership", () => {
  const membershipTypes = createResource({
    url: "non_profit.non_profit.api.get_membership_types",
    cache: "MembershipTypes",
    auto: true,
  });

  return {
    membershipTypes,
  };
});
