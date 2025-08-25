// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Volunteer Availability Slot", {
  refresh(frm) {},

  validate(frm) {
    if (!frm.doc.starts_on || !frm.doc.ends_on) {
      frappe.throw(__("Start Time and End Time are required."));
    }

    validateTimes(frm);
  },

  starts_on: function (frm) {
    validateTimes(frm);
  },

  ends_on: function (frm) {
    validateTimes(frm);
  },
});
function validateTimes(frm) {
  if (frm.doc.starts_on && frm.doc.ends_on) {
    if (frm.doc.starts_on >= frm.doc.ends_on) {
      frm.set_value("ends_on", "");
      frappe.throw(__("Start Time must be before End Time."));
    }
  }
}
