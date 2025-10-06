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
from frappe.translate import get_all_translations
from datetime import datetime

from non_profit.non_profit.utils import (
    get_current_fiscal_year,
    get_shift_types,
    get_dates_for_day_of_week,
)
from collections import defaultdict
from frappe.utils import getdate


@frappe.whitelist(allow_guest=True)
def get_list(
    doctype,
    fields=None,
    filters=None,
    order_by=None,
    limit_start=0,
    limit_page_length=20,
):
    """
    Override standard get_list to allow fetching lists with ignore_permissions=True
    """
    if not doctype:
        frappe.throw(_("Doctype is required"))

    if isinstance(fields, str):
        fields = json.loads(fields)

    if isinstance(filters, str):
        filters = json.loads(filters)

    if isinstance(order_by, str) and order_by == "null":
        order_by = None

    results = frappe.get_list(
        doctype=doctype,
        fields=fields,
        filters=filters,
        order_by=order_by,
        start=limit_start,
        page_length=limit_page_length,
        ignore_permissions=True,
    )

    return results


@frappe.whitelist(allow_guest=True)
def search_doctype(
    doctype: str,
    name: str | None = None,
    filters: str | None | dict | list = None,
    first: bool = False,
):
    """
    Search for a doctype by name or filters.
    If name is provided, it will return the document with that name.
    If filters are provided, it will return documents matching those filters.
    """
    if not doctype:
        frappe.throw(_("Doctype is required"))

    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid Doctype: {0}").format(doctype))

    if name:
        return frappe.get_doc(doctype, name)

    if isinstance(filters, str):
        filters = json.loads(filters)

    results = frappe.get_all(doctype, filters=filters, as_list=False)

    if first:
        data = frappe.get_doc(doctype, results[0].name) if results else None
        return _convert_table_multiselect(data)

    return results


def _convert_table_multiselect(doc):
    meta = frappe.get_meta(doc.doctype)
    doc_dict = doc.as_dict()

    for df in meta.fields:
        if df.fieldtype == "Table MultiSelect":
            child_doctype = df.options
            child_meta = frappe.get_meta(child_doctype)

            link_field = next(
                (f.fieldname for f in child_meta.fields if f.fieldtype == "Link"),
                None,
            )
            if not link_field:
                continue

            linked_doctype = next(
                (f.options for f in child_meta.fields if f.fieldname == link_field),
                None,
            )
            title_field = frappe.get_meta(linked_doctype).title_field or "name"

            values = []
            for row in doc_dict.get(df.fieldname, []):
                link_value = row.get(link_field)
                if link_value:
                    label = (
                        frappe.db.get_value(linked_doctype, link_value, title_field)
                        or link_value
                    )
                    values.append({"value": link_value, "label": label})

            doc_dict[df.fieldname] = values

    return doc_dict


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
    memberships = frappe.get_all(
        "Membership Type",
        fields=["name", "membership_type", "amount"],
        order_by="amount asc",
    )
    for membership in memberships:
        membership_benefits = frappe.get_all(
            "Membership Benefit", {"parent": membership.name}, ["benefit"]
        )

        if membership_benefits:
            membership["benefits"] = [b.benefit for b in membership_benefits]

    return memberships


