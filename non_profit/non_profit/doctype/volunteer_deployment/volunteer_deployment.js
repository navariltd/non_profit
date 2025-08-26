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

    if (frm.doc.docstatus === 0) {
      frm
        .add_custom_button(__("Fetch Available Volunteers"), function () {
          frm.events.fetch_volunteers(frm);
        })
        .addClass("btn-primary");
    }
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
              fieldname: "volunteer",
              fieldtype: "Link",
              label: __("Volunteer"),
              options: "Volunteer",
              in_list_view: 1,
              read_only: 1,
              cols: 3,
            },
            {
              fieldname: "skills",
              fieldtype: "Data",
              label: __("Skills"),
              in_list_view: 1,
              read_only: 1,
              cols: 4,
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
      row.volunteer = volunteer.volunteer;
      row.volunteer_name = volunteer.volunteer_name;
      row.status = "Pending";
      row.assignment_date = frappe.datetime.get_today();
    });

    frm.refresh_field("volunteers");
    frappe.msgprint(
      __("Added {0} volunteers to deployment", [volunteers.length])
    );
  },
});
