import json
import re
import random
import string

import frappe
from frappe import _, cint, cstr
from frappe.desk.search import (
    build_for_autosuggest,
    get_std_fields_list,
    LinkSearchResults,
    relevance_sorter,
    sanitize_searchfield,
)
from frappe.model.db_query import get_order_by
from frappe.utils.data import make_filter_tuple
from frappe.utils.file_manager import save_file


@frappe.whitelist(allow_guest=True)
def search_widget(
    doctype: str,
    txt: str,
    query: str | None = None,
    searchfield: str | None = None,
    start: int = 0,
    page_length: int = 10,
    filters: str | None | dict | list = None,
    filter_fields=None,
    as_dict: bool = False,
    reference_doctype: str | None = None,
    ignore_permissions: bool = True,
):

    start = cint(start)

    if isinstance(filters, str):
        filters = json.loads(filters)

    if searchfield:
        sanitize_searchfield(searchfield)

    if not searchfield:
        searchfield = "name"

    standard_queries = frappe.get_hooks().standard_queries or {}

    if not query and doctype in standard_queries:
        query = standard_queries[doctype][-1]

    if query:
        try:
            return frappe.call(
                query,
                doctype,
                txt,
                searchfield,
                start,
                page_length,
                filters,
                as_dict=as_dict,
                reference_doctype=reference_doctype,
                ignore_user_permissions=True,
            )
        except Exception:
            return []

    meta = frappe.get_meta(doctype)

    if isinstance(filters, dict):
        filters_items = filters.items()
        filters = []
        for key, value in filters_items:
            filters.append(make_filter_tuple(doctype, key, value))

    if filters is None:
        filters = []
    or_filters = []

    if txt:
        field_types = {
            "Data",
            "Text",
            "Small Text",
            "Long Text",
            "Link",
            "Select",
            "Read Only",
            "Text Editor",
        }
        search_fields = ["name"]
        if meta.title_field:
            search_fields.append(meta.title_field)

        if meta.search_fields:
            search_fields.extend(meta.get_search_fields())

        for f in search_fields:
            fmeta = meta.get_field(f.strip())
            if not meta.translated_doctype and (
                f == "name" or (fmeta and fmeta.fieldtype in field_types)
            ):
                or_filters.append([doctype, f.strip(), "like", f"%{txt}%"])

    if meta.get("fields", {"fieldname": "enabled", "fieldtype": "Check"}):
        filters.append([doctype, "enabled", "=", 1])
    if meta.get("fields", {"fieldname": "disabled", "fieldtype": "Check"}):
        filters.append([doctype, "disabled", "!=", 1])

    fields = get_std_fields_list(meta, searchfield or "name")
    if filter_fields:
        fields = list(set(fields + json.loads(filter_fields)))
    formatted_fields = [f"`tab{meta.name}`.`{f.strip()}`" for f in fields]

    if meta.show_title_field_in_link and meta.title_field:
        formatted_fields.insert(1, f"`tab{meta.name}`.{meta.title_field} as `label`")

    order_by_based_on_meta = get_order_by(doctype, meta)
    order_by = f"`tab{doctype}`.idx desc, {order_by_based_on_meta}"

    if not meta.translated_doctype:
        _txt = frappe.db.escape((txt or "").replace("%", "").replace("@", ""))
        _relevance = f"(1 / nullif(locate({_txt}, `tab{doctype}`.`name`), 0))"
        formatted_fields.append(f"""{_relevance} as `_relevance`""")
        if frappe.db.db_type == "mariadb":
            order_by = f"ifnull(_relevance, -9999) desc, {order_by}"
        elif frappe.db.db_type == "postgres":
            order_by = f"{len(formatted_fields)} desc nulls last, {order_by}"

    ignore_permissions = True

    values = frappe.get_list(
        doctype,
        filters=filters,
        fields=formatted_fields,
        or_filters=or_filters,
        limit_start=start,
        limit_page_length=None if meta.translated_doctype else page_length,
        order_by=order_by,
        ignore_permissions=ignore_permissions,
        reference_doctype=reference_doctype,
        as_list=not as_dict,
        strict=False,
    )

    if meta.translated_doctype:
        values = (
            result
            for result in values
            if any(
                re.search(f"{re.escape(txt)}.*", _(cstr(value)) or "", re.IGNORECASE)
                for value in (result.values() if as_dict else result)
            )
        )

    values = sorted(values, key=lambda x: relevance_sorter(x, txt, as_dict))

    if not meta.translated_doctype:
        if as_dict:
            for r in values:
                r.pop("_relevance", None)
        else:
            values = [r[:-1] for r in values]

    return values


