frappe.ui.form.on("Job Opening", {
  validate: function (frm) {
    if (frm.doc.opportunity_type === "Internal") {
      if (!frm.doc.required_skills || frm.doc.required_skills.length === 0) {
        frappe.msgprint({
          title: __("Missing Skills"),
          message: __(
            "At least one Required Skill must be added for Internal opportunities."
          ),
          indicator: "red",
        });
        frappe.validated = false;
        return;
      }
    }
  },

  designation: function (frm) {
    if (frm.doc.designation) {
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Designation",
          name: frm.doc.designation,
        },
        callback: function (r) {
          if (r.message && r.message.skills && r.message.skills.length > 0) {
            frm.clear_table("required_skills");

            r.message.skills.forEach(function (skill) {
              let row = frm.add_child("required_skills");
              row.skill = skill.skill;
            });

            frm.refresh_field("required_skills");
            frappe.show_alert(__("Skills updated from Designation"));
          }
        },
      });
    }
  },
});