@frappe.whitelist(allow_guest=True)
def get_job_openings(filters=None, orFilters=None):
    if not filters:
        filters = {}
    filters["publish"] = 1
    filters["status"] = "Open"
    now = datetime.now()
    filters["posted_on"] = ["<=", now]

    or_filters = orFilters or []

    user = frappe.session.user

    if user == "Guest":
        filters["opportunity_type"] = "Guest"

    regions = None
    if "region" in filters:
        region_value = filters.pop("region")
        if (
            isinstance(region_value, list)
            and region_value
            and isinstance(region_value[0], dict)
        ):
            regions = [item.get("value") for item in region_value if item.get("value")]
        else:
            regions = region_value

    companies = None
    if "company" in filters:
        companies_value = filters.pop("company")
        if (
            isinstance(companies_value, list)
            and companies_value
            and isinstance(companies_value[0], dict)
        ):
            companies = [
                item.get("value") for item in companies_value if item.get("value")
            ]
        else:
            companies = companies_value

    company_list = []

    if regions:
        children = []

        if isinstance(regions, list):
            for region in regions:
                region_children = frappe.get_all(
                    "Company",
                    filters={"parent_company": region},
                    pluck="name",
                )
                children.extend(region_children)
        else:
            children = frappe.get_all(
                "Company",
                filters={"parent_company": regions},
                pluck="name",
            )

        if companies:
            company_list = regions + companies
        else:
            company_list = regions + children

        filters["company"] = ["in", company_list]
    elif companies:
        filters["company"] = ["in", companies]

    jobs = frappe.get_all(
        "Job Opening",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "job_title",
            "posted_on",
            "closes_on",
            "closed_on",
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

    if user != "Guest":
        user_email = frappe.db.get_value("User", user, "email")
        if user_email:
            applied_jobs = frappe.get_all(
                "Job Applicant",
                filters={"email_id": user_email},
                pluck="job_title",
            )
            jobs = [job for job in jobs if job.name not in applied_jobs]

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
            "designation",
            "vacancies",
            "location",
            "employment_type",
            "opportunity_type",
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

    job_details["designation"] = frappe.get_doc(
        "Designation", job_details["designation"]
    ).as_dict()

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


def _attach_file(doc, file_info, field_name=None):
    file_url = file_info.get("file_url") if isinstance(file_info, dict) else file_info
    file_name = file_info.get("file_name") if isinstance(file_info, dict) else None

    if not file_url:
        return

    already_attached = frappe.db.exists(
        "File",
        {
            "attached_to_doctype": doc.doctype,
            "attached_to_name": doc.name,
            "file_url": file_url,
        },
    )
    if already_attached:
        return

    file_doc = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": file_name or file_url.split("/")[-1],
            "file_url": file_url,
            "attached_to_doctype": doc.doctype,
            "attached_to_name": doc.name,
            "is_private": 0,
            "file_size": 0,
            "content": None,
        }
    )

    file_doc.insert(ignore_permissions=True)

    if field_name:
        frappe.db.set_value(
            doc.doctype,
            doc.name,
            {field_name: file_doc.file_url},
        )
        frappe.db.commit()


def handle_attachment_files(application, files_data):
    profile_photo = files_data.get("profile_photo")
    documents = files_data.get("documents")
    resume = files_data.get("resume")
    for doc in documents or []:
        _attach_file(application, doc)
    if resume:
        _attach_file(application, resume, field_name="resume_attachment")

    if profile_photo:
        _attach_file(application, profile_photo, field_name="profile_photo")

    return application


def set_field_value(doc, fieldname, value, fieldtype=None):
    if not fieldtype:
        fieldmeta = frappe.get_meta(doc.doctype).get_field(fieldname)
        fieldtype = fieldmeta.fieldtype

    if fieldtype == "Table MultiSelect":
        child_table = frappe.get_meta(doc.doctype).get_field(fieldname).options
        child_meta = frappe.get_meta(child_table)
        link_field = next(
            (df.fieldname for df in child_meta.fields if df.fieldtype == "Link"), None
        )
        if not link_field:
            frappe.throw(f"No Link field found in child table {child_table}")
        doc.set(fieldname, [])
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and item.get("value"):
                    doc.append(fieldname, {link_field: item["value"]})
                elif isinstance(item, str) and item.strip():
                    doc.append(fieldname, {link_field: item})
        else:
            frappe.throw(
                f"Expected list of values for Table MultiSelect field {fieldname}"
            )

    elif fieldtype == "Table":
        if isinstance(value, list):
            doc.set(fieldname, [])
            child_meta = frappe.get_meta(
                frappe.get_meta(doc.doctype).get_field(fieldname).options
            )
            for row in value:
                if isinstance(row, dict):
                    processed_row = {}
                    for k, v in row.items():
                        if k.startswith("__"):
                            continue
                        df = child_meta.get_field(k)
                        if not df:
                            continue
                        if df.fieldtype in ("Attach", "Attach Image"):
                            if isinstance(v, dict) and v.get("file_url"):
                                processed_row[k] = v["file_url"]
                            elif isinstance(v, str) and v.strip():
                                processed_row[k] = v
                            else:
                                processed_row[k] = None
                        else:
                            processed_row[k] = v
                    has_values = any(
                        val not in (None, "", []) for val in processed_row.values()
                    )
                    if has_values:
                        doc.append(fieldname, processed_row)
        else:
            frappe.throw(f"Expected list of dicts for Table field {fieldname}")

    elif fieldtype in ("Attach", "Attach Image"):
        if isinstance(value, dict) and value.get("file_url"):
            doc.set(fieldname, value["file_url"])
        elif isinstance(value, str):
            doc.set(fieldname, value)
        elif value in (None, "", []):
            doc.set(fieldname, None)
        else:
            frappe.throw(
                f"Expected file url (string) or object with file_url for field {fieldname}"
            )

    else:
        doc.set(fieldname, value)


