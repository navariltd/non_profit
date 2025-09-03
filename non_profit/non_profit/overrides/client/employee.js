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

    if (frm.doc.job_applicant) {
      fetchJobApplicantDetails(frm);
    }

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
  job_applicant(frm) {
    if (!frm.doc.job_applicant) return;
    fetchJobApplicantDetails(frm);
  },
});

function fetchJobApplicantDetails(frm) {
  frappe.model.with_doc("Job Applicant", frm.doc.job_applicant, function () {
    const job_applicant = frappe.get_doc(
      "Job Applicant",
      frm.doc.job_applicant
    );
    const update_fields = {};

    const same_fields = [
      "branch",
      "company",
      "gender",
      "blood_group",
      "marital_status",
      "place_of_work",
      "date_of_birth",
      "highest_level_of_education",
      "mpesa_mobile_phone",
      "ward",
      "profession",
      "reason_to_join",
    ];

    const field_mapping = {
      surname: "last_name",
      other_names: "first_name",
      email_id: "personal_email",
      phone_number: "cell_number",
      idpassport_number: "id_passport_number",
      cover_letter: "bio",
      profile_photo: "image",
    };

    const table_fields = [
      "disabilities",
      "allergies",
      "trainings",
      "additional_skills",
      "languages",
    ];

    same_fields.forEach((field) => {
      if (job_applicant[field] && !frm.doc[field]) {
        update_fields[field] = job_applicant[field];
      }
    });

    Object.entries(field_mapping).forEach(
      ([applicant_field, employee_field]) => {
        if (job_applicant[applicant_field] && !frm.doc[employee_field]) {
          update_fields[employee_field] = job_applicant[applicant_field];
        }
      }
    );

    if (Object.keys(update_fields).length > 0) {
      frm.set_value(update_fields);
    }

    table_fields.forEach((field) => {
      if (job_applicant[field] && job_applicant[field].length > 0) {
        frm.clear_table(field);

        job_applicant[field].forEach((row) => {
          const new_row = frm.add_child(field);

          Object.keys(row).forEach((key) => {
            if (
              ![
                "name",
                "parent",
                "parentfield",
                "parenttype",
                "updated",
                "idx",
              ].includes(key)
            ) {
              new_row[key] = row[key];
            }
          });
        });

        frm.refresh_field(field);
      }
    });
  });
}
