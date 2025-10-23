from datetime import datetime

import frappe
from frappe.utils import add_to_date
from frappe.utils.password import update_password


@frappe.whitelist(allow_guest=True)
def create_user(**kwargs):

    try:
        frappe.db.begin()
        if frappe.db.exists("User", {"email": kwargs.get("email")}):
            frappe.throw("User already exists with this email")

        # if frappe.db.get_creation_count("User", 60) > 300:
        #     return frappe.respond_as_web_page(
        #         _("Temporarily Disabled"),
        #         _(
        #             "Too many users signed up recently, so the registration is disabled. Please try back in an hour"
        #         ),
        #         http_status_code=429,
        #     )

        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": kwargs.get("email") or "",
                "first_name": kwargs.get("first_name") or "",
                "last_name": kwargs.get("last_name") or "",
                "full_name": f'{kwargs.get("first_name") or ""} {kwargs.get("last_name") or ""}',
                "phone": kwargs.get("phone") or "",
                "gender": kwargs.get("gender") or "",
                "enabled": 1,
                "default_app": "non_profit",
            }
        )

        user.insert(ignore_permissions=True)

        user.add_roles("Vmms Guest")

        frappe.db.commit()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error signing up")
        frappe.throw("Error signing up")


@frappe.whitelist(allow_guest=True)
def create_membership(**kwargs):

    try:
        frappe.db.begin()

        member = None
        membership = None
        branch = kwargs.get("branch")

        if frappe.db.exists("Member", {"email_id": kwargs.get("email_id")}):
            member = frappe.db.get_value(
                "Member", {"email_id": kwargs.get("email_id")}, "name"
            )

            membership = frappe.db.exists(
                "Membership", {"member": member, "company": branch}
            )
        if member and membership:
            frappe.throw("Membership already exists for this member")

        if not member:
            member = frappe.get_doc(
                {
                    "doctype": "Member",
                    "member_name": kwargs.get("member_name"),
                    "email_id": kwargs.get("email_id"),
                    "membership_type": kwargs.get("membership_type"),
                }
            )
            member.insert(ignore_permissions=True)
        else:
            member = frappe.get_doc("Member", member)

        if kwargs.get("membership_type"):
            doc_name = kwargs.get("membership_type")
            amount = frappe.db.get_value("Membership Type", doc_name, "amount")
            from_date = frappe.utils.today()
            to_date = add_to_date(from_date, years=1)

            membership = frappe.get_doc(
                {
                    "doctype": "Membership",
                    "member": member.name,
                    "membership_type": doc_name,
                    "company": kwargs.get("branch"),
                    "membership_status": "Pending",
                    "amount": amount,
                    "from_date": from_date,
                    "to_date": to_date,
                    "member_since_date": from_date,
                }
            )

            membership.insert(ignore_permissions=True)

        frappe.db.commit()
        return membership.name

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating membership")
        frappe.throw("Error creating membership")


@frappe.whitelist(allow_guest=True)
def renew_membership(**kwargs):
    try:
        membership = frappe.get_doc("Membership", kwargs.get("id"))
        membership.initiate_payment(phone_number=kwargs.get("phone_number"))
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error renewing membership")
