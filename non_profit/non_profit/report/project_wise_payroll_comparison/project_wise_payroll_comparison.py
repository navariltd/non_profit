# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

"""Project-wise Payroll Comparison.

Distributes an employee's salary *earnings* across projects for a period using the
same Salary Project Allocation split as the Project-wise Salary Register. Rows are
grouped by Department / Employee / Company (selected with the *Based On* filter) and
every group expands into one row per Earning salary component. The value columns are
one per project followed by a final ``Unallocated`` column holding the earnings that
are not tied to any project.
"""

from collections import defaultdict

import erpnext
import frappe
from frappe import _
from frappe.utils import flt, getdate

from non_profit.non_profit.report.project_wise_payroll_comparison.allocation import (
	build_records,
	get_allocation_map,
	get_component_map,
	get_project_names,
)

salary_slip = frappe.qb.DocType("Salary Slip")

UNALLOCATED = "Unallocated"
OTHERS = "Others"
COMPONENT_TITLE = "SALARY COMPONENT"

COMPONENT_TYPE_FIELDS = {"Earnings": "earnings", "Deductions": "deductions"}
COMPONENT_SECTIONS = (("earnings", "EARNINGS"), ("deductions", "DEDUCTIONS"))


def execute(filters=None):
	"""Entry point for the Script Report."""
	filters = filters or {}
	company_currency = erpnext.get_company_currency(filters.get("company"))

	validate_filters(filters)

	columns, data = get_data(filters, company_currency)
	return columns, data


def validate_filters(filters):
	"""Raise when the selected period is inverted."""
	if filters.get("from_date") and filters.get("to_date"):
		if getdate(filters["to_date"]) < getdate(filters["from_date"]):
			frappe.throw(_("To Date cannot be before From Date"))


def get_data(filters, company_currency):
	"""Collect the salary slips, resolve their project split and build the rows."""
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return get_columns(filters, []), []

	component_map = get_component_map(salary_slips)
	allocation_map = get_allocation_map(salary_slips)
	records = build_records(salary_slips, component_map, allocation_map)
	records = filter_records_by_type(filters, records)

	projects = sorted({record["project"] for record in records if record["project"]})
	project_names = get_project_names(projects)
	project_fields = get_project_fields(projects, project_names)

	columns = get_columns(filters, project_fields)
	data = build_rows(filters, records, project_fields)

	return columns, data


def get_salary_slips(filters, company_currency):
	"""Return the submitted Salary Slips matching the filters."""
	query = (
		frappe.qb.from_(salary_slip)
		.select(
			salary_slip.name,
			salary_slip.employee,
			salary_slip.employee_name,
			salary_slip.department,
			salary_slip.company,
			salary_slip.salary_structure,
			salary_slip.salary_project_allocation,
			salary_slip.posting_date,
			salary_slip.end_date,
		)
		.where(salary_slip.docstatus == 1)
		.orderby(salary_slip.department)
		.orderby(salary_slip.employee_name)
	)

	if filters.get("from_date"):
		query = query.where(salary_slip.start_date >= filters["from_date"])
	if filters.get("to_date"):
		query = query.where(salary_slip.end_date <= filters["to_date"])
	if filters.get("company"):
		query = query.where(salary_slip.company == filters["company"])
	if filters.get("employee"):
		query = query.where(salary_slip.employee == filters["employee"])
	if filters.get("department"):
		query = query.where(salary_slip.department == filters["department"])
	if filters.get("currency") and filters.get("currency") != company_currency:
		query = query.where(salary_slip.currency == filters["currency"])

	return query.run(as_dict=1) or []


def get_project_fields(projects, project_names):
	"""Map each project to a unique fieldname and its ``project_name`` label."""
	fields = []
	used = set()

	for project in projects:
		fieldname = f"project_{frappe.scrub(project)}"
		while fieldname in used:
			fieldname = f"{fieldname}_1"
		used.add(fieldname)
		fields.append(
			{"project": project, "fieldname": fieldname, "label": project_names.get(project, project)}
		)

	return fields


