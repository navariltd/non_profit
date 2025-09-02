// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Volunteer Deployment", {
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

    if (frm.doc.docstatus === 0 && !frm.is_new()) {
      frm
        .add_custom_button(__("Fetch Available Volunteers"), function () {
          frm.events.fetch_volunteers(frm);
        })
        .addClass("btn-primary");
    }
    frm.fields_dict["volunteers"].grid.get_field("volunteer").get_query =
      function (doc, cdt, cdn) {
        const row = locals[cdt][cdn];

        const selectedVolunteers = [];
        (doc.volunteers || []).forEach(function (d) {
          if (d.name !== row.name && d.volunteer) {
            selectedVolunteers.push(d.volunteer);
          }
        });

        return {
          filters: {
            is_volunteer: 1,
            status: "Active",
            branch: doc.branch,
            name: ["not in", selectedVolunteers],
          },
        };
      };
  },

  task(frm) {
    if (!frm.doc.task) return;

    frappe.db.get_value("Task", frm.doc.task, "project").then((r) => {
      if (r && r.message && r.message.project) {
        frm.set_value("project", r.message.project);
      }
    });
  },

  project(frm) {
    if (!frm.doc.project) return;

    frappe.db
      .get_value("Project", frm.doc.project, [
        "company",
        "branch",
        "expected_start_date",
        "expected_end_date",
      ])
      .then((r) => {
        if (r && r.message) {
          frm.set_value("company", r.message.company || "");
          frm.set_value("branch", r.message.branch || "");
          frm.set_value(
            "expected_start_date",
            r.message.expected_start_date || ""
          );
          frm.set_value("expected_end_date", r.message.expected_end_date || "");
        }
      });
  },

  volunteers_add(frm, cdt, cdn) {
    set_volunteer_query(frm);
  },

  fetch_available_volunteers(frm) {
    frm.events.fetch_volunteers(frm);
  },

  fetch_volunteers: function (frm) {
    if (!frm.doc.company) {
      frappe.msgprint(__("Please select a Company first"));
      return;
    }
    if (!frm.doc.branch) {
      frappe.msgprint(__("Please select a Branch first"));
      return;
    }

    frappe.call({
      method:
        "non_profit.non_profit.doctype.volunteer_deployment.volunteer_deployment.get_available_volunteers",
      args: {
        company: frm.doc.company,
        branch: frm.doc.branch,
        deployment: frm.doc.name,
      },
      callback: function (r) {
        if (r.message) {
          frm.events.show_volunteer_selection_dialog(frm, r.message);
        }
      },
    });
  },

  show_volunteer_selection_dialog: function (frm, volunteers) {
    var dialog = new frappe.ui.Dialog({
      title: __("Select Volunteers"),
      fields: [
        {
          fieldname: "volunteers",
          fieldtype: "Table",
          label: __("Available Volunteers"),
          cannot_add_rows: true,
          in_place_edit: true,
          data: volunteers,
          fields: [
            {
              fieldname: "select",
              fieldtype: "Check",
              label: __("Select"),
              in_list_view: 1,
              width: 50,
            },
            {
              fieldname: "employee",
              fieldtype: "Link",
              label: __("Volunteer ID"),
              options: "Employee",
              in_list_view: 1,
              read_only: 1,
              width: 120,
            },
            {
              fieldname: "employee_name",
              fieldtype: "Data",
              label: __("Volunteer Name"),
              in_list_view: 1,
              read_only: 1,
              width: 180,
            },
            {
              fieldname: "skills",
              fieldtype: "Data",
              label: __("Skills"),
              in_list_view: 1,
              read_only: 1,
              width: 250,
            },
          ],
        },
      ],
      primary_action: function () {
        var all_volunteers = dialog.fields_dict.volunteers.df.data;

        if (all_volunteers.length === 0) {
          frappe.msgprint(__("No volunteers available"));
          return;
        }

        frm.events.add_selected_volunteers(frm, all_volunteers);
        dialog.hide();
      },
      primary_action_label: __("Add Selected Volunteers"),
    });

    dialog.show();
  },

  add_selected_volunteers: function (frm, volunteers) {
    volunteers.forEach(function (volunteer) {
      var row = frm.add_child("volunteers");
      row.volunteer = volunteer.employee;
      row.volunteer_name = volunteer.employee_name;
      row.status = "Pending";
    });

    frm.refresh_field("volunteers");
    frappe.msgprint(
      __("Added {0} volunteers to deployment", [volunteers.length])
    );
  },
});

frappe.ui.form.on("Volunteer Deployment Assignee", {
  volunteer: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let duplicate = frm.doc.volunteers.filter(
      (v) => v.volunteer === row.volunteer
    );
    if (duplicate.length > 1) {
      frappe.msgprint(__("This volunteer is already selected."));
      frappe.model.set_value(cdt, cdn, "volunteer", "");
    }
  },

  form_render: function (frm, cdt, cdn) {
    set_volunteer_query(frm);
  },
});

function set_volunteer_query(frm) {
  frm.fields_dict.volunteers.grid.get_field("volunteer").get_query = function (
    doc,
    cdt,
    cdn
  ) {
    let used = (frm.doc.volunteers || [])
      .filter((v) => v.volunteer)
      .map((v) => v.volunteer);

    return {
      filters: {
        name: ["not in", used],
        branch: frm.doc.branch,
        is_volunteer: 1,
        status: "Active",
      },
    };
  };
}
