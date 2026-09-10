// Copyright (c) 2026, Frappe and contributors
// For license information, please see license.txt

frappe.query_reports["Project-wise Payroll Comparison"] = {
  filters: [
    {
      fieldname: "based_on",
      label: __("Based On"),
      fieldtype: "Select",
      options: [
        { value: "Department", label: __("Department") },
        { value: "Employee", label: __("Employee") },
        { value: "Company", label: __("Company") },
      ],
      default: "Company",
      reqd: 1,
      width: "100px",
    },
    {
      fieldname: "department",
      label: __("Department"),
      fieldtype: "Link",
      options: "Department",
      depends_on: "eval:doc.based_on==='Employee' || doc.based_on==='Department'",
      get_query: function () {
        return {
          filters: {
            company: frappe.query_report.get_filter_value("company"),
          },
        };
      },
      width: "100px",
    },
    {
      fieldname: "component_type",
      label: __("Type"),
      fieldtype: "Select",
      options: [
        { value: "", label: __("") },
        { value: "Earnings", label: __("Earnings") },
        { value: "Deductions", label: __("Deductions") },
      ],
      default: "",
      width: "100px",
    },
    {
      fieldname: "from_date",
      label: __("From"),
      fieldtype: "Date",
      default: frappe.datetime.add_months(frappe.datetime.month_start(), -2),
      reqd: 1,
      width: "100px",
    },
    {
      fieldname: "to_date",
      label: __("To"),
      fieldtype: "Date",
      default: frappe.datetime.add_months(frappe.datetime.month_end(), -1),
      reqd: 1,
      width: "100px",
    },
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      default: frappe.defaults.get_user_default("Company"),
      reqd: 1,
      width: "100px",
    },
    {
      fieldname: "employee",
      label: __("Employee"),
      fieldtype: "Link",
      options: "Employee",
      depends_on: "eval:doc.based_on==='Employee'",
      width: "100px",
    },
    {
      fieldname: "currency",
      fieldtype: "Link",
      options: "Currency",
      label: __("Currency"),
      default: erpnext.get_currency(frappe.defaults.get_default("Company")),
      width: "50px",
    },
  ],

  formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (data && data.is_title) {
      value = `<b>${value}</b>`;
    }

    return value;
  },
};
