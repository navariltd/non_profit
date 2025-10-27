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
def create_membership(
    phone: str,
    amount: float,
    membership_type: str,
    branch: str,
) -> None:

    if not phone or not amount or not membership_type or not branch:
        frappe.throw("All fields are required")

    user = frappe.db.get_value(
        "User", frappe.session.user, ["full_name"], as_dict=1
    ).full_name

    try:
        frappe.db.begin()

        member = frappe.db.exists("Member", {"email_id": frappe.session.user})
        if not member:
            member = frappe.get_doc(
                {
                    "doctype": "Member",
                    "member_name": user,
                    "email_id": frappe.session.user,
                    "phone_number": phone,
                }
            )
            member.insert(ignore_permissions=True)

        else:
            member = frappe.get_doc("Member", member)

        if frappe.db.exists(
            "Membership",
            {"member": member.name, "membership_status": "Active", "company": branch},
        ):
            frappe.throw("You already have an active membership for this branch")

        from_date = datetime.today().date()

        membership = frappe.get_doc(
            {
                "doctype": "Membership",
                "member": member.name,
                "membership_type": membership_type,
                "amount": amount,
                "company": branch,
                "membership_status": "Draft",
                "from_date": from_date,
                "to_date": add_to_date(from_date, years=1, days=-1),
                "member_since_date": from_date,
            }
        )

        membership.insert(ignore_permissions=True)

        invoice = renew_membership(id=membership.name, phone_number=phone)

        frappe.db.commit()

        return invoice.name

    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error creating membership")
        frappe.throw("Error creating membership")


@frappe.whitelist(allow_guest=True)
def renew_membership(**kwargs):
    try:
        membership = frappe.get_doc("Membership", kwargs.get("id"))
        _, invoice = membership.initiate_payment(
            phone_number=kwargs.get("phone_number")
        )

        return invoice
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error renewing membership")
        frappe.throw("Error creating membership")
