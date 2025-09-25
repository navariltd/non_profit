frappe.ui.form.on("Job Applicant", {
  refresh: function (frm) {
    if (frm.doc.status === "Accepted" && frm.doc.is_volunteer == 1) {
      frappe.db
        .get_value("Employee", { job_applicant: frm.doc.name }, "name")
        .then((r) => {
          if (r && !r.message.name) {
            frm.add_custom_button(
              __("Volunteer"),
              () => {
                frappe.route_options = {
                  job_applicant: frm.doc.name,
                  company: frm.doc.company,
                };
                frappe.new_doc("Employee");
              },
              __("Create")
            );
          }
        });
    }
  },
});
