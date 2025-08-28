frappe.ui.form.on("Membership", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button("Initiate Payment", () => {
        frappe.msgprint("Payment process initiated ");
      });
    }
  },
});
