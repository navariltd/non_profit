frappe.ui.form.on("Job Applicant", {
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

    if (frm.doc.status === "Accepted" && frm.doc.is_volunteer == 1) {
      frappe.db
        .get_value("Employee", { job_applicant: frm.doc.name }, "name")
        .then((r) => {
          if (r && !r.message.name) {
            frm.add_custom_button(
              __("Create Employee"),
              () => {
                frappe.route_options = {
                  job_applicant: frm.doc.name,
                  company: frm.doc.company,
                  branch: frm.doc.branch,
                };
                frappe.new_doc("Employee");
              },
              __("Create")
            );
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
