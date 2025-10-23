// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Membership", {
  setup: function (frm) {
    frappe.db
      .get_single_value(
        "Non Profit Settings",
        "enable_razorpay_for_memberships"
      )
      .then((val) => {
        if (val)
          frm.set_df_property("razorpay_details_section", "hidden", false);
      });
  },

  refresh: function (frm) {
    if (frm.doc.__islocal) return;

    if (!frm.is_new()) {
      frm.add_custom_button("Request Payment", () => {
        frappe.prompt(
          [
            {
              fieldname: "phone_number",
              label: __("Phone Number"),
              fieldtype: "Data",
              reqd: 1,
              description: __("Enter the phone number for payment request"),
            },
          ],
          (values) => {
            frm.call({
              doc: frm.doc,
              method: "initiate_payment",
              args: { phone_number: values.phone_number },
              freeze: true,
              freeze_message: __("Requesting Payment"),
              callback: function (r) {
                if (r.invoice) frm.reload_doc();
              },
            });
          },
          __("Enter Phone Number"),
          __("Request Payment")
        );
      });
    }

    !frm.doc.invoice &&
      frm.add_custom_button("Generate Invoice", () => {
        frm.call({
          doc: frm.doc,
          method: "generate_invoice",
          args: { save: true },
          freeze: true,
          freeze_message: __("Creating Membership Invoice"),
          callback: function (r) {
            if (r.invoice) frm.reload_doc();
          },
        });
      });

    frappe.db
      .get_single_value("Non Profit Settings", "send_email")
      .then((val) => {
        if (val)
          frm.add_custom_button("Send Acknowledgement", () => {
            frm.call("send_acknowlement").then(() => {
              frm.reload_doc();
            });
          });
      });
  },

  membership_type: function (frm) {
    if (frm.doc.membership_type) {
      frappe.db.get_value(
        "Membership Type",
        frm.doc.membership_type,
        ["amount", "currency"],
        (r) => {
          if (r) {
            frm.set_value("amount", r.amount);
            frm.set_value("currency", r.currency);
          }
        }
      );
    }
  },

  onload: function (frm) {
    frm.add_fetch("membership_type", "amount", "amount");
  },
});
