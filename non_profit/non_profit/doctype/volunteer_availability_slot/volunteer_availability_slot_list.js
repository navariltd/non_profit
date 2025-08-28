// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.listview_settings["Volunteer Availability Slot"] = {
  onload: function (listview) {
    listview.page.add_inner_button(__("View Calendar"), function () {
      const query_params = new URLSearchParams(window.location.search);

      const filters_str = query_params.toString()
        ? `?${query_params.toString()}`
        : "";

      const url = `/app/volunteer-availability-slot/view/calendar/Volunteer%20Availability${filters_str}`;

      window.open(url, "_blank");
    });
  },
};
