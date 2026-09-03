# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

"""Salary Slip document-event overrides.

Wired via ``doc_events`` in hooks.py. When a Salary Slip is validated the
override links the latest *submitted* Salary Project Allocation that matches the
slip's Employee and Salary Structure and is valid on the slip's posting date, so
the slip can later be re-costed against the correct project split.
"""

import frappe


def validate(doc, method=None):
	"""Populate ``salary_project_allocation`` on the slip when it is not set."""
	if doc.get("salary_project_allocation"):
		return

	posting_date = doc.get("posting_date") or doc.get("end_date")
	allocation = get_latest_valid_allocation(
		employee=doc.get("employee"),
		salary_structure=doc.get("salary_structure"),
		posting_date=posting_date,
	)

	if allocation:
		doc.salary_project_allocation = allocation


def get_latest_valid_allocation(employee=None, salary_structure=None, posting_date=None):
	"""Return the most recent applicable submitted allocation for a slip.

	Args:
		employee (str): Employee on the Salary Slip.
		salary_structure (str): Salary Structure on the Salary Slip.
		posting_date (date|str): effective date the allocation must cover.

	Returns:
		str: name of the Salary Project Allocation, or None when nothing matches.
	"""
	if not (employee and salary_structure and posting_date):
		return None

	assignment_names = frappe.db.get_all(
		"Salary Structure Assignment",
		filters={"salary_structure": salary_structure},
		pluck="name",
	)
	if not assignment_names:
		return None

	allocation = frappe.db.get_all(
		"Salary Project Allocation",
		filters={
			"docstatus": 1,
			"employee": employee,
			"salary_structure_assignment": ["in", assignment_names],
			"from_date": ["<=", posting_date],
		},
		or_filters=[
			["to_date", "is", "not set"],
			["to_date", ">=", posting_date],
		],
		order_by="from_date desc, modified desc",
		limit=1,
		pluck="name",
	)

	return allocation[0] if allocation else None

