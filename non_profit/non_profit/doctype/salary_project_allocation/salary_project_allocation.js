// Copyright (c) 2026, Frappe and contributors
// For license information, please see license.txt

const MODULE_PATH =
  "non_profit.non_profit.doctype.salary_project_allocation.salary_project_allocation";

function toNumber(value) {
  const num = parseFloat(value);
  return Number.isNaN(num) ? 0 : num;
}

function round2(value) {
  return Math.round(value * 100) / 100;
}

frappe.ui.form.on("Salary Project Allocation", {
  refresh(frm) {
    frm.events.setup(frm);
    if (!frm.doc.from_date) {
      frm.set_value("from_date", frappe.datetime.get_today());
    }
  },

  employee(frm) {
    frm.events.setup_assignment_query(frm);
    frm.events.clear_mismatched_assignment(frm);
  },

  salary_structure_assignment(frm) {
    frm.events.load_assignment_details(frm);
  },

  from_date(frm) {
    frm.events.validate_date_range(frm);
  },

  to_date(frm) {
    frm.events.validate_date_range(frm);
  },

  // Client-side gate; the server re-validates on submit regardless.
  validate(frm) {
    const result = frm.events.validate_allocations(frm, { throw_error: true });
    if (!result.valid) {
      frappe.validated = false;
    }
  },

  setup(frm) {
    frm.events.setup_assignment_query(frm);
    frm.events.setup_component_query(frm);
    if (!frm.is_new()) {
      frm.events.derive_allowed_components(frm);
    }
  },

  setup_assignment_query(frm) {
    frm.set_query("salary_structure_assignment", () => {
      const filters = { docstatus: 1 };
      if (frm.doc.employee) filters.employee = frm.doc.employee;
      return { filters };
    });
  },

  // Only Earning components present in the selected structure stay pickable.
  setup_component_query(frm) {
    frm.set_query("salary_component", "allocations", () => {
      const allowed = frm.earnings_components || [];
      const filters = { type: "Earning" };
      if (allowed.length) filters.name = ["in", allowed];
      return { filters };
    });
  },

  derive_allowed_components(frm) {
    // On reload the structure is not re-fetched; keep the grid's own components.
    const rows = (frm.doc.allocations || []).filter((row) => row.salary_component);
    frm.earnings_components = [...new Set(rows.map((row) => row.salary_component))];
  },

  clear_mismatched_assignment(frm) {
    if (!frm.doc.employee || !frm.doc.salary_structure_assignment) return;
    frappe.db
      .get_value(
        "Salary Structure Assignment",
        frm.doc.salary_structure_assignment,
        "employee"
      )
      .then(({ message }) => {
        if (message && message.employee && message.employee !== frm.doc.employee) {
          frappe.show_alert({
            message: __("Assignment belongs to another employee and was cleared."),
            indicator: "red",
          });
          frm.set_value("salary_structure_assignment", null);
          frm.set_value("allocations", []);
        }
      });
  },

  load_assignment_details(frm) {
    const assignment = frm.doc.salary_structure_assignment;
    if (!assignment) {
      frm.earnings_components = [];
      frm.set_value("allocations", []);
      return;
    }

    frappe.call({
      method: `${MODULE_PATH}.get_assignment_details`,
      args: { assignment },
      callback(r) {
        const data = r.message || {};
        if (!data || !data.employee) return;

        frm.earnings_components = data.earnings || [];
        frm.set_value({
          employee: data.employee,
          company: data.company,
          from_date: data.from_date || frm.doc.from_date,
        });
        frm.events.rebuild_allocations(frm, data.earnings || []);
      },
    });
  },

  // Auto-add a single row per Earning component (default 100%) so the user can
  // drop in a project, or add extra rows to split one component across projects.
  rebuild_allocations(frm, earnings) {
    const rows = (earnings || []).map((component) => ({
      salary_component: component,
      project: null,
      percentage: 100,
    }));
    frm.set_value("allocations", rows);
    frm.refresh_field("allocations");
  },

  validate_date_range(frm) {
    if (!frm.doc.from_date || !frm.doc.to_date) return;
    const from = frappe.datetime.str_to_obj(frm.doc.from_date);
    const to = frappe.datetime.str_to_obj(frm.doc.to_date);
    if (to < from) {
      frappe.show_alert({
        message: __("To Date cannot be earlier than From Date."),
        indicator: "red",
      });
      frm.set_value("to_date", "");
    }
  },

  validate_allocations(frm, { throw_error = false } = {}) {
    const issues = [];
    let missing_fields = false;
    const combos = new Set();
    const totals = {};
    const allowed = frm.earnings_components || [];

    for (const row of frm.doc.allocations || []) {
      if (!row.salary_component || !row.project) {
        missing_fields = true;
        continue;
      }

      if (allowed.length && !allowed.includes(row.salary_component)) {
        issues.push(
          __("{0} is not part of the selected salary structure.", row.salary_component)
        );
      }

      const key = `${row.salary_component}::${row.project}`;
      if (combos.has(key)) {
        issues.push(
          __("{0} is already allocated to project {1}.", [
            row.salary_component,
            row.project,
          ])
        );
      }
      combos.add(key);
      totals[row.salary_component] =
        (totals[row.salary_component] || 0) + toNumber(row.percentage);
    }

    if (missing_fields) {
      issues.push(__("Every row needs both a Salary Component and a Project."));
    }

    for (const [component, total] of Object.entries(totals)) {
      if (round2(total) > 100) {
        issues.push(
          __("{0} is allocated {1}% which exceeds the allowed 100%.", [
            component,
            round2(total),
          ])
        );
      } else if (round2(total) < 100) {
        issues.push(
          __("{0} is only {1}% allocated; the total must be exactly 100%.", [
            component,
            round2(total),
          ])
        );
      }
    }

    const valid = issues.length === 0;
    if (!valid && throw_error) {
      const list = issues.map((issue) => `<li>${issue}</li>`).join("");
      frappe.msgprint({
        title: __("Allocation Errors"),
        indicator: "red",
        message: `<ul style="padding-left: 1rem; margin: 0;">${list}</ul>`,
      });
    }
    return { valid, issues, totals };
  },

  // Lightweight live warning when a component total crosses 100%.
  check_live(frm) {
    const result = frm.events.validate_allocations(frm);
    const over = (result.issues || []).filter((issue) => issue.indexOf("exceeds") !== -1);
    if (over.length) {
      frappe.show_alert({ message: over[0], indicator: "orange" });
    }
  },
});

frappe.ui.form.on("Salary Project Allocation Detail", {
  salary_component(frm) {
    frm.events.check_live(frm);
  },

  project(frm) {
    frm.events.check_live(frm);
  },

  percentage(frm) {
    frm.events.check_live(frm);
  },
});
