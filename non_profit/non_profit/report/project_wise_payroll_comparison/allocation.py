# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

"""Data collection for the Project-wise Payroll Comparison report.

Gathers each Salary Slip's earning components and resolves the effective Salary
Project Allocation so every earning can be split into per-project amounts plus an
unallocated remainder.
"""

from collections import defaultdict

import frappe
from frappe.query_builder.functions import Sum
from frappe.utils import flt

from non_profit.overrides.salary_slip import get_latest_valid_allocation

salary_detail = frappe.qb.DocType("Salary Detail")


def get_component_map(salary_slips):
	"""Return ``{salary_slip: {(parentfield, salary_component): total}}``.

	Covers both Earning and Deduction components so the report can group rows by type.
	"""
	names = [slip.name for slip in salary_slips]

	rows = (
		frappe.qb.from_(salary_detail)
		.select(
			salary_detail.parent,
			salary_detail.parentfield,
			salary_detail.salary_component,
			Sum(salary_detail.amount).as_("amount"),
		)
		.where(salary_detail.parent.isin(names))
		.where(salary_detail.parentfield.isin(["earnings", "deductions"]))
		.groupby(salary_detail.parent, salary_detail.parentfield, salary_detail.salary_component)
	).run(as_dict=1)

	component_map = defaultdict(dict)
	for row in rows:
		component_map[row.parent][(row.parentfield, row.salary_component)] = flt(row.amount)

	return component_map


def get_project_names(projects):
	"""Return ``{project: project_name}`` for the given project ids."""
	if not projects:
		return {}

	rows = frappe.db.get_all(
		"Project",
		filters={"name": ["in", list(projects)]},
		fields=["name", "project_name"],
	)

	return {row.name: row.project_name or row.name for row in rows}


def get_allocation_map(salary_slips):
	"""Return ``{salary_slip: [allocation detail rows]}`` for the effective split."""
	slip_allocation = {}
	allocation_names = set()

	for slip in salary_slips:
		# Prefer the allocation captured on the slip; fall back to the latest
		# valid one for slips created before the allocation was linked.
		name = slip.get("salary_project_allocation") or get_latest_valid_allocation(
			employee=slip.employee,
			salary_structure=slip.salary_structure,
			posting_date=slip.posting_date or slip.end_date,
		)
		slip_allocation[slip.name] = name
		if name:
			allocation_names.add(name)

	if not allocation_names:
		return {}

	detail_rows = frappe.db.get_all(
		"Salary Project Allocation Detail",
		filters={"parent": ["in", list(allocation_names)], "parentfield": "allocations"},
		fields=["parent", "salary_component", "project", "percentage"],
	)

	by_allocation = defaultdict(list)
	for row in detail_rows:
		by_allocation[row.parent].append(row)

	return {
		slip.name: by_allocation.get(slip_allocation.get(slip.name), [])
		for slip in salary_slips
	}


def build_records(salary_slips, component_map, allocation_map):
	"""Split every earning into per-project amounts plus an unallocated remainder.

	Deduction components are never project-allocated, so they are reported wholly
	under the ``Unallocated`` column.
	"""
	records = []

	for slip in salary_slips:
		components = component_map.get(slip.name, {})
		allocations = allocation_map.get(slip.name, [])

		for (parentfield, component), total in components.items():
			if parentfield != "earnings":
				records.append(build_record(slip, component, None, total, parentfield))
				continue

			allocated = 0.0

			for row in allocations:
				if row.salary_component != component:
					continue
				amount = flt(total) * flt(row.percentage) / 100.0
				allocated += amount
				records.append(build_record(slip, component, row.project, amount, parentfield))

			unallocated = flt(total) - allocated
			if flt(unallocated, 2):
				records.append(build_record(slip, component, None, unallocated, parentfield))

	return records


def build_record(slip, component, project, amount, parentfield):
	"""Return a flat record describing one project (or unallocated) split."""
	return {
		"employee": slip.employee,
		"employee_name": slip.employee_name,
		"department": slip.department,
		"company": slip.company,
		"salary_component": component,
		"parentfield": parentfield,
		"project": project,
		"amount": flt(amount, 2),
	}