@frappe.whitelist(allow_guest=True)
def update_job_application(id: str, **kwargs) -> dict:
    try:

        application = frappe.get_doc("Job Applicant", id)

        for fieldname, value in kwargs.items():
            if application.meta.has_field(fieldname):
                fieldtype = application.meta.get_field(fieldname).fieldtype
                set_field_value(application, fieldname, value, fieldtype)

        application.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Application updated successfully",
            "name": application.name,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Application Update Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def submit_job_application(id: str = None) -> dict:
    try:
        if not id or not frappe.db.exists("Job Applicant", id):
            return {"error": "Invalid Job Application ID"}

        application = frappe.get_doc("Job Applicant", id)

        if application.status != "Draft":
            return {"error": "Only applications with status 'Draft' can be submitted."}

        application.status = "Open"
        application.save(ignore_permissions=True)
        frappe.db.commit()
        return {"message": "Application submitted successfully"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def create_job_application(job_opening: str = None, id: str = None, **kwargs) -> dict:
    try:
        if id and frappe.db.exists("Job Applicant", id):
            return update_job_application(id, **kwargs)

        company = kwargs.get("company")

        if job_opening:
            job_opening_data = frappe.db.get_value(
                "Job Opening", job_opening, ["company"]
            )
            if job_opening_data:
                company = job_opening_data or company

        if not company:
            frappe.throw("Company is required")

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
            kwargs["phone_number"] = user_doc.phone or user_doc.mobile_no or ""

        email_id = kwargs.get("email_id")
        if (
            email_id
            and job_opening
            and frappe.db.exists(
                "Job Applicant", {"job_title": job_opening, "email_id": email_id}
            )
        ):
            return {
                "success": False,
                "message": "You have already applied for this position.",
            }

        surname = kwargs.get("surname", "")
        other_names = kwargs.get("other_names", "")
        name_to_use = f"{other_names} {surname}".strip()

        minimal_doc_data = {
            "doctype": "Job Applicant",
            "applicant_name": name_to_use,
            "email_id": email_id,
            "company": company,
            "status": "Draft",
        }

        if job_opening:
            minimal_doc_data["job_title"] = job_opening

        job_application = frappe.get_doc(minimal_doc_data)
        job_application.insert(ignore_permissions=True)
        frappe.db.commit()

        update_fields = kwargs.copy()
        update_fields.pop("email_id", None)
        update_fields.pop("surname", None)
        update_fields.pop("other_names", None)

        return update_job_application(job_application.name, **update_fields)

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
def get_branches():
    return frappe.get_all("Company", filters={"is_group": 0})


@frappe.whitelist(allow_guest=True)
def get_user_info():
    if frappe.session.user == "Guest":
        return "Guest"

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
            "phone",
        ],
        as_dict=1,
    )

    roles = frappe.get_roles(user.name)
    user["roles"] = roles

    job_applicant = frappe.db.get_value(
        "Job Applicant",
        {"email_id": user.email, "is_volunteer": 1},
        ["name", "status"],
        as_dict=True,
    )

    if job_applicant and job_applicant.get("status") == "Open":
        user["is_pending_approval"] = True
    else:
        user["is_pending_approval"] = False

    employee_name = employee_company = None
    employee_is_volunteer = False

    if frappe.db.exists("Employee", {"user_id": user.name, "status": "Active"}):

        employee = frappe.db.get_value(
            "Employee",
            {"user_id": user.name},
            ["name", "company", "is_volunteer"],
            as_dict=True,
        )
        if employee:

            employee_name = employee.get("name")
            employee_company = employee.get("company")
            employee_is_volunteer = True if employee.get("is_volunteer") else False

        user["non_profit_member"] = "Non Profit Member" in roles
        user["employee"] = employee_name
        user["company"] = employee_company
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


