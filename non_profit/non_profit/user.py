import frappe


@frappe.whitelist(allow_guest=True)
def sign_up(**kwargs):

    print("Sign Up Function Called with kwargs:", kwargs.get("email"))

    user = frappe.db.get("User", {"email": kwargs.get("email")})

    if user:
        return "User already exists"

    else:
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
        }
    )

    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True

    user.insert()

    if kwargs.get("category_volunteer"):

        user.add_roles("Employee")
        volunteer = frappe.get_doc(
            {
                "doctype": "Employee",
                "first_name": kwargs.get("first_name"),
                "last_name": kwargs.get("last_name"),
                "user_id": user.name,
                "company": kwargs.get("region"),
                "branch": kwargs.get("branch"),
            }
        )

        volunteer.flags.ignore_permissions = True
        volunteer.insert()

    if kwargs.get("category_member"):

        user.add_roles("Non Profit Member")
        member = frappe.get_doc(
            {
                "doctype": "Member",
                "member_name": f"{kwargs.get("first_name")} {kwargs.get("last_name")}",
                "email_id": user.name,
                "custom_company": kwargs.get("region"),
                "custom_branch": kwargs.get("branch"),
            }
        )

        member.flags.ignore_permissions = True
        member.insert()

    return "Sign Up Successful"
