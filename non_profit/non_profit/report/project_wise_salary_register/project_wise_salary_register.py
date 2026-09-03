# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

"""Project-wise Salary Register.

Earnings-focused Salary Register. Without a project it behaves like a normal
register but shows only earnings components. When a project is selected, each
earning amount on a Salary Slip is multiplied by the employee's *effective*
Salary Project Allocation percentage for that project (unallocated components
are shown as zero).
"""

import frappe
from frappe import _
from frappe.utils import flt

from non_profit.overrides.salary_slip import get_latest_valid_allocation

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")


def execute(filters=None):
	filters = filters or {}

	currency = frappe.db.get_value("Company", filters.get("company"), "default_currency") or ""

	salary_slips = get_salary_slips(filters)
	if not salary_slips:
		return [], []

	earning_types = get_earning_types(salary_slips)
	columns = get_columns(earning_types, currency)
	ss_earning_map = get_salary_slip_earnings(salary_slips)

	project = filters.get("project")
	ss_allocation_map = get_project_allocation_map(salary_slips, project) if project else {}

	data = []
	for ss in salary_slips:
		row = {
			"salary_slip_id": ss.name,
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"department": ss.department,
			"company": ss.company,
			"start_date": ss.start_date,
			"end_date": ss.end_date,
			"currency": currency,
		}

		earnings = ss_earning_map.get(ss.name, {})
		allocation = ss_allocation_map.get(ss.name, {})

		for earning in earning_types:
			amount = flt(earnings.get(earning, 0))
			if project:
				percentage = flt(allocation.get(earning, 0))
				row[frappe.scrub(earning)] = amount * percentage / 100.0
			else:
				row[frappe.scrub(earning)] = amount

		data.append(row)

	return columns, data


def get_salary_slips(filters):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = frappe.qb.from_(salary_slip).select(salary_slip.star)

	if filters.get("docstatus"):
		query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])
	if filters.get("from_date"):
		query = query.where(salary_slip.start_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(salary_slip.end_date <= filters.get("to_date"))
	if filters.get("company"):
		query = query.where(salary_slip.company == filters.get("company"))
	if filters.get("employee"):
		query = query.where(salary_slip.employee == filters.get("employee"))
	if filters.get("department"):
		query = query.where(salary_slip.department == filters.get("department"))
	if filters.get("designation"):
		query = query.where(salary_slip.designation == filters.get("designation"))
	if filters.get("branch"):
		query = query.where(salary_slip.branch == filters.get("branch"))

	return query.run(as_dict=1) or []


def get_earning_types(salary_slips):
	return (
		frappe.qb.from_(salary_detail)
		.where((salary_detail.amount != 0) & (salary_detail.parentfield == "earnings"))
		.where(salary_detail.parent.isin([d.name for d in salary_slips]))
		.select(salary_detail.salary_component)
		.distinct()
	).run(pluck=True)


def get_salary_slip_earnings(salary_slips):
	"""Return {salary_slip: {component: amount}} for every earning row."""
	names = [ss.name for ss in salary_slips]

	result = (
		frappe.qb.from_(salary_slip)
		.join(salary_detail)
		.on(salary_slip.name == salary_detail.parent)
		.where((salary_detail.parent.isin(names)) & (salary_detail.parentfield == "earnings"))
		.select(salary_detail.parent, salary_detail.salary_component, salary_detail.amount)
	).run(as_dict=1)

	ss_map = {}
	for d in result:
		ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		ss_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_map


def get_project_allocation_map(salary_slips, project):
	"""Resolve each slip's effective allocation % per component for a project."""
	slip_allocation = {}
	for ss in salary_slips:
		# Prefer the allocation already captured on the slip (set on validate);
		# fall back to resolving the latest valid one for older slips.
		name = ss.get("salary_project_allocation")
		if not name:
			name = get_latest_valid_allocation(
				employee=ss.employee,
				salary_structure=ss.salary_structure,
				posting_date=ss.posting_date or ss.end_date,
			)
		slip_allocation[ss.name] = name

	alloc_names = {name for name in slip_allocation.values() if name}
	if not alloc_names:
		return {ss.name: {} for ss in salary_slips}

	detail_rows = frappe.db.get_all(
		"Salary Project Allocation Detail",
		filters={"parent": ["in", list(alloc_names)], "project": project},
		fields=["parent", "salary_component", "percentage"],
	)

	by_parent = {}
	for row in detail_rows:
		by_parent.setdefault(row.parent, {})[row.salary_component] = flt(row.percentage)

	return {ss.name: by_parent.get(slip_allocation[ss.name], {}) for ss in salary_slips}


def get_columns(earning_types, currency):
	columns = [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 150,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 120,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120,
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 100,
		},
	]

	for earning in sorted(earning_types):
		columns.append(
			{
				"label": earning,
				"fieldname": frappe.scrub(earning),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	columns.append(
		{
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Data",
			"options": "Currency",
			"hidden": 1,
		}
	)

	return columns

