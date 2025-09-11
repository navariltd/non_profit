// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
  refresh: function (frm) {
    if (frm.fields_dict.branch && frm.fields_dict.company) {
      frm.set_query("branch", function (doc) {
        if (doc.company) {
          return {
            filters: {
              company: doc.company,
            },
          };
        }
      });
    }
  },

  company: function (frm) {
    if (frm.fields_dict.branch && frm.fields_dict.company) {
      if (frm.doc.branch) {
        frappe.db.get_value("Branch", frm.doc.branch, "company", (response) => {
          if (response && response.company !== frm.doc.company) {
            frm.set_value("branch", "");
          }
        });
      }
    }
  },

  branch: function (frm) {
    if (frm.doc.branch && !frm.doc.company) {
      frappe.db.get_value("Branch", frm.doc.branch, "company", (response) => {
        if (response && response.company) {
          frm.set_value("company", response.company);
        }
      });
    }
  },
});
