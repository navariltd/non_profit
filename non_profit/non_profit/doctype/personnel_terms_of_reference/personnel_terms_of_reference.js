// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Personnel Terms of Reference", {
  refresh(frm) {
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
});