@frappe.whitelist(allow_guest=True)
def get_events():
    user_info = get_user_info()

    fields = [
        "name",
        "title",
        "short_description",
        "start_date",
        "start_time",
        "venue",
        "banner_image",
        "event_access",
    ]

    base_filters = {"start_date": [">=", datetime.now().date()]}

    if user_info == "Guest":
        base_filters["event_access"] = ["in", ["Public", "Private"]]

    elif user_info.get("is_member"):
        pass
    elif user_info.get("is_volunteer"):
        base_filters["event_access"] = ["in", ["Public", "Private"]]

    events = frappe.get_all("FE Event", fields=fields, filters=base_filters)

    for event in events:
        event.short_description = (
            frappe.utils.strip_html_tags(event.short_description)
            if event.short_description
            else ""
        )

    return events


@frappe.whitelist(allow_guest=True)
def register_event(event_name, user):
    try:
        user_info = get_user_info()

        if not frappe.db.exists("FE Event", event_name):
            frappe.throw("Event does not exist")

        attendee_registration = frappe.db.get_value(
            "Attendee Registration", {"event": event_name}, "name"
        )
        if not attendee_registration:
            frappe.throw("Attendee Registration not set up for this event")

        if frappe.db.exists(
            "Event Attendee Registration",
            {"parent": event_name, "email": user.get("email")},
        ):
            frappe.throw("This email has already been registered for the event")

        EAR = frappe.new_doc("Event Attendee Registration")
        EAR.parent = event_name
        EAR.parenttype = "Attendee Registration"
        EAR.parentfield = "event_attendees"
        EAR.email = user.get("email")
        EAR.full_name = user.get("full_name")
        EAR.phone_number = user.get("phone")
        EAR.personnel_type = (
            "Guest"
            if user_info == "Guest"
            else (
                "Volunteer"
                if user_info.get("is_volunteer")
                else (
                    "Member"
                    if user_info.get("is_member")
                    else "Employee" if user_info.get("employee") else "Other"
                )
            )
        )

        EAR.insert(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Event Registration Error")
        frappe.throw("Event Registration Error")


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

        if frappe.db.exists(
            "Volunteer Availability Slot",
            {
                "employee": slot_data.get("employee"),
                "starts_on": slot_data.get("starts_on"),
                "ends_on": slot_data.get("ends_on"),
            },
        ):
            frappe.throw("You have already created this availability slot")

        employee = slot_data.get("employee")
        starts_on = slot_data.get("starts_on")
        ends_on = slot_data.get("ends_on")

        conflict_slots = frappe.db.get_all(
            "Volunteer Availability Slot",
            filters={
                "employee": employee,
                "starts_on": ["<", ends_on],
                "ends_on": [">", starts_on],
            },
            fields=["name", "starts_on", "ends_on"],
        )
        if conflict_slots:
            frappe.throw(
                "This slot conflicts with an existing availability slot. Please choose a different time range and check Calendar for existing slots.",
            )

        doc = frappe.get_doc({"doctype": "Volunteer Availability Slot", **slot_data})

        doc.insert(ignore_permissions=True)

        frappe.db.commit()

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Availability Slot Creation Error")

        frappe.throw("Availability Slot Creation Error")


@frappe.whitelist()
def create_availability_schedule(slot_data):
    """
    Creates Personnel Availability Schedule and generates Weekly Schedule Patterns
    """
    try:
        employee = slot_data.get("employee")
        fiscal_year = get_current_fiscal_year()
        weekly_availability = slot_data.get("weekly_availability", {})

        if frappe.db.exists("Personnel Availability Schedule", {"employee": employee}):
            existing_doc = frappe.get_value(
                "Personnel Availability Schedule", {"employee": employee}, "name"
            )
            frappe.delete_doc(
                "Personnel Availability Schedule", existing_doc, ignore_permissions=True
            )

        personal_schedule_name = create_personal_schedule(employee, fiscal_year)
        create_schedule(personal_schedule_name, weekly_availability)

        # generate_weekly_patterns(
        #     personal_schedule_name, weekly_availability, fiscal_year
        # )

        return {"employee": employee}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Availability Schedule Creation Error")
        frappe.throw("Availability Schedule Creation Error")


def create_personal_schedule(employee, fiscal_year):
    """Create or get existing Personnel Availability Schedule"""
    existing = frappe.db.exists(
        "Personnel Availability Schedule",
        {"employee": employee, "fiscal_year": fiscal_year},
    )

    if existing:
        return existing

    schedule_doc = frappe.new_doc("Personnel Availability Schedule")
    schedule_doc.employee = employee
    schedule_doc.fiscal_year = fiscal_year
    schedule_doc.save(ignore_permissions=True)

    return schedule_doc.name


def generate_weekly_patterns(schedule_name, weekly_availability, fiscal_year):
    """Generate individual date/shift records based on weekly pattern"""

    fy_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    start_date = fy_doc.year_start_date
    end_date = fy_doc.year_end_date

    shifts = get_shift_types()

    for day_name, selected_shifts in weekly_availability.items():
        if not selected_shifts:
            continue

        day_dates = get_dates_for_day_of_week(start_date, end_date, day_name)

        for date in day_dates:
            for shift_name in selected_shifts:
                shift_info = next((s for s in shifts if s.name == shift_name), None)
                if shift_info:
                    create_weekly_pattern_record(
                        schedule_name, date, day_name, shift_info
                    )


def create_weekly_pattern_record(schedule_name, date, day_name, shift_info):
    """Create individual Weekly Schedule Pattern record"""

    pattern_doc = frappe.new_doc("Weekly Schedule Pattern")
    pattern_doc.parent = schedule_name
    pattern_doc.parenttype = "Personnel Availability Schedule"
    pattern_doc.parentfield = "available_days"
    pattern_doc.day = date
    pattern_doc.from_time = f"{date} {shift_info.start_time}"
    pattern_doc.to_time = f"{date} {shift_info.end_time}"
    pattern_doc.save(ignore_permissions=True)


def create_schedule(schedule_name, weekly_availability):
    schedule_doc = frappe.new_doc("Schedule")
    schedule_doc.parent = schedule_name
    schedule_doc.parenttype = "Personnel Availability Schedule"
    schedule_doc.parentfield = "schedules"
    for day_name, selected_shifts in weekly_availability.items():
        if not selected_shifts:
            continue
        for shift in selected_shifts:
            schedule_doc = frappe.new_doc("Schedule")
            schedule_doc.parent = schedule_name
            schedule_doc.parenttype = "Personnel Availability Schedule"
            schedule_doc.parentfield = "schedules"
            schedule_doc.day = day_name
            schedule_doc.shift_type = shift
            schedule_doc.insert(ignore_permissions=True)


@frappe.whitelist()
def get_availability_slots():

    user = get_user_info().get("employee")

    parent = frappe.db.get_value(
        "Personnel Availability Schedule", {"employee": user}, "name"
    )
    schedules = frappe.get_all(
        "Schedule",
        filters={"parent": parent},
        fields=["name", "day", "shift_type"],
    )

    return schedules


@frappe.whitelist()
def get_present_slots():
    user = get_user_info().get("employee")

    slot = frappe.db.exists("Personnel Availability Schedule", {"employee": user})

    if slot:
        return True

    return None


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
    volunteer = get_current_volunteer()

    assignees = frappe.get_all(
        "Personnel Deployment Assignment",
        filters={
            "employee": volunteer,
            "status": "Pending",
            "docstatus": 1,
        },
        fields=["name", "deployment"],
    )

    if not assignees:
        return []

    projects = []
    for assignee in assignees:
        deployment_name = assignee.deployment
        assignee_name = assignee.name

        deployment = frappe.get_doc("Personnel Deployment Request", deployment_name)
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
def get_project_details(project_name):

    project = frappe.db.get_value(
        "Project",
        project_name,
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

    project["notes"] = (
        frappe.utils.strip_html_tags(project["notes"])
        if project and project.get("notes")
        else ""
    )

    return project


@frappe.whitelist()
def get_assignment_details(assignment_name):

    assignment = frappe.get_doc(
        "Personnel Deployment Assignment",
        assignment_name,
    ).as_dict()

    if not assignment:
        return {}

    if assignment.get("require_contract_before_deployment") == 1:
        contract = None
        if frappe.db.exists(
            "Contract", {"personnel_deployment_assignment": assignment["name"]}
        ):
            contract = frappe.get_doc(
                "Contract",
                {"personnel_deployment_assignment": assignment["name"]},
            ).as_dict()
        assignment["contract"] = contract

    deployment = frappe.get_doc("Personnel Deployment Request", assignment.deployment)

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
        project["notes"] = (
            frappe.utils.strip_html_tags(project["notes"])
            if project.get("notes")
            else ""
        )

    assignment["project"] = project
    assignment["deployment_details"] = deployment.as_dict()
    assignment["term_details"] = (
        frappe.utils.strip_html_tags(assignment["term_details"])
        if assignment.get("term_details")
        else ""
    )

    return assignment


@frappe.whitelist()
def accept_assignment(name, accepted=True, contract_name=None):

    try:

        if frappe.db.exists("Contract", contract_name):
            frappe.db.set_value("Contract", contract_name, {"is_signed": 1})

        assignee = frappe.get_doc(
            "Personnel Deployment Assignment", name, ignore_permissions=True
        )
        assignee.status = "Accepted" if accepted else "Rejected"
        assignee.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Accept Assignment Error")
        frappe.throw("Accept Assignment Error")


@frappe.whitelist()
def get_current_membership():
    if frappe.session.user == "Guest":
        return []

    member = frappe.db.get_value(
        "Member",
        {"email_id": frappe.session.user},
        ["name"],
        as_dict=True,
    )

    if not member:
        return []

    memberships = frappe.get_all(
        "Membership",
        filters={"member": member.name},
        fields=[
            "name",
        ],
        order_by="from_date desc",
    )

    if not memberships:
        return []

    result = []
    for membership_item in memberships:
        membership = frappe.get_doc("Membership", membership_item.name)
        membership_data = membership.as_dict()

        if membership.membership_type:
            membership_type_doc = frappe.get_doc(
                "Membership Type", membership.membership_type
            )
            membership_data["type_details"] = membership_type_doc.as_dict()

        result.append(membership_data)
    return result


@frappe.whitelist()
def fetch_applications(email: str):
    """
    Fetch all job applications (Job Applicant) for a given email,
    along with related Job Opening details.
    """
    if not email:
        frappe.throw(_("Email is required to fetch job applications."))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"email_id": email, "job_title": ("!=", None), "is_volunteer": 0},
        fields=[
            "name",
            "applicant_name",
            "designation",
            "job_title",
            "status",
            "company",
            "cover_letter",
            "creation",
            "modified",
        ],
        order_by="creation desc",
    )

    if not applicants:
        return []

    for app in applicants:
        job_opening = (
            frappe.get_doc("Job Opening", app.get("job_title")).as_dict()
            if app.get("job_title")
            else {}
        )
        app["job_opening_details"] = job_opening

    return applicants


