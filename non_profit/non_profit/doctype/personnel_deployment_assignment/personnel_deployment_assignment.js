// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Personnel Deployment Assignment", {
  refresh(frm) {
    frappe.call({
      method: "non_profit.non_profit.utils.get_expense_and_advance_approvers",
      callback: function (r) {
        if (r.message) {
          frm.allowed_approvers = r.message;

          frm.set_query("expense_approver", function () {
            return {
              filters: {
                name: ["in", frm.allowed_approvers],
              },
            };
          });

          frm.set_query("advance_approver", function () {
            return {
              filters: {
                name: ["in", frm.allowed_approvers],
              },
            };
          });
        }
      },
    });
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
  task(frm) {
    if (!frm.doc.task) return;

    frappe.db
      .get_value("Task", frm.doc.task, [
        "company",
        "exp_start_date",
        "exp_end_date",
        "description",
        "project",
      ])
      .then((r) => {
        if (r && r.message) {
          if (r.message.company) frm.set_value("company", r.message.company);
          if (r.message.exp_start_date)
            frm.set_value("expected_start_date", r.message.exp_start_date);
          if (r.message.exp_end_date)
            frm.set_value("expected_end_date", r.message.exp_end_date);
          if (r.message.description)
            frm.set_value("notes", r.message.description);
          if (r.message.project) frm.set_value("project", r.message.project);
        }
      });
    frm.trigger("get_employees");
  },

  project(frm) {
    if (!frm.doc.project) return;
    frm.events.set_task_filter(frm);
    frappe.db
      .get_value("Project", frm.doc.project, [
        "company",
        "expected_start_date",
        "expected_end_date",
        "notes",
        "expense_approver",
        "advance_approver",
        "project_manager",
      ])
      .then((r) => {
        if (r && r.message) {
          if (r.message.company) frm.set_value("company", r.message.company);
          if (r.message.expected_start_date)
            frm.set_value("expected_start_date", r.message.expected_start_date);
          if (r.message.expected_end_date)
            frm.set_value("expected_end_date", r.message.expected_end_date);
          if (r.message.notes) frm.set_value("notes", r.message.notes);
          if (r.message.expense_approver)
            frm.set_value("expense_approver", r.message.expense_approver);
          if (r.message.advance_approver)
            frm.set_value("advance_approver", r.message.advance_approver);
          if (r.message.project_manager)
            frm.set_value("deployment_approver", r.message.project_manager);
        }
      });
    frm.trigger("get_employees");
  },

  deployment(frm) {
    if (!frm.doc.deployment) return;
    frappe.db
      .get_value("Personnel Deployment Request", frm.doc.deployment, [
        "project",
        "expense_approver",
        "advance_approver",
        "deployment_approver",
        "terms_of_reference",
        "term_details",
        "require_contract_before_deployment",
        "expected_start_date",
        "expected_end_date",
        "notes",
      ])
      .then((r) => {
        if (r && r.message) {
          if (r.message.project) frm.set_value("project", r.message.project);
          if (r.message.expense_approver)
            frm.set_value("expense_approver", r.message.expense_approver);
          if (r.message.advance_approver)
            frm.set_value("advance_approver", r.message.advance_approver);
          if (r.message.deployment_approver)
            frm.set_value("deployment_approver", r.message.deployment_approver);
          if (r.message.terms_of_reference)
            frm.set_value("terms_of_reference", r.message.terms_of_reference);
          if (r.message.term_details)
            frm.set_value("term_details", r.message.term_details);
          if (r.message.require_contract_before_deployment !== undefined)
            frm.set_value(
              "require_contract_before_deployment",
              r.message.require_contract_before_deployment
            );
          if (r.message.expected_start_date)
            frm.set_value("expected_start_date", r.message.expected_start_date);
          if (r.message.expected_end_date)
            frm.set_value("expected_end_date", r.message.expected_end_date);
          if (r.message.notes) frm.set_value("notes", r.message.notes);
        }
      });
  },

  set_task_filter(frm) {
    frm.set_query("task", function () {
      return {
        filters: {
          project: frm.doc.project || "",
        },
      };
    });
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
