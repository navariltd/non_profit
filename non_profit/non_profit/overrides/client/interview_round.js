frappe.ui.form.on("Interview Round", {
  refresh(frm) {
    frappe.call({
      method: "non_profit.non_profit.utils.get_interviewers",
      callback: function (r) {
        if (r.message) {
          frm.allowed_interviewers = r.message;
          frm.set_query("interviewers", function () {
            return {
              filters: {
                name: ["in", frm.allowed_interviewers],
              },
            };
          });
        }
      },
    });
  },
});
