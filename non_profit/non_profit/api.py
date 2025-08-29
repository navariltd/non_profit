import json
import re

import frappe
from frappe import _, cint, cstr
from frappe.desk.search import build_for_autosuggest, get_std_fields_list, LinkSearchResults, relevance_sorter, sanitize_searchfield
from frappe.model.db_query import get_order_by
from frappe.utils.data import make_filter_tuple


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
            "Data", "Text", "Small Text", "Long Text", "Link",
            "Select", "Read Only", "Text Editor"
        }
        search_fields = ["name"]
        if meta.title_field:
            search_fields.append(meta.title_field)

        if meta.search_fields:
            search_fields.extend(meta.get_search_fields())

        for f in search_fields:
            fmeta = meta.get_field(f.strip())
            if not meta.translated_doctype and (f == "name" or (fmeta and fmeta.fieldtype in field_types)):
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
def custom_search_link(	doctype: str,
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
def submit_job_application(job_opening, applicant_name, email, phone, cover_letter, resume=None):
    try:
        company, branch = frappe.db.get_value("Job Opening", job_opening, ["company", "branch"])
        
        job_application = frappe.get_doc({
            "doctype": "Job Applicant",
            "job_title": job_opening,
            "applicant_name": applicant_name,
            "email_id": email,
            "phone_number": phone,
            "cover_letter": cover_letter,
            "status": "Open",
            "company": company,
            "branch": branch
        })
        
        if resume:
            job_application.resume_attachment = resume
            
        job_application.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Job application submitted successfully",
            "name": job_application.name
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Application Submission Error")
        return {
            "success": False,
            "message": f"Failed to submit job application: {str(e)}"
        }

@frappe.whitelist(allow_guest=True)
def get_regions():
    return frappe.get_all("Company", filters={"is_group": 0})


@frappe.whitelist(allow_guest=True)
def get_branches():
    return frappe.get_all("Branch")


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

    employee_name, employee_company, employee_branch = frappe.db.get_value(
        "Employee", {"user_id": user.name}, ["name", "company", "branch"]
    )

    user["non_profit_member"] = "Non Profit Member" in roles
    user["volunteer"] = "Volunteer" in roles
    user["employee"] = employee_name if employee_name else None
    user["company"] = employee_company if employee_company else None
    user["branch"] = employee_branch if employee_name else None

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
    return frappe.get_all(
        "Event",
        fields=[
            "name",
            "subject",
            "event_category",
            "event_type",
            "starts_on",
            "ends_on",
            "status",
        ],
    )


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