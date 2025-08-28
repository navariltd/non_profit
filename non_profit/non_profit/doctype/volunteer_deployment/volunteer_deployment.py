# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class VolunteerDeployment(Document):
    def validate(self):
        self.validate_volunteer_count()

    def on_submit(self):
        self.add_volunteers_to_project()

    def add_volunteers_to_project(self):
        if not self.project:
            return

        project = frappe.get_doc("Project", self.project)

        existing_users = {row.user for row in project.users}

        for row in self.volunteers:
            if not row.volunteer:
                continue

            employee = frappe.get_value("Employee", row.volunteer, ["user_id"], as_dict=True)
            if not employee or not employee.user_id:
                continue

            if employee.user_id not in existing_users:
                project.append("users", {"user": employee.user_id})
                existing_users.add(employee.user_id)

        project.save(ignore_permissions=True)
        frappe.db.commit()

    
    def validate_volunteer_count(self):
        """Validate that assigned volunteers don't exceed required count"""
        if self.number_of_volunteers_required and len(self.volunteers) > self.number_of_volunteers_required:
            frappe.throw(_("Number of assigned volunteers ({0}) exceeds required count ({1})").format(
                len(self.volunteers), self.number_of_volunteers_required
            ))

@frappe.whitelist()
def get_available_volunteers(company, branch, deployment=None, expected_start_date=None):

    required_skills = []
    if deployment:
        dep_doc = frappe.get_doc("Volunteer Deployment", deployment)
        required_skills = [d.skill for d in dep_doc.required_skills]

        if not expected_start_date and dep_doc.expected_start_date:
            expected_start_date = dep_doc.expected_start_date

    employees = frappe.get_all(
        "Employee",
        filters={
            "company": company,
            "branch": branch,
            "is_volunteer": 1,
            "status": "Active"
        },
        fields=["name as employee", "employee_name", "status"]
    )
    

    filtered_employees = []

    for emp in employees:
        if expected_start_date:
            available = frappe.get_all(
                "Volunteer Availability Slot",
                filters={
                    "employee": emp.get("employee"),
                    "company": company,
                    "branch": branch,
                    "starts_on": ["<=", expected_start_date],
                    "ends_on": [">=", expected_start_date],
                },
                limit=1
            )
            print(available)
            if not available:
                continue 

        skill_maps = frappe.get_all(
            "Employee Skill Map",
            filters={"employee": emp["employee"]},
            fields=["name"]
        )

        skills = set()
        for sm in skill_maps:
            child_skills = frappe.get_all(
                "Employee Skill",
                filters={"parent": sm["name"]},
                pluck="skill"
            )
            skills.update(child_skills)

        emp["skills"] = ", ".join(skills) if skills else "No skills listed"
        

        if required_skills:
            if any(req in skills for req in required_skills):
                filtered_employees.append(emp)
        else:
            filtered_employees.append(emp)

    return filtered_employees



