import frappe
from datetime import datetime
from frappe.utils import add_to_date
from frappe.utils.password import update_password


@frappe.whitelist(allow_guest=True)
def create_user(**kwargs):

    try:
        if frappe.db.exists("User", {"email": kwargs.get("email")}):
            frappe.throw("User already exists with this email")

        if frappe.db.get_creation_count("User", 60) > 300:
            return frappe.respond_as_web_page(
                _("Temporarily Disabled"),
                _(
                    "Too many users signed up recently, so the registration is disabled. Please try back in an hour"
                ),
                http_status_code=429,
            )

        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": kwargs.get("email"),
                "first_name": kwargs.get("first_name"),
                "last_name": kwargs.get("last_name"),
                "full_name": f'{kwargs.get("first_name")} {kwargs.get("last_name")}',
                "phone": kwargs.get("phone"),
                "gender": kwargs.get("gender"),
                "enabled": 1,
                "default_app": "non_profit",
                "module_profile": "Member",
                "role_profile_name": "Member",
            }
        )

        user.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error signing up")
        frappe.throw("Error signing up")


@frappe.whitelist(allow_guest=True)
def create_membership(**kwargs):

    try:
        frappe.db.begin()

        member = None
        membership = None

        if frappe.db.exists("Member", {"email_id": kwargs.get("email_id")}):
            member = frappe.db.get_value("Member", {"email_id": kwargs.get("email_id")}, "name")
        
            membership = frappe.db.exists("Membership", {"member": member})
        if member and membership:
            frappe.throw("Membership already exists for this member")

        member = frappe.get_doc(
            {
                "doctype": "Member",
                "member_name": kwargs.get("member_name"),
                "email_id": kwargs.get("email_id"),
                "membership_type": kwargs.get("membership_type"),
                "custom_company": kwargs.get("region"),
                "pan_number": kwargs.get("phone_number"),
            }
        )
        member.insert(ignore_permissions=True)

        user = frappe.get_doc("User", {"email": member.email_id})

        user.save(ignore_permissions=True)

        if kwargs.get("membership_type"):
            doc_name = kwargs.get("membership_type")
            from_date = frappe.utils.today()
            to_date = add_to_date(from_date, years=1)

            membership = frappe.get_doc(
                {
                    "doctype": "Membership",
                    "member": member.name,
                    "membership_type": doc_name,
                    "company": kwargs.get("region"),
                    "membership_status": "Pending",
                    "from_date": from_date,
                    "to_date": to_date,
                    "member_since_date": from_date,
                }
            )

            membership.insert(ignore_permissions=True)

        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating membership")
        frappe.throw("Error creating membership")