@frappe.whitelist(allow_guest=True)
def custom_search_link(
    doctype: str,
    txt: str,
    query: str | None = None,
    filters: str | dict | list | None = None,
    page_length: int = 10,
    searchfield: str | None = None,
    reference_doctype: str | None = None,
    ignore_permissions: bool = False,
) -> list[LinkSearchResults]:
    results = search_widget(
        doctype,
        txt.strip(),
        query,
        searchfield=searchfield,
        page_length=page_length,
        filters=filters,
        reference_doctype=reference_doctype,
        ignore_permissions=ignore_permissions,
    )

    return build_for_autosuggest(results, doctype=doctype)


@frappe.whitelist(allow_guest=True)
def get_membership_types():

    return frappe.get_all(
        "Membership Type", fields=["name", "membership_type", "amount"]
    )


@frappe.whitelist(allow_guest=True)
def get_job_openings(filters=None, orFilters=None):
    if not filters:
        filters = {}
    filters["publish"] = 1
    jobs = frappe.get_all(
        "Job Opening",
        filters=filters,
        or_filters=orFilters,
        fields=[
            "job_title",
            "posted_on",
            "closes_on",
            "closed_on",
            "branch",
            "designation",
            "vacancies",
            "location",
            "employment_type",
            "company",
            "department",
            "name",
            "creation",
            "description",
            "status",
            "is_internal",
        ],
        order_by="creation desc",
    )

    for job in jobs:
        job.description = (
            frappe.utils.strip_html_tags(job.description) if job.description else ""
        )
        job.applicants = frappe.db.count("Job Applicant", {"job_title": job.name})
    return jobs


@frappe.whitelist(allow_guest=True)
def get_job_details(job):
    job_details = frappe.db.get_value(
        "Job Opening",
        job,
        [
            "job_title",
            "posted_on",
            "closes_on",
            "closed_on",
            "branch",
            "designation",
            "vacancies",
            "location",
            "employment_type",
            "company",
            "department",
            "name",
            "creation",
            "description",
            "route",
            "status",
            "is_internal",
        ],
        as_dict=1,
    )

    if not job_details:
        return {}

    job_details["applicant_count"] = frappe.db.count(
        "Job Applicant", {"job_title": job_details["name"]}
    )

    if job_details.get("company"):
        company = frappe.db.get_value(
            "Company",
            job_details["company"],
            [
                "company_name",
                "company_logo",
                "website",
                "email",
                "phone_no",
            ],
            as_dict=1,
        )
        job_details.update(company or {})

    return job_details


