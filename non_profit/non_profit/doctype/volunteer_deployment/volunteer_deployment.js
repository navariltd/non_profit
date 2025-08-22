// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Volunteer Deployment", {
  refresh(frm) {
    frm.set_query("branch", function (doc) {
      if (!doc.company) {
        return {
          filters: {
            name: ["in", []],
          },
        };
      }

      return {
        filters: {
          company: doc.company,
        },
      };
    });
  },

  company: function (frm) {
    if (frm.doc.branch) {
      frm.set_value("branch", "");
    }
  },
});
