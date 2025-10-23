// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Personnel Terms of Reference", {
  refresh(frm) {
    if (!frm.doc.expected_start_date) {
      frm.set_value("expected_start_date", frappe.datetime.get_today());
    }
    frm.add_custom_button(
      __("Deployment Request"),
      function () {
        frappe.new_doc("Personnel Deployment Request", {
          terms_of_reference: frm.doc.name,
        });
      },
      __("Create")
    );
  },

  validate(frm) {
    if (frm.doc.expected_end_date && frm.doc.expected_start_date) {
      if (frm.doc.expected_end_date < frm.doc.expected_start_date) {
        frappe.msgprint(
          __("Expected End Date cannot be before Expected Start Date")
        );
        frappe.validated = false;
      }
    }

    if (frm.doc.expected_start_date && frm.doc) {
      const today = frappe.datetime.get_today();
      if (frm.doc.expected_start_date < today) {
        frappe.msgprint(__("Expected Start Date cannot be in the past"));
        frappe.validated = false;
      }
    }
  },
});