def get_current_volunteer():
    user = frappe.session.user

    volunteer = frappe.db.get_value("Employee", {"user_id": user}, "name")

    return volunteer


@frappe.whitelist()
def get_dashboard_stats():

    volunteer = get_current_volunteer()

    project_stats = {}

    total_projects_deployed = frappe.db.count(
        "Volunteer Deployment Assignee", {"volunteer": volunteer}
    )
    pending_projects = frappe.db.count(
        "Volunteer Deployment Assignee", {"volunteer": volunteer, "status": "Pending"}
    )
    accepted_projects = frappe.db.count(
        "Volunteer Deployment Assignee", {"volunteer": volunteer, "status": "Accepted"}
    )
    rejected_projects = frappe.db.count(
        "Volunteer Deployment Assignee", {"volunteer": volunteer, "status": "Rejected"}
    )

    project_stats["total_projects_deployed"] = total_projects_deployed
    project_stats["pending_projects"] = pending_projects
    project_stats["accepted_projects"] = accepted_projects
    project_stats["rejected_projects"] = rejected_projects

    return project_stats


@frappe.whitelist()
def get_all_deployed_projects(**kwargs):

    volunteer = get_current_volunteer()

    accepted_filters = {"status": "Accepted"}
    rejected_filters = {"status": "Rejected"}

    deployments = frappe.get_all(
        "Volunteer Deployment Assignee",
        (
            {"volunteer": volunteer} | accepted_filters
            if kwargs.get("accepted")
            else {} | rejected_filters if kwargs.get("rejected") else {}
        ),
        ["parent"],
    )

    project = None
    projects = []
    projects_details = []

    for deployment in deployments:

        project = frappe.db.get_value(
            "Volunteer Deployment", deployment.parent, "project", as_dict=True
        )

        if project:
            projects.append(project)

    for project in projects:
        project_details = frappe.db.get_value(
            "Project",
            project.project,
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
            as_dict=True,
        )
        if project_details:
            projects_details.append(project_details)

    return projects_details


