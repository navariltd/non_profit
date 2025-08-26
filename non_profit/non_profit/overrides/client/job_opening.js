frappe.ui.form.on("Job Opening", {
  setup: function (frm) {
    if (frm.fields_dict.branch && frm.fields_dict.company) {
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
    }
  },

  company: function (frm) {
    if (frm.fields_dict.branch && frm.fields_dict.company) {
      if (frm.doc.branch) {
        frm.set_value("branch", "");
      }
    }
  },
});
