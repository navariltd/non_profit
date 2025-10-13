// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Donation", {
  refresh: async function (frm) {
    if (frm.doc.docstatus === 1 && !frm.doc.paid) {
      frm.add_custom_button(__("Create Payment Entry"), function () {
        frm.events.make_payment_entry(frm);
      });
    }
    if (!frm.doc.date) {
      frm.set_value("date", frappe.datetime.get_today());
    }

    const { message: setting } = await frappe.db.get_value(
      "Non Profit Settings",
      "Non Profit Settings",
      ["enable_payment_table_on_donation"]
    );

    if (setting && setting.enable_payment_table_on_donation == "1") {
      frm.set_df_property("donation_payments", "hidden", 0);
    }

    frm.events.update_project_options(frm);
  },

  donor(frm) {
    frm.events.update_project_options(frm);
  },

  update_project_options(frm) {
    frappe.call({
      method:
        "non_profit.non_profit.doctype.donation.donation.project_filter_by_donor",
      args: { donor: frm.doc.donor || null },
      callback(r) {
        const project_list = (r.message || []).map((p) => p.name);

        if (frm.get_field("project").df.fieldtype === "Select") {
          frm.set_df_property("project", "options", ["", ...project_list]);

          if (!project_list.includes(frm.doc.project)) {
            frm.set_value("project", "");
          }

          frm.refresh_field("project");
          return;
        }

        frm.set_query("project", () => ({
          filters: { name: ["in", project_list.length ? project_list : [""]] },
        }));

        if (frm.doc.project && !project_list.includes(frm.doc.project)) {
          frm.set_value("project", "");
        }
      },
    });
  },

  make_payment_entry: function (frm) {
    return frappe.call({
      method:
        "non_profit.non_profit.custom_doctype.payment_entry.get_donation_payment_entry",
      args: {
        dt: frm.doc.doctype,
        dn: frm.doc.name,
      },
      callback: function (r) {
        var doc = frappe.model.sync(r.message);
        frappe.set_route("Form", doc[0].doctype, doc[0].name);
      },
    });
  },
});

frappe.ui.form.on("Donation Payment Item", {
  amount: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (frm.doc.amount > 0) {
      row.percentage = (row.amount / frm.doc.amount) * 100;
    }
    frm.refresh_field("donation_payments");
  },

  percentage: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (frm.doc.amount > 0) {
      row.amount = (row.percentage / 100) * frm.doc.amount;
    }
    frm.refresh_field("donation_payments");
  },
});