@frappe.whitelist()
def can_edit_job_application(applicant_id: str) -> bool:
    if not applicant_id:
        return False

    try:
        applicant = frappe.get_doc(
            "Job Applicant", applicant_id, ignore_permissions=True
        )

        if applicant.status and applicant.status.lower() != "draft":
            return False

        if applicant.job_title:
            job_opening = frappe.get_doc(
                "Job Opening", applicant.job_title, ignore_permissions=True
            )
            if job_opening.status.lower() != "open":
                return False

        interview = frappe.db.exists("Interview", {"job_applicant": applicant_id})
        if interview:
            return False

        offer = frappe.db.exists("Job Offer", {"job_applicant": applicant_id})
        if offer:
            return False

        return True
    except Exception:
        frappe.log_error(
            frappe.get_traceback(), "Error checking job application edit permission"
        )
        return False


@frappe.whitelist()
def get_meta_info(type, route):
    if frappe.db.exists("Website Meta Tag", {"parent": f"{type}/{route}"}):
        meta_tags = frappe.get_all(
            "Website Meta Tag",
            {
                "parent": f"{type}/{route}",
            },
            ["name", "key", "value"],
        )

        return meta_tags

    return []


@frappe.whitelist()
def update_meta_info(type, route, meta_tags):
    parent_name = f"{type}/{route}"
    if not isinstance(meta_tags, list):
        frappe.throw(_("Meta tags should be a list."))

    for tag in meta_tags:
        existing_tag = frappe.db.exists(
            "Website Meta Tag",
            {
                "parent": parent_name,
                "parenttype": "Website Route Meta",
                "parentfield": "meta_tags",
                "key": tag["key"],
            },
        )
        if existing_tag:
            if not tag.get("value"):
                frappe.db.delete("Website Meta Tag", existing_tag)
                continue
            frappe.db.set_value("Website Meta Tag", existing_tag, "value", tag["value"])
        elif tag.get("value"):
            tag_properties = {
                "parent": parent_name,
                "parenttype": "Website Route Meta",
                "parentfield": "meta_tags",
                "key": tag["key"],
                "value": tag["value"],
            }

            parent_exists = frappe.db.exists("Website Route Meta", parent_name)
            if not parent_exists:
                route_meta = frappe.new_doc("Website Route Meta")
                route_meta.update(
                    {
                        "__newname": parent_name,
                    }
                )
                route_meta.append("meta_tags", tag_properties)
                route_meta.insert()
            else:
                new_tag = frappe.new_doc("Website Meta Tag")
                new_tag.update(tag_properties)
                print(new_tag)
                new_tag.insert()
                print(new_tag.as_dict())


