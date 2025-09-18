frappe.ui.form.on("Contract", {
  refresh(frm) {
    frm.events.set_task_filter(frm);
  },

  project(frm) {
    frm.events.set_task_filter(frm);

    if (!frm.doc.project) {
      frm.set_value("task", null);
    }
  },

  task(frm) {
    if (frm.doc.task && !frm.doc.project) {
      frappe.db.get_value("Task", frm.doc.task, "project", (r) => {
        if (r && r.project) {
          frm.set_value("project", r.project);
        }
      });
    }
  },

  personnel_deployment(frm) {
    if (frm.doc.personnel_deployment) {
      frappe.db.get_value(
        "Volunteer Deployment",
        frm.doc.personnel_deployment,
        ["project", "task"],
        (r) => {
          if (r) {
            if (r.project) {
              frm.set_value("project", r.project);
            }
            if (r.task) {
              frm.set_value("task", r.task);
            }
          }
        }
      );
    }
  },

  set_task_filter(frm) {
    frm.set_query("task", () => {
      return {
        filters: {
          project: frm.doc.project || "",
        },
      };
    });
  },
});
