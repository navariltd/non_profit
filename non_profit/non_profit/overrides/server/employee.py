import frappe
from frappe import _
from frappe.model.document import Document


@frappe.whitelist()
def after_insert(doc: Document, method: str) -> None:
    """
    Handle after_insert event for Employee document
    Creates user account and updates employee fields from Job Applicant or Volunteer Signup
    """
    try:
        needs_save = False

        if doc.personal_email and not doc.user_id:
            user_id = create_user_for_employee(doc)
            if user_id:
                doc.user_id = user_id
                needs_save = True

        if doc.job_applicant:
            if update_fields_from_applicant(doc):
                needs_save = True

            if doc.is_volunteer:
                ensure_job_offer_for_volunteer(doc.job_applicant)

        if needs_save:
            doc.save(ignore_permissions=True)
            frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Error in Employee after_insert for {doc.name}", f"{str(e)}")
        frappe.throw(_("Error processing employee creation: {0}").format(str(e)))


def ensure_job_offer_for_volunteer(job_applicant: str) -> None:
    """
    Ensure a Job Offer exists for the given Volunteer.
    If not found, auto-create from linked Job Applicant.
    """
    if not job_applicant:
        return

    existing_offer = frappe.db.exists(
        "Job Offer",
        {"job_applicant": job_applicant},
    )
    if existing_offer:
        return

    applicant = frappe.get_doc("Job Applicant", job_applicant)

    designation = applicant.designation
    if not designation:
        if not frappe.db.exists("Designation", {"designation_name": "Volunteer"}):
            designation_doc = frappe.get_doc(
                {
                    "doctype": "Designation",
                    "designation_name": "Volunteer",
                }
            )
            designation_doc.insert(ignore_permissions=True)
        designation = "Volunteer"

    job_offer = frappe.new_doc("Job Offer")
    job_offer.job_applicant = applicant.name
    job_offer.company = applicant.company
    job_offer.designation = designation

    job_offer.status = "Accepted"
    job_offer.offer_date = frappe.utils.today()

    job_offer.insert(ignore_permissions=True)
    job_offer.submit()
    frappe.db.commit()


def copy_table_data(source_doc, target_doc, source_table, target_table):
    """
    Copy table data from source to target document if target table is empty
    Returns True if data was copied
    """
    try:
        if not target_doc.get(target_table) and source_doc.get(source_table):
            source_table_data = source_doc.get(source_table)

            for source_row in source_table_data:
                new_row = target_doc.append(target_table, {})

                for fieldname in source_row.as_dict().keys():
                    if fieldname not in [
                        "name",
                        "parent",
                        "parentfield",
                        "parenttype",
                        "doctype",
                        "idx",
                        "docstatus",
                    ]:
                        new_row.set(fieldname, source_row.get(fieldname))

            return True

    except Exception as e:
        frappe.log_error(
            f"Error copying table data from {source_table} to {target_table}",
            f"{str(e)}",
        )
        return False

    return False


def create_user_for_employee(doc: Document) -> str:
    """
    Create a user account for the employee
    Returns the user ID if created successfully, None otherwise
    """
    existing_user = frappe.db.get_value("User", {"email": doc.personal_email}, "name")

    user = None
    if existing_user:
        user = frappe.get_doc("User", existing_user)
    else:
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": doc.personal_email,
                "first_name": doc.first_name or "Volunteer",
                "last_name": doc.last_name or "",
                "enabled": 1,
                "user_type": "System User",
                "send_welcome_email": 0,
                "default_app": "non_profit",
            }
        )
        user.insert(ignore_permissions=True)
    try:
        user.role_profile_name = "Volunteer"
        user.module_profile = "Volunteer"
        user.save(ignore_permissions=True)

        frappe.db.commit()
        return user.name

    except Exception as e:
        frappe.log_error(f"Error creating user for employee {doc.name}", f"{str(e)}")
        return None


def update_fields_from_applicant(doc: Document) -> bool:
    """
    Update employee fields from linked Job Applicant document
    Only updates if the employee field is empty
    Returns True if any fields were updated
    """
    try:
        job_applicant = frappe.get_doc("Job Applicant", doc.job_applicant)
        updated = False

        field_mapping = {
            "company": "company",
            "gender": "gender",
            "blood_group": "blood_group",
            "marital_status": "marital_status",
            "place_of_work": "place_of_work",
            "date_of_birth": "date_of_birth",
            "highest_level_of_education": "highest_level_of_education",
            "mpesa_mobile_phone": "mpesa_mobile_phone",
            "ward": "ward",
            "profession": "profession",
            "reason_to_join": "reason_to_join",
            "surname": "last_name",
            "other_names": "first_name",
            "email_id": "personal_email",
            "phone_number": "cell_number",
            "idpassport_number": "id_passport_number",
            "cover_letter": "bio",
            # "profile_photo": "image"
        }

        for applicant_field, employee_field in field_mapping.items():
            if (
                hasattr(job_applicant, applicant_field)
                and job_applicant.get(applicant_field)
                and not doc.get(employee_field)
            ):
                doc.set(employee_field, job_applicant.get(applicant_field))
                updated = True

        table_fields = [
            "disabilities",
            "allergies",
            "trainings",
            "additional_skills",
            "languages",
        ]

        for table_field in table_fields:
            if (
                hasattr(job_applicant, table_field)
                and job_applicant.get(table_field)
                and not doc.get(table_field)
            ):
                if copy_table_data(job_applicant, doc, table_field, table_field):
                    updated = True

        return updated

    except Exception as e:
        frappe.log_error(
            f"Error updating from job applicant {doc.job_applicant}", f"{str(e)}"
        )
        return False
