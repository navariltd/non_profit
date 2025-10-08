# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form

from hrms.hr.utils import validate_bulk_tool_fields


class PersonnelDeploymentRequest(Document):
    def validate_fields(self, employees: list):
        mandatory_fields = [
            "project",
            "location",
            "expected_start_date",
            "expected_end_date",
        ]
        validate_bulk_tool_fields(
            self,
            mandatory_fields,
            employees,
            "expected_start_date",
            "expected_end_date",
        )

        number_of_volunteers_required = int(self.number_of_volunteers_required or 0)
        assigned_count = frappe.db.count(
            "Personnel Deployment Assignment",
            {"deployment": self.name, "docstatus": 1, "status": "Accepted"},
        )
        if assigned_count >= number_of_volunteers_required:
            frappe.throw(
                f"Cannot deploy personnel. The number of personnel required ({number_of_volunteers_required}) has already been met."
            )

    @frappe.whitelist()
    def deploy_employees(self, employees: list):
        """Deploy employees by creating Personnel Deployment Assignment records"""
        self.validate_fields(employees)
        return self.create_deployment_assignments(employees)

    def create_deployment_assignments(self, employees: list) -> dict:
        failure = []
        success = []
        savepoint = "before_deployment_creation"

        for employee in employees:
            try:
                existing = frappe.get_all(
                    "Personnel Deployment Assignment",
                    filters={
                        "employee": employee,
                        "deployment": self.name,
                        "status": ["in", ["Pending", "Accepted"]],
                        "docstatus": 1,
                    },
                    fields=["name", "status"],
                )

                if existing:
                    failure.append(
                        {
                            "employee": employee,
                            "reason": f"Existing {existing[0].status} assignment (<a href='{frappe.utils.get_url_to_form('Personnel Deployment Assignment', existing[0].name)}' target='_blank'>{existing[0].name}</a>) found.",
                        }
                    )
                    continue

                frappe.db.savepoint(savepoint)
                assignment = frappe.new_doc("Personnel Deployment Assignment")

                fields_to_copy = {
                    "project": self.project,
                    "task": self.task,
                    "location": self.location,
                    "company": self.company,
                    "expected_start_date": self.expected_start_date,
                    "expected_end_date": self.expected_end_date,
                    "notes": self.notes,
                    "require_contract_before_deployment": self.require_contract_before_deployment,
                    "terms_of_reference": self.terms_of_reference,
                    "expense_approver": self.expense_approver,
                    "advance_approver": self.advance_approver,
                    "deployment_approver": self.deployment_approver,
                }

                if self.get("deployment_request_term_template"):
                    fields_to_copy["deployment_request_term_template"] = (
                        self.deployment_request_term_template
                    )

                assignment.employee = employee
                assignment.deployment = self.name
                assignment.status = "Pending"

                for field, value in fields_to_copy.items():
                    assignment.set(field, value)

                assignment.insert()
                assignment.submit()

                success.append(
                    {
                        "doc": get_link_to_form(
                            "Personnel Deployment Assignment", assignment.name
                        ),
                        "employee": employee,
                    }
                )

            except Exception as e:
                frappe.db.rollback(save_point=savepoint)
                frappe.log_error(
                    f"Personnel Deployment Assignment failed for employee {employee}.",
                    str(e),
                )
                failure.append({"employee": employee, "reason": str(e)})

        return {"success": success, "failure": failure}

    @frappe.whitelist()
    def get_employees(self, advanced_filters: list = None) -> list:
        """Get employees based on filter criteria"""
        if advanced_filters is None:
            advanced_filters = []

        base_filters = self.get_base_filters()
        all_filters = base_filters + advanced_filters

        employees = frappe.get_list(
            "Employee",
            filters=all_filters,
            fields=[
                "name",
                "employee",
                "employee_name",
                "company",
                "department",
                "designation",
                "employment_type",
                "date_of_joining",
                "status",
            ],
        )

        filtered_employees = self.apply_multiselect_filters(employees)

        return filtered_employees

    def get_base_filters(self):
        """Get basic filters for employee query"""
        filters = [["status", "=", "Active"]]

        if self.company:
            filters.append(["company", "=", self.company])

        return filters

    def apply_multiselect_filters(self, employees: list) -> list:
        """Apply multiselect field filters to employee list"""
        if not employees:
            return []

        filtered_employees = employees

        if self.get("companies"):
            company_list = [row.company for row in self.companies]
            filtered_employees = [
                emp for emp in filtered_employees if emp.company in company_list
            ]

        if self.get("department"):
            dept_list = [row.department for row in self.department]
            filtered_employees = [
                emp for emp in filtered_employees if emp.department in dept_list
            ]

        if self.get("employment_type"):
            emp_type_list = [row.employment_type for row in self.employment_type]
            filtered_employees = [
                emp
                for emp in filtered_employees
                if emp.employment_type in emp_type_list
            ]

        if self.get("designation"):
            designation_list = [row.designation for row in self.designation]
            filtered_employees = [
                emp for emp in filtered_employees if emp.designation in designation_list
            ]

        if self.get("courses"):
            course_list = [row.course for row in self.courses]
            employees_with_courses = self.get_employees_with_courses(course_list)
            filtered_employees = [
                emp for emp in filtered_employees if emp.name in employees_with_courses
            ]

        if self.get("skills"):
            skill_list = [row.skill for row in self.skills]
            employees_with_skills = self.get_employees_with_skills(skill_list)
            filtered_employees = [
                emp for emp in filtered_employees if emp.name in employees_with_skills
            ]

        if self.get("licences"):
            licence_list = [row.licence for row in self.licences]
            employees_with_licences = self.get_employees_with_licences(licence_list)
            filtered_employees = [
                emp for emp in filtered_employees if emp.name in employees_with_licences
            ]

        if (
            self.get("filter_criteria")
            and self.expected_start_date
            and self.expected_end_date
        ):
            if self.filter_criteria == "Availability":
                filtered_employees = self.filter_by_availability(
                    filtered_employees, self.expected_start_date, self.expected_end_date
                )

        return filtered_employees

    def filter_by_availability(
        self, employees: list, expected_start_date, expected_end_date
    ) -> list:
        available_employees = []

        for emp in employees:
            schedules = frappe.get_all(
                "Personnel Availability Schedule",
                filters={
                    "employee": emp.get("employee"),
                    "start_date": ["<=", expected_end_date],
                    "end_date": [">=", expected_start_date],
                },
                fields=["name", "start_date", "end_date"],
            )

            found_overlap = False

            for schedule in schedules:
                shifts = frappe.get_all(
                    "Schedule",
                    filters={"parent": schedule.name},
                    fields=["day", "shift_type"],
                )

                for shift in shifts:
                    shift_details = frappe.db.get_value(
                        "Shift Type",
                        shift.shift_type,
                        ["start_time", "end_time"],
                        as_dict=True,
                    )

                    if not shift_details:
                        continue

                    found_overlap = True
                    break

                if found_overlap:
                    break

            if found_overlap:
                available_employees.append(emp)

        return available_employees

    def get_employees_with_courses(self, course_list: list) -> list:
        """Get employees who have completed any of the specified courses"""
        if not course_list:
            return []

        return frappe.get_all(
            "Related Courses",
            filters={"course": ["in", course_list]},
            distinct=True,
            pluck="parent",
        )

    def get_employees_with_skills(self, skill_list: list) -> list:
        """Get employees who have any of the specified skills"""
        if not skill_list:
            return []

        skill_maps = frappe.get_all(
            "Employee Skill",
            filters={"skill": ["in", skill_list]},
            distinct=True,
            pluck="parent",
        )

        employees = []
        if skill_maps:
            employees = frappe.get_all(
                "Employee Skill Map",
                filters={"name": ["in", skill_maps]},
                pluck="employee",
            )

        return employees

    def get_employees_with_licences(self, licence_list: list) -> list:
        """Get employees who have any of the specified licenses"""
        if not licence_list:
            return []

        if not licence_list:
            return []

        return frappe.get_all(
            "Personnel Licence",
            filters={"license_type": ["in", licence_list]},
            distinct=True,
            pluck="parent",
        )

    @frappe.whitelist()
    def get_filter_criteria_options(self):
        """Get available filter criteria options"""
        return frappe.get_list(
            "Volunteer Deployment Criteria",
            fields=["name", "criteria_name", "description"],
        )
