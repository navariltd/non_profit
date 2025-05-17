// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Donation", {
  refresh: function (frm) {
    if (frm.doc.docstatus === 1 && !frm.doc.paid) {
      frm.add_custom_button(__("Create Payment Entry"), function () {
        frm.events.make_payment_entry(frm);
      });
    }
    if (!frm.doc.date) {
      frm.set_value("date", frappe.datetime.get_today());
    }
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
