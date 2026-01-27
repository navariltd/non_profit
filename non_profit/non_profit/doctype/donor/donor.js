// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Donor", {
  refresh: function (frm) {
    frappe.dynamic_link = { doc: frm.doc, fieldname: "name", doctype: "Donor" };

    frm.toggle_display(["address_html", "contact_html"], !frm.doc.__islocal);
    frm.toggle_display(
      "create_customer",
      !frm.doc.customer && !frm.doc.__islocal,
    );

    if (!frm.doc.__islocal) {
      frappe.contacts.render_address_and_contact(frm);
    } else {
      frappe.contacts.clear_address_and_contact(frm);
    }
  },

  create_customer: (frm) => {
    frm.call({
      method: "create_customer",
      doc: frm.doc,
      callback: function (r) {
        if (r.message) {
          frappe.msgprint("Customer " + r.message + " created.");
        }
      },
    });
  },
});
