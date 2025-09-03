# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VolunteerSignup(Document):

    def on_submit(self):
        if self.status == "Pending":
            frappe.throw("Volunteer status must be either Rejected or Accepted")

        if self.status == "Accepted":
            try:
                frappe.sendmail(
                    recipients=[self.email],
                    subject="Volunteer Signup Approved",
                    message="Congratulations! Your volunteer signup has been approved.",
                )

                user = self.create_user()
                self.create_employee(user)

            except Exception as e:
                frappe.throw("An error occurred while processing your request.")
                frappe.log_error(
                    frappe.get_traceback(), f"Volunteer Signup Approval Failed {str(e)}"
                )
        if self.status == "Rejected":
            frappe.sendmail(
                recipients=[self.email],
                subject="Volunteer Signup Rejected",
                message="We're sorry to inform you that your volunteer signup has been rejected.",
            )

    def create_user(self):
        existing_user = frappe.db.get_value("User", {"email": self.email}, "name")
        if existing_user:
            link = frappe.utils.get_url_to_form("User", existing_user)
            frappe.throw(
                f"User already exists with this email. <a href='{link}' target='_blank'>View User</a>"
            )

        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": self.email,
                "first_name": self.surname,
                "last_name": self.other_names,
                "gender": self.gender,
                "enabled": 1,
                "module_profile": "Volunteer",
                "default_app": "lms",
            }
        )

        user.insert(ignore_permissions=True)

        return user

    def create_employee(self, user):
        employee = frappe.get_doc(
            {
                "doctype": "Employee",
                "email": user.name,
                "first_name": self.surname,
                "last_name": self.other_names,
                "gender": self.gender,
                "employee_name": f"{self.surname} {self.other_names}",
                "date_of_birth": self.date_of_birth,
                "date_of_joining": frappe.utils.nowdate(),
                "status": "Active",
                "department": "Volunteer",
                "user_id": user.name,
                "company": self.region,
                "branch": self.countybranch,
                "is_volunteer": 1,
                "cell_number": self.phone_number,
                "personal_email": self.email,
                "marital_status": self.marital_status,
                "blood_group": self.blood_group,
                "volunteer_signup": self.name
            }
        )

        employee.insert(ignore_permissions=True)
        frappe.db.set_value("User", user.name, "role_profile_name", "Volunteer")