@frappe.whitelist(allow_guest=True)
def submit_job_application(job_opening: str, **kwargs) -> dict:
    try:
        company, branch = frappe.db.get_value(
            "Job Opening", job_opening, ["company", "branch"]
        )

        user_id = frappe.session.user
        user_doc = None
        if user_id != "Guest":
            user_doc = frappe.get_doc("User", user_id)
            kwargs["surname"] = user_doc.last_name or ""
            first_name = user_doc.first_name or ""
            middle_name = user_doc.middle_name or ""
            kwargs["other_names"] = f"{first_name} {middle_name}".strip()
            kwargs["email_id"] = user_doc.email or ""
            kwargs["gender"] = user_doc.gender or ""
            kwargs["date_of_birth"] = user_doc.birth_date or ""
            kwargs["phone"] = user_doc.phone or user_doc.mobile_no or ""

        employee_fields_map = {
            "surname": "last_name",
            "other_names": "first_name",
            "branch": "branch",
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
            "email_id": "personal_email",
            "phone": "cell_number",
            "idpassport_number": "id_passport_number",
            "cover_letter": "bio",
            "profile_photo": "image",
        }

        if user_doc:
            employee = None
            employee_doc = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
            if employee_doc:
                employee = frappe.get_doc("Employee", employee_doc)
                for app_field, emp_field in employee_fields_map.items():
                    if hasattr(employee, emp_field) and getattr(employee, emp_field):
                        kwargs[app_field] = getattr(employee, emp_field)
        surname = kwargs.pop("surname", "")
        other_names = kwargs.pop("other_names", "")
        name_to_use = f"{other_names} {surname}".strip()

        resume = kwargs.pop("resume", None)
        profile_photo = kwargs.pop("profile_photo", None)

        table_fields = {
            "disabilities": ("disability", None),
            "allergies": ("allergy", None),
            "additional_skills": ("additional_skill", None),
            "trainings": ("training_program", "Training Program"),
            "languages": ("language", "Language"),
        }

        other_languages = kwargs.pop("other_languages", None)
        table_data = {key: kwargs.pop(key, None) for key in table_fields}

        doc_data = {
            "doctype": "Job Applicant",
            "job_title": job_opening,
            "applicant_name": name_to_use,
            "status": "Open",
            "company": company,
            "branch": branch,
            **kwargs,
        }

        job_application = frappe.get_doc(doc_data)
        job_application.insert(ignore_permissions=True)

        if resume:
            frappe.db.set_value(
                "File",
                resume,
                {
                    "attached_to_name": job_application.name,
                    "attached_to_doctype": "Job Applicant",
                    "attached_to_field": "resume_attachment",
                },
                update_modified=False,
            )

        if profile_photo:
            frappe.db.set_value(
                "File",
                profile_photo,
                {
                    "attached_to_name": job_application.name,
                    "attached_to_doctype": "Job Applicant",
                    "attached_to_field": "profile_photo",
                },
                update_modified=False,
            )

        def split_items(value):
            if not value:
                return []
            try:
                parsed = frappe.parse_json(value)
            except Exception:
                parsed = value

            if isinstance(parsed, list):
                items = []
                for v in parsed:
                    items.extend(split_items(v))
                return items

            items = []
            for part in str(parsed).split("\n"):
                items.extend([x.strip() for x in part.split(",") if x.strip()])
            return items

        for key, (fieldname, linked_doctype) in table_fields.items():
            value = table_data.get(key)
            if not value:
                continue

            for item in split_items(value):
                if linked_doctype and not frappe.get_all(
                    linked_doctype, filters={"name": item}, limit=1
                ):
                    frappe.get_doc({"doctype": linked_doctype, "name": item}).insert(
                        ignore_permissions=True
                    )

                job_application.append(key, {fieldname or "value": item})

        if other_languages:
            try:
                parsed = frappe.parse_json(other_languages)
            except Exception:
                parsed = other_languages

            for lang_name in split_items(parsed):
                existing_lang = frappe.get_all(
                    "Language", filters=[["language_name", "like", lang_name]], limit=1
                )
                if existing_lang:
                    lang_doc_name = existing_lang[0].name
                else:
                    unique_code = generate_language_code(lang_name)
                    lang_doc = frappe.get_doc(
                        {
                            "doctype": "Language",
                            "language_name": lang_name,
                            "language_code": unique_code,
                        }
                    ).insert(ignore_permissions=True)
                    lang_doc_name = lang_doc.name

                job_application.append("languages", {"language": lang_doc_name})

        if employee:
            for key, (fieldname, _) in table_fields.items():
                if hasattr(employee, key):
                    child_entries = employee.get(key)
                    if child_entries:
                        for entry in child_entries:
                            skip_fields = [
                                "name",
                                "parent",
                                "parentfield",
                                "parenttype",
                                "idx",
                                "creation",
                                "modified",
                                "owner",
                                "docstatus",
                            ]
                            new_entry_data = {
                                k: v
                                for k, v in entry.as_dict().items()
                                if k not in skip_fields
                            }
                            if new_entry_data:
                                job_application.append(key, new_entry_data)

        job_application.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Job application submitted successfully",
            "name": job_application.name,
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Job Application Submission Error")
        return {
            "success": False,
            "message": f"Failed to submit job application: {str(e)}",
        }


