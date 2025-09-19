// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Personnel Deployment Request", {
  setup: function (frm) {
    frm.trigger("set_query");
    hrms.setup_employee_filter_group(frm);
  },

  refresh: function (frm) {
    frm.page.clear_indicator();
    frm.trigger("get_employees");
    frm.trigger("set_primary_action");

    frm.events.set_task_filter(frm);
    frm
      .add_custom_button(__("Deploy Selected"), () => {
        frm.trigger("deploy_employees");
      })
      .addClass("btn-primary");
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
      ])
      .then((r) => {
        if (r && r.message) {
          if (r.message.company) frm.set_value("company", r.message.company);
          if (r.message.expected_start_date)
            frm.set_value("expected_start_date", r.message.expected_start_date);
          if (r.message.expected_end_date)
            frm.set_value("expected_end_date", r.message.expected_end_date);
          if (r.message.notes) frm.set_value("notes", r.message.notes);
        }
      });
    frm.trigger("get_employees");
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

  companies: function (frm) {
    frm.trigger("get_employees");
  },

  department: function (frm) {
    frm.trigger("get_employees");
  },

  employment_type: function (frm) {
    frm.trigger("get_employees");
  },

  designation: function (frm) {
    frm.trigger("get_employees");
  },

  courses: function (frm) {
    frm.trigger("get_employees");
  },

  skills: function (frm) {
    frm.trigger("get_employees");
  },

  licences: function (frm) {
    frm.trigger("get_employees");
  },

  filter_criteria: function (frm) {
    frm.trigger("get_employees");
  },

  location: function (frm) {
    frm.trigger("get_employees");
  },

  expected_start_date: function (frm) {
    frm.trigger("get_employees");
  },

  expected_end_date: function (frm) {
    frm.trigger("get_employees");
  },

  get_employees: function (frm) {
    if (!frm.doc.project || !frm.doc.location || !frm.doc.expected_start_date) {
      frm.events.render_employees_datatable(frm, []);
      return;
    }

    frm
      .call({
        method: "get_employees",
        args: {
          advanced_filters: frm.advanced_filters || [],
        },
        doc: frm.doc,
      })
      .then((r) => {
        const columns = frm.events.get_employees_datatable_columns();
        frm.events.render_employees_datatable(frm, r.message || []);

        if (r.message) {
        }
      });
  },

  render_employees_datatable: function (frm, employees) {
    const columns = frm.events.get_employees_datatable_columns();

    if (frm.employees_datatable) {
      frm.employees_datatable.destroy();
    }

    const wrapper = frm.get_field("employee_list").$wrapper;
    wrapper.empty();

    if (employees && employees.length > 0) {
      frm.employees_datatable = new frappe.DataTable(wrapper[0], {
        columns: columns,
        data: employees,
        checkboxColumn: true,
        layout: "fluid",
        cellHeight: 40,
        noDataMessage: __("No employees found matching the criteria"),
      });
    } else {
      wrapper.html(`
        <div class="text-muted text-center" style="padding: 40px;">
          <i class="fa fa-users fa-3x" style="opacity: 0.3; margin-bottom: 15px;"></i>
          <p>${__("No employees found matching the criteria")}</p>
          <small>${__("Adjust your filters to find eligible employees")}</small>
        </div>
      `);
    }
  },

  get_employees_datatable_columns: function () {
    return [
      {
        name: "employee",
        id: "employee",
        content: __("Employee ID"),
        width: 120,
        format: (value, row, column, data) => {
          return value
            ? `<a href="/app/employee/${data.employee}" target="_blank">${value}</a>`
            : "";
        },
      },
      {
        name: "employee_name",
        id: "employee_name",
        content: __("Employee Name"),
        width: 180,
        format: (value, row, column, data) => {
          return value
            ? `<a href="/app/employee/${data.employee}" target="_blank">${value}</a>`
            : "";
        },
      },
      {
        name: "company",
        id: "company",
        content: __("Company"),
        width: 150,
        format: (value, row, column, data) => {
          return value
            ? `<a href="/app/company/${value}" target="_blank">${value}</a>`
            : "";
        },
      },
      {
        name: "department",
        id: "department",
        content: __("Department"),
        width: 150,
        format: (value, row, column, data) => {
          return value
            ? `<a href="/app/department/${value}" target="_blank">${value}</a>`
            : "";
        },
      },
      {
        name: "designation",
        id: "designation",
        content: __("Designation"),
        width: 150,
        format: (value, row, column, data) => {
          return value
            ? `<a href="/app/designation/${value}" target="_blank">${value}</a>`
            : "";
        },
      },
      {
        name: "employment_type",
        id: "employment_type",
        content: __("Employment Type"),
        width: 130,
        format: (value) => {
          return value || "";
        },
      },
    ].map((x) => ({
      ...x,
      editable: false,
      focusable: false,
      dropdown: false,
      align: "left",
    }));
  },

  deploy_employees: function (frm) {
    if (
      !frm.employees_datatable ||
      !frm.employees_datatable.rowmanager.checkMap
    ) {
      frappe.msgprint(__("Please select employees to deploy"));
      return;
    }

    const check_map = frm.employees_datatable.rowmanager.checkMap;
    const selected_employees = [];

    check_map.forEach((is_checked, idx) => {
      if (is_checked && frm.employees_datatable.datamanager.data[idx]) {
        selected_employees.push(
          frm.employees_datatable.datamanager.data[idx].employee
        );
      }
    });

    if (selected_employees.length === 0) {
      frappe.msgprint(__("Please select at least one employee to deploy"));
      return;
    }

    hrms.validate_mandatory_fields(frm, selected_employees);

    if (frm.is_dirty()) {
      frm.save().then(() => {
        frm.events.confirm_deployment(frm, selected_employees);
      });
    } else {
      frm.events.confirm_deployment(frm, selected_employees);
    }
  },

  confirm_deployment: function (frm, selected_employees) {
    frappe.confirm(
      __("Deploy {0} employee(s) for this project?", [
        selected_employees.length,
      ]),
      () => frm.events.bulk_deploy_employees(frm, selected_employees)
    );
  },

  bulk_deploy_employees: function (frm, employees) {
    frm
      .call({
        method: "deploy_employees",
        doc: frm.doc,
        args: {
          employees: employees,
        },
        freeze: true,
        freeze_message: __("Creating Deployment Assignments..."),
      })
      .then((r) => {
        if (r.message) {
          const { success, failure } = r.message;

          let message = "";
          if (success && success.length > 0) {
            message += __("Successfully created {0} deployment assignment(s)", [
              success.length,
            ]);
          }
          if (failure && failure.length > 0) {
            message +=
              (message ? "<br>" : "") +
              __("Failed to create {0} assignment(s)", [failure.length]);
          }

          if (message) {
            frappe.msgprint({
              title: __("Deployment Status"),
              message: message,
              indicator: success && success.length > 0 ? "green" : "red",
            });
          }

          frm.refresh();
        }
      });
  },
});

$.each(
  [
    "companies",
    "department",
    "employment_type",
    "designation",
    "courses",
    "skills",
    "licences",
  ],
  function (i, fieldname) {
    frappe.ui.form.on(
      "Personnel Deployment Request",
      fieldname,
      function (frm) {
        frm.trigger("get_employees");
      }
    );
  }
);
