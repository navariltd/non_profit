// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Personnel Deployment Assignment", {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.require_contract_before_deployment) {
      frappe.db.get_value(
        "Contract",
        {
          personnel_deployment_assignment: frm.doc.name,
          docstatus: ["!=", 2],
        },
        ["name"],
        (r) => {
          if (r && !r.name) {
            frm.add_custom_button(__("Create Contract"), () => {
              frappe.model.with_doctype("Contract", () => {
                let contract = frappe.model.get_new_doc("Contract");
                contract.party_type = "Employee";
                contract.party_name = frm.doc.employee;
                contract.start_date = frm.doc.expected_start_date;
                contract.end_date = frm.doc.expected_end_date;
                contract.project = frm.doc.project;
                contract.task = frm.doc.task;
                contract.personnel_deployment_assignment = frm.doc.name;
                contract.personnel_deployment_request = frm.doc.deployment;

                frappe.set_route("Form", "Contract", contract.name);
              });
            });
          }
        }
      );
    }
  },

  terms_of_reference: function (frm) {
    if (!frm.doc.terms_of_reference) {
      frm.set_value("term_details", "");
      return;
    }
    frappe.call({
      method: "frappe.client.get_value",
      args: {
        doctype: "Terms and Conditions",
        fieldname: "terms",
        filters: {
          name: frm.doc.terms_of_reference,
        },
      },
      callback: function (r) {
        if (r.message && r.message.terms) {
          frm.set_value("term_details", r.message.terms);
        }
      },
    });
  },
});
