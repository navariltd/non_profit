// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
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

    frappe.db
      .get_value("Member", { email_id: frm.doc.personal_email }, "name")
      .then((r) => {
        if (!(r && r.message && r.message.name)) {
          frm.add_custom_button(__("Create Member"), () => {
            frm
              .call({
                method: "non_profit.non_profit.api.create_member",
                args: { name: frm.doc.name },
              })
              .then(() => {
                frappe.show_alert({
                  message: __("Member created successfully"),
                  indicator: "green",
                });
                frm.reload_doc();
              });
          });
        }
      });
  },
});
