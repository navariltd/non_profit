// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
  refresh(frm) {
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
    if (frm.doc.job_applicant) {
      fetchJobApplicantDetails(frm);
    }

    // if (frm.doc.volunteer_signup) {
    //   fetchVolunteerSignupDetails(frm);
    // }

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
  job_applicant(frm) {
    if (!frm.doc.job_applicant) return;
    fetchJobApplicantDetails(frm);
  },
  // volunteer_signup(frm) {
  //   if (!frm.doc.volunteer_signup) return;
  //   fetchVolunteerSignupDetails(frm);
  // },
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

// function fetchVolunteerSignupDetails(frm) {
//   frappe.model.with_doc(
//     "Volunteer Signup",
//     frm.doc.volunteer_signup,
//     function () {
//       const volunteer_signup = frappe.get_doc(
//         "Volunteer Signup",
//         frm.doc.volunteer_signup
//       );
//       const update_fields = {};

//       const field_mapping = {
//         status: "status",
//         surname: "last_name",
//         other_names: "first_name",
//         email: "personal_email",
//         phone_number: "cell_number",
//         mobile_money_number: "mpesa_mobile_phone",
//         profile_photo: "image",
//         gender: "gender",
//         date_of_birth: "date_of_birth",
//         idpassport: "id_passport_number",
//         countybranch: "branch",
//         region: "region",
//         ward: "ward",
//         marital_status: "marital_status",
//         education: "highest_level_of_education",
//         profession: "profession",
//         place_of_work: "place_of_work",
//         reason_to_join: "reason_to_join",
//         blood_group: "blood_group",
//       };

//       const table_fields_mapping = {
//         disabilities: "disabilities",
//         languages: "languages",
//         additional_skills: "additional_skills",
//         trainings: "trainings",
//         relevant_documents: "relevant_documents",
//       };

//       Object.entries(field_mapping).forEach(
//         ([signup_field, employee_field]) => {
//           if (volunteer_signup[signup_field] && !frm.doc[employee_field]) {
//             update_fields[employee_field] = volunteer_signup[signup_field];
//           }
//         }
//       );

//       if (Object.keys(update_fields).length > 0) {
//         frm.set_value(update_fields);
//       }

//       Object.entries(table_fields_mapping).forEach(
//         ([signup_table, employee_table]) => {
//           if (
//             volunteer_signup[signup_table] &&
//             volunteer_signup[signup_table].length > 0
//           ) {
//             frm.clear_table(employee_table);

//             volunteer_signup[signup_table].forEach((row) => {
//               const new_row = frm.add_child(employee_table);

//               Object.keys(row).forEach((key) => {
//                 if (
//                   ![
//                     "name",
//                     "parent",
//                     "parentfield",
//                     "parenttype",
//                     "updated",
//                     "idx",
//                   ].includes(key)
//                 ) {
//                   new_row[key] = row[key];
//                 }
//               });
//             });

//             frm.refresh_field(employee_table);
//           }
//         }
//       );
//     }
//   );
// }