@frappe.whitelist(allow_guest=True)
def get_translations():
    if frappe.session.user != "Guest":
        language = frappe.db.get_value("User", frappe.session.user, "language")
    else:
        language = frappe.db.get_single_value("System Settings", "language")
    return get_all_translations(language)


@frappe.whitelist(allow_guest=True)
def get_branding():
    """Get branding details."""
    website_settings = frappe.get_single("Website Settings")
    image_fields = ["banner_image", "footer_logo", "favicon"]

    for field in image_fields:
        if website_settings.get(field):
            file_info = get_file_info(website_settings.get(field))
            website_settings.update({field: json.loads(json.dumps(file_info))})
        else:
            website_settings.update({field: None})

    return website_settings


@frappe.whitelist()
def get_file_info(file_url):
    """Get file info for the given file URL."""
    file_info = frappe.db.get_value(
        "File",
        {"file_url": file_url},
        ["file_name", "file_size", "file_url"],
        as_dict=1,
    )
    return file_info


@frappe.whitelist()
def get_job_application(name=None):
    if not name:
        return {"error": "Application ID is required"}

    try:
        job_application = frappe.get_doc("Job Applicant", name).as_dict()

        if (
            frappe.session.user != "Administrator"
            and job_application.get("email_id") != frappe.session.user
        ):
            return {"error": "You don't have permission to access this application"}

        if job_application.get("job_title"):
            job_opening = frappe.get_doc(
                "Job Opening", job_application.get("job_title"), ignore_permissions=True
            ).as_dict()
            job_application["job_opening_details"] = job_opening

        return job_application

    except Exception as e:
        frappe.log_error(str(e), "Error fetching job application")
        return {"error": "Failed to retrieve application details"}


