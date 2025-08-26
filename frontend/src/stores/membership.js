import { defineStore } from "pinia";
import { createResource } from "frappe-ui";

export const membershipStore = defineStore("membership", () => {
  const membershipTypes = createResource({
    url: "non_profit.non_profit.api.get_membership_types",
    cache: "MembershipTypes",
    auto: true,
  });

  const events = createResource({
    url: "non_profit.non_profit.api.get_events",
    auto: true,
    cache: ["events"],
  });

  return {
    membershipTypes,
    events,
  };
});
