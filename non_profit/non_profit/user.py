import frappe


@frappe.whitelist(allow_guest=True)
def sign_up(**kwargs):
    """
    Handles user sign-up by creating a new User, and optionally
    an Employee (for volunteers) or Member document.
    """

    print(kwargs)
    try:
        frappe.db.begin()

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
                "password": kwargs.get("password"),
                "gender": kwargs.get("gender"),
                "enabled": 1,
                "user_type": "Website User",
            }
        )

        frappe.set_user("Administrator")

        user.insert(ignore_permissions=True)

        if kwargs.get("category_volunteer"):
            user.add_roles("Volunteer")
        if kwargs.get("category_member"):
            user.add_roles("Non Profit Member")

        if kwargs.get("category_volunteer"):
            volunteer = frappe.get_doc(
                {
                    "doctype": "Employee",
                    "first_name": kwargs.get("first_name"),
                    "last_name": kwargs.get("last_name"),
                    "user_id": user.name,
                    "company": kwargs.get("region"),
                    "branch": kwargs.get("branch"),
                    "gender": kwargs.get("gender"),
                    "date_of_birth": frappe.utils.nowdate(),
                    "date_of_joining": frappe.utils.nowdate(),
                    "status": "Inactive",
                }
            )
            volunteer.insert(ignore_permissions=True)

        if kwargs.get("category_member"):
            member = frappe.get_doc(
                {
                    "doctype": "Member",
                    "member_name": f'{kwargs.get("first_name")} {kwargs.get("last_name")}',
                    "email_id": user.name,
                    "membership_type": kwargs.get("membership_type"),
                    "custom_company": kwargs.get("region"),
                    "custom_branch": kwargs.get("branch"),
                }
            )
            member.insert(ignore_permissions=True)

        frappe.db.commit()

        return {"success": True, "message": "Sign Up Successful"}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Sign Up Error")
        frappe.throw(str(e))
