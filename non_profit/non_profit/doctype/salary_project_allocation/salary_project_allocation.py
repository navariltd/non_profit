# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

"""Salary Project Allocation.

Allocates an employee's salary *earnings* (defined on a Salary Structure) across
projects. Each submitted allocation acts as one effective/versioned record so a
historical Salary Slip can be re-costed using the version active on its posting
date without modifying the core Salary Structure Assignment.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class SalaryProjectAllocation(Document):
	"""Enforce the component/project allocation rules.

	Responsibilities:
	- validate the effective date range (To Date must not precede From Date),
	- keep the selected Salary Structure Assignment consistent with the Employee,
	- restrict allocation rows to Earning components of the linked structure,
	- reject duplicate (component, project) rows and any component whose total
	  is not exactly 100%.
	"""

	def validate(self):
		self.validate_date_range()
		self.validate_assignment_and_employee()
		self.validate_allocations()

	def validate_date_range(self):
		"""Raise if To Date falls before From Date."""
		if not self.from_date or not self.to_date:
			return

		if getdate(self.to_date) < getdate(self.from_date):
			frappe.throw(
				_("To Date ({0}) cannot be earlier than From Date ({1}).").format(
					self.to_date, self.from_date
				),
				title=_("Invalid Date Range"),
			)

	def validate_assignment_and_employee(self):
		"""Ensure the assignment belongs to the selected Employee and Company."""
		assignment = self.salary_structure_assignment
		if not assignment:
			frappe.throw(
				_("Please select a Salary Structure Assignment."),
				title=_("Assignment Required"),
			)

		fields = ["employee", "company", "salary_structure"]
		assignment_meta = frappe.db.get_value(
			"Salary Structure Assignment", assignment, fields, as_dict=True
		)
		if not assignment_meta:
			frappe.throw(
				_("Salary Structure Assignment {0} no longer exists.").format(assignment)
			)

		if self.employee and assignment_meta.employee and assignment_meta.employee != self.employee:
			frappe.throw(
				_("Salary Structure Assignment {0} belongs to employee {1}, not {2}.").format(
					frappe.bold(assignment),
					frappe.bold(assignment_meta.employee),
					frappe.bold(self.employee),
				),
				title=_("Employee Mismatch"),
			)

		if self.company and assignment_meta.company and assignment_meta.company != self.company:
			frappe.throw(
				_("Salary Structure Assignment {0} belongs to company {1}, not {2}.").format(
					frappe.bold(assignment),
					frappe.bold(assignment_meta.company),
					frappe.bold(self.company),
				),
				title=_("Company Mismatch"),
			)

	def validate_allocations(self):
		"""Validate every allocation row and enforce 100% totals per component."""
		rows = self.get("allocations") or []
		if not rows:
			frappe.throw(
				_("Please add at least one allocation row."),
				title=_("Allocations Required"),
			)

		expected_earnings = self.get_structure_earnings()
		component_totals = {}
		seen_pairs = set()

		for idx, row in enumerate(rows, start=1):
			if not row.salary_component:
				frappe.throw(_("Row {0}: Salary Component is required.").format(idx))
			if not row.project:
				frappe.throw(
					_("Row {0} ({1}): Project is required.").format(
						idx, row.salary_component
					)
				)

			component_type = frappe.get_cached_value(
				"Salary Component", row.salary_component, "type"
			)
			if component_type != "Earning":
				frappe.throw(
					_("{0} is a Deduction and cannot be allocated.").format(
						frappe.bold(row.salary_component)
					),
					title=_("Invalid Component"),
				)

			if expected_earnings and row.salary_component not in expected_earnings:
				frappe.throw(
					_("{0} is not part of the linked Salary Structure.").format(
						frappe.bold(row.salary_component)
					),
					title=_("Invalid Component"),
				)

			percentage = flt(row.percentage)
			if percentage <= 0:
				frappe.throw(
					_("Row {0} ({1}): allocation percentage must be greater than zero.").format(
						idx, row.salary_component
					)
				)
			if percentage > 100:
				frappe.throw(
					_("Row {0} ({1}): a single allocation cannot exceed 100%.").format(
						idx, row.salary_component
					)
				)

			pair = (row.salary_component, row.project)
			if pair in seen_pairs:
				frappe.throw(
					_("{0} is already allocated to project {1}.").format(
						frappe.bold(row.salary_component), frappe.bold(row.project)
					),
					title=_("Duplicate Allocation"),
				)
			seen_pairs.add(pair)

			component_totals[row.salary_component] = (
				component_totals.get(row.salary_component, 0) + percentage
			)

		for component, total in sorted(component_totals.items()):
			if flt(total, 2) != 100:
				frappe.throw(
					_("{0} is allocated {1}% in total; each component must total exactly 100%.").format(
						frappe.bold(component), flt(total, 2)
					),
					title=_("Incomplete Allocation"),
				)

	def get_structure_earnings(self):
		"""Return the Earning component names defined on the linked structure."""
		if not self.salary_structure_assignment:
			return []

		salary_structure = frappe.db.get_value(
			"Salary Structure Assignment", self.salary_structure_assignment, "salary_structure"
		)
		if not salary_structure:
			return []

		structure = frappe.get_cached_doc("Salary Structure", salary_structure)
		earnings = []
		for row in structure.get("earnings", []):
			component = row.get("salary_component")
			if component and (
				frappe.get_cached_value("Salary Component", component, "type") == "Earning"
			):
				earnings.append(component)

		return earnings


@frappe.whitelist()
def get_assignment_details(assignment):
	"""Return details the client needs once a Salary Structure Assignment is picked.

	Args:
		assignment (str): name of the Salary Structure Assignment.

	Returns:
		dict: employee, employee_name, company, salary_structure, from_date and
		the list of Earning component names belonging to the linked structure.
	"""
	if not assignment:
		return {}

	assignment_doc = frappe.get_cached_doc("Salary Structure Assignment", assignment)
	salary_structure = assignment_doc.get("salary_structure")
	earnings = []

	if salary_structure:
		structure = frappe.get_cached_doc("Salary Structure", salary_structure)
		for row in structure.get("earnings", []):
			component = row.get("salary_component")
			if component and (
				frappe.get_cached_value("Salary Component", component, "type") == "Earning"
			):
				earnings.append(component)

	return {
		"employee": assignment_doc.get("employee"),
		"employee_name": assignment_doc.get("employee_name"),
		"company": assignment_doc.get("company"),
		"salary_structure": salary_structure,
		"from_date": assignment_doc.get("from_date"),
		"earnings": earnings,
	}