@frappe.whitelist(allow_guest=True)
def get_event_details(event_name):

    try:
        event = frappe.get_doc("FE Event", event_name).as_dict()

        event["description"] = (
            frappe.utils.strip_html_tags(event["description"])
            if event.get("description")
            else ""
        )

        event["about"] = (
            frappe.utils.strip_html_tags(event["about"]) if event.get("about") else ""
        )

        return event

    except Exception as e:
        frappe.log_error(str(e), "Error fetching event details")
        return {"error": "Failed to retrieve event details"}


@frappe.whitelist(allow_guest=True)
def get_speaker_profiles(event_speakers):
    try:
        speakers_list = json.loads(event_speakers)

        speaker_profiles = []
        for speaker in speakers_list:

            speaker_profile = frappe.get_doc(
                "Speaker Profile", speaker.get("speaker")
            ).as_dict()
            speaker_profiles.append(speaker_profile)

        return speaker_profiles
    except Exception as e:
        frappe.log_error(title="Speaker Profile Fetch Error", message=str(e))
        frappe.throw("Error fetching speaker profiles")


@frappe.whitelist()
def get_user_details():
    """
    Returns the logged-in user's details.
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw(
            _("You must be logged in to access user details"), frappe.PermissionError
        )

    user_doc = frappe.get_doc("User", frappe.session.user)
    user_info = user_doc.as_dict()

    return user_info


@frappe.whitelist()
def update_user_details(data):
    """
    Updates the logged-in user's details.
    `data` should be a dict of fields to update.
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw(
            _("You must be logged in to update your profile"), frappe.PermissionError
        )

    if isinstance(data, str):
        import json

        try:
            data = json.loads(data)
        except Exception:
            frappe.throw(_("Invalid data format"))

    user_doc = frappe.get_doc("User", frappe.session.user)

    for field, value in data.items():
        if hasattr(user_doc, field):
            setattr(user_doc, field, value)
        else:
            frappe.throw(_("Field {0} does not exist on User").format(field))

    user_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": _("Profile updated successfully")}
