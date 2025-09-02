# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class VolunteerDeployment(Document):
    def before_save(self):
        """Check volunteer changes and sync assignments even in Draft"""
        changed = self._volunteers_changed()
        if changed:
            self.remove_outdated_assignments()
            self.assign_volunteers()

    def validate(self):
        self.validate_volunteer_count()
        self.validate_volunteers()

    def on_submit(self):
        """Still ensure everything is synced on submit"""
        self.assign_volunteers()

    def before_update_after_submit(self):
        """Sync if volunteers changed after submit"""
        changed = self._volunteers_changed()
        if changed:
            self.remove_outdated_assignments()
            self.assign_volunteers()

    def validate_volunteers(self):
        seen_volunteers = set()

        for row in self.volunteers:
            if row.volunteer in seen_volunteers:
                frappe.throw(_("Volunteer {0} is duplicated in the table.").format(row.volunteer))
            seen_volunteers.add(row.volunteer)

            employee = frappe.db.get_value(
                "Employee",
                row.volunteer,
                ["branch", "status", "is_volunteer"],
                as_dict=True,
            )

            if not employee:
                frappe.throw(_("Employee {0} not found.").format(row.volunteer))

            if employee.branch != self.branch:
                frappe.throw(
                    _("Volunteer {0} is from branch {1}, but this deployment is for branch {2}.")
                    .format(row.volunteer, employee.branch, self.branch)
                )

            if employee.status != "Active":
                frappe.throw(_("Volunteer {0} is not Active.").format(row.volunteer))

            if not employee.is_volunteer:
                frappe.throw(_("Employee {0} is not marked as a Volunteer.").format(row.volunteer))

    def _volunteers_changed(self):
        """Check if volunteers table changed compared to DB"""
        if not self.get("name"):
            return True  

        old_volunteers = set(
            frappe.db.get_all(
                "Volunteer Deployment Assignee",  
                filters={"parent": self.name},
                pluck="volunteer"
            )
        )
        new_volunteers = {row.volunteer for row in self.volunteers if row.volunteer}
        return old_volunteers != new_volunteers

    def remove_outdated_assignments(self):
        """Remove project users and ToDos for volunteers no longer assigned"""     
        other_deployments = frappe.get_all(
            "Volunteer Deployment",
            filters={
            "docstatus": ["!=", 2],  
            "name": ["!=", self.name],
            "project": self.project,
            "task": self.task
            },
            pluck="name"
        )
        
        active_volunteers = set()
        for deployment in other_deployments:
            deployment_volunteers = frappe.get_all(
            "Volunteer Deployment Assignee",
            filters={"parent": deployment},
            pluck="volunteer"
            )
            
            active_volunteers.update(deployment_volunteers)
        
        current_volunteers = {row.volunteer for row in self.volunteers if row.volunteer}
        active_volunteers.update(current_volunteers)
        
        if self.task:
            todos = frappe.get_all(
                "ToDo",
                filters={"reference_type": "Task", "reference_name": self.task},
                fields=["name", "allocated_to"]
            )
            for todo in todos:
                employee = frappe.db.get_value("Employee", {"user_id": todo.allocated_to}, "name")
                if employee and employee not in active_volunteers:
                    frappe.delete_doc("ToDo", todo.name, ignore_permissions=True)
                    
        elif self.project:
            project = frappe.get_doc("Project", self.project)
            to_remove = []
            for i, user_row in enumerate(project.users):
                employee = frappe.db.get_value("Employee", {"user_id": user_row.user}, "name")
                if employee and employee not in active_volunteers:
                    to_remove.append(i)
            for i in sorted(to_remove, reverse=True):
                project.users.pop(i)
            if to_remove:
                project.save(ignore_permissions=True)
                
            todos = frappe.get_all(
                "ToDo",
                filters={"reference_type": "Project", "reference_name": self.project},
                fields=["name", "allocated_to"]
            )
            for todo in todos:
                employee = frappe.db.get_value("Employee", {"user_id": todo.allocated_to}, "name")
                if employee and employee not in active_volunteers:
                    frappe.delete_doc("ToDo", todo.name, ignore_permissions=True)


    def assign_volunteers(self):
        """Ensure ToDos for Project and Task exist for each volunteer"""
        for row in self.volunteers:
            if not row.volunteer:
                continue
            employee = frappe.get_value("Employee", row.volunteer, ["user_id"], as_dict=True)
            if not employee or not employee.user_id:
                continue

            if self.task:
                self._ensure_todo(employee.user_id, "Task", self.task)
                
            elif self.project:
                self._ensure_todo(employee.user_id, "Project", self.project)
                
                project = frappe.get_doc("Project", self.project)
                existing_users = {row.user for row in project.users}
                employee = frappe.get_value("Employee", row.volunteer, ["user_id"], as_dict=True)
                user_added = False
                if employee and employee.user_id and employee.user_id not in existing_users:
                    project.append("users", {"user": employee.user_id})
                    existing_users.add(employee.user_id)
                    user_added = True
                if user_added:
                    project.save(ignore_permissions=True)


    def _ensure_todo(self, user_id, ref_type, ref_name):
        """Insert a ToDo if it doesn't exist"""
        if not frappe.db.exists("ToDo", {
            "reference_type": ref_type,
            "reference_name": ref_name,
            "allocated_to": user_id
        }):
            frappe.get_doc({
                "doctype": "ToDo",
                "reference_type": ref_type,
                "reference_name": ref_name,
                "allocated_to": user_id,
                "description": f"Assigned from Volunteer Deployment {self.name}"
            }).insert(ignore_permissions=True)

    def validate_volunteer_count(self):
        """Ensure volunteer count does not exceed requirement"""
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