def generate_language_code(language_name):
    alpha_only = "".join([c for c in language_name if c.isalpha()])

    if not alpha_only:
        return "".join(random.choices(string.ascii_lowercase, k=2))

    for length in range(3, len(alpha_only) + 1):
        code = alpha_only[:length].lower()
        if not frappe.db.exists("Language", {"language_code": code}):
            return code

    base_code = alpha_only.lower()
    suffix = "a"

    while frappe.db.exists("Language", {"language_code": base_code + suffix}):
        if suffix[-1] == "z":
            suffix = suffix[:-1] + "aa"
        else:
            suffix = suffix[:-1] + chr(ord(suffix[-1]) + 1)

    return base_code + suffix


@frappe.whitelist(allow_guest=True)
def get_regions():
    return frappe.get_all("Company", filters={"is_group": 0})


@frappe.whitelist(allow_guest=True)
def get_branches():
    return frappe.get_all("Branch", fields=["name", "company"])


@frappe.whitelist(allow_guest=True)
def get_user_info():
    if frappe.session.user == "Guest":
        return None

    user = frappe.db.get_value(
        "User",
        frappe.session.user,
        [
            "name",
            "email",
            "enabled",
            "user_image",
            "full_name",
            "user_type",
            "username",
        ],
        as_dict=1,
    )

    roles = frappe.get_roles(user.name)
    user["roles"] = roles

    employee_name = employee_company = employee_branch = None
    employee_is_volunteer = False

    if frappe.db.exists("Employee", {"user_id": user.name, "status": "Active"}):

        employee = frappe.db.get_value(
            "Employee",
            {"user_id": user.name},
            ["name", "company", "branch", "is_volunteer"],
            as_dict=True,
        )
        if employee:

            employee_name = employee.get("name")
            employee_company = employee.get("company")
            employee_branch = employee.get("branch")
            employee_is_volunteer = True if employee.get("is_volunteer") else False

        user["non_profit_member"] = "Non Profit Member" in roles
        user["employee"] = employee_name
        user["company"] = employee_company
        user["branch"] = employee_branch
        user["is_volunteer"] = employee_is_volunteer

    if frappe.db.exists("Member", {"email_id": user.email}):
        member = frappe.db.get_value(
            "Member",
            {"email_id": user.email},
            ["name", "membership_type"],
            as_dict=True,
        )
        if member:
            user["member"] = member.get("name")
            user["membership_type"] = member.get("membership_type")
            user["is_member"] = True


    if frappe.db.exists("Job Applicant", {"email_id": user.email}):
        applicant = frappe.db.get_value(
            "Job Applicant",
            {"email_id": user.email},
            ["name", "status"],
            as_dict=True,
        )
        if applicant:
            user["job_applicant"] = applicant.get("name")
            user["application_status"] = applicant.get("status")
            user["applied_for"] = applicant.get("job_title")

    return user


def check_app_permission():
    """Check if the user has permission to access the app."""
    if frappe.session.user == "Administrator":
        return True

    roles = frappe.get_roles()
    vmms_roles = ["Volunteer", "Non Profit Member"]
    if any(role in roles for role in vmms_roles):
        return True

    return False


