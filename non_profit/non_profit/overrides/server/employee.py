import frappe
from frappe import _
from frappe.model.document import Document

@frappe.whitelist()
def after_insert(doc: Document, method: str) -> None:
    if doc.personal_email:
        existing_user = frappe.db.get_value("User", {"email": doc.personal_email}, "name")
        
        if not existing_user and not doc.user_id:
            user = frappe.get_doc({
            "doctype": "User",
            "email": doc.personal_email,
            "first_name": doc.first_name or "Volunteer",
            "last_name": doc.last_name or "",
            "enabled": 1,
            "user_type": "System User",
            "send_welcome_email": 0
            })
            user.insert(ignore_permissions=True)
            
            user.role_profile_name = "Volunteer"
            user.module_profile = "Volunteer"
            user.save(ignore_permissions=True)
            existing_user = user.name
            
            frappe.db.commit()
        
        update_fields = {"user_id": existing_user}

        if doc.job_applicant:
            job_applicant = frappe.get_doc("Job Applicant", doc.job_applicant)
            if job_applicant.branch and not doc.branch:
                update_fields["branch"] = job_applicant.branch
            if job_applicant.company and not doc.company:
                update_fields["company"] = job_applicant.company
                
        frappe.db.set_value("Employee", doc.name, update_fields)
