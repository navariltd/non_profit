frappe.ui.form.on("Job Opening", {
  validate: function (frm) {
    if (frm.doc.opportunity_type === "Internal" && frm.doc.designation) {
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Designation",
          name: frm.doc.designation,
        },
        callback: function (r) {
          if (
            r.message &&
            (!r.message.skills || r.message.skills.length === 0)
          ) {
            frappe.msgprint({
              title: __("Missing Skills"),
              message: __(
                "The selected Designation must have at least one Skill entry."
              ),
              indicator: "red",
            });
            frappe.validated = false;
          }
        },
      });
    }
  },
});