def get_columns(filters, project_fields):
	"""Build the grouping columns, one column per project and the Unallocated column."""
	columns = []

	if filters.get("based_on") == "Department":
		columns.append(link_column("department", "Department", "Department"))
	elif filters.get("based_on") == "Employee":
		columns.append(data_column("employee", "Employee"))
		columns.append(link_column("department", "Department", "Department"))
	else:
		columns.append(link_column("company", "Company", "Company"))

	columns.append(data_column("salary_component", "Salary Component"))

	for field in project_fields:
		columns.append(amount_column(field["fieldname"], field["label"]))

	columns.append(amount_column("unallocated", UNALLOCATED))
	columns.append(amount_column("total", "Total"))

	return columns


def data_column(fieldname, label):
	"""Return a plain Data column definition."""
	return {"fieldname": fieldname, "label": _(label), "fieldtype": "Data", "width": 200}


def link_column(fieldname, label, options):
	"""Return a Link column definition."""
	return {
		"fieldname": fieldname,
		"label": _(label),
		"fieldtype": "Link",
		"options": options,
		"width": 200,
	}


def amount_column(fieldname, label):
	"""Return a Float (currency) column definition."""
	return {
		"fieldname": fieldname,
		"label": _(label),
		"fieldtype": "Float",
		"precision": 2,
		"width": 150,
	}


def get_group_key(filters, record):
	"""Return the grouping tuple for a record based on the *Based On* filter."""
	based_on = filters.get("based_on")

	if based_on == "Employee":
		return (
			record["department"] or OTHERS,
			record["employee_name"] or record["employee"] or "",
		)
	if based_on == "Company":
		return (record["company"] or "",)
	return (record["department"] or OTHERS,)


def build_rows(filters, records, project_fields):
	"""Aggregate records per group/type/component and emit the report rows.

	Each group opens with a heading row, then an ``EARNINGS`` and/or ``DEDUCTIONS``
	section heading followed by that section's component rows.
	"""
	grouped = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(lambda: {"projects": defaultdict(float), "unallocated": 0.0})
		)
	)
	meta = {}

	for record in records:
		key = get_group_key(filters, record)
		bucket = grouped[key][record["parentfield"]][record["salary_component"]]

		if record["project"]:
			bucket["projects"][record["project"]] += record["amount"]
		else:
			bucket["unallocated"] += record["amount"]

		meta.setdefault(key, record)

	rows = []
	for key in sorted(grouped):
		rows.append(build_title_row(filters, meta[key], project_fields))

		for parentfield, label in COMPONENT_SECTIONS:
			components = grouped[key].get(parentfield)
			if not components:
				continue

			rows.append(build_section_row(label, project_fields))

			for component in sorted(components):
				bucket = components[component]
				row = {"salary_component": component}

				for field in project_fields:
					row[field["fieldname"]] = flt(bucket["projects"].get(field["project"], 0), 2)

				row["unallocated"] = flt(bucket["unallocated"], 2)
				row["total"] = flt(sum(bucket["projects"].values()) + bucket["unallocated"], 2)
				rows.append(row)

	return rows


def build_title_row(filters, record, project_fields):
	"""Return the bold group heading row that precedes the component rows."""
	row = {"salary_component": COMPONENT_TITLE, "is_title": True}
	based_on = filters.get("based_on")

	if based_on == "Employee":
		row["employee"] = record["employee_name"] or record["employee"]
		row["department"] = record["department"] or OTHERS
	elif based_on == "Company":
		row["company"] = record["company"]
	else:
		row["department"] = record["department"] or OTHERS

	for field in project_fields:
		row[field["fieldname"]] = None
	row["unallocated"] = None
	row["total"] = None

	return row


def build_section_row(label, project_fields):
	"""Return a bold ``EARNINGS`` / ``DEDUCTIONS`` section heading row."""
	row = {"salary_component": label, "is_title": True}

	for field in project_fields:
		row[field["fieldname"]] = None
	row["unallocated"] = None
	row["total"] = None

	return row


def filter_records_by_type(filters, records):
	"""Keep only the component type chosen in the *Type* filter, when one is set."""
	parentfield = COMPONENT_TYPE_FIELDS.get(filters.get("component_type"))
	if not parentfield:
		return records
	return [record for record in records if record["parentfield"] == parentfield]