@frappe.whitelist()
def get_events():
    events = frappe.get_all(
        "Event",
        fields=[
            "name",
            "subject",
            "event_category",
            "event_type",
            "starts_on",
            "ends_on",
            "status",
            "description",
        ],
        filters=[{"status": "Open"}],
    )

    for event in events:
        event.description = (
            frappe.utils.strip_html_tags(event.description) if event.description else ""
        )

    return events


@frappe.whitelist()
def confirm_event_status():
    user_info = get_user_info()
    events = get_events()

    confirmed_events = []

    for event in events:
        if frappe.db.exists(
            "Event Participants", {"email": user_info.get("email"), "parent": event.name}
        ):
            confirmed_events.append({"event": event, "confirmed": True})
        else:
            confirmed_events.append({"event": event, "confirmed": False})

    return confirmed_events


@frappe.whitelist()
def attend_event(**kwargs):
    try:

        user_info = get_user_info()

        reference_doctype = reference_docname = ""

        if user_info.get("employee"):
            reference_doctype = "Employee"
            reference_docname = user_info.get("employee")
        else:
            frappe.throw("Only employees can attend events")

        if frappe.db.exists(
            "Event Participants",
            {
                "reference_doctype": reference_doctype,
                "reference_docname": reference_docname,
                "parent": kwargs.get("name"),
                "email": user_info.get("email"),
            },
        ):
            frappe.throw("You are already registered for this event")

        event_participant = frappe.get_doc(
            {
                "doctype": "Event Participants",
                "reference_doctype": reference_doctype,
                "reference_docname": reference_docname,
                "email": user_info.get("email"),
                "parent": kwargs.get("name"),
                "parentfield": "event_participants",
                "parenttype": "Event",
            }
        )

        event_participant.insert(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Attend Event Error")
        frappe.throw("Attend Event Error")


@frappe.whitelist()
def get_projects():
    return frappe.get_all(
        "Project",
        fields=[
            "name",
            "project_name",
            "status",
            "project_type",
            "is_active",
            "percent_complete",
            "priority",
            "expected_start_date",
            "expected_end_date",
        ],
    )


@frappe.whitelist()
def create_availability_slot(slot_data):

    try:

        doc = frappe.get_doc({"doctype": "Volunteer Availability Slot", **slot_data})

        doc.insert(ignore_permissions=True)

        frappe.db.commit()
        return {"success": True, "name": doc.name, "data": doc.as_dict()}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Availability Slot Creation Error")

        frappe.throw("Availability Slot Creation Error")


@frappe.whitelist()
def create_volunteer(user_details):
    volunteer = frappe.new_doc("Employee")
    volunteer.first_name = user_details.fullname
    volunteer.full_name = user_details.fullname
    volunteer.email = user_details.email
    volunteer.phone = user_details.phone
    volunteer.is_volunteer = 1
    volunteer.date_of_joining = frappe.utils.today()
    volunteer.insert(ignore_permissions=True)
    return volunteer.name


@frappe.whitelist()
def create_member(name):
    volunteer_details = frappe.get_doc("Employee", name)
    member = frappe.new_doc("Member")
    member.member_name = volunteer_details.employee_name
    member.email_id = volunteer_details.personal_email
    member.volunteer = volunteer_details.name
    member.insert(ignore_permissions=True)
    return member.name


@frappe.whitelist(allow_guest=True)
def create_link_doc(data: dict):
    try:
        doctype = data.get("doctype")
        if not doctype:
            return {"status": "error", "message": "Missing 'doctype' in data"}

        if not frappe.db.exists("DocType", doctype):
            return {"status": "error", "message": f"Invalid doctype: {doctype}"}

        doc = frappe.get_doc(data).insert(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "name": doc.name}

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Create Link Doc Error")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_doc_info(doctype: str):
    """
    Get doctype metadata: fields, labels, and other configurations
    """
    try:
        if not frappe.db.exists("DocType", doctype):
            frappe.throw(_("Invalid Doctype: {0}").format(doctype))

        meta = frappe.get_meta(doctype)
        fields = [
            {
                "fieldname": f.fieldname,
                "fieldtype": f.fieldtype,
                "label": f.label,
                "options": f.options,
                "reqd": f.reqd,
                "hidden": f.hidden,
                "read_only": f.read_only,
            }
            for f in meta.fields
            if not f.hidden
        ]

        return {
            "doctype": doctype,
            "fields": fields,
            "title_field": meta.title_field,
            "module": meta.module,
            "issingle": meta.issingle,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_doc_info API Error")
        frappe.throw(_("Error fetching doctype info: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def upload_file():
    try:
        if "file" not in frappe.request.files:
            frappe.throw(_("No file attached"))

        upload = frappe.request.files["file"]
        filename = frappe.request.form.get("filename") or upload.filename
        doctype = frappe.request.form.get("doctype")
        docname = frappe.request.form.get("docname")
        folder = frappe.request.form.get("folder")
        is_private = cint(frappe.request.form.get("is_private", 0))

        file_doc = save_file(
            fname=filename,
            content=upload.stream.read(),
            dt=doctype,
            dn=docname,
            folder=folder,
            is_private=is_private,
        )

        frappe.db.commit()
        return {
            "file_url": file_doc.file_url,
            "name": file_doc.name,
            "file_name": file_doc.file_name,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Upload File Failed"))
        frappe.throw(_("Upload failed: {0}").format(str(e)))


@frappe.whitelist()
def fetch_assigned_projects():
    user = frappe.db.get_value("User", frappe.session.user, ["name"])

    volunteer = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not volunteer:
        return []

    assignees = frappe.get_all(
        "Volunteer Deployment Assignee",
        filters={
            "volunteer": volunteer,
            "parenttype": "Volunteer Deployment",
            "status": "Pending",
        },
        fields=["name", "parent"],
    )

    if not assignees:
        return []

    projects = []
    for assignee in assignees:
        deployment_name = assignee.parent  # parent is the Volunteer Deployment name
        assignee_name = assignee.name  # childtable row name

        deployment = frappe.get_doc("Volunteer Deployment", deployment_name)
        if not deployment or not deployment.project:
            continue

        project = frappe.db.get_value(
            "Project",
            deployment.project,
            [
                "name",
                "project_name",
                "status",
                "project_type",
                "is_active",
                "percent_complete",
                "priority",
                "expected_start_date",
                "expected_end_date",
                "priority",
                "notes",
            ],
            as_dict=1,
        )
        if project:
            project["deployment_name"] = assignee_name  # Use childtable row name
            # Add task info if exists
            if getattr(deployment, "task", None):
                task = frappe.db.get_value(
                    "Task",
                    deployment.task,
                    [
                        "name",
                        "subject",
                        "status",
                        "priority",
                        "exp_start_date",
                        "exp_end_date",
                        "project",
                        "description",
                    ],
                    as_dict=1,
                )
                project["task"] = task
            else:
                project["task"] = None
            projects.append(project)

    return projects


@frappe.whitelist()
def accept_assignment(name, accepted=True):
    assignee = frappe.get_doc(
        "Volunteer Deployment Assignee", name, ignore_permissions=True
    )
    assignee.status = "Accepted" if accepted else "Rejected"
    assignee.save(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def get_current_membership():
    if frappe.session.user == "Guest":
        return None

    member = frappe.db.get_value(
        "Member",
        {"email_id": frappe.session.user},
        as_dict=1,
    )

    if not member:
        return None

    membership = frappe.db.get_value(
        "Membership",
        {"member": member.name},
        ["name", "membership_type", "from_date", "to_date", "membership_status"],
        as_dict=1,
    )

    amount = frappe.db.get_value(
        "Membership Type",
        membership.get("membership_type"),
        ["amount"],
        as_dict=1,
    )

    membership["amount"] = amount.get("amount") if amount else 0

    return membership
