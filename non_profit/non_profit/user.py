import frappe
from datetime import datetime
from frappe.utils import add_to_date
from frappe.utils.password import update_password


@frappe.whitelist(allow_guest=True)
def sign_up(**kwargs):

    print(kwargs)

    frappe.db.begin()

    try:

        if kwargs.get("category_member"):
            user = create_user(kwargs)

            create_member(kwargs, user)

        if kwargs.get("category_volunteer"):
            create_volunteer(kwargs)

        frappe.db.commit()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Sign Up Error")
        frappe.throw(str(e))


def create_user(kwargs):

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
            "gender": kwargs.get("gender"),
            "enabled": 1,
            "role_profile_name": (
                "Member" if kwargs.get("category_member") else "Volunteer"
            ),
            "module_profile": (
                "Member" if kwargs.get("category_member") else "Volunteer"
            ),
        }
    )

    user.insert(ignore_permissions=True)
    update_password(user.name, kwargs.get("password"))

    return user


def create_member(kwargs, user=None):

    member = frappe.get_doc(
        {
            "doctype": "Member",
            "member_name": f'{kwargs.get("first_name")} {kwargs.get("last_name")}',
            "email_id": user.name,
            "membership_type": kwargs.get("membership_type"),
            "custom_company": kwargs.get("region"),
            "custom_branch": kwargs.get("branch"),
            "pan_number": kwargs.get("phone_number"),
        }
    )
    member.insert(ignore_permissions=True)

    if kwargs.get("membership_type"):
        doc_name = kwargs.get("membership_type")
        from_date = datetime.now().date()
        to_date = add_to_date(from_date, years=1)

        membership = frappe.get_doc(
            {
                "doctype": "Membership",
                "member": member.name,
                "membership_type": doc_name,
                "company": kwargs.get("region"),
                "branch": kwargs.get("branch"),
                "membership_status": "Pending",
                "from_date": from_date,
                "to_date": to_date,
                "member_since_date": from_date,
            }
        )

        membership.insert(ignore_permissions=True)


def create_volunteer(kwargs):

    if frappe.db.exists("User", {"email": kwargs.get("email")}):
        frappe.throw("User already exists with this email")

    # Prepare child table data for array fields
    trainings_data = [{"training_program": "test"}]

    additional_skills_data = [
        {"additional_skill": skill} for skill in kwargs.get("additional_skills", [])
    ]

    # allergies_data = [{"allergies": allergy} for allergy in kwargs.get("allergies", [])]

    disabilities_data = [
        {"disability": disability} for disability in kwargs.get("disabilities", [])
    ]

    volunteer_signup = frappe.get_doc(
        {
            "doctype": "Volunteer Signup",
            "status": "Pending",
            "surname": kwargs.get("last_name"),
            "other_names": kwargs.get("first_name"),
            "email": kwargs.get("email"),
            "phone_number": kwargs.get("phone_number"),
            "mobile_money_number": kwargs.get("mobile_money_number"),
            "gender": kwargs.get("gender"),
            "date_of_birth": kwargs.get("date_of_birth"),
            "idpassport": kwargs.get("idpassport"),
            "region": kwargs.get("region"),
            "countybranch": kwargs.get("branch"),
            "marital_status": kwargs.get("marital_status"),
            "education": kwargs.get("education"),
            "place_of_work": kwargs.get("place_of_work"),
            "profession": kwargs.get("profession"),
            "reason_to_join": kwargs.get("reason_to_join"),
            "blood_group": kwargs.get("blood_group"),
            "docstatus": 0,
            "trainings": trainings_data,
            "additional_skills": additional_skills_data,
            # "allergies": allergies_data,
            "disabilities": disabilities_data,
        }
    )

    volunteer_signup.insert(ignore_permissions=True)
